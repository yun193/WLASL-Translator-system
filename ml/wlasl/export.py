"""匯出（Kaggle）：best.pt → model.onnx + labels.json + reference.npz + metrics.json。

reference.npz 存 test split 的模型輸入與 PyTorch logits，本機驗證時拿同一份輸入跑 ONNX 比對，
確認匯出沒有走樣；test 指標本身留給本機 evaluate.py 算，這裡只記錄 val。
若環境有 onnxruntime，匯出後立刻在 Kaggle 端先比對一次，壞掉就直接報錯。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from wlasl.dataset import load_raw, load_split, prepare
from wlasl.landmarks import K
from wlasl.model import SignTransformer


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--ckpt", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--opset", type=int, default=17)
    args = ap.parse_args(argv)

    ck = torch.load(args.ckpt, map_location="cpu", weights_only=False)
    model = SignTransformer(**ck["config"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    seq_len = ck["config"]["seq_len"]

    # 關掉 MHA fast path：它的融合算子無法匯出成 ONNX
    torch.backends.mha.set_fastpath_enabled(False)
    onnx_path = args.out / "model.onnx"
    dummy = torch.zeros(1, seq_len, K, 3)
    torch.onnx.export(
        model, (dummy,), str(onnx_path), input_names=["keypoints"], output_names=["logits"],
        dynamic_axes={"keypoints": {0: "batch"}, "logits": {0: "batch"}}, opset_version=args.opset, dynamo=False,
    )
    (args.out / "labels.json").write_text(json.dumps(ck["labels"], ensure_ascii=False, indent=1), encoding="utf-8")

    splits, _ = load_split(args.data)
    te = splits["test"]
    x = np.stack([prepare(s) for s in load_raw(args.data, te)])
    with torch.no_grad():
        logits = model(torch.from_numpy(x)).numpy()
    np.savez_compressed(args.out / "reference.npz", inputs=x, logits=logits,
                        video_ids=np.array([r["video_id"] for r in te]), labels=np.array([r["label"] for r in te]))

    metrics = {"best_epoch": ck["epoch"], "val": ck["val"], "seq_len": seq_len, "opset": args.opset,
               "torch": torch.__version__}
    try:
        import onnxruntime as ort

        sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        ort_logits = sess.run(None, {"keypoints": x})[0]
        diff = float(np.abs(ort_logits - logits).max())
        metrics["kaggle_onnx_max_abs_diff"] = diff
        print(f"ONNX 與 PyTorch logits 最大差 {diff:.2e}", flush=True)
        if diff > 1e-3:
            raise RuntimeError(f"ONNX 匯出走樣：最大差 {diff}")
    except ImportError:
        print("沒有 onnxruntime，略過 Kaggle 端比對", flush=True)
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    print(json.dumps(metrics, indent=1), flush=True)


if __name__ == "__main__":
    main()
