"""分類器：一段原始關鍵點 → gloss 與機率。只用 CPU 版 onnxruntime。

前處理一律走 wlasl.dataset.prepare，和訓練、本機驗證是同一個函式，不在後端另寫一份。
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from wlasl.dataset import BG, prepare, resample_mode
from wlasl.spotter import Prediction


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max(-1, keepdims=True))
    return e / e.sum(-1, keepdims=True)


class Classifier:
    def __init__(self, model_dir: Path):
        import onnxruntime as ort

        opts = ort.SessionOptions()
        opts.log_severity_level = 3
        # 模型很小，單執行緒就夠；把 CPU 留給 MediaPipe
        opts.intra_op_num_threads = 1
        self.session = ort.InferenceSession(str(model_dir / "model.onnx"), opts, providers=["CPUExecutionProvider"])
        labels: list[str] = json.loads((model_dir / "labels.json").read_text(encoding="utf-8"))
        # 有背景類（不是詞）的模型：最後一類是背景，不列進詞彙與候選
        self.has_background = labels[-1] == BG
        self.labels = labels[:-1] if self.has_background else labels
        self.run_name = model_dir.name
        self.mode = resample_mode(model_dir)

    def logits(self, raw: np.ndarray) -> np.ndarray:
        return self.session.run(None, {"keypoints": prepare(raw, mode=self.mode)[None]})[0][0]

    def predict(self, raw: np.ndarray) -> Prediction:
        """raw：(T, K, 3) 未正規化的關鍵點。"""
        probs = softmax(self.logits(raw))
        bg = float(probs[-1]) if self.has_background else 0.0
        return _prediction(self.labels, probs[: len(self.labels)], bg)


class Ensemble:
    """兩個獨立訓練的模型平均詞機率：模型沒把握時比較不會一起錯，詞彙表外的詞才不容易過信心門檻（docs/open-set/report.md）。

    use_background：窗口偵測用，另外回報最後一個模型的背景類機率（docs/spot-gate/report.md）。
    """

    def __init__(self, *classifiers: Classifier, use_background: bool = False):
        self.classifiers = classifiers
        self.labels = classifiers[0].labels
        self.run_name = "+".join(c.run_name for c in classifiers)
        self.use_background = use_background

    def predict(self, raw: np.ndarray) -> Prediction:
        n = len(self.labels)
        logits = [c.logits(raw) for c in self.classifiers]
        words = np.mean([softmax(x[:n]) for x in logits], axis=0)
        return _prediction(self.labels, words, float(softmax(logits[-1])[-1]) if self.use_background else 0.0)


def _prediction(labels: list[str], words: np.ndarray, background: float = 0.0) -> Prediction:
    order = np.argsort(-words)[:5]
    top5 = [(labels[i], float(words[i])) for i in order]
    return Prediction(gloss=top5[0][0], prob=top5[0][1], top5=top5, background=background)
