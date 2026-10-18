# 模型輸出：w100（20261018-w2000n，100 詞）

- 流程和後端影片檔模式相同：原生 fps 逐幀關鍵點 → 切詞器（手放下 0.5 秒切詞、單詞上限 4 秒）→ 分類
- 影片 71138 幀（29.97 fps、39:33.64），有手的幀 97%
- 切出 574 個詞；長度中位 4.00 秒，碰到 4 秒上限的 100%
- 信心 ≥ 0.5 的 148 個；低於門檻顯示成 ?(前 3 名)

## 切詞器輸出（和網頁上看到的一樣）

| 開始 | 結束 | 長度 | 輸出 | 信心 | 前 3 名 |
| --- | --- | --- | --- | --- | --- |
| 00:05.61 | 00:09.61 | 4.0s | ? | 25% | last 25% / graduate 11% / now 6% |
| 00:09.64 | 00:13.65 | 4.0s | ? | 26% | last 26% / secretary 15% / letter 10% |
| 00:13.68 | 00:17.68 | 4.0s | black | 88% | black 88% / book 2% / thin 2% |
| 00:17.72 | 00:21.72 | 4.0s | accident | 95% | accident 95% / jacket 2% / dark 1% |
| 00:21.75 | 00:25.76 | 4.0s | ? | 16% | last 16% / paint 9% / book 6% |
| 00:25.79 | 00:29.80 | 4.0s | ? | 49% | last 49% / before 8% / graduate 6% |
| 00:29.83 | 00:33.83 | 4.0s | ? | 36% | later 36% / last 19% / thanksgiving 5% |
| 00:33.87 | 00:37.87 | 4.0s | ? | 16% | decide 16% / cool 6% / dark 6% |
| 00:37.91 | 00:41.91 | 4.0s | ? | 20% | want 20% / man 17% / thanksgiving 13% |
| 00:41.94 | 00:45.95 | 4.0s | ? | 47% | last 47% / medicine 11% / work 5% |
| 00:45.98 | 00:49.98 | 4.0s | ? | 29% | before 29% / cool 10% / help 5% |
| 00:50.02 | 00:54.02 | 4.0s | ? | 22% | letter 22% / last 16% / cool 16% |
| 00:54.05 | 00:58.06 | 4.0s | ? | 18% | decide 18% / graduate 17% / birthday 12% |
| 00:58.09 | 01:02.09 | 4.0s | secretary | 71% | secretary 71% / city 7% / all 7% |
| 01:02.13 | 01:06.13 | 4.0s | ? | 47% | graduate 47% / jacket 21% / all 18% |
| 01:06.17 | 01:10.17 | 4.0s | ? | 32% | last 32% / accident 13% / thin 9% |
| 01:10.20 | 01:14.21 | 4.0s | ? | 15% | graduate 15% / decide 9% / accident 6% |
| 01:14.24 | 01:18.25 | 4.0s | ? | 20% | change 20% / pizza 15% / last 10% |
| 01:18.28 | 01:22.28 | 4.0s | ? | 41% | before 41% / last 5% / give 4% |
| 01:22.32 | 01:26.32 | 4.0s | ? | 44% | accident 44% / decide 29% / clothes 2% |
| 01:26.35 | 01:30.36 | 4.0s | ? | 26% | last 26% / what 20% / now 10% |
| 01:30.39 | 01:34.39 | 4.0s | ? | 37% | change 37% / accident 8% / black 7% |
| 01:34.43 | 01:38.43 | 4.0s | ? | 11% | accident 11% / wrong 10% / kiss 7% |
| 01:38.47 | 01:42.47 | 4.0s | ? | 39% | decide 39% / thin 33% / black 6% |
| 01:42.50 | 01:46.51 | 4.0s | last | 74% | last 74% / accident 3% / meet 2% |
| 01:46.54 | 01:50.54 | 4.0s | ? | 16% | accident 16% / last 14% / right 11% |
| 01:50.58 | 01:54.58 | 4.0s | what | 65% | what 65% / last 18% / graduate 2% |
| 01:54.61 | 01:58.62 | 4.0s | ? | 18% | jacket 18% / all 12% / cook 7% |
| 01:58.65 | 02:02.66 | 4.0s | before | 77% | before 77% / cook 4% / change 2% |
| 02:02.69 | 02:06.69 | 4.0s | last | 66% | last 66% / pizza 5% / graduate 4% |
| 02:06.73 | 02:10.73 | 4.0s | ? | 28% | accident 28% / secretary 24% / year 19% |
| 02:10.76 | 02:14.77 | 4.0s | ? | 20% | accident 20% / same 8% / short 7% |
| 02:14.80 | 02:18.81 | 4.0s | ? | 45% | graduate 45% / last 12% / secretary 10% |
| 02:18.84 | 02:22.84 | 4.0s | change | 78% | change 78% / accident 6% / secretary 3% |
| 02:22.88 | 02:26.88 | 4.0s | jacket | 50% | jacket 50% / many 19% / graduate 6% |
| 02:26.91 | 02:30.92 | 4.0s | ? | 39% | all 39% / secretary 14% / later 6% |
| 02:30.95 | 02:34.96 | 4.0s | ? | 20% | wrong 20% / accident 17% / now 17% |
| 02:34.99 | 02:38.99 | 4.0s | ? | 46% | graduate 46% / all 8% / candy 6% |
| 02:39.03 | 02:43.03 | 4.0s | accident | 67% | accident 67% / play 5% / clothes 4% |
| 02:43.06 | 02:47.07 | 4.0s | ? | 21% | change 21% / computer 18% / accident 16% |
| 02:47.10 | 02:51.10 | 4.0s | ? | 35% | decide 35% / work 12% / enjoy 4% |
| 02:51.14 | 02:55.14 | 4.0s | last | 86% | last 86% / letter 6% / what 3% |
| 02:55.18 | 02:59.18 | 4.0s | ? | 20% | secretary 20% / accident 16% / family 14% |
| 02:59.21 | 03:03.22 | 4.0s | ? | 17% | all 17% / finish 10% / decide 5% |
| 03:03.25 | 03:07.25 | 4.0s | change | 54% | change 54% / accident 9% / family 4% |
| 03:07.29 | 03:11.29 | 4.0s | ? | 32% | basketball 32% / dark 21% / accident 11% |
| 03:11.32 | 03:15.33 | 4.0s | ? | 35% | finish 35% / play 6% / thanksgiving 5% |
| 03:15.36 | 03:19.37 | 4.0s | ? | 32% | all 32% / accident 11% / what 5% |
| 03:19.40 | 03:23.40 | 4.0s | ? | 24% | decide 24% / book 10% / help 6% |
| 03:23.44 | 03:27.44 | 4.0s | ? | 28% | all 28% / decide 20% / forget 14% |
| 03:27.47 | 03:31.48 | 4.0s | ? | 21% | computer 21% / study 17% / shirt 8% |
| 03:31.51 | 03:35.51 | 4.0s | ? | 31% | pizza 31% / accident 11% / language 5% |
| 03:35.55 | 03:39.55 | 4.0s | ? | 30% | decide 30% / computer 16% / birthday 7% |
| 03:39.59 | 03:43.59 | 4.0s | ? | 45% | decide 45% / basketball 12% / go 3% |
| 03:43.62 | 03:47.63 | 4.0s | accident | 95% | accident 95% / secretary 1% / last 0% |
| 03:47.66 | 03:51.66 | 4.0s | ? | 24% | all 24% / cook 10% / want 8% |
| 03:51.70 | 03:55.70 | 4.0s | ? | 41% | accident 41% / what 17% / before 4% |
| 03:55.74 | 03:59.74 | 4.0s | ? | 24% | letter 24% / play 12% / walk 8% |
| 03:59.77 | 04:03.78 | 4.0s | accident | 62% | accident 62% / secretary 22% / change 3% |
| 04:03.81 | 04:07.81 | 4.0s | ? | 50% | secretary 50% / all 31% / letter 10% |
| 04:07.85 | 04:11.85 | 4.0s | last | 57% | last 57% / now 11% / purple 4% |
| 04:11.88 | 04:15.89 | 4.0s | ? | 15% | want 15% / cook 11% / walk 6% |
| 04:15.92 | 04:19.93 | 4.0s | ? | 13% | secretary 13% / black 10% / how 7% |
| 04:19.96 | 04:23.96 | 4.0s | ? | 48% | play 48% / walk 15% / black 7% |
| 04:24.00 | 04:28.00 | 4.0s | ? | 44% | cheat 44% / accident 39% / last 6% |
| 04:28.03 | 04:32.04 | 4.0s | ? | 28% | graduate 28% / full 21% / all 12% |
| 04:32.07 | 04:36.08 | 4.0s | right | 67% | right 67% / what 11% / year 3% |
| 04:36.11 | 04:40.11 | 4.0s | last | 61% | last 61% / secretary 13% / graduate 4% |
| 04:40.15 | 04:44.15 | 4.0s | ? | 7% | accident 7% / drink 7% / africa 7% |
| 04:44.18 | 04:48.19 | 4.0s | ? | 28% | computer 28% / basketball 16% / decide 10% |
| 04:48.22 | 04:52.23 | 4.0s | ? | 24% | secretary 24% / change 22% / accident 12% |
| 04:52.26 | 04:56.26 | 4.0s | all | 73% | all 73% / cook 10% / man 4% |
| 04:56.30 | 05:00.30 | 4.0s | accident | 65% | accident 65% / graduate 7% / secretary 7% |
| 05:00.33 | 05:04.34 | 4.0s | accident | 52% | accident 52% / all 9% / secretary 6% |
| 05:04.37 | 05:08.38 | 4.0s | accident | 71% | accident 71% / dark 4% / fine 2% |
| 05:08.41 | 05:12.41 | 4.0s | ? | 14% | shirt 14% / fine 9% / accident 6% |
| 05:12.44 | 05:16.45 | 4.0s | ? | 14% | last 14% / graduate 13% / purple 9% |
| 05:16.48 | 05:20.49 | 4.0s | change | 56% | change 56% / accident 17% / secretary 10% |
| 05:20.52 | 05:24.52 | 4.0s | last | 66% | last 66% / doctor 7% / graduate 4% |
| 05:24.56 | 05:28.56 | 4.0s | ? | 32% | play 32% / last 15% / accident 10% |
| 05:28.60 | 05:32.60 | 4.0s | family | 56% | family 56% / dark 8% / accident 4% |
| 05:32.63 | 05:36.64 | 4.0s | ? | 27% | meet 27% / but 6% / cook 4% |
| 05:36.67 | 05:40.67 | 4.0s | ? | 12% | later 12% / thanksgiving 7% / chair 7% |
| 05:40.71 | 05:44.71 | 4.0s | ? | 20% | give 20% / city 16% / cheat 12% |
| 05:44.74 | 05:48.75 | 4.0s | ? | 18% | accident 18% / secretary 14% / thanksgiving 10% |
| 05:48.78 | 05:52.79 | 4.0s | accident | 72% | accident 72% / help 5% / year 3% |
| 05:52.82 | 05:56.82 | 4.0s | accident | 86% | accident 86% / secretary 4% / dark 2% |
| 05:56.86 | 06:00.86 | 4.0s | ? | 33% | birthday 33% / before 23% / change 8% |
| 06:00.89 | 06:04.90 | 4.0s | ? | 38% | all 38% / accident 8% / graduate 8% |
| 06:04.93 | 06:08.94 | 4.0s | all | 51% | all 51% / cook 23% / secretary 5% |
| 06:08.97 | 06:12.97 | 4.0s | accident | 79% | accident 79% / all 3% / how 2% |
| 06:13.01 | 06:17.01 | 4.0s | ? | 18% | cow 18% / what 15% / accident 9% |
| 06:17.04 | 06:21.05 | 4.0s | ? | 24% | paint 24% / corn 9% / black 6% |
| 06:21.08 | 06:25.08 | 4.0s | decide | 56% | decide 56% / play 12% / clothes 4% |
| 06:25.12 | 06:29.12 | 4.0s | secretary | 55% | secretary 55% / accident 27% / dog 3% |
| 06:29.15 | 06:33.16 | 4.0s | ? | 21% | year 21% / accident 17% / computer 12% |
| 06:33.19 | 06:37.20 | 4.0s | ? | 28% | jacket 28% / accident 18% / play 11% |
| 06:37.23 | 06:41.23 | 4.0s | secretary | 65% | secretary 65% / accident 31% / thin 1% |
| 06:41.27 | 06:45.27 | 4.0s | ? | 28% | secretary 28% / all 28% / what 4% |
| 06:45.31 | 06:49.31 | 4.0s | ? | 30% | last 30% / doctor 14% / now 12% |
| 06:49.34 | 06:53.35 | 4.0s | ? | 17% | before 17% / cook 11% / accident 9% |
| 06:53.38 | 06:57.38 | 4.0s | cheat | 58% | cheat 58% / who 6% / dog 5% |
| 06:57.42 | 07:01.42 | 4.0s | short | 58% | short 58% / medicine 10% / color 5% |
| 07:01.45 | 07:05.46 | 4.0s | ? | 40% | medicine 40% / short 12% / white 8% |
| 07:05.49 | 07:09.50 | 4.0s | ? | 12% | birthday 12% / graduate 12% / pink 10% |
| 07:09.53 | 07:13.53 | 4.0s | ? | 24% | later 24% / no 20% / go 10% |
| 07:13.57 | 07:17.57 | 4.0s | ? | 13% | before 13% / what 7% / help 6% |
| 07:17.60 | 07:21.61 | 4.0s | ? | 35% | last 35% / right 8% / short 8% |
| 07:21.64 | 07:25.64 | 4.0s | secretary | 62% | secretary 62% / short 10% / same 8% |
| 07:25.68 | 07:29.68 | 4.0s | ? | 33% | graduate 33% / all 33% / corn 7% |
| 07:29.72 | 07:33.72 | 4.0s | ? | 46% | all 46% / what 8% / graduate 7% |
| 07:33.75 | 07:37.76 | 4.0s | ? | 23% | thursday 23% / how 20% / fine 7% |
| 07:37.79 | 07:41.80 | 4.0s | ? | 29% | birthday 29% / school 5% / year 5% |
| 07:41.83 | 07:45.83 | 4.0s | ? | 22% | year 22% / thursday 9% / accident 6% |
| 07:45.87 | 07:49.87 | 4.0s | ? | 12% | play 12% / black 12% / before 4% |
| 07:49.90 | 07:53.91 | 4.0s | ? | 22% | dark 22% / graduate 16% / family 11% |
| 07:53.94 | 07:57.94 | 4.0s | ? | 27% | before 27% / change 10% / graduate 7% |
| 07:57.98 | 08:01.98 | 4.0s | what | 61% | what 61% / graduate 8% / basketball 4% |
| 08:02.01 | 08:06.02 | 4.0s | ? | 42% | graduate 42% / last 36% / fine 5% |
| 08:06.05 | 08:10.06 | 4.0s | ? | 21% | wrong 21% / short 20% / help 8% |
| 08:10.09 | 08:14.09 | 4.0s | ? | 22% | graduate 22% / what 12% / wrong 9% |
| 08:14.13 | 08:18.13 | 4.0s | ? | 23% | short 23% / secretary 12% / last 9% |
| 08:18.16 | 08:22.17 | 4.0s | ? | 15% | accident 15% / language 14% / clothes 8% |
| 08:22.20 | 08:26.21 | 4.0s | ? | 17% | all 17% / give 13% / many 13% |
| 08:26.24 | 08:30.24 | 4.0s | last | 70% | last 70% / secretary 5% / no 2% |
| 08:30.28 | 08:34.28 | 4.0s | ? | 27% | secretary 27% / accident 8% / last 7% |
| 08:34.31 | 08:38.32 | 4.0s | secretary | 83% | secretary 83% / accident 6% / all 1% |
| 08:38.35 | 08:42.36 | 4.0s | ? | 45% | accident 45% / dark 9% / change 6% |
| 08:42.39 | 08:46.39 | 4.0s | ? | 22% | play 22% / change 12% / black 12% |
| 08:46.43 | 08:50.43 | 4.0s | ? | 28% | accident 28% / graduate 20% / change 9% |
| 08:50.46 | 08:54.47 | 4.0s | ? | 28% | computer 28% / accident 11% / change 8% |
| 08:54.50 | 08:58.50 | 4.0s | ? | 16% | secretary 16% / same 13% / later 9% |
| 08:58.54 | 09:02.54 | 4.0s | change | 52% | change 52% / accident 35% / secretary 2% |
| 09:02.58 | 09:06.58 | 4.0s | ? | 43% | change 43% / accident 24% / wrong 4% |
| 09:06.61 | 09:10.62 | 4.0s | ? | 27% | accident 27% / last 11% / secretary 8% |
| 09:10.65 | 09:14.65 | 4.0s | ? | 18% | secretary 18% / all 15% / cook 11% |
| 09:14.69 | 09:18.69 | 4.0s | ? | 36% | secretary 36% / all 23% / graduate 11% |
| 09:18.73 | 09:22.73 | 4.0s | cook | 69% | cook 69% / graduate 10% / all 6% |
| 09:22.76 | 09:26.77 | 4.0s | ? | 14% | last 14% / want 13% / now 11% |
| 09:26.80 | 09:30.80 | 4.0s | later | 57% | later 57% / last 7% / no 6% |
| 09:30.84 | 09:34.84 | 4.0s | ? | 20% | year 20% / accident 9% / black 8% |
| 09:34.87 | 09:38.88 | 4.0s | accident | 59% | accident 59% / secretary 13% / wrong 5% |
| 09:38.91 | 09:42.92 | 4.0s | ? | 20% | what 20% / hot 12% / study 7% |
| 09:42.95 | 09:46.95 | 4.0s | ? | 10% | want 10% / now 9% / last 9% |
| 09:46.99 | 09:50.99 | 4.0s | ? | 48% | accident 48% / cook 8% / orange 5% |
| 09:51.02 | 09:55.03 | 4.0s | ? | 15% | decide 15% / before 12% / last 10% |
| 09:55.06 | 09:59.07 | 4.0s | ? | 36% | accident 36% / short 10% / thin 9% |
| 09:59.10 | 10:03.10 | 4.0s | all | 62% | all 62% / graduate 5% / give 4% |
| 10:03.14 | 10:07.14 | 4.0s | ? | 38% | last 38% / go 7% / thin 6% |
| 10:07.17 | 10:11.18 | 4.0s | ? | 15% | graduate 15% / computer 8% / wrong 5% |
| 10:11.21 | 10:15.22 | 4.0s | later | 52% | later 52% / secretary 12% / orange 8% |
| 10:15.25 | 10:19.25 | 4.0s | year | 52% | year 52% / work 11% / language 9% |
| 10:19.28 | 10:23.29 | 4.0s | ? | 15% | secretary 15% / now 7% / want 6% |
| 10:23.32 | 10:27.33 | 4.0s | accident | 68% | accident 68% / secretary 3% / now 3% |
| 10:27.36 | 10:31.36 | 4.0s | accident | 90% | accident 90% / help 1% / tell 1% |
| 10:31.40 | 10:35.40 | 4.0s | ? | 29% | accident 29% / secretary 24% / last 9% |
| 10:35.43 | 10:39.44 | 4.0s | ? | 17% | work 17% / tall 7% / no 6% |
| 10:39.47 | 10:43.48 | 4.0s | accident | 69% | accident 69% / black 4% / wrong 3% |
| 10:43.51 | 10:47.51 | 4.0s | ? | 11% | woman 11% / man 8% / letter 8% |
| 10:47.55 | 10:51.55 | 4.0s | ? | 16% | work 16% / accident 8% / right 8% |
| 10:51.58 | 10:55.59 | 4.0s | ? | 23% | last 23% / thanksgiving 9% / decide 5% |
| 10:55.62 | 10:59.63 | 4.0s | ? | 30% | accident 30% / secretary 24% / all 20% |
| 10:59.66 | 11:03.66 | 4.0s | ? | 20% | secretary 20% / computer 7% / change 7% |
| 11:03.70 | 11:07.70 | 4.0s | ? | 31% | last 31% / letter 12% / all 11% |
| 11:07.73 | 11:11.74 | 4.0s | ? | 42% | secretary 42% / last 28% / accident 5% |
| 11:11.77 | 11:15.77 | 4.0s | ? | 13% | secretary 13% / accident 12% / decide 9% |
| 11:15.81 | 11:19.81 | 4.0s | ? | 12% | secretary 12% / wrong 12% / same 6% |
| 11:19.85 | 11:23.85 | 4.0s | ? | 19% | secretary 19% / all 17% / decide 8% |
| 11:23.88 | 11:27.89 | 4.0s | ? | 44% | clothes 44% / enjoy 24% / accident 9% |
| 11:27.92 | 11:31.92 | 4.0s | ? | 13% | last 13% / secretary 9% / all 6% |
| 11:31.96 | 11:35.96 | 4.0s | decide | 69% | decide 69% / want 6% / give 3% |
| 11:36.00 | 11:40.00 | 4.0s | ? | 25% | same 25% / go 11% / letter 8% |
| 11:40.03 | 11:44.04 | 4.0s | ? | 21% | black 21% / decide 14% / all 9% |
| 11:44.07 | 11:48.07 | 4.0s | ? | 23% | want 23% / what 12% / clothes 9% |
| 11:48.11 | 11:52.11 | 4.0s | ? | 34% | last 34% / before 9% / corn 8% |
| 11:52.14 | 11:56.15 | 4.0s | ? | 20% | want 20% / now 19% / many 18% |
| 11:56.18 | 12:00.19 | 4.0s | decide | 60% | decide 60% / finish 4% / short 3% |
| 12:00.22 | 12:04.22 | 4.0s | ? | 36% | decide 36% / no 6% / clothes 6% |
| 12:04.26 | 12:08.26 | 4.0s | ? | 16% | short 16% / decide 12% / secretary 12% |
| 12:08.29 | 12:12.30 | 4.0s | ? | 35% | accident 35% / change 9% / wrong 6% |
| 12:12.33 | 12:16.34 | 4.0s | ? | 29% | thin 29% / accident 12% / black 8% |
| 12:16.37 | 12:20.37 | 4.0s | ? | 46% | decide 46% / graduate 15% / basketball 10% |
| 12:20.41 | 12:24.41 | 4.0s | ? | 46% | what 46% / accident 15% / finish 8% |
| 12:24.44 | 12:28.45 | 4.0s | ? | 15% | black 15% / book 13% / accident 9% |
| 12:28.48 | 12:32.49 | 4.0s | ? | 18% | city 18% / finish 13% / short 7% |
| 12:32.52 | 12:36.52 | 4.0s | ? | 19% | dark 19% / accident 17% / before 13% |
| 12:36.56 | 12:40.56 | 4.0s | all | 69% | all 69% / school 13% / enjoy 4% |
| 12:40.59 | 12:44.60 | 4.0s | ? | 35% | meet 35% / secretary 17% / change 8% |
| 12:44.63 | 12:48.63 | 4.0s | thin | 58% | thin 58% / secretary 16% / accident 2% |
| 12:48.67 | 12:52.67 | 4.0s | ? | 40% | secretary 40% / accident 16% / what 7% |
| 12:52.71 | 12:56.71 | 4.0s | secretary | 57% | secretary 57% / accident 25% / what 3% |
| 12:56.74 | 13:00.75 | 4.0s | ? | 17% | decide 17% / study 8% / last 6% |
| 13:00.78 | 13:04.78 | 4.0s | ? | 32% | decide 32% / cook 8% / black 7% |
| 13:04.82 | 13:08.82 | 4.0s | ? | 33% | thanksgiving 33% / bird 5% / decide 5% |
| 13:08.99 | 13:12.99 | 4.0s | ? | 33% | accident 33% / change 22% / basketball 8% |
| 13:13.03 | 13:17.03 | 4.0s | black | 54% | black 54% / graduate 9% / thin 6% |
| 13:17.06 | 13:21.07 | 4.0s | ? | 14% | accident 14% / black 9% / secretary 7% |
| 13:21.10 | 13:25.10 | 4.0s | ? | 20% | all 20% / accident 15% / dark 13% |
| 13:25.14 | 13:29.14 | 4.0s | ? | 25% | change 25% / graduate 20% / cook 10% |
| 13:29.17 | 13:33.18 | 4.0s | ? | 49% | later 49% / no 7% / tell 4% |
| 13:33.21 | 13:37.22 | 4.0s | graduate | 56% | graduate 56% / last 14% / medicine 4% |
| 13:37.25 | 13:41.25 | 4.0s | ? | 32% | later 32% / secretary 11% / change 11% |
| 13:41.29 | 13:45.29 | 4.0s | ? | 11% | what 11% / cook 9% / tall 8% |
| 13:45.33 | 13:49.33 | 4.0s | ? | 50% | graduate 50% / thin 14% / black 5% |
| 13:49.36 | 13:53.37 | 4.0s | ? | 33% | forget 33% / accident 29% / all 6% |
| 13:53.40 | 13:57.40 | 4.0s | ? | 49% | cook 49% / accident 41% / cow 1% |
| 13:57.44 | 14:01.44 | 4.0s | ? | 23% | cook 23% / jacket 14% / apple 9% |
| 14:01.47 | 14:05.48 | 4.0s | ? | 22% | last 22% / graduate 19% / doctor 16% |
| 14:05.51 | 14:09.51 | 4.0s | ? | 42% | many 42% / want 21% / now 5% |
| 14:09.55 | 14:13.55 | 4.0s | ? | 47% | all 47% / dark 26% / secretary 7% |
| 14:13.59 | 14:17.59 | 4.0s | secretary | 82% | secretary 82% / accident 10% / same 2% |
| 14:17.62 | 14:21.63 | 4.0s | secretary | 60% | secretary 60% / accident 8% / deaf 3% |
| 14:21.66 | 14:25.66 | 4.0s | ? | 42% | change 42% / apple 9% / accident 6% |
| 14:25.70 | 14:29.70 | 4.0s | ? | 19% | before 19% / birthday 11% / orange 8% |
| 14:29.74 | 14:33.74 | 4.0s | ? | 16% | accident 16% / last 13% / graduate 11% |
| 14:33.77 | 14:37.78 | 4.0s | ? | 23% | wrong 23% / accident 15% / language 7% |
| 14:37.81 | 14:41.81 | 4.0s | accident | 68% | accident 68% / all 6% / dark 2% |
| 14:41.85 | 14:45.85 | 4.0s | ? | 23% | play 23% / all 21% / letter 16% |
| 14:45.88 | 14:49.89 | 4.0s | ? | 42% | accident 42% / cook 39% / cow 4% |
| 14:49.92 | 14:53.93 | 4.0s | accident | 79% | accident 79% / change 6% / jacket 3% |
| 14:53.96 | 14:57.96 | 4.0s | ? | 14% | year 14% / accident 8% / computer 7% |
| 14:58.00 | 15:02.00 | 4.0s | ? | 25% | cook 25% / later 9% / secretary 8% |
| 15:02.03 | 15:06.04 | 4.0s | secretary | 55% | secretary 55% / accident 26% / all 5% |
| 15:06.07 | 15:10.08 | 4.0s | ? | 28% | decide 28% / tall 10% / give 7% |
| 15:10.11 | 15:14.11 | 4.0s | ? | 24% | change 24% / accident 20% / graduate 7% |
| 15:14.15 | 15:18.15 | 4.0s | ? | 20% | secretary 20% / hot 10% / graduate 9% |
| 15:18.18 | 15:22.19 | 4.0s | ? | 16% | cousin 16% / basketball 15% / clothes 7% |
| 15:22.22 | 15:26.23 | 4.0s | ? | 41% | school 41% / all 10% / apple 7% |
| 15:26.26 | 15:30.26 | 4.0s | ? | 40% | all 40% / accident 13% / secretary 12% |
| 15:30.30 | 15:34.30 | 4.0s | ? | 20% | birthday 20% / last 8% / change 8% |
| 15:34.33 | 15:38.34 | 4.0s | ? | 50% | all 50% / cook 31% / secretary 2% |
| 15:38.37 | 15:42.38 | 4.0s | accident | 57% | accident 57% / cook 13% / all 4% |
| 15:42.41 | 15:46.41 | 4.0s | ? | 21% | last 21% / secretary 19% / later 18% |
| 15:46.45 | 15:50.45 | 4.0s | ? | 23% | want 23% / shirt 22% / give 18% |
| 15:50.48 | 15:54.49 | 4.0s | ? | 38% | accident 38% / pizza 13% / last 5% |
| 15:54.52 | 15:58.52 | 4.0s | ? | 19% | play 19% / last 16% / what 11% |
| 15:58.56 | 16:02.56 | 4.0s | ? | 24% | accident 24% / change 9% / now 7% |
| 16:02.60 | 16:06.60 | 4.0s | ? | 14% | secretary 14% / letter 10% / last 7% |
| 16:06.63 | 16:10.64 | 4.0s | accident | 89% | accident 89% / secretary 4% / dark 2% |
| 16:10.67 | 16:14.67 | 4.0s | ? | 23% | all 23% / accident 11% / cook 11% |
| 16:14.71 | 16:18.71 | 4.0s | can | 64% | can 64% / cow 7% / graduate 4% |
| 16:18.74 | 16:22.75 | 4.0s | ? | 34% | graduate 34% / decide 8% / corn 5% |
| 16:22.78 | 16:26.79 | 4.0s | ? | 41% | later 41% / last 19% / no 4% |
| 16:26.82 | 16:30.82 | 4.0s | accident | 72% | accident 72% / pizza 8% / wrong 3% |
| 16:30.86 | 16:34.86 | 4.0s | ? | 27% | change 27% / cheat 23% / accident 18% |
| 16:34.89 | 16:38.90 | 4.0s | ? | 44% | accident 44% / cook 9% / before 6% |
| 16:38.93 | 16:42.93 | 4.0s | family | 56% | family 56% / all 16% / cook 5% |
| 16:42.97 | 16:46.97 | 4.0s | ? | 30% | dark 30% / family 13% / jacket 10% |
| 16:47.01 | 16:51.01 | 4.0s | secretary | 56% | secretary 56% / all 34% / thanksgiving 3% |
| 16:51.04 | 16:55.05 | 4.0s | secretary | 57% | secretary 57% / accident 13% / short 7% |
| 16:55.08 | 16:59.09 | 4.0s | ? | 15% | last 15% / black 8% / play 4% |
| 16:59.12 | 17:03.12 | 4.0s | ? | 32% | decide 32% / black 30% / forget 4% |
| 17:03.15 | 17:07.16 | 4.0s | ? | 32% | accident 32% / secretary 30% / computer 4% |
| 17:07.19 | 17:11.20 | 4.0s | ? | 18% | thin 18% / hat 13% / black 10% |
| 17:11.23 | 17:15.23 | 4.0s | ? | 12% | basketball 12% / decide 10% / paint 6% |
| 17:15.27 | 17:19.27 | 4.0s | ? | 23% | accident 23% / many 11% / cook 6% |
| 17:19.31 | 17:23.31 | 4.0s | ? | 30% | short 30% / can 6% / tall 5% |
| 17:23.34 | 17:27.35 | 4.0s | ? | 30% | black 30% / decide 10% / orange 7% |
| 17:27.38 | 17:31.38 | 4.0s | all | 60% | all 60% / cook 19% / accident 5% |
| 17:31.42 | 17:35.42 | 4.0s | ? | 33% | all 33% / secretary 25% / what 9% |
| 17:35.45 | 17:39.46 | 4.0s | ? | 22% | year 22% / accident 15% / change 11% |
| 17:39.49 | 17:43.50 | 4.0s | ? | 18% | year 18% / black 11% / secretary 10% |
| 17:43.53 | 17:47.53 | 4.0s | ? | 11% | city 11% / thin 10% / thursday 9% |
| 17:47.57 | 17:51.57 | 4.0s | ? | 46% | last 46% / what 18% / letter 8% |
| 17:51.60 | 17:55.61 | 4.0s | ? | 10% | change 10% / bowling 7% / same 7% |
| 17:55.64 | 17:59.64 | 4.0s | ? | 26% | secretary 26% / black 14% / accident 9% |
| 17:59.68 | 18:03.68 | 4.0s | all | 71% | all 71% / secretary 15% / accident 5% |
| 18:03.72 | 18:07.72 | 4.0s | accident | 69% | accident 69% / secretary 23% / decide 1% |
| 18:07.75 | 18:11.76 | 4.0s | ? | 23% | play 23% / accident 21% / walk 8% |
| 18:11.79 | 18:15.80 | 4.0s | ? | 10% | now 10% / work 7% / later 6% |
| 18:15.83 | 18:19.83 | 4.0s | ? | 23% | last 23% / play 7% / what 7% |
| 18:19.87 | 18:23.87 | 4.0s | ? | 11% | deaf 11% / computer 8% / graduate 7% |
| 18:23.90 | 18:27.91 | 4.0s | ? | 13% | wrong 13% / now 11% / computer 11% |
| 18:27.94 | 18:31.94 | 4.0s | ? | 20% | want 20% / wrong 9% / decide 7% |
| 18:31.98 | 18:35.98 | 4.0s | ? | 14% | accident 14% / walk 7% / book 6% |
| 18:36.02 | 18:40.02 | 4.0s | ? | 46% | all 46% / accident 33% / secretary 7% |
| 18:40.05 | 18:44.06 | 4.0s | ? | 36% | letter 36% / thin 26% / last 18% |
| 18:44.09 | 18:48.09 | 4.0s | ? | 28% | what 28% / forget 8% / study 5% |
| 18:48.13 | 18:52.13 | 4.0s | ? | 16% | secretary 16% / accident 9% / hot 8% |
| 18:52.16 | 18:56.17 | 4.0s | ? | 21% | right 21% / secretary 18% / pizza 13% |
| 18:56.20 | 19:00.21 | 4.0s | ? | 17% | computer 17% / year 8% / thanksgiving 7% |
| 19:00.24 | 19:04.24 | 4.0s | ? | 45% | accident 45% / dark 13% / change 7% |
| 19:04.28 | 19:08.28 | 4.0s | ? | 18% | birthday 18% / year 17% / basketball 12% |
| 19:08.31 | 19:12.32 | 4.0s | year | 78% | year 78% / basketball 5% / work 4% |
| 19:12.35 | 19:16.36 | 4.0s | ? | 36% | play 36% / accident 9% / walk 5% |
| 19:16.39 | 19:20.39 | 4.0s | accident | 58% | accident 58% / dark 8% / meet 6% |
| 19:20.43 | 19:24.43 | 4.0s | ? | 32% | cheat 32% / now 18% / accident 8% |
| 19:24.46 | 19:28.47 | 4.0s | ? | 15% | cow 15% / forget 9% / letter 7% |
| 19:28.50 | 19:32.51 | 4.0s | ? | 22% | how 22% / accident 15% / dog 7% |
| 19:32.54 | 19:36.54 | 4.0s | ? | 40% | accident 40% / what 19% / secretary 9% |
| 19:36.58 | 19:40.58 | 4.0s | ? | 27% | last 27% / before 8% / medicine 4% |
| 19:40.61 | 19:44.62 | 4.0s | ? | 46% | accident 46% / change 10% / cook 10% |
| 19:44.65 | 19:48.65 | 4.0s | ? | 26% | change 26% / graduate 18% / wrong 10% |
| 19:48.69 | 19:52.69 | 4.0s | ? | 9% | want 9% / cousin 7% / before 5% |
| 19:52.72 | 19:56.73 | 4.0s | ? | 14% | walk 14% / go 10% / orange 8% |
| 19:56.76 | 20:00.77 | 4.0s | ? | 17% | right 17% / want 10% / go 7% |
| 20:00.80 | 20:04.80 | 4.0s | accident | 57% | accident 57% / secretary 14% / cow 5% |
| 20:04.84 | 20:08.84 | 4.0s | secretary | 81% | secretary 81% / accident 11% / thin 1% |
| 20:08.87 | 20:12.88 | 4.0s | ? | 37% | secretary 37% / accident 22% / graduate 14% |
| 20:12.91 | 20:16.92 | 4.0s | secretary | 70% | secretary 70% / accident 16% / all 2% |
| 20:16.95 | 20:20.95 | 4.0s | ? | 16% | clothes 16% / what 11% / play 10% |
| 20:20.99 | 20:24.99 | 4.0s | ? | 46% | jacket 46% / accident 46% / shirt 2% |
| 20:25.02 | 20:29.03 | 4.0s | ? | 30% | black 30% / book 12% / thin 8% |
| 20:29.06 | 20:33.07 | 4.0s | ? | 30% | thin 30% / hot 12% / accident 7% |
| 20:33.10 | 20:37.10 | 4.0s | ? | 17% | go 17% / play 16% / computer 10% |
| 20:37.14 | 20:41.14 | 4.0s | ? | 19% | wrong 19% / birthday 7% / accident 6% |
| 20:41.17 | 20:45.18 | 4.0s | ? | 25% | decide 25% / secretary 25% / graduate 15% |
| 20:45.21 | 20:49.21 | 4.0s | ? | 35% | accident 35% / secretary 11% / wrong 10% |
| 20:49.25 | 20:53.25 | 4.0s | secretary | 58% | secretary 58% / graduate 9% / all 3% |
| 20:53.29 | 20:57.29 | 4.0s | ? | 35% | jacket 35% / play 19% / many 9% |
| 20:57.32 | 21:01.33 | 4.0s | ? | 25% | last 25% / secretary 23% / accident 16% |
| 21:01.36 | 21:05.36 | 4.0s | ? | 27% | wrong 27% / graduate 14% / secretary 12% |
| 21:05.40 | 21:09.40 | 4.0s | accident | 63% | accident 63% / basketball 3% / dark 3% |
| 21:09.43 | 21:13.44 | 4.0s | ? | 48% | accident 48% / what 12% / fine 9% |
| 21:13.47 | 21:17.48 | 4.0s | ? | 20% | cheat 20% / wrong 12% / last 11% |
| 21:17.51 | 21:21.51 | 4.0s | ? | 20% | secretary 20% / all 18% / graduate 17% |
| 21:21.55 | 21:25.55 | 4.0s | ? | 9% | birthday 9% / secretary 8% / thin 7% |
| 21:25.58 | 21:29.59 | 4.0s | accident | 59% | accident 59% / secretary 25% / change 2% |
| 21:29.62 | 21:33.63 | 4.0s | ? | 24% | computer 24% / same 9% / dark 7% |
| 21:33.66 | 21:37.66 | 4.0s | ? | 29% | secretary 29% / change 20% / accident 18% |
| 21:37.70 | 21:41.70 | 4.0s | secretary | 90% | secretary 90% / accident 3% / thin 1% |
| 21:41.73 | 21:45.74 | 4.0s | ? | 24% | last 24% / play 8% / before 7% |
| 21:45.77 | 21:49.78 | 4.0s | ? | 31% | all 31% / study 8% / accident 5% |
| 21:49.81 | 21:53.81 | 4.0s | ? | 30% | all 30% / secretary 27% / change 8% |
| 21:53.85 | 21:57.85 | 4.0s | ? | 25% | accident 25% / family 14% / all 12% |
| 21:57.88 | 22:01.89 | 4.0s | accident | 61% | accident 61% / cow 7% / secretary 6% |
| 22:01.92 | 22:05.92 | 4.0s | ? | 26% | graduate 26% / thursday 7% / black 6% |
| 22:05.96 | 22:09.96 | 4.0s | ? | 27% | secretary 27% / accident 14% / graduate 13% |
| 22:09.99 | 22:14.00 | 4.0s | ? | 16% | black 16% / accident 14% / orange 14% |
| 22:14.03 | 22:18.04 | 4.0s | ? | 44% | secretary 44% / last 17% / accident 7% |
| 22:18.07 | 22:22.07 | 4.0s | ? | 49% | last 49% / secretary 17% / letter 6% |
| 22:22.11 | 22:26.11 | 4.0s | ? | 39% | what 39% / secretary 10% / all 7% |
| 22:26.14 | 22:30.15 | 4.0s | ? | 17% | pizza 17% / now 9% / accident 9% |
| 22:30.18 | 22:34.19 | 4.0s | ? | 16% | study 16% / pizza 12% / kiss 12% |
| 22:34.22 | 22:38.22 | 4.0s | ? | 25% | change 25% / computer 12% / secretary 10% |
| 22:38.26 | 22:42.26 | 4.0s | ? | 16% | all 16% / africa 16% / family 14% |
| 22:42.29 | 22:46.30 | 4.0s | ? | 24% | graduate 24% / computer 5% / all 5% |
| 22:46.33 | 22:50.34 | 4.0s | ? | 13% | jacket 13% / now 10% / woman 9% |
| 22:50.37 | 22:54.37 | 4.0s | ? | 21% | man 21% / accident 21% / secretary 8% |
| 22:54.41 | 22:58.41 | 4.0s | ? | 42% | accident 42% / secretary 35% / all 4% |
| 22:58.44 | 23:02.45 | 4.0s | ? | 19% | accident 19% / decide 7% / change 7% |
| 23:02.48 | 23:06.48 | 4.0s | ? | 37% | family 37% / finish 9% / before 7% |
| 23:06.52 | 23:10.52 | 4.0s | ? | 41% | accident 41% / family 14% / change 13% |
| 23:10.56 | 23:14.56 | 4.0s | secretary | 90% | secretary 90% / accident 6% / black 1% |
| 23:14.59 | 23:18.60 | 4.0s | ? | 22% | before 22% / change 20% / finish 7% |
| 23:18.63 | 23:22.63 | 4.0s | graduate | 76% | graduate 76% / all 6% / candy 3% |
| 23:22.67 | 23:26.67 | 4.0s | ? | 32% | what 32% / graduate 9% / want 7% |
| 23:26.70 | 23:30.71 | 4.0s | ? | 10% | forget 10% / dance 9% / black 8% |
| 23:30.74 | 23:34.75 | 4.0s | change | 63% | change 63% / accident 19% / secretary 5% |
| 23:34.78 | 23:38.78 | 4.0s | ? | 16% | computer 16% / change 15% / meet 5% |
| 23:38.82 | 23:42.82 | 4.0s | ? | 38% | change 38% / accident 22% / wrong 5% |
| 23:42.86 | 23:46.86 | 4.0s | ? | 32% | secretary 32% / accident 17% / now 8% |
| 23:46.89 | 23:50.90 | 4.0s | ? | 25% | graduate 25% / all 11% / work 6% |
| 23:50.93 | 23:54.93 | 4.0s | secretary | 70% | secretary 70% / accident 8% / now 4% |
| 23:54.97 | 23:58.97 | 4.0s | ? | 34% | short 34% / now 13% / want 10% |
| 23:59.00 | 24:03.01 | 4.0s | ? | 31% | last 31% / change 10% / wrong 5% |
| 24:03.04 | 24:07.05 | 4.0s | ? | 44% | graduate 44% / secretary 23% / last 8% |
| 24:07.08 | 24:11.08 | 4.0s | secretary | 63% | secretary 63% / accident 9% / all 7% |
| 24:11.12 | 24:15.12 | 4.0s | ? | 16% | full 16% / cheat 13% / change 12% |
| 24:15.15 | 24:19.16 | 4.0s | ? | 16% | change 16% / tell 11% / fine 8% |
| 24:19.19 | 24:23.19 | 4.0s | ? | 20% | graduate 20% / change 9% / year 8% |
| 24:23.23 | 24:27.23 | 4.0s | decide | 58% | decide 58% / thin 4% / forget 4% |
| 24:27.27 | 24:31.27 | 4.0s | ? | 24% | accident 24% / secretary 16% / study 8% |
| 24:31.30 | 24:35.31 | 4.0s | accident | 99% | accident 99% / change 1% / jacket 0% |
| 24:35.34 | 24:39.35 | 4.0s | short | 90% | short 90% / letter 1% / cousin 1% |
| 24:39.38 | 24:43.38 | 4.0s | secretary | 73% | secretary 73% / graduate 6% / black 5% |
| 24:43.41 | 24:47.42 | 4.0s | accident | 54% | accident 54% / pizza 6% / enjoy 3% |
| 24:47.45 | 24:51.46 | 4.0s | ? | 16% | accident 16% / graduate 13% / cheat 9% |
| 24:51.49 | 24:55.49 | 4.0s | accident | 56% | accident 56% / year 4% / orange 3% |
| 24:55.53 | 24:59.53 | 4.0s | secretary | 67% | secretary 67% / later 10% / wrong 2% |
| 24:59.57 | 25:03.57 | 4.0s | ? | 31% | accident 31% / year 14% / thin 13% |
| 25:03.60 | 25:07.61 | 4.0s | ? | 24% | all 24% / fine 16% / cook 9% |
| 25:07.64 | 25:11.64 | 4.0s | ? | 13% | black 13% / what 11% / hot 8% |
| 25:11.68 | 25:15.68 | 4.0s | ? | 14% | thanksgiving 14% / play 12% / language 7% |
| 25:15.71 | 25:19.72 | 4.0s | ? | 33% | accident 33% / secretary 16% / decide 8% |
| 25:19.75 | 25:23.76 | 4.0s | ? | 12% | graduate 12% / before 9% / last 8% |
| 25:23.79 | 25:27.79 | 4.0s | secretary | 57% | secretary 57% / all 18% / accident 13% |
| 25:27.83 | 25:31.83 | 4.0s | ? | 33% | shirt 33% / change 28% / accident 10% |
| 25:31.86 | 25:35.87 | 4.0s | ? | 23% | birthday 23% / thin 20% / last 12% |
| 25:35.90 | 25:39.90 | 4.0s | ? | 15% | secretary 15% / graduate 11% / accident 11% |
| 25:39.94 | 25:43.94 | 4.0s | ? | 48% | accident 48% / cow 8% / what 4% |
| 25:43.98 | 25:47.98 | 4.0s | ? | 34% | accident 34% / graduate 8% / finish 6% |
| 25:48.01 | 25:52.02 | 4.0s | secretary | 72% | secretary 72% / last 7% / what 3% |
| 25:52.05 | 25:56.05 | 4.0s | ? | 42% | secretary 42% / later 11% / last 8% |
| 25:56.09 | 26:00.09 | 4.0s | secretary | 76% | secretary 76% / accident 14% / decide 2% |
| 26:00.12 | 26:04.13 | 4.0s | ? | 26% | accident 26% / thin 22% / decide 9% |
| 26:04.16 | 26:08.17 | 4.0s | ? | 14% | full 14% / change 14% / graduate 10% |
| 26:08.20 | 26:12.20 | 4.0s | decide | 59% | decide 59% / orange 4% / corn 3% |
| 26:12.24 | 26:16.24 | 4.0s | all | 70% | all 70% / family 5% / man 4% |
| 26:16.28 | 26:20.28 | 4.0s | ? | 24% | last 24% / right 13% / pizza 9% |
| 26:20.31 | 26:24.32 | 4.0s | ? | 26% | finish 26% / dark 19% / accident 7% |
| 26:24.35 | 26:28.35 | 4.0s | ? | 20% | graduate 20% / help 10% / secretary 6% |
| 26:28.39 | 26:32.39 | 4.0s | ? | 17% | accident 17% / basketball 11% / tall 10% |
| 26:32.42 | 26:36.43 | 4.0s | ? | 8% | computer 8% / corn 8% / finish 7% |
| 26:36.46 | 26:40.47 | 4.0s | ? | 18% | orange 18% / accident 12% / finish 9% |
| 26:40.50 | 26:44.50 | 4.0s | all | 51% | all 51% / computer 19% / cow 3% |
| 26:44.54 | 26:48.54 | 4.0s | accident | 68% | accident 68% / book 8% / play 3% |
| 26:48.57 | 26:52.58 | 4.0s | ? | 29% | decide 29% / last 18% / corn 9% |
| 26:52.61 | 26:56.62 | 4.0s | ? | 12% | basketball 12% / thin 10% / finish 8% |
| 26:56.65 | 27:00.65 | 4.0s | ? | 36% | basketball 36% / decide 28% / play 7% |
| 27:00.69 | 27:04.69 | 4.0s | ? | 18% | work 18% / pizza 9% / wrong 8% |
| 27:04.72 | 27:08.73 | 4.0s | ? | 34% | secretary 34% / graduate 16% / change 14% |
| 27:08.76 | 27:12.76 | 4.0s | ? | 9% | accident 9% / meet 7% / want 5% |
| 27:12.80 | 27:16.80 | 4.0s | ? | 16% | computer 16% / accident 12% / work 9% |
| 27:16.84 | 27:20.84 | 4.0s | ? | 17% | want 17% / play 9% / shirt 7% |
| 27:20.87 | 27:24.88 | 4.0s | accident | 66% | accident 66% / what 11% / last 5% |
| 27:24.91 | 27:28.91 | 4.0s | ? | 19% | year 19% / secretary 13% / last 6% |
| 27:28.95 | 27:32.95 | 4.0s | ? | 39% | meet 39% / before 27% / change 13% |
| 27:32.98 | 27:36.99 | 4.0s | ? | 23% | accident 23% / pizza 10% / tall 7% |
| 27:37.02 | 27:41.03 | 4.0s | ? | 11% | wrong 11% / now 7% / secretary 7% |
| 27:41.06 | 27:45.06 | 4.0s | last | 61% | last 61% / graduate 12% / letter 5% |
| 27:45.10 | 27:49.10 | 4.0s | ? | 17% | change 17% / graduate 14% / accident 14% |
| 27:49.13 | 27:53.14 | 4.0s | decide | 77% | decide 77% / now 4% / short 2% |
| 27:53.17 | 27:57.18 | 4.0s | ? | 12% | play 12% / want 11% / all 10% |
| 27:57.21 | 28:01.21 | 4.0s | ? | 26% | later 26% / secretary 12% / orange 7% |
| 28:01.25 | 28:05.25 | 4.0s | ? | 23% | decide 23% / graduate 8% / work 5% |
| 28:05.28 | 28:09.29 | 4.0s | ? | 11% | what 11% / play 9% / accident 8% |
| 28:09.32 | 28:13.33 | 4.0s | accident | 56% | accident 56% / what 10% / fine 5% |
| 28:13.36 | 28:17.36 | 4.0s | ? | 13% | birthday 13% / graduate 9% / accident 9% |
| 28:17.40 | 28:21.40 | 4.0s | ? | 22% | year 22% / before 13% / city 8% |
| 28:21.43 | 28:25.44 | 4.0s | ? | 20% | all 20% / thanksgiving 10% / bed 6% |
| 28:25.47 | 28:29.47 | 4.0s | ? | 18% | basketball 18% / last 6% / forget 6% |
| 28:29.51 | 28:33.51 | 4.0s | ? | 25% | last 25% / corn 11% / basketball 7% |
| 28:33.55 | 28:37.55 | 4.0s | ? | 11% | now 11% / what 10% / last 9% |
| 28:37.58 | 28:41.59 | 4.0s | secretary | 69% | secretary 69% / graduate 6% / accident 4% |
| 28:41.62 | 28:45.62 | 4.0s | decide | 53% | decide 53% / all 23% / secretary 9% |
| 28:45.66 | 28:49.66 | 4.0s | ? | 24% | want 24% / thanksgiving 19% / family 10% |
| 28:49.69 | 28:53.70 | 4.0s | ? | 18% | want 18% / family 16% / decide 12% |
| 28:53.73 | 28:57.74 | 4.0s | ? | 13% | decide 13% / dance 13% / accident 11% |
| 28:57.77 | 29:01.77 | 4.0s | ? | 28% | graduate 28% / last 11% / orange 9% |
| 29:01.81 | 29:05.81 | 4.0s | ? | 27% | graduate 27% / decide 14% / computer 11% |
| 29:05.84 | 29:09.85 | 4.0s | ? | 23% | play 23% / black 15% / walk 5% |
| 29:09.88 | 29:13.88 | 4.0s | change | 56% | change 56% / accident 22% / secretary 4% |
| 29:13.92 | 29:17.92 | 4.0s | ? | 43% | accident 43% / jacket 7% / change 7% |
| 29:17.96 | 29:21.96 | 4.0s | ? | 34% | secretary 34% / last 13% / same 5% |
| 29:21.99 | 29:26.00 | 4.0s | ? | 18% | last 18% / letter 13% / study 11% |
| 29:26.03 | 29:30.04 | 4.0s | ? | 23% | accident 23% / secretary 12% / graduate 11% |
| 29:30.07 | 29:34.07 | 4.0s | ? | 44% | secretary 44% / accident 12% / cook 6% |
| 29:34.11 | 29:38.11 | 4.0s | ? | 17% | accident 17% / pizza 16% / last 11% |
| 29:38.14 | 29:42.15 | 4.0s | all | 79% | all 79% / cook 11% / graduate 2% |
| 29:42.18 | 29:46.18 | 4.0s | ? | 13% | accident 13% / secretary 9% / dark 9% |
| 29:46.22 | 29:50.22 | 4.0s | ? | 32% | graduate 32% / change 16% / accident 10% |
| 29:50.26 | 29:54.26 | 4.0s | ? | 31% | decide 31% / secretary 16% / finish 9% |
| 29:54.29 | 29:58.30 | 4.0s | finish | 59% | finish 59% / family 10% / all 7% |
| 29:58.33 | 30:02.33 | 4.0s | all | 60% | all 60% / secretary 25% / black 2% |
| 30:02.37 | 30:06.37 | 4.0s | ? | 8% | help 8% / accident 7% / computer 6% |
| 30:06.40 | 30:10.41 | 4.0s | ? | 30% | secretary 30% / same 19% / accident 13% |
| 30:10.44 | 30:14.45 | 4.0s | accident | 59% | accident 59% / secretary 12% / now 5% |
| 30:14.48 | 30:18.48 | 4.0s | ? | 9% | play 9% / decide 7% / clothes 6% |
| 30:18.52 | 30:22.52 | 4.0s | accident | 54% | accident 54% / secretary 24% / cook 8% |
| 30:22.55 | 30:26.56 | 4.0s | accident | 80% | accident 80% / secretary 11% / dark 3% |
| 30:26.59 | 30:30.60 | 4.0s | ? | 34% | what 34% / give 10% / letter 6% |
| 30:30.63 | 30:34.63 | 4.0s | ? | 40% | all 40% / secretary 11% / pizza 9% |
| 30:34.67 | 30:38.67 | 4.0s | ? | 32% | accident 32% / secretary 17% / kiss 7% |
| 30:38.70 | 30:42.71 | 4.0s | secretary | 77% | secretary 77% / accident 13% / thanksgiving 2% |
| 30:42.74 | 30:46.74 | 4.0s | ? | 32% | change 32% / before 13% / wrong 10% |
| 30:46.78 | 30:50.78 | 4.0s | ? | 32% | accident 32% / secretary 20% / wrong 8% |
| 30:50.82 | 30:54.82 | 4.0s | ? | 18% | last 18% / want 15% / thanksgiving 10% |
| 30:54.85 | 30:58.86 | 4.0s | ? | 46% | accident 46% / secretary 14% / many 12% |
| 30:58.89 | 31:02.89 | 4.0s | ? | 28% | secretary 28% / accident 20% / decide 20% |
| 31:02.93 | 31:06.93 | 4.0s | accident | 55% | accident 55% / hot 22% / secretary 11% |
| 31:06.96 | 31:10.97 | 4.0s | ? | 19% | all 19% / thanksgiving 18% / family 10% |
| 31:11.00 | 31:15.01 | 4.0s | ? | 27% | cheat 27% / accident 16% / wrong 12% |
| 31:15.04 | 31:19.04 | 4.0s | ? | 30% | graduate 30% / accident 27% / secretary 27% |
| 31:19.08 | 31:23.08 | 4.0s | ? | 26% | accident 26% / change 16% / many 12% |
| 31:23.12 | 31:27.12 | 4.0s | dark | 57% | dark 57% / accident 36% / family 1% |
| 31:27.15 | 31:31.16 | 4.0s | ? | 15% | graduate 15% / accident 10% / dark 8% |
| 31:31.19 | 31:35.19 | 4.0s | secretary | 53% | secretary 53% / no 3% / fine 3% |
| 31:35.23 | 31:39.23 | 4.0s | cool | 53% | cool 53% / how 7% / letter 3% |
| 31:39.26 | 31:43.27 | 4.0s | ? | 41% | graduate 41% / all 24% / corn 5% |
| 31:43.30 | 31:47.31 | 4.0s | ? | 37% | change 37% / graduate 6% / school 5% |
| 31:47.34 | 31:51.34 | 4.0s | ? | 39% | secretary 39% / accident 10% / many 9% |
| 31:51.38 | 31:55.38 | 4.0s | ? | 46% | graduate 46% / before 7% / birthday 5% |
| 31:55.41 | 31:59.42 | 4.0s | ? | 43% | graduate 43% / accident 13% / secretary 5% |
| 31:59.45 | 32:03.45 | 4.0s | accident | 65% | accident 65% / basketball 26% / dark 2% |
| 32:03.49 | 32:07.49 | 4.0s | accident | 94% | accident 94% / change 1% / secretary 1% |
| 32:07.53 | 32:11.53 | 4.0s | ? | 25% | accident 25% / man 8% / jacket 7% |
| 32:11.56 | 32:15.57 | 4.0s | ? | 21% | birthday 21% / before 14% / graduate 9% |
| 32:15.60 | 32:19.60 | 4.0s | ? | 16% | graduate 16% / accident 12% / year 11% |
| 32:19.64 | 32:23.64 | 4.0s | ? | 17% | pizza 17% / study 16% / accident 9% |
| 32:23.67 | 32:27.68 | 4.0s | ? | 19% | last 19% / decide 12% / thanksgiving 7% |
| 32:27.71 | 32:31.72 | 4.0s | all | 85% | all 85% / accident 2% / what 2% |
| 32:31.75 | 32:35.75 | 4.0s | accident | 57% | accident 57% / many 8% / secretary 4% |
| 32:35.79 | 32:39.79 | 4.0s | ? | 28% | secretary 28% / accident 27% / all 5% |
| 32:39.83 | 32:43.83 | 4.0s | accident | 50% | accident 50% / drink 10% / jacket 5% |
| 32:43.86 | 32:47.87 | 4.0s | ? | 27% | accident 27% / now 11% / thin 8% |
| 32:47.90 | 32:51.90 | 4.0s | ? | 32% | change 32% / book 7% / city 6% |
| 32:51.94 | 32:55.94 | 4.0s | ? | 20% | accident 20% / thanksgiving 10% / tell 8% |
| 32:55.97 | 32:59.98 | 4.0s | ? | 20% | thin 20% / last 19% / black 7% |
| 33:00.01 | 33:04.02 | 4.0s | ? | 44% | tall 44% / work 7% / basketball 4% |
| 33:04.05 | 33:08.05 | 4.0s | all | 67% | all 67% / cook 15% / corn 3% |
| 33:08.09 | 33:12.09 | 4.0s | all | 73% | all 73% / cook 8% / family 5% |
| 33:12.12 | 33:16.13 | 4.0s | ? | 20% | accident 20% / thin 18% / thanksgiving 14% |
| 33:16.16 | 33:20.16 | 4.0s | ? | 36% | man 36% / thanksgiving 17% / secretary 9% |
| 33:20.20 | 33:24.20 | 4.0s | ? | 43% | secretary 43% / all 12% / what 11% |
| 33:24.24 | 33:28.24 | 4.0s | ? | 40% | now 40% / accident 30% / last 5% |
| 33:28.27 | 33:32.28 | 4.0s | accident | 87% | accident 87% / change 9% / jacket 0% |
| 33:32.31 | 33:36.31 | 4.0s | ? | 44% | last 44% / hot 6% / help 5% |
| 33:36.35 | 33:40.35 | 4.0s | ? | 19% | graduate 19% / accident 17% / all 16% |
| 33:40.38 | 33:44.39 | 4.0s | ? | 10% | meet 10% / cool 9% / change 7% |
| 33:44.42 | 33:48.43 | 4.0s | accident | 91% | accident 91% / cook 1% / play 1% |
| 33:48.46 | 33:52.46 | 4.0s | accident | 51% | accident 51% / wrong 3% / family 3% |
| 33:52.50 | 33:56.50 | 4.0s | ? | 22% | dark 22% / secretary 20% / accident 15% |
| 33:56.53 | 34:00.54 | 4.0s | ? | 40% | all 40% / secretary 40% / decide 3% |
| 34:00.57 | 34:04.58 | 4.0s | decide | 72% | decide 72% / play 7% / want 6% |
| 34:04.61 | 34:08.61 | 4.0s | all | 56% | all 56% / secretary 10% / enjoy 7% |
| 34:08.65 | 34:12.65 | 4.0s | ? | 28% | kiss 28% / decide 25% / study 9% |
| 34:12.68 | 34:16.69 | 4.0s | decide | 64% | decide 64% / accident 7% / now 7% |
| 34:16.72 | 34:20.72 | 4.0s | ? | 33% | decide 33% / orange 14% / finish 7% |
| 34:20.76 | 34:24.76 | 4.0s | ? | 17% | thin 17% / accident 16% / black 12% |
| 34:24.80 | 34:28.80 | 4.0s | ? | 17% | accident 17% / enjoy 14% / fine 6% |
| 34:28.83 | 34:32.84 | 4.0s | ? | 19% | last 19% / before 12% / many 6% |
| 34:32.87 | 34:36.88 | 4.0s | ? | 25% | enjoy 25% / secretary 11% / accident 8% |
| 34:36.91 | 34:40.91 | 4.0s | ? | 7% | computer 7% / change 7% / accident 7% |
| 34:40.95 | 34:44.95 | 4.0s | ? | 42% | secretary 42% / graduate 25% / thin 10% |
| 34:44.98 | 34:48.99 | 4.0s | ? | 26% | what 26% / brown 6% / clothes 6% |
| 34:49.02 | 34:53.02 | 4.0s | accident | 51% | accident 51% / family 13% / secretary 5% |
| 34:53.06 | 34:57.06 | 4.0s | ? | 25% | what 25% / all 14% / last 12% |
| 34:57.09 | 35:01.10 | 4.0s | ? | 14% | thin 14% / pizza 13% / right 6% |
| 35:01.13 | 35:05.14 | 4.0s | graduate | 58% | graduate 58% / all 6% / school 4% |
| 35:05.17 | 35:09.17 | 4.0s | ? | 15% | all 15% / last 14% / decide 10% |
| 35:09.21 | 35:13.21 | 4.0s | ? | 26% | last 26% / accident 16% / secretary 11% |
| 35:13.24 | 35:17.25 | 4.0s | accident | 61% | accident 61% / walk 4% / hot 4% |
| 35:17.28 | 35:21.29 | 4.0s | accident | 70% | accident 70% / change 6% / graduate 4% |
| 35:21.32 | 35:25.32 | 4.0s | ? | 27% | before 27% / black 12% / last 9% |
| 35:25.36 | 35:29.36 | 4.0s | ? | 23% | thanksgiving 23% / black 21% / man 13% |
| 35:29.39 | 35:33.40 | 4.0s | ? | 18% | black 18% / thanksgiving 16% / pizza 10% |
| 35:33.43 | 35:37.43 | 4.0s | ? | 25% | pizza 25% / work 17% / accident 7% |
| 35:37.47 | 35:41.47 | 4.0s | ? | 26% | decide 26% / accident 10% / black 8% |
| 35:41.51 | 35:45.51 | 4.0s | ? | 10% | cousin 10% / cheat 8% / graduate 7% |
| 35:45.54 | 35:49.55 | 4.0s | ? | 11% | computer 11% / secretary 10% / birthday 8% |
| 35:49.58 | 35:53.59 | 4.0s | accident | 58% | accident 58% / pizza 4% / wrong 4% |
| 35:53.62 | 35:57.62 | 4.0s | ? | 29% | all 29% / accident 10% / work 6% |
| 35:57.66 | 36:01.66 | 4.0s | ? | 31% | letter 31% / what 13% / shirt 12% |
| 36:01.69 | 36:05.70 | 4.0s | ? | 25% | graduate 25% / thin 16% / last 12% |
| 36:05.73 | 36:09.73 | 4.0s | ? | 32% | year 32% / work 18% / wrong 8% |
| 36:09.77 | 36:13.77 | 4.0s | accident | 70% | accident 70% / basketball 5% / dark 4% |
| 36:13.80 | 36:17.81 | 4.0s | ? | 11% | pink 11% / how 7% / paint 5% |
| 36:17.84 | 36:21.85 | 4.0s | ? | 31% | letter 31% / thin 15% / fine 10% |
| 36:21.88 | 36:25.88 | 4.0s | decide | 56% | decide 56% / walk 8% / black 4% |
| 36:25.92 | 36:29.92 | 4.0s | ? | 22% | secretary 22% / pizza 20% / accident 10% |
| 36:29.95 | 36:33.96 | 4.0s | want | 54% | want 54% / accident 8% / play 7% |
| 36:33.99 | 36:38.00 | 4.0s | accident | 59% | accident 59% / secretary 21% / man 4% |
| 36:38.03 | 36:42.03 | 4.0s | ? | 18% | black 18% / before 9% / decide 7% |
| 36:42.07 | 36:46.07 | 4.0s | ? | 27% | short 27% / decide 10% / wrong 9% |
| 36:46.10 | 36:50.11 | 4.0s | ? | 38% | accident 38% / book 7% / secretary 7% |
| 36:50.14 | 36:54.14 | 4.0s | ? | 29% | all 29% / clothes 8% / cook 7% |
| 36:54.18 | 36:58.18 | 4.0s | ? | 22% | what 22% / graduate 15% / fine 6% |
| 36:58.22 | 37:02.22 | 4.0s | accident | 92% | accident 92% / secretary 3% / dark 1% |
| 37:02.25 | 37:06.26 | 4.0s | ? | 24% | what 24% / fine 21% / all 14% |
| 37:06.29 | 37:10.30 | 4.0s | ? | 20% | year 20% / work 11% / secretary 8% |
| 37:10.33 | 37:14.33 | 4.0s | ? | 41% | accident 41% / secretary 24% / change 18% |
| 37:14.36 | 37:18.37 | 4.0s | change | 61% | change 61% / secretary 19% / accident 12% |
| 37:18.40 | 37:22.41 | 4.0s | ? | 49% | accident 49% / family 12% / change 7% |
| 37:22.44 | 37:26.44 | 4.0s | ? | 22% | accident 22% / black 14% / dog 7% |
| 37:26.48 | 37:30.48 | 4.0s | ? | 33% | cook 33% / change 9% / graduate 7% |
| 37:30.51 | 37:34.52 | 4.0s | accident | 62% | accident 62% / secretary 14% / shirt 2% |
| 37:34.55 | 37:38.56 | 4.0s | accident | 68% | accident 68% / change 14% / cook 9% |
| 37:38.59 | 37:42.59 | 4.0s | ? | 38% | accident 38% / secretary 12% / wrong 6% |
| 37:42.63 | 37:46.63 | 4.0s | ? | 30% | play 30% / black 18% / accident 13% |
| 37:46.66 | 37:50.67 | 4.0s | cook | 66% | cook 66% / all 8% / later 5% |
| 37:50.70 | 37:54.71 | 4.0s | accident | 74% | accident 74% / change 8% / thin 7% |
| 37:54.74 | 37:58.74 | 4.0s | ? | 47% | accident 47% / wrong 16% / change 14% |
| 37:58.78 | 38:02.78 | 4.0s | accident | 83% | accident 83% / what 2% / hot 2% |
| 38:02.81 | 38:06.82 | 4.0s | secretary | 86% | secretary 86% / accident 10% / same 1% |
| 38:06.85 | 38:10.86 | 4.0s | ? | 15% | year 15% / accident 13% / letter 13% |
| 38:10.89 | 38:14.89 | 4.0s | go | 54% | go 54% / graduate 7% / jacket 6% |
| 38:14.93 | 38:18.93 | 4.0s | ? | 24% | short 24% / now 13% / wrong 12% |
| 38:18.96 | 38:22.97 | 4.0s | ? | 16% | accident 16% / all 10% / orange 9% |
| 38:23.00 | 38:27.01 | 4.0s | change | 57% | change 57% / accident 14% / computer 4% |
| 38:27.04 | 38:31.04 | 4.0s | ? | 25% | graduate 25% / accident 23% / all 20% |
| 38:31.07 | 38:35.08 | 4.0s | ? | 49% | pizza 49% / last 9% / thanksgiving 4% |
| 38:35.11 | 38:39.12 | 4.0s | ? | 19% | decide 19% / accident 13% / black 9% |
| 38:39.15 | 38:43.15 | 4.0s | ? | 32% | last 32% / basketball 8% / corn 7% |

## 不經切詞器：1 秒滑動窗口、信心 ≥ 0.5（相鄰同詞合併，共 1154 個）

| 時間 | 輸出 | 最高信心 |
| --- | --- | --- |
| 00:09.14–00:09.61 | last | 80% |
| 00:10.78–00:10.78 | letter | 51% |
| 00:12.18–00:12.18 | last | 69% |
| 00:15.45–00:15.68 | black | 62% |
| 00:18.95–00:18.95 | play | 71% |
| 00:19.42–00:19.65 | accident | 68% |
| 00:20.35–00:20.35 | help | 73% |
| 00:21.75–00:21.75 | hot | 60% |
| 00:29.23–00:29.23 | meet | 50% |
| 00:30.40–00:30.63 | later | 69% |
| 00:38.57–00:38.80 | thanksgiving | 63% |
| 00:39.97–00:39.97 | all | 51% |
| 00:40.44–00:40.67 | cook | 87% |
| 00:41.14–00:41.14 | want | 59% |
| 00:41.38–00:41.38 | now | 81% |
| 00:41.61–00:41.84 | play | 74% |
| 00:43.94–00:43.94 | no | 81% |
| 00:45.34–00:46.05 | later | 94% |
| 00:55.39–00:55.86 | short | 93% |
| 01:01.23–01:01.23 | man | 51% |
| 01:06.60–01:06.60 | last | 76% |
| 01:07.53–01:07.77 | thin | 55% |
| 01:18.98–01:18.98 | what | 70% |
| 01:22.02–01:22.25 | short | 66% |
| 01:23.42–01:23.42 | finish | 64% |
| 01:24.58–01:24.58 | go | 82% |
| 01:25.28–01:25.52 | last | 64% |
| 01:27.15–01:27.15 | later | 62% |
| 01:28.79–01:28.79 | dance | 53% |
| 01:33.46–01:33.69 | change | 57% |
| 01:34.39–01:34.63 | many | 75% |
| 01:35.80–01:35.80 | short | 51% |
| 01:36.96–01:37.66 | family | 95% |
| 01:39.07–01:39.07 | thanksgiving | 68% |
| 01:40.70–01:41.17 | decide | 81% |
| 01:44.44–01:44.67 | last | 68% |
| 01:45.37–01:45.84 | last | 94% |
| 01:46.07–01:46.54 | play | 81% |
| 01:47.71–01:47.71 | black | 51% |
| 01:49.58–01:49.58 | cool | 56% |
| 01:53.31–01:53.55 | what | 82% |
| 01:54.01–01:54.25 | thin | 86% |
| 01:54.95–01:55.42 | basketball | 81% |
| 01:58.69–01:58.92 | before | 54% |
| 01:59.15–01:59.15 | short | 60% |
| 02:00.09–02:00.09 | shirt | 60% |
| 02:00.55–02:00.55 | now | 63% |
| 02:04.06–02:04.06 | last | 82% |
| 02:08.26–02:08.26 | letter | 52% |
| 02:08.96–02:09.90 | year | 95% |
| 02:11.53–02:11.53 | last | 68% |
| 02:14.57–02:14.57 | what | 55% |
| 02:18.31–02:18.31 | before | 56% |
| 02:21.81–02:22.04 | all | 75% |
| 02:26.71–02:27.18 | play | 98% |
| 02:27.88–02:28.12 | right | 68% |
| 02:29.28–02:29.28 | cool | 52% |
| 02:31.15–02:31.15 | what | 52% |
| 02:32.79–02:32.79 | decide | 93% |
| 02:34.66–02:34.89 | last | 80% |
| 02:36.29–02:36.29 | last | 54% |
| 02:37.46–02:37.46 | go | 64% |
| 02:40.26–02:40.49 | study | 58% |
| 02:43.53–02:43.76 | play | 95% |
| 02:44.23–02:44.46 | accident | 70% |
| 02:45.63–02:46.10 | go | 85% |
| 02:52.17–02:52.41 | last | 85% |
| 02:58.48–02:58.48 | want | 68% |
| 02:58.71–02:58.71 | now | 92% |
| 03:01.28–03:01.51 | decide | 81% |
| 03:03.62–03:03.85 | cool | 76% |
| 03:04.55–03:04.55 | basketball | 59% |
| 03:06.89–03:07.12 | later | 91% |
| 03:07.59–03:07.59 | study | 70% |
| 03:10.16–03:10.62 | basketball | 83% |
| 03:12.03–03:12.26 | thanksgiving | 57% |
| 03:13.19–03:13.43 | finish | 77% |
| 03:14.83–03:15.06 | play | 67% |
| 03:15.76–03:16.00 | black | 51% |
| 03:17.16–03:17.16 | letter | 74% |
| 03:17.63–03:17.63 | play | 73% |
| 03:18.56–03:18.56 | last | 54% |
| 03:20.43–03:20.90 | go | 89% |
| 03:23.24–03:23.47 | secretary | 68% |
| 03:24.64–03:24.64 | thanksgiving | 71% |
| 03:26.27–03:26.51 | decide | 81% |
| 03:27.44–03:28.14 | can | 98% |
| 03:30.24–03:30.71 | decide | 74% |
| 03:31.41–03:31.41 | decide | 88% |
| 03:31.65–03:31.88 | can | 99% |
| 03:36.08–03:36.08 | secretary | 52% |
| 03:36.55–03:36.55 | want | 54% |
| 03:38.42–03:38.65 | decide | 71% |
| 03:39.82–03:40.05 | white | 67% |
| 03:40.52–03:40.99 | basketball | 96% |
| 03:42.39–03:42.39 | decide | 61% |
| 03:42.62–03:42.86 | can | 99% |
| 03:44.26–03:44.26 | last | 50% |
| 03:45.19–03:45.19 | play | 86% |
| 03:45.43–03:45.89 | accident | 98% |
| 03:47.53–03:47.76 | before | 60% |
| 03:48.23–03:48.23 | city | 78% |
| 03:49.63–03:50.56 | play | 88% |
| 03:51.73–03:51.73 | change | 52% |
| 03:52.67–03:53.37 | letter | 83% |
| 03:56.17–03:56.17 | change | 58% |
| 03:56.40–03:56.40 | graduate | 52% |
| 03:58.74–03:58.74 | play | 59% |
| 04:02.71–04:02.71 | paint | 71% |
| 04:05.75–04:06.68 | letter | 76% |
| 04:10.65–04:10.65 | medicine | 52% |
| 04:10.88–04:11.35 | year | 60% |
| 04:13.69–04:13.69 | want | 57% |
| 04:16.96–04:17.19 | later | 84% |
| 04:18.36–04:18.36 | letter | 53% |
| 04:19.99–04:19.99 | walk | 53% |
| 04:22.33–04:22.56 | letter | 51% |
| 04:22.80–04:23.26 | walk | 97% |
| 04:25.37–04:25.60 | last | 91% |
| 04:30.04–04:30.04 | short | 58% |
| 04:33.54–04:34.47 | right | 88% |
| 04:35.18–04:35.64 | last | 88% |
| 04:36.81–04:36.81 | last | 53% |
| 04:37.04–04:37.04 | thin | 53% |
| 04:39.85–04:39.85 | last | 64% |
| 04:46.85–04:48.02 | basketball | 93% |
| 04:49.19–04:49.66 | can | 97% |
| 04:49.89–04:49.89 | clothes | 62% |
| 04:50.12–04:50.59 | finish | 95% |
| 04:54.33–04:54.56 | all | 74% |
| 04:55.73–04:55.73 | want | 57% |
| 05:00.87–05:00.87 | help | 52% |
| 05:02.50–05:02.50 | letter | 51% |
| 05:05.31–05:05.31 | dark | 51% |
| 05:06.47–05:06.47 | last | 77% |
| 05:10.68–05:10.68 | before | 79% |
| 05:15.58–05:15.58 | letter | 52% |
| 05:16.05–05:16.05 | cheat | 59% |
| 05:17.92–05:18.15 | accident | 71% |
| 05:18.62–05:18.85 | year | 71% |
| 05:21.19–05:21.42 | play | 60% |
| 05:22.59–05:22.82 | last | 76% |
| 05:23.76–05:23.76 | deaf | 51% |
| 05:24.93–05:25.86 | want | 83% |
| 05:27.73–05:27.73 | last | 54% |
| 05:28.89–05:28.89 | decide | 54% |
| 05:34.03–05:34.27 | but | 71% |
| 05:36.37–05:36.37 | corn | 55% |
| 05:38.24–05:38.47 | go | 58% |
| 05:40.57–05:40.57 | chair | 51% |
| 05:41.04–05:41.04 | city | 71% |
| 05:43.38–05:43.38 | give | 57% |
| 05:43.61–05:43.61 | play | 52% |
| 05:45.01–05:45.25 | basketball | 91% |
| 05:45.95–05:45.95 | study | 51% |
| 05:46.18–05:46.18 | go | 62% |
| 05:46.41–05:46.41 | study | 52% |
| 05:48.28–05:48.75 | how | 92% |
| 05:49.45–05:49.45 | medicine | 79% |
| 05:51.32–05:51.32 | play | 51% |
| 05:52.72–05:53.42 | thanksgiving | 92% |
| 05:54.35–05:54.35 | thanksgiving | 56% |
| 05:55.06–05:55.06 | secretary | 60% |
| 05:56.46–05:56.46 | cow | 58% |
| 05:59.73–05:59.73 | later | 72% |
| 06:00.89–06:00.89 | last | 65% |
| 06:03.23–06:03.70 | what | 78% |
| 06:03.93–06:03.93 | last | 75% |
| 06:06.73–06:06.73 | basketball | 73% |
| 06:07.67–06:07.67 | want | 67% |
| 06:09.30–06:09.77 | help | 77% |
| 06:11.40–06:11.40 | secretary | 51% |
| 06:11.87–06:11.87 | accident | 50% |
| 06:12.34–06:12.34 | letter | 86% |
| 06:13.97–06:14.21 | letter | 70% |
| 06:16.08–06:16.08 | right | 70% |
| 06:19.35–06:19.35 | last | 94% |
| 06:21.21–06:21.21 | black | 63% |
| 06:21.45–06:21.45 | thanksgiving | 51% |
| 06:22.15–06:22.15 | basketball | 50% |
| 06:23.55–06:23.78 | play | 76% |
| 06:36.40–06:36.86 | play | 94% |
| 06:37.56–06:37.80 | thanksgiving | 96% |
| 06:38.50–06:38.50 | accident | 69% |
| 06:44.34–06:44.34 | what | 51% |
| 06:45.04–06:45.27 | decide | 70% |
| 06:47.61–06:47.61 | letter | 61% |
| 06:47.84–06:48.07 | study | 93% |
| 06:51.58–06:51.58 | change | 58% |
| 06:52.75–06:53.68 | play | 91% |
| 06:54.85–06:54.85 | medicine | 55% |
| 06:56.25–06:58.82 | short | 87% |
| 06:59.99–06:59.99 | letter | 55% |
| 07:05.12–07:05.36 | short | 70% |
| 07:06.53–07:06.99 | last | 87% |
| 07:07.93–07:07.93 | basketball | 55% |
| 07:13.53–07:13.53 | walk | 50% |
| 07:14.70–07:14.70 | letter | 74% |
| 07:17.04–07:17.27 | secretary | 64% |
| 07:17.97–07:18.20 | letter | 89% |
| 07:19.37–07:19.37 | last | 57% |
| 07:19.61–07:19.84 | letter | 92% |
| 07:20.77–07:21.24 | letter | 79% |
| 07:27.55–07:27.78 | last | 60% |
| 07:28.71–07:29.18 | paper | 83% |
| 07:31.52–07:31.52 | what | 54% |
| 07:33.85–07:33.85 | paint | 72% |
| 07:36.66–07:36.66 | pull | 54% |
| 07:38.29–07:38.76 | medicine | 83% |
| 07:39.46–07:39.46 | medicine | 64% |
| 07:42.26–07:42.50 | year | 67% |
| 07:43.66–07:43.66 | dance | 60% |
| 07:46.47–07:46.93 | letter | 87% |
| 07:47.40–07:47.40 | study | 55% |
| 07:49.97–07:50.20 | last | 62% |
| 07:50.44–07:50.44 | graduate | 81% |
| 07:50.67–07:50.90 | secretary | 91% |
| 07:53.24–07:53.47 | graduate | 81% |
| 07:57.68–07:57.68 | play | 67% |
| 07:58.85–07:59.55 | help | 88% |
| 07:59.78–08:00.01 | what | 57% |
| 08:01.88–08:01.88 | right | 54% |
| 08:03.05–08:03.05 | son | 60% |
| 08:05.38–08:05.38 | later | 62% |
| 08:05.62–08:05.62 | last | 61% |
| 08:11.22–08:11.22 | year | 74% |
| 08:11.69–08:11.69 | thin | 57% |
| 08:15.66–08:16.13 | but | 96% |
| 08:17.30–08:18.23 | play | 97% |
| 08:19.17–08:19.17 | last | 66% |
| 08:19.87–08:19.87 | last | 63% |
| 08:22.20–08:22.20 | play | 50% |
| 08:25.70–08:25.70 | want | 57% |
| 08:28.74–08:28.74 | dog | 57% |
| 08:31.31–08:31.31 | corn | 69% |
| 08:32.25–08:32.25 | last | 63% |
| 08:32.95–08:32.95 | black | 64% |
| 08:33.41–08:33.41 | thin | 65% |
| 08:35.28–08:35.28 | secretary | 62% |
| 08:42.05–08:42.05 | later | 66% |
| 08:42.29–08:42.29 | walk | 52% |
| 08:43.92–08:44.16 | play | 84% |
| 08:48.13–08:48.60 | help | 86% |
| 08:49.29–08:49.53 | before | 54% |
| 08:50.23–08:50.93 | what | 91% |
| 08:53.03–08:53.50 | can | 99% |
| 08:55.60–08:55.84 | go | 88% |
| 08:57.00–08:57.00 | black | 57% |
| 08:57.24–08:57.47 | play | 62% |
| 09:02.61–09:02.61 | year | 61% |
| 09:06.11–09:06.35 | last | 76% |
| 09:06.81–09:06.81 | thin | 62% |
| 09:08.45–09:08.45 | later | 51% |
| 09:08.91–09:09.38 | letter | 80% |
| 09:10.32–09:10.78 | last | 80% |
| 09:13.12–09:13.12 | cook | 57% |
| 09:13.82–09:13.82 | before | 67% |
| 09:16.86–09:17.32 | decide | 88% |
| 09:18.26–09:18.26 | school | 66% |
| 09:18.96–09:19.43 | cook | 94% |
| 09:20.13–09:20.13 | graduate | 57% |
| 09:22.93–09:23.16 | accident | 86% |
| 09:23.40–09:24.56 | play | 96% |
| 09:26.67–09:26.67 | but | 71% |
| 09:26.90–09:27.13 | go | 81% |
| 09:31.10–09:31.34 | last | 89% |
| 09:32.50–09:32.74 | year | 85% |
| 09:33.67–09:33.67 | decide | 92% |
| 09:34.14–09:34.37 | play | 73% |
| 09:35.31–09:35.31 | clothes | 56% |
| 09:35.77–09:35.77 | accident | 63% |
| 09:40.91–09:40.91 | study | 51% |
| 09:43.02–09:43.25 | right | 78% |
| 09:46.52–09:46.75 | last | 76% |
| 09:48.15–09:48.39 | basketball | 74% |
| 09:50.02–09:50.26 | later | 58% |
| 09:50.49–09:50.49 | last | 56% |
| 09:53.53–09:53.76 | play | 67% |
| 09:57.73–09:57.96 | letter | 57% |
| 09:58.20–09:58.20 | short | 57% |
| 09:59.13–09:59.60 | all | 98% |
| 10:04.04–10:04.04 | meet | 66% |
| 10:04.27–10:04.74 | last | 78% |
| 10:04.97–10:04.97 | thin | 56% |
| 10:09.64–10:09.64 | what | 57% |
| 10:10.81–10:10.81 | computer | 59% |
| 10:11.98–10:12.45 | later | 62% |
| 10:16.65–10:16.65 | letter | 69% |
| 10:18.52–10:18.75 | go | 77% |
| 10:19.92–10:19.92 | later | 60% |
| 10:23.42–10:23.66 | decide | 58% |
| 10:26.23–10:26.23 | before | 52% |
| 10:28.56–10:28.79 | decide | 52% |
| 10:29.50–10:29.50 | play | 80% |
| 10:31.36–10:31.36 | basketball | 78% |
| 10:32.07–10:32.07 | letter | 96% |
| 10:32.30–10:32.30 | secretary | 51% |
| 10:32.53–10:32.53 | how | 63% |
| 10:33.23–10:33.23 | accident | 52% |
| 10:33.93–10:34.40 | right | 60% |
| 10:34.87–10:35.10 | later | 62% |
| 10:43.51–10:43.74 | right | 59% |
| 10:46.31–10:46.31 | city | 51% |
| 10:47.25–10:47.48 | want | 74% |
| 10:51.92–10:51.92 | decide | 64% |
| 10:52.62–10:52.62 | cook | 63% |
| 10:53.32–10:53.32 | play | 51% |
| 10:54.72–10:55.19 | last | 80% |
| 10:56.59–10:56.59 | secretary | 55% |
| 11:01.73–11:01.73 | orange | 53% |
| 11:03.83–11:03.83 | what | 61% |
| 11:04.30–11:04.53 | secretary | 89% |
| 11:06.87–11:07.10 | enjoy | 79% |
| 11:07.57–11:07.57 | what | 54% |
| 11:08.97–11:08.97 | secretary | 60% |
| 11:09.43–11:09.67 | before | 52% |
| 11:10.14–11:10.84 | later | 100% |
| 11:11.54–11:11.54 | letter | 84% |
| 11:14.57–11:14.57 | decide | 51% |
| 11:15.04–11:15.27 | walk | 92% |
| 11:16.21–11:16.21 | right | 60% |
| 11:20.65–11:21.11 | decide | 96% |
| 11:23.68–11:24.38 | decide | 93% |
| 11:24.62–11:24.62 | play | 71% |
| 11:25.08–11:25.08 | want | 51% |
| 11:28.35–11:28.35 | want | 61% |
| 11:29.29–11:29.29 | want | 58% |
| 11:33.03–11:33.73 | decide | 91% |
| 11:37.23–11:37.23 | right | 55% |
| 11:40.73–11:40.73 | want | 51% |
| 11:45.40–11:46.11 | want | 91% |
| 11:46.34–11:46.34 | cook | 71% |
| 11:50.54–11:50.54 | medicine | 60% |
| 11:52.18–11:52.41 | later | 61% |
| 11:53.11–11:53.11 | letter | 51% |
| 11:53.35–11:53.58 | last | 63% |
| 11:55.68–11:55.68 | many | 78% |
| 11:56.15–11:56.85 | decide | 84% |
| 11:58.95–11:58.95 | thin | 77% |
| 12:01.52–12:01.75 | short | 97% |
| 12:03.16–12:03.16 | decide | 52% |
| 12:05.02–12:05.02 | secretary | 71% |
| 12:05.26–12:05.49 | short | 96% |
| 12:05.73–12:05.73 | bed | 50% |
| 12:05.96–12:05.96 | letter | 62% |
| 12:11.56–12:11.56 | play | 56% |
| 12:16.94–12:17.17 | basketball | 72% |
| 12:17.40–12:17.87 | decide | 96% |
| 12:19.97–12:20.21 | help | 76% |
| 12:21.61–12:21.61 | finish | 57% |
| 12:22.77–12:23.01 | what | 63% |
| 12:27.21–12:27.45 | black | 71% |
| 12:27.68–12:27.68 | graduate | 61% |
| 12:28.38–12:28.62 | accident | 73% |
| 12:28.85–12:28.85 | hot | 63% |
| 12:29.78–12:29.78 | decide | 55% |
| 12:30.48–12:30.48 | decide | 70% |
| 12:34.69–12:34.69 | now | 75% |
| 12:34.92–12:35.15 | accident | 59% |
| 12:38.42–12:38.42 | all | 60% |
| 12:38.66–12:39.12 | decide | 97% |
| 12:42.39–12:42.39 | but | 72% |
| 12:42.63–12:42.86 | meet | 93% |
| 12:43.56–12:44.03 | meet | 75% |
| 12:44.50–12:44.73 | tell | 76% |
| 12:45.43–12:46.13 | thanksgiving | 84% |
| 12:47.07–12:47.77 | last | 85% |
| 12:48.70–12:48.70 | black | 55% |
| 12:49.64–12:49.87 | decide | 57% |
| 12:52.67–12:52.90 | thin | 85% |
| 12:53.61–12:53.61 | secretary | 52% |
| 12:53.84–12:54.31 | letter | 80% |
| 12:55.94–12:56.17 | secretary | 57% |
| 13:02.72–13:03.18 | decide | 74% |
| 13:03.65–13:03.65 | play | 59% |
| 13:08.09–13:08.09 | accident | 50% |
| 13:14.39–13:14.63 | thin | 60% |
| 13:15.79–13:16.50 | decide | 81% |
| 13:17.90–13:18.36 | letter | 84% |
| 13:20.00–13:20.47 | thin | 81% |
| 13:22.34–13:22.34 | letter | 51% |
| 13:23.04–13:23.27 | meet | 86% |
| 13:27.94–13:28.41 | change | 86% |
| 13:29.11–13:29.34 | but | 79% |
| 13:30.74–13:30.98 | computer | 75% |
| 13:33.31–13:33.31 | help | 51% |
| 13:34.71–13:34.71 | what | 51% |
| 13:35.18–13:35.18 | study | 64% |
| 13:35.88–13:35.88 | thursday | 62% |
| 13:36.58–13:36.58 | secretary | 71% |
| 13:38.22–13:38.45 | go | 89% |
| 13:40.79–13:40.79 | last | 52% |
| 13:41.02–13:41.02 | secretary | 82% |
| 13:41.72–13:42.19 | letter | 80% |
| 13:43.12–13:43.12 | letter | 58% |
| 13:44.76–13:44.76 | cool | 58% |
| 13:50.60–13:50.60 | what | 67% |
| 13:51.30–13:51.30 | what | 58% |
| 13:53.17–13:53.63 | play | 89% |
| 13:54.57–13:54.57 | cook | 95% |
| 13:55.03–13:55.03 | accident | 58% |
| 13:56.44–13:56.67 | cook | 72% |
| 13:57.37–13:57.37 | medicine | 55% |
| 13:59.94–14:00.17 | what | 93% |
| 14:02.27–14:03.21 | medicine | 62% |
| 14:05.08–14:05.08 | last | 54% |
| 14:05.78–14:06.25 | go | 97% |
| 14:06.48–14:06.48 | last | 66% |
| 14:08.11–14:08.11 | many | 59% |
| 14:09.05–14:09.05 | want | 53% |
| 14:10.45–14:10.45 | thanksgiving | 75% |
| 14:10.92–14:11.15 | decide | 82% |
| 14:12.09–14:12.09 | cook | 78% |
| 14:12.32–14:12.32 | all | 72% |
| 14:12.55–14:12.55 | graduate | 51% |
| 14:13.49–14:13.49 | decide | 74% |
| 14:13.72–14:13.95 | secretary | 91% |
| 14:15.59–14:15.59 | black | 50% |
| 14:17.69–14:17.92 | secretary | 74% |
| 14:20.73–14:21.43 | play | 75% |
| 14:21.89–14:21.89 | paint | 73% |
| 14:25.63–14:25.63 | before | 69% |
| 14:27.27–14:27.27 | medicine | 71% |
| 14:28.20–14:28.20 | letter | 50% |
| 14:28.43–14:28.43 | last | 73% |
| 14:31.24–14:31.70 | play | 60% |
| 14:32.17–14:32.64 | but | 86% |
| 14:33.11–14:33.11 | last | 60% |
| 14:33.57–14:34.04 | letter | 69% |
| 14:38.48–14:38.48 | play | 62% |
| 14:38.95–14:39.41 | cook | 56% |
| 14:40.11–14:40.35 | play | 80% |
| 14:40.81–14:41.05 | study | 74% |
| 14:43.62–14:43.62 | letter | 61% |
| 14:44.55–14:44.55 | want | 65% |
| 14:45.25–14:45.95 | enjoy | 83% |
| 14:46.42–14:46.89 | play | 97% |
| 14:47.35–14:47.35 | walk | 62% |
| 14:48.52–14:48.52 | cook | 69% |
| 14:49.46–14:49.46 | thanksgiving | 63% |
| 14:49.69–14:50.62 | want | 79% |
| 14:52.26–14:52.49 | accident | 81% |
| 14:53.19–14:53.19 | letter | 78% |
| 14:56.46–14:56.46 | thin | 50% |
| 14:59.03–14:59.03 | letter | 57% |
| 15:00.20–15:00.20 | letter | 68% |
| 15:01.13–15:01.60 | letter | 73% |
| 15:03.70–15:03.70 | secretary | 55% |
| 15:06.51–15:06.51 | give | 67% |
| 15:07.67–15:08.14 | decide | 93% |
| 15:09.78–15:10.01 | decide | 77% |
| 15:11.41–15:11.64 | can | 75% |
| 15:11.88–15:12.35 | walk | 78% |
| 15:13.98–15:14.45 | fish | 87% |
| 15:15.15–15:15.15 | graduate | 71% |
| 15:15.62–15:15.62 | secretary | 63% |
| 15:16.32–15:16.32 | can | 76% |
| 15:16.78–15:16.78 | walk | 75% |
| 15:17.48–15:17.72 | give | 76% |
| 15:23.09–15:23.32 | drink | 71% |
| 15:25.19–15:25.19 | year | 54% |
| 15:25.42–15:25.42 | black | 56% |
| 15:32.20–15:32.20 | walk | 89% |
| 15:33.83–15:34.07 | meet | 74% |
| 15:35.47–15:35.70 | last | 85% |
| 15:37.10–15:37.10 | before | 56% |
| 15:37.80–15:38.27 | before | 59% |
| 15:38.50–15:38.50 | cook | 61% |
| 15:39.67–15:39.67 | basketball | 57% |
| 15:41.54–15:41.54 | study | 68% |
| 15:42.01–15:42.01 | letter | 61% |
| 15:43.41–15:43.64 | later | 68% |
| 15:45.51–15:45.75 | walk | 77% |
| 15:48.78–15:48.78 | decide | 54% |
| 15:49.25–15:49.72 | now | 62% |
| 15:50.42–15:50.42 | play | 57% |
| 15:50.88–15:50.88 | drink | 50% |
| 15:54.15–15:54.39 | right | 90% |
| 15:54.62–15:54.85 | secretary | 81% |
| 15:55.32–15:55.55 | last | 60% |
| 15:59.06–15:59.29 | letter | 93% |
| 16:01.63–16:01.86 | accident | 67% |
| 16:02.09–16:02.09 | secretary | 61% |
| 16:10.04–16:10.04 | son | 61% |
| 16:10.74–16:10.74 | cook | 57% |
| 16:11.67–16:11.90 | play | 89% |
| 16:12.37–16:12.37 | cow | 56% |
| 16:12.61–16:12.61 | can | 77% |
| 16:13.07–16:13.07 | play | 92% |
| 16:14.47–16:14.47 | secretary | 87% |
| 16:14.94–16:15.17 | cow | 71% |
| 16:15.41–16:15.64 | can | 99% |
| 16:18.68–16:19.14 | can | 96% |
| 16:19.38–16:19.85 | walk | 86% |
| 16:20.78–16:21.01 | thursday | 65% |
| 16:23.12–16:23.12 | dark | 53% |
| 16:24.52–16:24.52 | play | 59% |
| 16:24.98–16:24.98 | walk | 73% |
| 16:25.45–16:26.15 | play | 75% |
| 16:36.66–16:36.66 | letter | 69% |
| 16:37.13–16:37.13 | before | 61% |
| 16:37.83–16:37.83 | accident | 89% |
| 16:39.47–16:40.17 | basketball | 84% |
| 16:41.33–16:41.80 | family | 96% |
| 16:42.27–16:42.74 | thanksgiving | 84% |
| 16:43.44–16:44.14 | what | 80% |
| 16:44.84–16:44.84 | accident | 59% |
| 16:47.64–16:48.11 | thanksgiving | 83% |
| 16:48.81–16:49.51 | decide | 89% |
| 16:52.54–16:52.54 | decide | 54% |
| 16:53.01–16:53.25 | give | 68% |
| 16:54.88–16:54.88 | short | 55% |
| 16:58.15–16:58.15 | black | 50% |
| 16:58.38–16:58.62 | last | 86% |
| 17:00.25–17:00.49 | decide | 66% |
| 17:01.19–17:01.19 | black | 53% |
| 17:05.39–17:05.62 | change | 84% |
| 17:11.23–17:11.93 | decide | 86% |
| 17:14.27–17:14.27 | last | 60% |
| 17:16.84–17:16.84 | decide | 53% |
| 17:18.00–17:18.24 | what | 64% |
| 17:22.67–17:23.14 | walk | 85% |
| 17:23.38–17:23.61 | can | 92% |
| 17:27.81–17:27.81 | play | 56% |
| 17:29.92–17:30.15 | all | 68% |
| 17:32.48–17:32.48 | right | 51% |
| 17:33.89–17:33.89 | decide | 52% |
| 17:34.59–17:34.59 | short | 61% |
| 17:35.76–17:36.22 | cook | 72% |
| 17:36.45–17:37.62 | accident | 74% |
| 17:38.56–17:38.56 | school | 63% |
| 17:40.43–17:40.66 | black | 70% |
| 17:44.40–17:44.40 | letter | 59% |
| 17:46.73–17:46.73 | medicine | 64% |
| 17:47.43–17:47.67 | before | 94% |
| 17:47.90–17:47.90 | letter | 73% |
| 17:49.30–17:49.30 | letter | 53% |
| 17:51.64–17:51.87 | decide | 70% |
| 17:55.14–17:55.37 | change | 86% |
| 17:55.61–17:55.61 | cook | 52% |
| 17:56.08–17:56.08 | study | 70% |
| 18:03.32–18:03.32 | all | 70% |
| 18:04.02–18:04.48 | secretary | 83% |
| 18:05.18–18:05.42 | accident | 60% |
| 18:06.35–18:06.35 | black | 59% |
| 18:09.86–18:09.86 | play | 50% |
| 18:10.79–18:11.02 | letter | 64% |
| 18:13.83–18:13.83 | cheat | 53% |
| 18:14.53–18:14.53 | short | 63% |
| 18:16.16–18:16.16 | last | 55% |
| 18:17.56–18:17.56 | decide | 53% |
| 18:21.77–18:21.77 | now | 52% |
| 18:26.20–18:26.20 | go | 64% |
| 18:29.01–18:29.01 | give | 55% |
| 18:29.47–18:29.47 | walk | 66% |
| 18:32.74–18:32.74 | want | 53% |
| 18:33.21–18:33.91 | walk | 98% |
| 18:34.38–18:34.61 | thin | 66% |
| 18:36.02–18:36.48 | black | 71% |
| 18:38.35–18:38.35 | give | 60% |
| 18:38.58–18:39.05 | all | 73% |
| 18:43.49–18:43.49 | last | 59% |
| 18:43.96–18:43.96 | letter | 52% |
| 18:45.59–18:45.83 | letter | 67% |
| 18:50.96–18:51.43 | last | 97% |
| 18:52.13–18:52.13 | study | 55% |
| 18:59.37–18:59.37 | no | 53% |
| 19:03.11–19:03.11 | pizza | 50% |
| 19:09.18–19:09.41 | work | 81% |
| 19:10.12–19:10.35 | year | 75% |
| 19:13.39–19:13.85 | play | 88% |
| 19:15.25–19:15.49 | black | 74% |
| 19:20.16–19:20.16 | change | 51% |
| 19:20.63–19:20.63 | go | 53% |
| 19:23.43–19:23.43 | pull | 51% |
| 19:25.53–19:25.77 | fish | 71% |
| 19:28.10–19:28.33 | enjoy | 88% |
| 19:29.50–19:29.50 | letter | 76% |
| 19:29.73–19:29.97 | time | 81% |
| 19:31.37–19:31.37 | orange | 61% |
| 19:37.44–19:37.44 | letter | 66% |
| 19:40.01–19:40.01 | last | 62% |
| 19:44.45–19:44.68 | year | 67% |
| 19:48.65–19:48.65 | before | 53% |
| 19:54.49–19:54.49 | walk | 84% |
| 19:57.06–19:57.30 | work | 75% |
| 19:57.76–19:57.76 | cook | 58% |
| 19:58.23–19:58.23 | language | 78% |
| 19:58.70–19:58.70 | right | 54% |
| 19:59.63–19:59.87 | right | 82% |
| 20:00.10–20:00.33 | year | 93% |
| 20:01.27–20:01.27 | shirt | 80% |
| 20:02.67–20:02.67 | tell | 53% |
| 20:04.30–20:04.30 | medicine | 74% |
| 20:05.47–20:05.47 | black | 55% |
| 20:06.87–20:07.11 | pizza | 62% |
| 20:08.27–20:08.27 | letter | 75% |
| 20:08.51–20:08.51 | study | 56% |
| 20:09.21–20:09.21 | decide | 85% |
| 20:10.61–20:11.31 | year | 88% |
| 20:12.01–20:12.24 | decide | 88% |
| 20:15.05–20:15.05 | what | 53% |
| 20:15.75–20:15.75 | letter | 59% |
| 20:16.21–20:16.21 | before | 61% |
| 20:18.08–20:19.25 | play | 88% |
| 20:19.72–20:19.72 | letter | 55% |
| 20:23.46–20:23.46 | jacket | 56% |
| 20:23.92–20:24.39 | help | 63% |
| 20:26.03–20:26.49 | play | 62% |
| 20:36.77–20:37.24 | go | 79% |
| 20:39.57–20:39.81 | right | 55% |
| 20:40.97–20:40.97 | basketball | 67% |
| 20:45.41–20:45.64 | right | 63% |
| 20:50.32–20:50.55 | thin | 54% |
| 20:51.02–20:51.72 | graduate | 98% |
| 20:53.35–20:53.35 | secretary | 62% |
| 20:54.05–20:54.05 | candy | 50% |
| 20:54.29–20:54.29 | how | 63% |
| 20:55.45–20:56.15 | play | 91% |
| 20:58.72–20:59.19 | paint | 95% |
| 21:00.13–21:00.83 | what | 91% |
| 21:01.29–21:01.53 | letter | 86% |
| 21:02.93–21:03.16 | letter | 98% |
| 21:04.10–21:04.56 | play | 83% |
| 21:05.03–21:05.03 | accident | 54% |
| 21:05.26–21:05.26 | but | 64% |
| 21:06.20–21:06.66 | accident | 91% |
| 21:08.53–21:08.77 | play | 72% |
| 21:09.23–21:09.23 | basketball | 51% |
| 21:09.93–21:09.93 | basketball | 83% |
| 21:10.17–21:10.40 | play | 68% |
| 21:15.54–21:15.54 | medicine | 55% |
| 21:16.71–21:16.94 | letter | 96% |
| 21:18.11–21:18.11 | all | 80% |
| 21:19.04–21:19.28 | decide | 70% |
| 21:25.12–21:25.12 | secretary | 71% |
| 21:28.62–21:28.85 | dark | 75% |
| 21:29.09–21:29.56 | accident | 78% |
| 21:34.69–21:34.69 | decide | 63% |
| 21:37.96–21:38.43 | letter | 97% |
| 21:39.13–21:39.13 | white | 69% |
| 21:41.23–21:41.70 | right | 99% |
| 21:44.50–21:44.50 | same | 51% |
| 21:50.11–21:50.34 | decide | 72% |
| 21:53.61–21:53.61 | thanksgiving | 62% |
| 21:56.88–21:56.88 | before | 74% |
| 22:00.39–22:00.62 | cow | 91% |
| 22:00.85–22:01.32 | can | 91% |
| 22:01.55–22:01.55 | walk | 50% |
| 22:06.46–22:06.46 | play | 72% |
| 22:09.03–22:09.03 | accident | 90% |
| 22:10.20–22:10.90 | decide | 97% |
| 22:12.53–22:12.53 | black | 68% |
| 22:16.97–22:17.20 | play | 70% |
| 22:22.34–22:22.34 | play | 58% |
| 22:22.81–22:23.04 | last | 76% |
| 22:24.44–22:24.68 | what | 54% |
| 22:26.31–22:26.31 | basketball | 73% |
| 22:27.25–22:27.25 | later | 58% |
| 22:27.71–22:27.71 | last | 52% |
| 22:27.95–22:28.41 | black | 75% |
| 22:34.49–22:34.49 | decide | 55% |
| 22:36.82–22:36.82 | short | 60% |
| 22:39.16–22:39.16 | decide | 60% |
| 22:39.62–22:39.86 | letter | 81% |
| 22:41.03–22:41.26 | decide | 80% |
| 22:44.30–22:44.30 | black | 66% |
| 22:45.46–22:45.46 | cook | 52% |
| 22:45.93–22:45.93 | last | 64% |
| 22:47.33–22:47.33 | jacket | 57% |
| 22:49.20–22:49.20 | medicine | 56% |
| 22:49.67–22:50.13 | short | 77% |
| 22:52.94–22:53.17 | cook | 88% |
| 22:54.81–22:54.81 | secretary | 67% |
| 22:56.21–22:56.21 | accident | 56% |
| 22:56.44–22:56.44 | change | 61% |
| 23:03.45–23:03.45 | shirt | 52% |
| 23:03.68–23:03.68 | change | 74% |
| 23:04.62–23:05.32 | finish | 99% |
| 23:05.55–23:06.02 | dark | 68% |
| 23:08.12–23:08.59 | study | 72% |
| 23:09.05–23:09.29 | kiss | 78% |
| 23:09.52–23:10.22 | change | 98% |
| 23:10.92–23:10.92 | finish | 92% |
| 23:12.09–23:12.32 | thursday | 63% |
| 23:13.26–23:13.49 | secretary | 94% |
| 23:13.73–23:13.73 | letter | 73% |
| 23:13.96–23:13.96 | but | 68% |
| 23:14.66–23:14.89 | change | 52% |
| 23:16.06–23:16.30 | can | 66% |
| 23:20.50–23:20.50 | thin | 52% |
| 23:20.73–23:20.97 | letter | 73% |
| 23:22.60–23:22.60 | all | 52% |
| 23:26.11–23:26.57 | decide | 60% |
| 23:27.97–23:27.97 | last | 69% |
| 23:29.84–23:29.84 | black | 54% |
| 23:30.78–23:30.78 | accident | 68% |
| 23:31.24–23:31.24 | cheat | 56% |
| 23:33.11–23:33.58 | change | 76% |
| 23:34.05–23:34.05 | decide | 59% |
| 23:34.28–23:34.51 | accident | 74% |
| 23:37.55–23:37.55 | basketball | 57% |
| 23:43.86–23:43.86 | play | 55% |
| 23:44.32–23:44.32 | accident | 63% |
| 23:45.02–23:45.49 | letter | 84% |
| 23:46.42–23:46.42 | before | 87% |
| 23:48.29–23:48.53 | letter | 54% |
| 23:49.23–23:49.23 | later | 69% |
| 23:50.16–23:50.16 | accident | 60% |
| 23:51.56–23:52.26 | letter | 95% |
| 23:52.50–23:52.50 | play | 54% |
| 23:54.37–23:54.37 | accident | 63% |
| 23:56.00–23:56.23 | last | 81% |
| 23:57.64–23:57.64 | study | 57% |
| 24:00.67–24:00.91 | medicine | 76% |
| 24:02.78–24:03.01 | short | 85% |
| 24:04.64–24:04.88 | graduate | 72% |
| 24:06.51–24:06.51 | study | 63% |
| 24:08.38–24:08.38 | dark | 66% |
| 24:17.26–24:17.26 | cheat | 52% |
| 24:22.86–24:22.86 | basketball | 76% |
| 24:25.90–24:26.37 | play | 90% |
| 24:27.07–24:27.53 | basketball | 76% |
| 24:29.87–24:29.87 | study | 52% |
| 24:31.27–24:31.27 | play | 67% |
| 24:32.20–24:32.20 | change | 54% |
| 24:32.67–24:32.67 | jacket | 51% |
| 24:33.61–24:34.07 | accident | 91% |
| 24:35.71–24:35.71 | letter | 56% |
| 24:36.41–24:36.41 | letter | 54% |
| 24:36.88–24:37.11 | short | 82% |
| 24:40.61–24:41.31 | last | 90% |
| 24:41.55–24:41.55 | secretary | 67% |
| 24:41.78–24:42.25 | letter | 83% |
| 24:44.58–24:45.05 | play | 93% |
| 24:47.39–24:47.85 | graduate | 88% |
| 24:49.25–24:49.49 | how | 64% |
| 24:49.72–24:49.72 | cheat | 50% |
| 24:51.12–24:51.36 | right | 66% |
| 24:52.76–24:52.76 | language | 72% |
| 24:53.93–24:53.93 | short | 64% |
| 24:56.73–24:56.73 | later | 63% |
| 24:57.20–24:57.20 | go | 52% |
| 24:59.30–24:59.30 | go | 68% |
| 24:59.77–24:59.77 | jacket | 52% |
| 25:02.80–25:02.80 | black | 55% |
| 25:05.84–25:06.07 | fine | 72% |
| 25:09.34–25:09.34 | black | 80% |
| 25:09.58–25:10.04 | want | 70% |
| 25:11.68–25:11.68 | play | 62% |
| 25:11.91–25:11.91 | letter | 55% |
| 25:12.38–25:12.38 | go | 71% |
| 25:12.61–25:12.85 | language | 55% |
| 25:14.71–25:14.71 | forget | 63% |
| 25:15.18–25:15.65 | play | 79% |
| 25:17.98–25:18.22 | decide | 82% |
| 25:18.92–25:19.15 | language | 63% |
| 25:20.55–25:20.79 | study | 84% |
| 25:21.25–25:21.25 | school | 51% |
| 25:22.65–25:22.89 | letter | 67% |
| 25:23.12–25:23.59 | short | 80% |
| 25:25.69–25:25.69 | letter | 77% |
| 25:27.56–25:28.03 | all | 72% |
| 25:30.36–25:30.36 | shirt | 64% |
| 25:32.00–25:32.00 | accident | 80% |
| 25:35.97–25:36.90 | last | 86% |
| 25:37.14–25:37.14 | letter | 80% |
| 25:37.60–25:38.07 | accident | 66% |
| 25:39.24–25:39.24 | later | 51% |
| 25:39.47–25:39.47 | play | 69% |
| 25:39.70–25:39.70 | letter | 54% |
| 25:39.94–25:39.94 | jacket | 68% |
| 25:40.17–25:40.17 | letter | 92% |
| 25:43.67–25:44.38 | letter | 95% |
| 25:49.52–25:49.52 | letter | 62% |
| 25:50.68–25:50.68 | letter | 53% |
| 25:53.48–25:53.72 | meet | 91% |
| 25:56.52–25:56.52 | last | 53% |
| 25:58.16–25:58.16 | accident | 51% |
| 26:00.03–26:00.49 | year | 79% |
| 26:01.89–26:01.89 | black | 68% |
| 26:03.06–26:03.30 | decide | 87% |
| 26:09.13–26:09.13 | decide | 59% |
| 26:17.31–26:17.78 | letter | 60% |
| 26:19.64–26:19.64 | decide | 60% |
| 26:19.88–26:20.11 | black | 72% |
| 26:21.28–26:21.28 | dark | 71% |
| 26:29.45–26:29.45 | jacket | 80% |
| 26:32.02–26:32.49 | decide | 79% |
| 26:35.06–26:35.29 | family | 56% |
| 26:36.93–26:36.93 | decide | 57% |
| 26:39.96–26:39.96 | all | 53% |
| 26:40.20–26:40.43 | family | 88% |
| 26:40.67–26:40.67 | thanksgiving | 62% |
| 26:42.53–26:42.53 | decide | 85% |
| 26:44.87–26:44.87 | accident | 54% |
| 26:45.57–26:45.57 | help | 81% |
| 26:48.14–26:48.37 | before | 60% |
| 26:51.18–26:51.64 | last | 85% |
| 26:52.58–26:52.58 | doctor | 53% |
| 26:53.98–26:53.98 | black | 51% |
| 26:57.95–26:58.18 | basketball | 59% |
| 26:59.35–26:59.82 | basketball | 59% |
| 27:05.66–27:06.12 | all | 96% |
| 27:07.29–27:07.29 | short | 53% |
| 27:07.53–27:07.53 | secretary | 60% |
| 27:09.86–27:09.86 | no | 50% |
| 27:13.37–27:13.37 | dark | 58% |
| 27:17.80–27:17.80 | go | 68% |
| 27:18.27–27:18.50 | letter | 95% |
| 27:19.20–27:19.67 | play | 91% |
| 27:19.90–27:19.90 | accident | 66% |
| 27:24.58–27:24.58 | accident | 59% |
| 27:25.04–27:25.28 | jacket | 77% |
| 27:26.21–27:26.44 | letter | 71% |
| 27:28.08–27:28.08 | secretary | 54% |
| 27:29.25–27:29.25 | but | 56% |
| 27:32.75–27:33.22 | right | 78% |
| 27:38.36–27:38.82 | letter | 96% |
| 27:41.39–27:42.33 | letter | 90% |
| 27:42.79–27:43.03 | last | 78% |
| 27:43.26–27:43.26 | study | 61% |
| 27:44.90–27:44.90 | how | 65% |
| 27:50.27–27:50.50 | decide | 95% |
| 27:53.31–27:53.31 | want | 54% |
| 27:55.64–27:55.64 | shirt | 54% |
| 27:57.98–27:57.98 | before | 56% |
| 27:58.68–27:59.38 | later | 81% |
| 28:00.31–28:00.55 | go | 79% |
| 28:02.88–28:03.12 | later | 58% |
| 28:05.68–28:06.15 | decide | 78% |
| 28:09.65–28:09.65 | accident | 60% |
| 28:10.12–28:10.36 | year | 70% |
| 28:10.59–28:10.59 | black | 68% |
| 28:11.76–28:11.76 | what | 55% |
| 28:18.06–28:18.30 | medicine | 60% |
| 28:19.70–28:19.70 | city | 76% |
| 28:19.93–28:20.16 | woman | 72% |
| 28:21.10–28:21.10 | all | 63% |
| 28:21.57–28:21.57 | before | 55% |
| 28:26.24–28:26.24 | cook | 57% |
| 28:29.51–28:29.74 | last | 63% |
| 28:34.88–28:34.88 | letter | 54% |
| 28:35.35–28:35.35 | medicine | 59% |
| 28:40.02–28:40.02 | before | 53% |
| 28:43.29–28:43.52 | basketball | 72% |
| 28:43.76–28:43.76 | all | 55% |
| 28:46.09–28:46.33 | cook | 74% |
| 28:47.03–28:47.03 | want | 89% |
| 28:47.26–28:47.26 | many | 57% |
| 28:51.70–28:52.16 | now | 79% |
| 28:54.97–28:54.97 | clothes | 55% |
| 28:56.13–28:56.13 | play | 51% |
| 28:58.70–28:58.94 | change | 62% |
| 29:00.81–29:00.81 | letter | 60% |
| 29:03.61–29:03.61 | basketball | 53% |
| 29:07.81–29:09.45 | play | 92% |
| 29:11.32–29:11.32 | basketball | 80% |
| 29:12.95–29:12.95 | change | 67% |
| 29:19.02–29:19.26 | secretary | 57% |
| 29:19.49–29:19.72 | letter | 83% |
| 29:20.19–29:20.19 | study | 59% |
| 29:25.56–29:25.56 | last | 61% |
| 29:29.30–29:29.30 | cook | 89% |
| 29:30.23–29:30.47 | accident | 56% |
| 29:32.57–29:32.57 | thanksgiving | 53% |
| 29:33.04–29:33.04 | finish | 57% |
| 29:34.67–29:34.67 | dance | 52% |
| 29:36.54–29:36.54 | shirt | 54% |
| 29:39.81–29:40.05 | decide | 62% |
| 29:40.98–29:40.98 | all | 64% |
| 29:42.85–29:42.85 | thanksgiving | 78% |
| 29:45.65–29:45.65 | letter | 55% |
| 29:47.05–29:47.05 | what | 57% |
| 29:47.52–29:47.75 | letter | 90% |
| 29:48.69–29:49.15 | short | 71% |
| 29:50.32–29:50.32 | finish | 61% |
| 29:50.56–29:51.02 | decide | 70% |
| 29:53.36–29:54.06 | finish | 99% |
| 29:54.29–29:54.29 | dark | 66% |
| 29:55.93–29:56.39 | finish | 84% |
| 29:58.50–29:58.73 | thanksgiving | 80% |
| 29:58.96–29:58.96 | all | 54% |
| 29:59.20–29:59.20 | decide | 62% |
| 30:04.34–30:04.34 | medicine | 55% |
| 30:07.61–30:07.84 | later | 63% |
| 30:09.24–30:09.47 | thanksgiving | 81% |
| 30:11.11–30:11.11 | black | 60% |
| 30:12.51–30:12.98 | accident | 56% |
| 30:13.44–30:13.44 | graduate | 62% |
| 30:15.31–30:15.55 | what | 72% |
| 30:18.82–30:18.82 | change | 50% |
| 30:20.92–30:21.15 | want | 74% |
| 30:21.62–30:22.55 | play | 99% |
| 30:23.26–30:23.26 | thanksgiving | 54% |
| 30:25.12–30:25.12 | letter | 74% |
| 30:28.16–30:28.16 | study | 93% |
| 30:28.86–30:28.86 | black | 80% |
| 30:29.33–30:29.56 | right | 71% |
| 30:30.03–30:30.03 | last | 72% |
| 30:33.53–30:33.53 | who | 52% |
| 30:38.90–30:38.90 | last | 61% |
| 30:39.14–30:39.14 | black | 62% |
| 30:39.37–30:39.60 | dog | 68% |
| 30:40.31–30:40.77 | cool | 74% |
| 30:41.24–30:41.24 | decide | 62% |
| 30:42.64–30:42.64 | letter | 85% |
| 30:48.01–30:48.01 | what | 66% |
| 30:49.88–30:49.88 | secretary | 67% |
| 30:53.85–30:53.85 | decide | 51% |
| 30:54.09–30:54.09 | thanksgiving | 75% |
| 30:54.79–30:54.79 | basketball | 61% |
| 30:55.49–30:55.49 | accident | 92% |
| 30:57.36–30:57.59 | thanksgiving | 89% |
| 30:58.76–30:58.99 | pull | 97% |
| 31:02.26–31:02.26 | basketball | 74% |
| 31:02.73–31:03.19 | change | 85% |
| 31:04.13–31:04.13 | hot | 67% |
| 31:04.60–31:04.60 | accident | 52% |
| 31:05.06–31:05.06 | clothes | 82% |
| 31:06.23–31:06.23 | decide | 56% |
| 31:06.46–31:06.70 | play | 55% |
| 31:09.03–31:09.73 | thanksgiving | 94% |
| 31:10.43–31:11.14 | bowling | 93% |
| 31:13.70–31:13.70 | before | 65% |
| 31:16.27–31:16.74 | right | 85% |
| 31:17.21–31:17.44 | change | 60% |
| 31:24.22–31:24.22 | thanksgiving | 80% |
| 31:24.45–31:24.92 | dark | 96% |
| 31:26.08–31:26.08 | short | 54% |
| 31:27.02–31:27.02 | fish | 56% |
| 31:27.49–31:27.49 | black | 53% |
| 31:27.95–31:27.95 | last | 58% |
| 31:34.26–31:34.49 | meet | 86% |
| 31:40.10–31:40.57 | last | 91% |
| 31:41.03–31:41.03 | before | 56% |
| 31:41.50–31:41.50 | paint | 56% |
| 31:42.20–31:42.20 | what | 53% |
| 31:42.90–31:42.90 | change | 67% |
| 31:44.30–31:44.30 | accident | 67% |
| 31:44.54–31:44.54 | secretary | 59% |
| 31:45.24–31:45.24 | last | 50% |
| 31:45.47–31:45.70 | letter | 66% |
| 31:47.57–31:47.81 | paint | 85% |
| 31:48.51–31:48.97 | paint | 60% |
| 31:50.14–31:50.14 | decide | 62% |
| 31:52.71–31:53.88 | cheat | 80% |
| 31:54.81–31:54.81 | tall | 74% |
| 31:58.55–31:58.78 | decide | 57% |
| 32:00.18–32:00.18 | basketball | 52% |
| 32:01.35–32:01.35 | basketball | 52% |
| 32:02.29–32:04.16 | play | 95% |
| 32:05.79–32:05.79 | basketball | 90% |
| 32:08.13–32:08.13 | decide | 55% |
| 32:08.83–32:08.83 | change | 51% |
| 32:10.69–32:10.69 | accident | 58% |
| 32:14.90–32:14.90 | son | 80% |
| 32:17.47–32:17.47 | dark | 62% |
| 32:19.57–32:19.57 | basketball | 63% |
| 32:20.04–32:20.27 | decide | 82% |
| 32:24.01–32:24.01 | short | 56% |
| 32:25.18–32:25.18 | play | 73% |
| 32:29.15–32:29.61 | all | 61% |
| 32:34.05–32:34.05 | what | 83% |
| 32:36.15–32:36.15 | city | 68% |
| 32:37.79–32:37.79 | letter | 51% |
| 32:39.42–32:39.42 | accident | 53% |
| 32:39.89–32:39.89 | last | 56% |
| 32:41.53–32:42.23 | but | 99% |
| 32:43.63–32:43.86 | accident | 90% |
| 32:45.96–32:45.96 | now | 50% |
| 32:46.90–32:46.90 | before | 62% |
| 32:47.37–32:47.60 | want | 72% |
| 32:50.87–32:50.87 | city | 63% |
| 32:52.97–32:52.97 | many | 62% |
| 32:53.44–32:53.44 | accident | 53% |
| 32:55.54–32:55.77 | paint | 89% |
| 32:57.64–32:57.64 | letter | 51% |
| 32:59.51–33:00.21 | right | 95% |
| 33:03.71–33:03.71 | decide | 54% |
| 33:04.88–33:05.58 | play | 81% |
| 33:06.98–33:07.69 | letter | 89% |
| 33:09.09–33:09.09 | family | 52% |
| 33:10.49–33:10.49 | city | 52% |
| 33:11.66–33:11.66 | thanksgiving | 55% |
| 33:13.53–33:13.99 | thanksgiving | 92% |
| 33:15.16–33:15.39 | last | 81% |
| 33:15.63–33:15.86 | dance | 54% |
| 33:21.00–33:21.23 | right | 95% |
| 33:22.40–33:22.40 | decide | 69% |
| 33:22.63–33:22.87 | all | 85% |
| 33:24.27–33:24.27 | tell | 51% |
| 33:25.90–33:25.90 | thanksgiving | 57% |
| 33:27.07–33:27.07 | cook | 78% |
| 33:27.77–33:27.77 | accident | 50% |
| 33:29.41–33:29.41 | can | 78% |
| 33:30.58–33:30.58 | black | 57% |
| 33:31.51–33:31.51 | accident | 72% |
| 33:32.44–33:32.68 | help | 74% |
| 33:34.55–33:34.55 | play | 70% |
| 33:38.52–33:38.75 | accident | 75% |
| 33:38.98–33:38.98 | help | 54% |
| 33:41.55–33:41.55 | later | 56% |
| 33:43.42–33:43.89 | right | 100% |
| 33:44.82–33:45.06 | play | 96% |
| 33:47.39–33:47.63 | accident | 72% |
| 33:48.09–33:48.33 | help | 83% |
| 33:48.79–33:49.03 | accident | 74% |
| 33:49.26–33:49.26 | finish | 67% |
| 33:53.00–33:53.00 | thanksgiving | 62% |
| 33:53.70–33:53.70 | dark | 51% |
| 33:56.03–33:56.27 | now | 78% |
| 33:59.54–33:59.54 | play | 57% |
| 34:01.41–34:01.87 | decide | 93% |
| 34:03.04–34:03.04 | cow | 56% |
| 34:04.21–34:04.91 | decide | 87% |
| 34:05.38–34:05.61 | all | 81% |
| 34:06.31–34:06.54 | thanksgiving | 90% |
| 34:06.78–34:07.01 | decide | 77% |
| 34:07.24–34:07.71 | all | 77% |
| 34:09.11–34:09.35 | thanksgiving | 75% |
| 34:09.81–34:10.28 | basketball | 73% |
| 34:11.68–34:11.68 | kiss | 62% |
| 34:12.85–34:12.85 | many | 57% |
| 34:14.49–34:14.49 | basketball | 52% |
| 34:18.22–34:18.69 | decide | 92% |
| 34:19.16–34:19.16 | orange | 55% |
| 34:28.73–34:28.73 | play | 52% |
| 34:30.60–34:30.84 | medicine | 83% |
| 34:31.54–34:31.54 | before | 62% |
| 34:33.87–34:34.34 | all | 81% |
| 34:34.81–34:34.81 | decide | 66% |
| 34:39.24–34:39.71 | but | 96% |
| 34:40.18–34:40.18 | basketball | 62% |
| 34:41.11–34:41.58 | secretary | 83% |
| 34:46.95–34:46.95 | fish | 64% |
| 34:48.35–34:48.35 | thursday | 67% |
| 34:49.75–34:49.75 | basketball | 53% |
| 34:50.22–34:50.22 | play | 72% |
| 34:53.02–34:53.26 | letter | 65% |
| 34:55.36–34:55.36 | later | 52% |
| 34:55.83–34:55.83 | black | 56% |
| 34:58.63–34:58.63 | letter | 51% |
| 35:01.43–35:01.67 | school | 78% |
| 35:02.13–35:02.37 | all | 68% |
| 35:04.70–35:04.70 | right | 52% |
| 35:05.17–35:05.40 | black | 80% |
| 35:05.64–35:05.64 | decide | 54% |
| 35:08.44–35:08.44 | last | 86% |
| 35:11.71–35:11.71 | letter | 63% |
| 35:12.64–35:12.64 | tell | 71% |
| 35:12.88–35:13.11 | letter | 78% |
| 35:13.34–35:13.81 | change | 72% |
| 35:14.51–35:14.51 | accident | 65% |
| 35:15.21–35:15.45 | short | 57% |
| 35:16.38–35:16.38 | dog | 56% |
| 35:17.32–35:17.78 | play | 53% |
| 35:18.25–35:18.25 | basketball | 52% |
| 35:19.65–35:19.65 | accident | 55% |
| 35:19.88–35:20.59 | change | 82% |
| 35:22.69–35:22.69 | what | 52% |
| 35:26.89–35:27.59 | thanksgiving | 86% |
| 35:30.63–35:30.63 | but | 65% |
| 35:33.90–35:34.13 | decide | 55% |
| 35:37.40–35:37.87 | decide | 89% |
| 35:40.20–35:40.91 | decide | 92% |
| 35:41.14–35:41.37 | accident | 77% |
| 35:46.28–35:46.51 | last | 81% |
| 35:52.12–35:52.35 | letter | 93% |
| 35:55.39–35:55.85 | decide | 78% |
| 35:57.49–35:57.49 | play | 57% |
| 35:58.42–35:58.66 | decide | 96% |
| 35:58.89–35:59.12 | letter | 68% |
| 36:00.06–36:00.06 | help | 68% |
| 36:02.63–36:02.86 | medicine | 72% |
| 36:04.96–36:05.20 | secretary | 62% |
| 36:05.43–36:05.43 | letter | 53% |
| 36:08.00–36:08.93 | work | 90% |
| 36:10.80–36:11.27 | but | 98% |
| 36:19.21–36:20.14 | last | 64% |
| 36:21.08–36:22.25 | letter | 85% |
| 36:23.65–36:23.88 | decide | 75% |
| 36:24.35–36:25.52 | walk | 98% |
| 36:28.09–36:28.09 | black | 59% |
| 36:29.72–36:29.72 | city | 63% |
| 36:31.12–36:31.36 | thanksgiving | 73% |
| 36:31.82–36:31.82 | many | 51% |
| 36:36.03–36:36.26 | black | 84% |
| 36:36.73–36:36.73 | decide | 71% |
| 36:36.96–36:36.96 | play | 67% |
| 36:38.36–36:38.60 | before | 52% |
| 36:41.63–36:41.87 | decide | 60% |
| 36:42.10–36:42.33 | short | 56% |
| 36:43.27–36:43.27 | study | 66% |
| 36:45.37–36:45.37 | dog | 52% |
| 36:46.54–36:46.54 | change | 87% |
| 36:47.01–36:47.01 | black | 66% |
| 36:47.24–36:47.24 | thanksgiving | 77% |
| 36:48.17–36:48.17 | can | 57% |
| 36:54.01–36:54.01 | letter | 54% |
| 36:57.98–36:58.45 | tell | 77% |
| 36:59.15–36:59.15 | hot | 55% |
| 37:03.35–37:03.35 | cheat | 62% |
| 37:03.82–37:03.82 | all | 70% |
| 37:04.05–37:04.05 | cook | 75% |
| 37:07.09–37:07.79 | right | 96% |
| 37:08.03–37:08.03 | year | 65% |
| 37:08.96–37:08.96 | before | 69% |
| 37:12.46–37:12.70 | change | 69% |
| 37:13.40–37:14.57 | change | 91% |
| 37:19.94–37:19.94 | accident | 66% |
| 37:23.68–37:23.68 | deaf | 53% |
| 37:25.31–37:25.31 | decide | 53% |
| 37:25.78–37:25.78 | finish | 59% |
| 37:26.24–37:26.24 | basketball | 50% |
| 37:27.18–37:27.41 | short | 54% |
| 37:28.11–37:28.35 | but | 98% |
| 37:28.81–37:28.81 | basketball | 72% |
| 37:30.45–37:30.45 | all | 52% |
| 37:31.15–37:31.15 | letter | 62% |
| 37:34.42–37:34.65 | want | 80% |
| 37:35.82–37:36.05 | accident | 66% |
| 37:36.99–37:36.99 | graduate | 58% |
| 37:37.69–37:37.69 | tell | 57% |
| 37:39.32–37:39.32 | clothes | 64% |
| 37:40.02–37:40.26 | chair | 86% |
| 37:46.56–37:46.56 | now | 65% |
| 37:47.50–37:48.43 | now | 76% |
| 37:49.60–37:50.07 | cook | 92% |
| 37:53.10–37:53.57 | accident | 82% |
| 37:53.80–37:54.51 | short | 91% |
| 37:55.21–37:55.67 | short | 60% |
| 37:56.84–37:56.84 | short | 69% |
| 37:57.54–37:57.78 | short | 69% |
| 37:58.01–37:58.01 | basketball | 58% |
| 37:58.24–37:58.48 | decide | 84% |
| 38:01.75–38:01.98 | accident | 74% |
| 38:07.12–38:07.35 | play | 68% |
| 38:09.45–38:09.45 | letter | 57% |
| 38:11.32–38:11.32 | can | 58% |
| 38:11.56–38:11.79 | jacket | 67% |
| 38:13.19–38:13.66 | go | 74% |
| 38:14.12–38:15.53 | short | 91% |
| 38:17.39–38:17.39 | short | 55% |
| 38:19.73–38:19.73 | basketball | 60% |
| 38:21.83–38:22.30 | decide | 82% |
| 38:22.53–38:23.00 | study | 69% |
| 38:24.64–38:24.64 | go | 73% |
| 38:26.50–38:26.50 | fish | 79% |
| 38:28.14–38:28.37 | dark | 69% |
| 38:28.84–38:28.84 | secretary | 74% |
| 38:31.88–38:32.34 | last | 80% |
| 38:38.65–38:38.65 | decide | 58% |
| 38:40.99–38:40.99 | cheat | 66% |
