# 單字手語辨識（ISLR）相關研究與可移植做法

> 2026-11-14 調研｜目的：找出能提高「換人泛化、top-1、顯示正確率」的架構與訓練做法

## 現況定位

| 基準 | 方法 | top-1 |
| --- | --- | --- |
| ASL Citizen test（2,731 詞、換人） | 原論文 I3D（RGB）／ST-GCN（pose） | 63%／59.5% |
| 同上 | SHuBERT（1,000 小時 ASL 自監督預訓練，ACL 2025） | 約 65% |
| 同上 | TCN 模型，加手性正規化／不加 | **74%**／69%（排行榜，2026-04，未找到原文） |
| **我們**（ASL Citizen test 中的 1,159 詞、換人） | Transformer＋MediaPipe pose | **81%** |
| WLASL2000（看過的人） | NLA-SLR（RGB＋關鍵點熱圖）／SAM-SLR（多模態） | 61%／59% |
| 同上 | Logos 預訓練（2025） | 67% |
| **我們** | 同上，雙模型 | **49%** |

- 我們的 ASL Citizen 只測 1,159 詞，比原基準的 2,731 詞容易，兩邊數字不能直接比。
- 這至少說明我們在「換人」這一項沒有落後。
- 差距主要在 WLASL 網路影片，以 RGB 為主的方法在那裡領先 10～15 點。

## 頂尖做法與我們的差異

| 做法 | 來源 | 我們目前 | 可能幫助 |
| --- | --- | --- | --- |
| **手性正規化**：判斷慣用手，左撇子整段鏡像成右手 | ASL Citizen 排行榜 TCN（+5 點）；Kaggle GISLR 前幾名 | 只有 50% 隨機鏡像增強，沒有正規化 | 換人泛化（手語者的慣用手不同） |
| **手部局部座標**：每隻手以手腕為原點、手掌大小為單位 | GISLR 前幾名、SignBart 的消融 | 只用以肩膀為準的全身座標 | 手形相近的詞（手指細節不被手臂位置淹沒） |
| **臉／嘴唇關鍵點** | GISLR 1、2 名都大量用嘴唇點；SHuBERT 有臉部流 | 只有 7 個粗略的臉部點（鼻、眼、耳、嘴角） | 位置在臉上的詞、非手部特徵 |
| **距離／角度特徵**（手指間距離、骨架角度） | GISLR 第 2 名、SL-GCN 多流 | 只有座標＋速度 | 對體型、鏡頭距離更不敏感 |
| **1D 卷積＋Transformer 混合** | GISLR 第 1 名（Conv1D 區塊和 Transformer 交替） | 純 Transformer | 局部時間的動作模式 |
| **重正則化，練更久**：late dropout、AWP 對抗權重擾動、數百輪 | GISLR 第 1 名 | 100 輪，最佳在第 89 輪，train／val loss 1.4 vs 2.7 | 還沒收斂，又有過擬合，兩者並存 |
| **多 seed／多流集成** | GISLR、SAM-SLR | 2 個模型集成 | 通常 +1～3 點 |
| **語意感知 label smoothing**：同義詞的標籤互相分一點機率 | NLA-SLR | 一般 label smoothing 0.1 | hurt/pain、hug/love 這類錯誤 |
| 大規模自監督預訓練 | SHuBERT、Uni-Sign | 無 | 有幫助，但要上千小時的影片，成本太高 |

## 建議實驗（依「效益／成本」排序）

每個實驗都是一次 Kaggle 重訓（約 2.5 小時），本機用 `vocab2000.py` 量換人 top-1，比較時固定同一套門檻流程。

1. **手性正規化＋手部局部座標**
   - 只改特徵，前處理不必重跑（關鍵點已經有），預期效益最大。
2. **加嘴唇／臉部關鍵點**
   - 要改 landmarks 並重跑全部前處理（WLASL＋ASL Citizen 約 4.5 萬支），成本高，放在第 1 項之後。
3. **Conv1D＋Transformer 混合、late dropout、練 200～300 輪**
4. **同義類語意 smoothing**：WLASL 本身有同手勢不同詞的情況，或是改成上線時合併顯示。

## 來源

- [ASL Citizen 論文](https://arxiv.org/pdf/2304.05934)｜[ASL Citizen 排行榜](https://sota2.com/research/sota/isolated-sign-recognition-on-asl-citizen)
- [SHuBERT](https://arxiv.org/abs/2411.16765)｜[SignBart](https://arxiv.org/abs/2506.21592)
- [GISLR 第 1 名](https://www.kaggle.com/competitions/asl-signs/discussion/406684)（[程式](https://github.com/hoyso48/Google---Isolated-Sign-Language-Recognition-1st-place-solution)）｜[GISLR 第 2 名](https://github.com/ffs333/2nd_place_GISLR)
- [WLASL2000 排行榜](https://hyper.ai/cn/sota/tasks/sign-language-recognition/benchmark/wlasl-2000)（NLA-SLR、SAM-SLR）
- [ASL Citizen 正規化消融（Perkins 等，2025）](https://arxiv.org/html/2512.14876v1)：逐幀質心正規化比原始座標高 16 點
