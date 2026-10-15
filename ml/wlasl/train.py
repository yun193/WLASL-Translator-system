"""訓練進入點（Kaggle）。單卡直接 python -m，多卡用 torchrun：

  torchrun --nproc_per_node=2 -m wlasl.train --data <前處理產出> --out /kaggle/working

產出：best.pt（含模型設定）、history.json（每個 epoch 的 loss 與 val 指標）。
關鍵點全部載入記憶體（WLASL2000 約 1 萬支、數百 MB）；增強在 DataLoader worker 裡用 numpy 做。

--classes 決定拿多少類一起訓練，--eval-classes 決定挑模型與匯出時看前幾類：
例如 --classes 2000 --eval-classes 100 是用 WLASL2000 全部資料學表示，但只對 WLASL100 負責。
val 另外量「上線條件」：切詞器決定起訖、每 3 幀取 1 幀（約 10 fps）三種相位的 top-1 與相位間一致率。
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

from wlasl.augment import augment, choose_span
from wlasl.dataset import labeled_span, load_raw, load_split, prepare
from wlasl.model import SignTransformer
from wlasl.segmenter import segment_spans


class TrainSet(Dataset):
    def __init__(self, raws, records, seed, mode, p_segmenter, subsample):
        self.raws, self.seed, self.mode = raws, seed, mode
        self.p_segmenter, self.subsample = p_segmenter, subsample
        self.labels = [r["label"] for r in records]
        self.fps = [r.get("fps") or 25.0 for r in records]
        self.labeled = [labeled_span(r, len(s)) for r, s in zip(records, raws)]
        # 切詞器範圍只和關鍵點有關，先算好；fork 出來的 DataLoader worker 共用
        self.segmented = [segment_spans(s, f) for s, f in zip(raws, self.fps)] if p_segmenter > 0 else None
        self.epoch = 0

    def __len__(self):
        return len(self.raws)

    def __getitem__(self, i):
        rng = np.random.default_rng((self.seed, self.epoch, i))
        seq = self.raws[i]
        a, b = choose_span(len(seq), self.labeled[i], self.segmented[i] if self.segmented else [], self.fps[i],
                           rng, p_segmenter=self.p_segmenter)
        x = prepare(augment(seq[a:b], rng, subsample=self.subsample), mode=self.mode)
        return torch.from_numpy(x), self.labels[i]


def live_inputs(raws, records, mode, stride=3) -> list[np.ndarray]:
    """模擬上線：切詞器決定起訖（找不到就用標註），每 stride 幀取 1 幀，每種相位一組輸入。"""
    phases = [[] for _ in range(stride)]
    for r, s in zip(records, raws):
        lab = labeled_span(r, len(s))
        segs = segment_spans(s, r.get("fps") or 25.0)
        a, b = max(segs, key=lambda x: min(x[1], lab[1]) - max(x[0], lab[0])) if segs else lab
        for p in range(stride):
            clip = s[a:b][p::stride]
            phases[p].append(prepare(clip if len(clip) else s[a:b], mode=mode))
    return [np.stack(x) for x in phases]


@torch.no_grad()
def predict(model, x, device, n_eval, bs=256):
    model.eval()
    return torch.cat([model(x[i : i + bs].to(device)).float().cpu()[:, :n_eval] for i in range(0, len(x), bs)])


@torch.no_grad()
def evaluate(model, x, y, device, n_eval, bs=256):
    logits = predict(model, x, device, n_eval, bs)
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
    ap.add_argument("--classes", type=int, default=0, help="拿前 N 類一起訓練；0 = labels.json 全部")
    ap.add_argument("--eval-classes", type=int, default=100, help="挑模型、匯出只看前 N 類")
    ap.add_argument("--resample", choices=["linear", "nearest"], default="linear")
    ap.add_argument("--p-segmenter", type=float, default=0.5, help="訓練時用切詞器起訖取代標註起訖的機率")
    ap.add_argument("--no-subsample", action="store_true", help="關掉時間抽幀增強")
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

    splits, labels = load_split(args.data, args.classes or None)
    n_eval = min(args.eval_classes, len(labels))
    tr = splits["train"]
    train_set = TrainSet(load_raw(args.data, tr), tr, args.seed, args.resample, args.p_segmenter,
                         not args.no_subsample)
    sampler = DistributedSampler(train_set, world, rank, shuffle=True, seed=args.seed) if ddp else None
    loader = DataLoader(train_set, args.bs, shuffle=sampler is None, sampler=sampler, num_workers=2,
                        drop_last=True, persistent_workers=False)
    va = [r for r in splits["val"] if r["label"] < n_eval]
    val_raw = load_raw(args.data, va)
    val_x = torch.from_numpy(np.stack([prepare(s[slice(*labeled_span(r, len(s)))], mode=args.resample)
                                       for r, s in zip(va, val_raw)]))
    val_y = torch.tensor([r["label"] for r in va])
    live_x = [torch.from_numpy(x) for x in live_inputs(val_raw, va, args.resample)]

    model = SignTransformer(len(labels), d=args.d, layers=args.layers, ff=args.d * 2).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    net = DDP(model, device_ids=[local] if device.type == "cuda" else None) if ddp else model
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.wd)
    steps_per_epoch = len(loader)
    total = args.epochs * steps_per_epoch
    warm = min(args.warmup, args.epochs - 1) * steps_per_epoch  # epochs ≤ warmup（如冒煙測試）時仍留一段 cosine
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: (s + 1) / warm if s < warm else 0.5 * (1 + math.cos(math.pi * (s - warm) / max(total - warm, 1)))
    )
    crit = nn.CrossEntropyLoss(label_smoothing=args.smoothing)
    if main_proc:
        print(f"params={n_params:,} classes={len(labels)} eval_classes={n_eval} train={len(tr)} val={len(va)} "
              f"steps/epoch={steps_per_epoch}", flush=True)

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
            m = evaluate(model, val_x, val_y, device, n_eval)
            live = [predict(model, x, device, n_eval).argmax(1) for x in live_x]
            m["live_top1"] = float(np.mean([(p == val_y).float().mean().item() for p in live]))
            m["live_agree"] = float(torch.stack(live).eq(live[0]).all(0).float().mean().item())
            m.update(epoch=epoch, train_loss=tot / n, lr=sched.get_last_lr()[0])
            history.append(m)
            if best is None or (m["top1"], -m["loss"]) > (best["top1"], -best["loss"]):
                best = m
                torch.save({"state_dict": model.state_dict(), "config": model.config, "labels": labels,
                            "eval_classes": n_eval, "resample": args.resample,
                            "epoch": epoch, "val": m}, args.out / "best.pt")
            if epoch % 10 == 0 or epoch == args.epochs - 1:
                print(f"ep {epoch:3d}  train {m['train_loss']:.3f}  val loss {m['loss']:.3f}  "
                      f"top1 {m['top1']:.3f}  top5 {m['top5']:.3f}  live {m['live_top1']:.3f}/{m['live_agree']:.2f}  best {best['top1']:.3f}@{best['epoch']}  "
                      f"{time.time() - t0:.0f}s", flush=True)
    if main_proc:
        (args.out / "history.json").write_text(json.dumps({"args": {k: str(v) for k, v in vars(args).items()},
                                                            "params": n_params, "best": best, "history": history}, indent=1))
    if ddp:
        dist.destroy_process_group()


if __name__ == "__main__":
    main()
