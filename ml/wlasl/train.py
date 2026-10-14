"""訓練進入點（Kaggle）。單卡直接 python -m，多卡用 torchrun：

  torchrun --nproc_per_node=2 -m wlasl.train --data <前處理產出> --out /kaggle/working

產出：best.pt（含模型設定）、history.json（每個 epoch 的 loss 與 val 指標）。
資料只有上千支，全部載入記憶體；增強在 DataLoader worker 裡用 numpy 做。
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, Dataset, DistributedSampler

from wlasl.augment import augment
from wlasl.dataset import load_raw, load_split, prepare
from wlasl.model import SignTransformer


class TrainSet(Dataset):
    def __init__(self, raws, labels, seed):
        self.raws, self.labels, self.seed = raws, labels, seed
        self.epoch = 0

    def __len__(self):
        return len(self.raws)

    def __getitem__(self, i):
        rng = np.random.default_rng((self.seed, self.epoch, i))
        return torch.from_numpy(prepare(augment(self.raws[i], rng))), self.labels[i]


@torch.no_grad()
def evaluate(model, x, y, device, bs=256):
    model.eval()
    logits = torch.cat([model(x[i : i + bs].to(device)).float().cpu() for i in range(0, len(x), bs)])
    loss = nn.functional.cross_entropy(logits, y).item()
    top5 = logits.topk(5, dim=1).indices
    return {
        "loss": loss,
        "top1": (top5[:, 0] == y).float().mean().item(),
        "top5": (top5 == y[:, None]).any(1).float().mean().item(),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--epochs", type=int, default=300)
    ap.add_argument("--bs", type=int, default=32, help="每張卡的 batch")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--wd", type=float, default=0.05)
    ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--smoothing", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--d", type=int, default=128)
    ap.add_argument("--layers", type=int, default=4)
    args = ap.parse_args(argv)

    ddp = "WORLD_SIZE" in os.environ
    if ddp:
        dist.init_process_group("nccl" if torch.cuda.is_available() else "gloo")
        rank, world = dist.get_rank(), dist.get_world_size()
        local = int(os.environ["LOCAL_RANK"])
    else:
        rank, world, local = 0, 1, 0
    device = torch.device(f"cuda:{local}" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(args.seed)
    main_proc = rank == 0
    if main_proc:
        args.out.mkdir(parents=True, exist_ok=True)
        print(f"world={world} device={device} torch={torch.__version__}", flush=True)

    splits, labels = load_split(args.data)
    tr = splits["train"]
    train_set = TrainSet(load_raw(args.data, tr), [r["label"] for r in tr], args.seed)
    sampler = DistributedSampler(train_set, world, rank, shuffle=True, seed=args.seed) if ddp else None
    loader = DataLoader(train_set, args.bs, shuffle=sampler is None, sampler=sampler, num_workers=2,
                        drop_last=True, persistent_workers=False)
    va = splits["val"]
    val_x = torch.from_numpy(np.stack([prepare(s) for s in load_raw(args.data, va)]))
    val_y = torch.tensor([r["label"] for r in va])

    model = SignTransformer(len(labels), d=args.d, layers=args.layers, ff=args.d * 2).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    net = DDP(model, device_ids=[local] if device.type == "cuda" else None) if ddp else model
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.wd)
    steps_per_epoch = len(loader)
    total = args.epochs * steps_per_epoch
    warm = args.warmup * steps_per_epoch
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: (s + 1) / warm if s < warm else 0.5 * (1 + math.cos(math.pi * (s - warm) / (total - warm)))
    )
    crit = nn.CrossEntropyLoss(label_smoothing=args.smoothing)
    if main_proc:
        print(f"params={n_params:,} train={len(tr)} val={len(va)} steps/epoch={steps_per_epoch}", flush=True)

    history, best, t0 = [], None, time.time()
    for epoch in range(args.epochs):
        net.train()
        train_set.epoch = epoch
        if sampler:
            sampler.set_epoch(epoch)
        tot, n = 0.0, 0
        for x, y in loader:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            loss = crit(net(x), y)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            tot, n = tot + loss.item() * len(y), n + len(y)
        if main_proc:
            m = evaluate(model, val_x, val_y, device)
            m.update(epoch=epoch, train_loss=tot / n, lr=sched.get_last_lr()[0])
            history.append(m)
            if best is None or (m["top1"], -m["loss"]) > (best["top1"], -best["loss"]):
                best = m
                torch.save({"state_dict": model.state_dict(), "config": model.config, "labels": labels,
                            "epoch": epoch, "val": m}, args.out / "best.pt")
            if epoch % 10 == 0 or epoch == args.epochs - 1:
                print(f"ep {epoch:3d}  train {m['train_loss']:.3f}  val loss {m['loss']:.3f}  "
                      f"top1 {m['top1']:.3f}  top5 {m['top5']:.3f}  best {best['top1']:.3f}@{best['epoch']}  "
                      f"{time.time() - t0:.0f}s", flush=True)
    if main_proc:
        (args.out / "history.json").write_text(json.dumps({"args": {k: str(v) for k, v in vars(args).items()},
                                                            "params": n_params, "best": best, "history": history}, indent=1))
    if ddp:
        dist.destroy_process_group()


if __name__ == "__main__":
    main()
