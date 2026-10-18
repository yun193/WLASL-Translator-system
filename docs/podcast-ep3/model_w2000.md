# 模型輸出：w2000（20261018-w2000n-2000，2000 詞）

- 流程和後端影片檔模式相同：原生 fps 逐幀關鍵點 → 切詞器（手放下 0.5 秒切詞、單詞上限 4 秒）→ 分類
- 影片 71138 幀（29.97 fps、39:33.64），有手的幀 97%
- 切出 574 個詞；長度中位 4.00 秒，碰到 4 秒上限的 100%
- 信心 ≥ 0.5 的 8 個；低於門檻顯示成 ?(前 3 名)

## 切詞器輸出（和網頁上看到的一樣）

| 開始 | 結束 | 長度 | 輸出 | 信心 | 前 3 名 |
| --- | --- | --- | --- | --- | --- |
| 00:05.61 | 00:09.61 | 4.0s | ? | 44% | exaggerate 44% / slip 2% / cancel 2% |
| 00:09.64 | 00:13.65 | 4.0s | ? | 8% | sign language 8% / when 7% / intersection 7% |
| 00:13.68 | 00:17.68 | 4.0s | ? | 29% | black 29% / ill 4% / judge 2% |
| 00:17.72 | 00:21.72 | 4.0s | ? | 49% | accident 49% / thousand 8% / approve 7% |
| 00:21.75 | 00:25.76 | 4.0s | ? | 7% | bless 7% / article 3% / river 2% |
| 00:25.79 | 00:29.80 | 4.0s | ? | 5% | rise 5% / last 4% / join 4% |
| 00:29.83 | 00:33.83 | 4.0s | ? | 6% | curriculum 6% / than 4% / hope 4% |
| 00:33.87 | 00:37.87 | 4.0s | ? | 10% | sting 10% / carnival 4% / champion 3% |
| 00:37.91 | 00:41.91 | 4.0s | ? | 10% | blood 10% / melt 9% / wet 5% |
| 00:41.94 | 00:45.95 | 4.0s | ? | 8% | thousand 8% / last 5% / impossible 4% |
| 00:45.98 | 00:49.98 | 4.0s | ? | 8% | build 8% / sting 7% / viewpoint 6% |
| 00:50.02 | 00:54.02 | 4.0s | ? | 16% | gymnastics 16% / monthly 7% / bully 4% |
| 00:54.05 | 00:58.06 | 4.0s | ? | 20% | quit 20% / above 8% / join 6% |
| 00:58.09 | 01:02.09 | 4.0s | ? | 10% | tale 10% / schedule 8% / secretary 7% |
| 01:02.13 | 01:06.13 | 4.0s | ? | 16% | thousand 16% / graduate 8% / cancel 6% |
| 01:06.17 | 01:10.17 | 4.0s | ? | 7% | sign 7% / exaggerate 7% / final 4% |
| 01:10.20 | 01:14.21 | 4.0s | ? | 9% | shine 9% / above 6% / balloon 4% |
| 01:14.24 | 01:18.25 | 4.0s | ? | 10% | example 10% / email 7% / braid 4% |
| 01:18.28 | 01:22.28 | 4.0s | ? | 27% | weekend 27% / build 12% / contribute 4% |
| 01:22.32 | 01:26.32 | 4.0s | ? | 13% | compromise 13% / agreement 10% / judge 4% |
| 01:26.35 | 01:30.36 | 4.0s | ? | 7% | cancel 7% / problem 4% / laundry 4% |
| 01:30.39 | 01:34.39 | 4.0s | ? | 8% | sign 8% / anatomy 4% / care 4% |
| 01:34.43 | 01:38.43 | 4.0s | ? | 6% | join 6% / special 4% / tale 4% |
| 01:38.47 | 01:42.47 | 4.0s | ? | 7% | decide 7% / disagree 6% / thin 6% |
| 01:42.50 | 01:46.51 | 4.0s | ? | 8% | last 8% / aim 4% / check 3% |
| 01:46.54 | 01:50.54 | 4.0s | ? | 9% | quit 9% / tissue 9% / when 6% |
| 01:50.58 | 01:54.58 | 4.0s | ? | 14% | deduct 14% / subtract 7% / what 7% |
| 01:54.61 | 01:58.62 | 4.0s | ? | 19% | classroom 19% / group 6% / rob 5% |
| 01:58.65 | 02:02.66 | 4.0s | ? | 10% | before 10% / category 5% / group 3% |
| 02:02.69 | 02:06.69 | 4.0s | ? | 24% | deduct 24% / mean 12% / subtract 11% |
| 02:06.73 | 02:10.73 | 4.0s | ? | 5% | accident 5% / win 5% / secretary 5% |
| 02:10.76 | 02:14.77 | 4.0s | ? | 8% | agreement 8% / hit 7% / intersection 6% |
| 02:14.80 | 02:18.81 | 4.0s | ? | 9% | quit 9% / when 5% / champion 3% |
| 02:18.84 | 02:22.84 | 4.0s | ? | 12% | change 12% / confused 6% / tale 5% |
| 02:22.88 | 02:26.88 | 4.0s | ? | 8% | when 8% / jacket 7% / robber 5% |
| 02:26.91 | 02:30.92 | 4.0s | ? | 3% | negative 3% / all 3% / popular 2% |
| 02:30.95 | 02:34.96 | 4.0s | ? | 10% | spanish 10% / sting 5% / rise 5% |
| 02:34.99 | 02:38.99 | 4.0s | ? | 5% | scientist 5% / finally 3% / illegal 3% |
| 02:39.03 | 02:43.03 | 4.0s | ? | 42% | compromise 42% / accident 4% / agreement 3% |
| 02:43.06 | 02:47.07 | 4.0s | ? | 7% | towel 7% / audience 3% / impossible 2% |
| 02:47.10 | 02:51.10 | 4.0s | ? | 25% | phrase 25% / awful 17% / message 7% |
| 02:51.14 | 02:55.14 | 4.0s | ? | 24% | last 24% / final 8% / seldom 5% |
| 02:55.18 | 02:59.18 | 4.0s | ? | 32% | identify 32% / confused 6% / pilot 5% |
| 02:59.21 | 03:03.22 | 4.0s | ? | 4% | diarrhea 4% / remove 3% / silent 3% |
| 03:03.25 | 03:07.25 | 4.0s | ? | 29% | example 29% / catch 3% / change 3% |
| 03:07.29 | 03:11.29 | 4.0s | ? | 22% | disturb 22% / schedule 3% / expect 3% |
| 03:11.32 | 03:15.33 | 4.0s | ? | 3% | finish 3% / divide 3% / wind 2% |
| 03:15.36 | 03:19.37 | 4.0s | ? | 8% | spanish 8% / window 5% / south america 3% |
| 03:19.40 | 03:23.40 | 4.0s | ? | 9% | student 9% / gymnastics 5% / resign 4% |
| 03:23.44 | 03:27.44 | 4.0s | ? | 5% | recover 5% / all 3% / judge 2% |
| 03:27.47 | 03:31.48 | 4.0s | ? | 10% | none 10% / nothing 8% / bar 7% |
| 03:31.51 | 03:35.51 | 4.0s | ? | 12% | tournament 12% / ticket 6% / shock 5% |
| 03:35.55 | 03:39.55 | 4.0s | ? | 11% | disconnect 11% / quit 11% / tale 5% |
| 03:39.59 | 03:43.59 | 4.0s | ? | 20% | shock 20% / argue 6% / test 5% |
| 03:43.62 | 03:47.63 | 4.0s | ? | 26% | accident 26% / dolphin 9% / jail 3% |
| 03:47.66 | 03:51.66 | 4.0s | ? | 3% | tale 3% / appointment 3% / forgive 3% |
| 03:51.70 | 03:55.70 | 4.0s | ? | 7% | correct 7% / from now on 4% / blend 4% |
| 03:55.74 | 03:59.74 | 4.0s | ? | 41% | vacant 41% / archery 6% / appointment 4% |
| 03:59.77 | 04:03.78 | 4.0s | ? | 9% | accident 9% / convince 4% / secretary 3% |
| 04:03.81 | 04:07.81 | 4.0s | ? | 16% | check 16% / schedule 11% / seldom 6% |
| 04:07.85 | 04:11.85 | 4.0s | ? | 13% | peel 13% / intersection 7% / upset 6% |
| 04:11.88 | 04:15.89 | 4.0s | ? | 4% | repeat 4% / tonight 4% / contract 3% |
| 04:15.92 | 04:19.93 | 4.0s | ? | 20% | resign 20% / gymnastics 12% / sting 5% |
| 04:19.96 | 04:23.96 | 4.0s | ? | 14% | sting 14% / pack 7% / agree 4% |
| 04:24.00 | 04:28.00 | 4.0s | ? | 7% | crash 7% / notice 6% / cheat 6% |
| 04:28.03 | 04:32.04 | 4.0s | ? | 5% | somewhere 5% / there 5% / sunrise 4% |
| 04:32.07 | 04:36.08 | 4.0s | ? | 15% | umbrella 15% / correct 12% / right 7% |
| 04:36.11 | 04:40.11 | 4.0s | ? | 38% | cancel 38% / last 5% / stretch 3% |
| 04:40.15 | 04:44.15 | 4.0s | ? | 7% | from 7% / reveal 6% / ruin 4% |
| 04:44.18 | 04:48.19 | 4.0s | ? | 7% | different 7% / shine 5% / quit 3% |
| 04:48.22 | 04:52.23 | 4.0s | ? | 6% | engagement 6% / confused 5% / rude 4% |
| 04:52.26 | 04:56.26 | 4.0s | ? | 29% | all 29% / confused 4% / cook 4% |
| 04:56.30 | 05:00.30 | 4.0s | ? | 19% | bookstore 19% / accident 8% / above 5% |
| 05:00.33 | 05:04.34 | 4.0s | ? | 6% | sign language 6% / student 4% / seldom 4% |
| 05:04.37 | 05:08.38 | 4.0s | ? | 13% | approve 13% / ticket 8% / accident 7% |
| 05:08.41 | 05:12.41 | 4.0s | ? | 13% | difficult 13% / trust 11% / discuss 6% |
| 05:12.44 | 05:16.45 | 4.0s | ? | 8% | sign 8% / people 7% / hit 7% |
| 05:16.48 | 05:20.49 | 4.0s | ? | 11% | change 11% / geometry 4% / hit 4% |
| 05:20.52 | 05:24.52 | 4.0s | ? | 6% | closet 6% / contribute 5% / last 5% |
| 05:24.56 | 05:28.56 | 4.0s | ? | 13% | guitar 13% / ill 5% / emotion 4% |
| 05:28.60 | 05:32.60 | 4.0s | ? | 9% | catch 9% / confused 6% / husband 4% |
| 05:32.63 | 05:36.64 | 4.0s | ? | 50% | flatter 50% / inspect 4% / check 4% |
| 05:36.67 | 05:40.67 | 4.0s | when | 63% | when 63% / different 3% / check 2% |
| 05:40.71 | 05:44.71 | 4.0s | ? | 7% | when 7% / remove 6% / pneumonia 4% |
| 05:44.74 | 05:48.75 | 4.0s | ? | 7% | rob 7% / classroom 6% / workshop 6% |
| 05:48.78 | 05:52.79 | 4.0s | ? | 7% | out 7% / accident 6% / swimming 5% |
| 05:52.82 | 05:56.82 | 4.0s | ? | 17% | accident 17% / repeat 6% / blend 5% |
| 05:56.86 | 06:00.86 | 4.0s | ? | 4% | confront 4% / birthday 2% / quit 2% |
| 06:00.89 | 06:04.90 | 4.0s | ? | 5% | above 5% / impossible 5% / remove 3% |
| 06:04.93 | 06:08.94 | 4.0s | ? | 41% | tale 41% / all 5% / story 4% |
| 06:08.97 | 06:12.97 | 4.0s | ? | 14% | accident 14% / seldom 5% / bookstore 3% |
| 06:13.01 | 06:17.01 | 4.0s | ? | 9% | correct 9% / easter 4% / hit 4% |
| 06:17.04 | 06:21.05 | 4.0s | ? | 9% | detach 9% / example 4% / hope 3% |
| 06:21.08 | 06:25.08 | 4.0s | ? | 37% | hope 37% / loud 8% / judge 8% |
| 06:25.12 | 06:29.12 | 4.0s | ? | 16% | agreement 16% / agree 7% / compromise 7% |
| 06:29.15 | 06:33.16 | 4.0s | ? | 7% | structure 7% / tournament 6% / swim 4% |
| 06:33.19 | 06:37.20 | 4.0s | ? | 7% | scientist 7% / judge 6% / introduce 5% |
| 06:37.23 | 06:41.23 | 4.0s | ? | 34% | secretary 34% / accident 16% / disagree 3% |
| 06:41.27 | 06:45.27 | 4.0s | ? | 6% | sign language 6% / disturb 4% / cancel 4% |
| 06:45.31 | 06:49.31 | 4.0s | ? | 9% | slip 9% / cancel 8% / support 6% |
| 06:49.34 | 06:53.35 | 4.0s | ? | 9% | counselor 9% / canoe 3% / lawyer 3% |
| 06:53.38 | 06:57.38 | 4.0s | ? | 40% | intersection 40% / conflict 6% / first 6% |
| 06:57.42 | 07:01.42 | 4.0s | ? | 36% | joke 36% / tease 23% / short 2% |
| 07:01.45 | 07:05.46 | 4.0s | ? | 36% | joke 36% / tease 24% / vote 3% |
| 07:05.49 | 07:09.50 | 4.0s | ? | 14% | above 14% / quit 12% / clock 6% |
| 07:09.53 | 07:13.53 | 4.0s | ? | 8% | cancel 8% / triangle 5% / shock 5% |
| 07:13.57 | 07:17.57 | 4.0s | ? | 19% | gymnastics 19% / sign 8% / quit 3% |
| 07:17.60 | 07:21.61 | 4.0s | ? | 18% | sign 18% / intersection 11% / when 4% |
| 07:21.64 | 07:25.64 | 4.0s | ? | 10% | resign 10% / article 8% / secretary 5% |
| 07:25.68 | 07:29.68 | 4.0s | ? | 5% | toilet paper 5% / when 5% / graduate 4% |
| 07:29.72 | 07:33.72 | 4.0s | ? | 15% | rich 15% / window 12% / above 5% |
| 07:33.75 | 07:37.76 | 4.0s | ? | 15% | town 15% / annoy 11% / lose 4% |
| 07:37.79 | 07:41.80 | 4.0s | ? | 7% | college 7% / ghost 4% / maximum 3% |
| 07:41.83 | 07:45.83 | 4.0s | ? | 38% | umbrella 38% / truck 5% / ireland 2% |
| 07:45.87 | 07:49.87 | 4.0s | ? | 13% | seldom 13% / spin 11% / double 3% |
| 07:49.90 | 07:53.91 | 4.0s | ? | 8% | bookshelf 8% / bookstore 3% / toilet paper 2% |
| 07:53.94 | 07:57.94 | 4.0s | ? | 5% | canoe 5% / beginning 3% / wrench 2% |
| 07:57.98 | 08:01.98 | 4.0s | ? | 4% | what 4% / sketch 4% / sixteen 3% |
| 08:02.01 | 08:06.02 | 4.0s | ? | 18% | cancel 18% / slip 8% / deduct 5% |
| 08:06.05 | 08:10.06 | 4.0s | ? | 25% | resign 25% / sting 14% / quit 4% |
| 08:10.09 | 08:14.09 | 4.0s | quit | 64% | quit 64% / straw 2% / correct 2% |
| 08:14.13 | 08:18.13 | 4.0s | ? | 16% | when 16% / hit 10% / sign language 5% |
| 08:18.16 | 08:22.17 | 4.0s | ? | 14% | people 14% / double 8% / sign 4% |
| 08:22.20 | 08:26.21 | 4.0s | ? | 14% | seldom 14% / next 6% / numerous 5% |
| 08:26.24 | 08:30.24 | 4.0s | ? | 7% | last 7% / argue 3% / difficult 3% |
| 08:30.28 | 08:34.28 | 4.0s | ? | 20% | deduct 20% / subtract 7% / disturb 5% |
| 08:34.31 | 08:38.32 | 4.0s | ? | 12% | confused 12% / secretary 12% / week 10% |
| 08:38.35 | 08:42.36 | 4.0s | ? | 5% | catch 5% / complex 4% / accident 3% |
| 08:42.39 | 08:46.39 | 4.0s | ? | 11% | court 11% / argue 10% / judge 7% |
| 08:46.43 | 08:50.43 | 4.0s | ? | 11% | scientist 11% / hit 4% / group 3% |
| 08:50.46 | 08:54.47 | 4.0s | ? | 6% | cancel 6% / australia 6% / envelope 5% |
| 08:54.50 | 08:58.50 | 4.0s | ? | 16% | square 16% / different 8% / when 7% |
| 08:58.54 | 09:02.54 | 4.0s | ? | 10% | engagement 10% / change 8% / accident 5% |
| 09:02.58 | 09:06.58 | 4.0s | ? | 12% | hit 12% / balloon 9% / different 7% |
| 09:06.61 | 09:10.62 | 4.0s | ? | 24% | construct 24% / gymnastics 5% / sign 3% |
| 09:10.65 | 09:14.65 | 4.0s | ? | 14% | flatter 14% / when 10% / attorney 5% |
| 09:14.69 | 09:18.69 | 4.0s | ? | 8% | recognize 8% / notice 5% / cancel 5% |
| 09:18.73 | 09:22.73 | 4.0s | ? | 24% | office 24% / cook 11% / buy 4% |
| 09:22.76 | 09:26.77 | 4.0s | ? | 7% | third 7% / librarian 5% / group 3% |
| 09:26.80 | 09:30.80 | 4.0s | ? | 10% | decrease 10% / later 4% / cancel 3% |
| 09:30.84 | 09:34.84 | 4.0s | ? | 10% | dolphin 10% / student 8% / robber 5% |
| 09:34.87 | 09:38.88 | 4.0s | ? | 6% | accident 6% / assistant 4% / sign language 4% |
| 09:38.91 | 09:42.92 | 4.0s | ? | 10% | sign 10% / army 9% / blend 7% |
| 09:42.95 | 09:46.95 | 4.0s | ? | 9% | when 9% / flatter 7% / present 4% |
| 09:46.99 | 09:50.99 | 4.0s | ? | 7% | temple 7% / librarian 4% / accident 3% |
| 09:51.02 | 09:55.03 | 4.0s | ? | 10% | tower 10% / anatomy 5% / individual 5% |
| 09:55.06 | 09:59.07 | 4.0s | ? | 13% | mainstream 13% / braid 13% / anatomy 3% |
| 09:59.10 | 10:03.10 | 4.0s | ? | 14% | bottle 14% / spoon 6% / all 5% |
| 10:03.14 | 10:07.14 | 4.0s | ? | 6% | any 6% / guitar 6% / lord 5% |
| 10:07.17 | 10:11.18 | 4.0s | ? | 6% | tournament 6% / scientist 4% / shine 4% |
| 10:11.21 | 10:15.22 | 4.0s | ? | 31% | river 31% / resign 5% / later 2% |
| 10:15.25 | 10:19.25 | 4.0s | ? | 8% | star 8% / moon 6% / year 4% |
| 10:19.28 | 10:23.29 | 4.0s | ? | 13% | friend 13% / gymnastics 13% / tie 6% |
| 10:23.32 | 10:27.33 | 4.0s | ? | 7% | individual 7% / agreement 6% / accident 4% |
| 10:27.36 | 10:31.36 | 4.0s | ? | 19% | accident 19% / court 3% / agreement 3% |
| 10:31.40 | 10:35.40 | 4.0s | ? | 5% | quit 5% / cancel 5% / join 3% |
| 10:35.43 | 10:39.44 | 4.0s | ? | 6% | quit 6% / bright 5% / clear 4% |
| 10:39.47 | 10:43.48 | 4.0s | ? | 8% | double 8% / accident 7% / tournament 4% |
| 10:43.51 | 10:47.51 | 4.0s | ? | 16% | gymnastics 16% / perspective 5% / until 3% |
| 10:47.55 | 10:51.55 | 4.0s | ? | 9% | double 9% / guitar 4% / librarian 4% |
| 10:51.58 | 10:55.59 | 4.0s | ? | 19% | contribute 19% / closet 4% / viewpoint 2% |
| 10:55.62 | 10:59.63 | 4.0s | ? | 7% | recognize 7% / approve 6% / accident 4% |
| 10:59.66 | 11:03.66 | 4.0s | ? | 11% | different 11% / hit 6% / resign 6% |
| 11:03.70 | 11:07.70 | 4.0s | ? | 12% | deduct 12% / cancel 4% / last 4% |
| 11:07.73 | 11:11.74 | 4.0s | ? | 6% | fall in love 6% / hit 5% / recognize 4% |
| 11:11.77 | 11:15.77 | 4.0s | ? | 9% | shine 9% / above 5% / shock 3% |
| 11:15.81 | 11:19.81 | 4.0s | ? | 13% | spanish 13% / when 4% / champion 4% |
| 11:19.85 | 11:23.85 | 4.0s | ? | 7% | above 7% / confused 4% / choir 3% |
| 11:23.88 | 11:27.89 | 4.0s | ? | 8% | clothes 8% / divide 8% / anatomy 5% |
| 11:27.92 | 11:31.92 | 4.0s | ? | 6% | toast 6% / else 2% / approach 2% |
| 11:31.96 | 11:35.96 | 4.0s | ? | 10% | decide 10% / classroom 6% / snow 4% |
| 11:36.00 | 11:40.00 | 4.0s | ? | 8% | agreement 8% / principal 5% / agree 3% |
| 11:40.03 | 11:44.04 | 4.0s | ? | 8% | seldom 8% / double 7% / once 6% |
| 11:44.07 | 11:48.07 | 4.0s | ? | 8% | check 8% / librarian 5% / sign language 3% |
| 11:48.11 | 11:52.11 | 4.0s | ? | 7% | slip 7% / hit 3% / plenty 3% |
| 11:52.14 | 11:56.15 | 4.0s | ? | 7% | gymnastics 7% / reply 3% / scientist 2% |
| 11:56.18 | 12:00.19 | 4.0s | ? | 32% | clock 32% / rain 5% / dive 5% |
| 12:00.22 | 12:04.22 | 4.0s | ? | 8% | robber 8% / river 6% / shock 5% |
| 12:04.26 | 12:08.26 | 4.0s | ? | 4% | resign 4% / spin 4% / seldom 3% |
| 12:08.29 | 12:12.30 | 4.0s | ? | 11% | tournament 11% / sting 8% / quit 7% |
| 12:12.33 | 12:16.34 | 4.0s | ? | 8% | sting 8% / vampire 4% / duty 3% |
| 12:16.37 | 12:20.37 | 4.0s | ? | 5% | disturb 5% / decide 5% / mean 3% |
| 12:20.41 | 12:24.41 | 4.0s | ? | 6% | what 6% / reveal 3% / approve 2% |
| 12:24.44 | 12:28.45 | 4.0s | ? | 10% | student 10% / don't want 4% / quarrel 3% |
| 12:28.48 | 12:32.49 | 4.0s | ? | 11% | divide 11% / tale 4% / lose 4% |
| 12:32.52 | 12:36.52 | 4.0s | ? | 10% | tonight 10% / blend 6% / degree 3% |
| 12:36.56 | 12:40.56 | 4.0s | ? | 25% | remove 25% / all 8% / college 5% |
| 12:40.59 | 12:44.60 | 4.0s | ? | 11% | hit 11% / flatter 9% / week 8% |
| 12:44.63 | 12:48.63 | 4.0s | ? | 8% | thin 8% / mean 4% / check 3% |
| 12:48.67 | 12:52.67 | 4.0s | ? | 7% | hippopotamus 7% / problem 3% / secretary 3% |
| 12:52.71 | 12:56.71 | 4.0s | ? | 7% | secretary 7% / window 6% / hippopotamus 5% |
| 12:56.74 | 13:00.75 | 4.0s | ? | 20% | double 20% / less 14% / jump 7% |
| 13:00.78 | 13:04.78 | 4.0s | ? | 23% | judge 23% / jump 6% / less 4% |
| 13:04.82 | 13:08.82 | 4.0s | ? | 13% | emotion 13% / allergy 10% / check 9% |
| 13:08.99 | 13:12.99 | 4.0s | ? | 7% | different 7% / recent 4% / office 3% |
| 13:13.03 | 13:17.03 | 4.0s | ? | 7% | soul 7% / spirit 6% / compare 6% |
| 13:17.06 | 13:21.07 | 4.0s | ? | 11% | jump 11% / learn 10% / witness 3% |
| 13:21.10 | 13:25.10 | 4.0s | ? | 8% | disturb 8% / interrupt 5% / bedroom 4% |
| 13:25.14 | 13:29.14 | 4.0s | ? | 26% | cancel 26% / recognize 9% / notice 5% |
| 13:29.17 | 13:33.18 | 4.0s | ? | 9% | spill 9% / bless 6% / different 5% |
| 13:33.21 | 13:37.22 | 4.0s | ? | 17% | exaggerate 17% / graduate 7% / international 6% |
| 13:37.25 | 13:41.25 | 4.0s | ? | 13% | convince 13% / cancel 4% / balloon 4% |
| 13:41.29 | 13:45.29 | 4.0s | ? | 8% | double 8% / soup 3% / jump 2% |
| 13:45.33 | 13:49.33 | 4.0s | ? | 5% | graduate 5% / final 4% / bottle 4% |
| 13:49.36 | 13:53.37 | 4.0s | ? | 17% | singer 17% / large 14% / assistant 4% |
| 13:53.40 | 13:57.40 | 4.0s | ? | 15% | tonight 15% / cook 13% / accident 10% |
| 13:57.44 | 14:01.44 | 4.0s | ? | 4% | transfer 4% / curtain 3% / destroy 3% |
| 14:01.47 | 14:05.48 | 4.0s | ? | 5% | torture 5% / physician 3% / deduct 3% |
| 14:05.51 | 14:09.51 | 4.0s | ? | 5% | librarian 5% / many 4% / pilot 3% |
| 14:09.55 | 14:13.55 | 4.0s | ? | 16% | all 16% / dark 9% / confused 6% |
| 14:13.59 | 14:17.59 | 4.0s | ? | 28% | secretary 28% / schedule 5% / accident 4% |
| 14:17.62 | 14:21.63 | 4.0s | ? | 20% | check 20% / robber 7% / allergy 4% |
| 14:21.66 | 14:25.66 | 4.0s | ? | 4% | canoe 4% / busy 3% / change 3% |
| 14:25.70 | 14:29.70 | 4.0s | ? | 4% | grapes 4% / interpreter 3% / quit 2% |
| 14:29.74 | 14:33.74 | 4.0s | ? | 6% | remove 6% / laundry 5% / swimsuit 4% |
| 14:33.77 | 14:37.78 | 4.0s | ? | 13% | sting 13% / quit 8% / people 2% |
| 14:37.81 | 14:41.81 | 4.0s | ? | 6% | disturb 6% / accident 5% / schedule 3% |
| 14:41.85 | 14:45.85 | 4.0s | ? | 5% | laundry 5% / play 3% / all 3% |
| 14:45.88 | 14:49.89 | 4.0s | ? | 14% | tonight 14% / accident 6% / cook 5% |
| 14:49.92 | 14:53.93 | 4.0s | ? | 12% | mainstream 12% / accident 11% / close 8% |
| 14:53.96 | 14:57.96 | 4.0s | ? | 12% | exaggerate 12% / awkward 3% / star 2% |
| 14:58.00 | 15:02.00 | 4.0s | ? | 7% | cancel 7% / different 4% / rude 4% |
| 15:02.03 | 15:06.04 | 4.0s | ? | 10% | student 10% / secretary 9% / expensive 8% |
| 15:06.07 | 15:10.08 | 4.0s | ? | 15% | jump 15% / student 6% / above 6% |
| 15:10.11 | 15:14.11 | 4.0s | ? | 3% | choir 3% / tale 2% / illegal 2% |
| 15:14.15 | 15:18.15 | 4.0s | ? | 9% | divide 9% / division 6% / dolphin 3% |
| 15:18.18 | 15:22.19 | 4.0s | ? | 11% | argue 11% / quarrel 8% / guitar 5% |
| 15:22.22 | 15:26.23 | 4.0s | ? | 7% | stitch 7% / middle 7% / slip 5% |
| 15:26.26 | 15:30.26 | 4.0s | ? | 6% | independent 6% / tale 4% / all 4% |
| 15:30.30 | 15:34.30 | 4.0s | ? | 25% | above 25% / quit 8% / exaggerate 3% |
| 15:34.33 | 15:38.34 | 4.0s | ? | 12% | tale 12% / center 5% / bedroom 4% |
| 15:38.37 | 15:42.38 | 4.0s | ? | 5% | accident 5% / swimsuit 5% / audience 5% |
| 15:42.41 | 15:46.41 | 4.0s | ? | 19% | gymnastics 19% / vacant 4% / sign 4% |
| 15:46.45 | 15:50.45 | 4.0s | ? | 4% | want 4% / shirt 4% / monkey 3% |
| 15:50.48 | 15:54.49 | 4.0s | ? | 28% | emotion 28% / double 20% / popcorn 2% |
| 15:54.52 | 15:58.52 | 4.0s | ? | 8% | assist 8% / sign language 8% / assistant 3% |
| 15:58.56 | 16:02.56 | 4.0s | ? | 11% | fight 11% / agreement 3% / rise 3% |
| 16:02.60 | 16:06.60 | 4.0s | ? | 8% | cancel 8% / difficult 6% / student 6% |
| 16:06.63 | 16:10.64 | 4.0s | ? | 29% | accident 29% / blend 10% / tonight 6% |
| 16:10.67 | 16:14.67 | 4.0s | ? | 17% | laundry 17% / swimsuit 6% / tale 3% |
| 16:14.71 | 16:18.71 | 4.0s | ? | 19% | sculpture 19% / scientist 6% / can 6% |
| 16:18.74 | 16:22.75 | 4.0s | ? | 9% | choir 9% / quit 7% / sting 7% |
| 16:22.78 | 16:26.79 | 4.0s | ? | 11% | librarian 11% / attorney 4% / bush 4% |
| 16:26.82 | 16:30.82 | 4.0s | ? | 10% | tournament 10% / accident 9% / pack 4% |
| 16:30.86 | 16:34.86 | 4.0s | ? | 5% | steal 5% / cancel 5% / rob 4% |
| 16:34.89 | 16:38.90 | 4.0s | ? | 10% | weekend 10% / schedule 8% / correct 5% |
| 16:38.93 | 16:42.93 | 4.0s | ? | 7% | family 7% / league 4% / approve 4% |
| 16:42.97 | 16:46.97 | 4.0s | ? | 11% | here 11% / match 7% / destroy 5% |
| 16:47.01 | 16:51.01 | 4.0s | ? | 23% | secretary 23% / all 14% / rainbow 5% |
| 16:51.04 | 16:55.05 | 4.0s | ? | 16% | above 16% / secretary 6% / resign 4% |
| 16:55.08 | 16:59.09 | 4.0s | ? | 8% | surgery 8% / sting 5% / touch 2% |
| 16:59.12 | 17:03.12 | 4.0s | ? | 8% | ill 8% / quarrel 7% / argue 6% |
| 17:03.15 | 17:07.16 | 4.0s | ? | 8% | bother 8% / bread 3% / window 3% |
| 17:07.19 | 17:11.20 | 4.0s | ? | 15% | learn 15% / rich 6% / expensive 4% |
| 17:11.23 | 17:15.23 | 4.0s | ? | 15% | viewpoint 15% / tournament 5% / point 3% |
| 17:15.27 | 17:19.27 | 4.0s | ? | 16% | approve 16% / allergy 8% / librarian 4% |
| 17:19.31 | 17:23.31 | 4.0s | ? | 9% | court 9% / tournament 8% / move 6% |
| 17:23.34 | 17:27.35 | 4.0s | ? | 47% | judge 47% / court 2% / sting 2% |
| 17:27.38 | 17:31.38 | 4.0s | ? | 8% | group 8% / cancel 8% / all 7% |
| 17:31.42 | 17:35.42 | 4.0s | ? | 10% | remove 10% / approve 6% / check 5% |
| 17:35.45 | 17:39.46 | 4.0s | ? | 7% | last week 7% / author 6% / canoe 4% |
| 17:39.49 | 17:43.50 | 4.0s | ? | 17% | hour 17% / university 7% / popular 2% |
| 17:43.53 | 17:47.53 | 4.0s | ? | 18% | individual 18% / generation 3% / coat 2% |
| 17:47.57 | 17:51.57 | 4.0s | ? | 13% | sign language 13% / last 4% / sign 4% |
| 17:51.60 | 17:55.61 | 4.0s | ? | 7% | olympics 7% / catch 4% / soda 3% |
| 17:55.64 | 17:59.64 | 4.0s | ? | 14% | college 14% / hour 8% / schedule 6% |
| 17:59.68 | 18:03.68 | 4.0s | ? | 15% | all 15% / schedule 7% / confused 4% |
| 18:03.72 | 18:07.72 | 4.0s | ? | 19% | accident 19% / secretary 7% / disturb 5% |
| 18:07.75 | 18:11.76 | 4.0s | ? | 21% | sting 21% / agree 3% / touch 3% |
| 18:11.79 | 18:15.80 | 4.0s | ? | 8% | new york 8% / intersection 6% / peel 3% |
| 18:15.83 | 18:19.83 | 4.0s | ? | 8% | lord 8% / guitar 8% / any 6% |
| 18:19.87 | 18:23.87 | 4.0s | ? | 15% | scientist 15% / individual 6% / pain 4% |
| 18:23.90 | 18:27.91 | 4.0s | ? | 11% | example 11% / join 8% / hurt 3% |
| 18:27.94 | 18:31.94 | 4.0s | ? | 6% | above 6% / sentence 6% / disconnect 5% |
| 18:31.98 | 18:35.98 | 4.0s | ? | 8% | touch 8% / judge 4% / skip 4% |
| 18:36.02 | 18:40.02 | 4.0s | ? | 26% | recognize 26% / all 8% / approve 8% |
| 18:40.05 | 18:44.06 | 4.0s | ? | 13% | final 13% / again 7% / price 7% |
| 18:44.09 | 18:48.09 | 4.0s | ? | 10% | most 10% / overwhelm 6% / final 4% |
| 18:48.13 | 18:52.13 | 4.0s | ? | 35% | university 35% / lord 3% / diarrhea 2% |
| 18:52.16 | 18:56.17 | 4.0s | ? | 10% | correct 10% / double 3% / spanish 3% |
| 18:56.20 | 19:00.21 | 4.0s | ? | 7% | swimming 7% / bottom 6% / tournament 6% |
| 19:00.24 | 19:04.24 | 4.0s | ? | 4% | blend 4% / accident 4% / above 3% |
| 19:04.28 | 19:08.28 | 4.0s | ? | 10% | there 10% / far 4% / outside 2% |
| 19:08.31 | 19:12.32 | 4.0s | ? | 40% | deodorant 40% / tornado 7% / year 7% |
| 19:12.35 | 19:16.36 | 4.0s | ? | 22% | guitar 22% / judge 12% / drama 7% |
| 19:16.39 | 19:20.39 | 4.0s | ? | 13% | illegal 13% / cancel 7% / accident 6% |
| 19:20.43 | 19:24.43 | 4.0s | ? | 10% | counselor 10% / rainbow 3% / steal 2% |
| 19:24.46 | 19:28.47 | 4.0s | ? | 13% | some 13% / from now on 8% / investigate 4% |
| 19:28.50 | 19:32.51 | 4.0s | ? | 6% | exaggerate 6% / gymnastics 2% / friend 2% |
| 19:32.54 | 19:36.54 | 4.0s | ? | 3% | canoe 3% / recognize 3% / accident 3% |
| 19:36.58 | 19:40.58 | 4.0s | ? | 8% | construct 8% / champion 7% / building 6% |
| 19:40.61 | 19:44.62 | 4.0s | ? | 20% | canoe 20% / week 6% / recognize 5% |
| 19:44.65 | 19:48.65 | 4.0s | ? | 6% | above 6% / choir 4% / construct 2% |
| 19:48.69 | 19:52.69 | 4.0s | ? | 15% | when 15% / diamond 7% / carnival 7% |
| 19:52.72 | 19:56.73 | 4.0s | ? | 9% | tournament 9% / judge 7% / agreement 5% |
| 19:56.76 | 20:00.77 | 4.0s | hit | 51% | hit 51% / correct 5% / illegal 4% |
| 20:00.80 | 20:04.80 | 4.0s | ? | 6% | accident 6% / bread 4% / annoy 4% |
| 20:04.84 | 20:08.84 | 4.0s | ? | 23% | secretary 23% / accident 3% / blend 2% |
| 20:08.87 | 20:12.88 | 4.0s | ? | 5% | secretary 5% / sign language 4% / umbrella 4% |
| 20:12.91 | 20:16.92 | 4.0s | ? | 20% | sign language 20% / check 12% / secretary 6% |
| 20:16.95 | 20:20.95 | 4.0s | ? | 12% | envelope 12% / group 8% / check 4% |
| 20:20.99 | 20:24.99 | 4.0s | ? | 21% | jacket 21% / accident 21% / workshop 3% |
| 20:25.02 | 20:29.03 | 4.0s | ? | 9% | spin 9% / cost 3% / ill 2% |
| 20:29.06 | 20:33.07 | 4.0s | ? | 23% | vampire 23% / touch 9% / tissue 8% |
| 20:33.10 | 20:37.10 | 4.0s | ? | 26% | scientist 26% / shape 3% / deny 2% |
| 20:37.14 | 20:41.14 | 4.0s | quit | 51% | quit 51% / sting 9% / clock 2% |
| 20:41.17 | 20:45.18 | 4.0s | ? | 7% | resign 7% / spanish 7% / robber 3% |
| 20:45.21 | 20:49.21 | 4.0s | ? | 11% | sign 11% / sign language 3% / principal 3% |
| 20:49.25 | 20:53.25 | 4.0s | ? | 6% | purpose 6% / secretary 5% / confused 5% |
| 20:53.29 | 20:57.29 | 4.0s | ? | 17% | address 17% / player 4% / overwhelm 4% |
| 20:57.32 | 21:01.33 | 4.0s | ? | 35% | check 35% / disturb 6% / robber 5% |
| 21:01.36 | 21:05.36 | 4.0s | ? | 9% | when 9% / resign 8% / triangle 2% |
| 21:05.40 | 21:09.40 | 4.0s | ? | 15% | box 15% / room 6% / near 5% |
| 21:09.43 | 21:13.44 | 4.0s | ? | 6% | approve 6% / rich 4% / somewhere 4% |
| 21:13.47 | 21:17.48 | 4.0s | ? | 6% | anatomy 6% / generation 5% / spanish 2% |
| 21:17.51 | 21:21.51 | 4.0s | ? | 6% | approve 6% / recognize 5% / schedule 4% |
| 21:21.55 | 21:25.55 | 4.0s | ? | 6% | olympics 6% / calculus 4% / example 4% |
| 21:25.58 | 21:29.59 | 4.0s | ? | 10% | accident 10% / check 9% / approve 5% |
| 21:29.62 | 21:33.63 | 4.0s | ? | 30% | viewpoint 30% / perspective 20% / example 6% |
| 21:33.66 | 21:37.66 | 4.0s | ? | 9% | join 9% / problem 7% / engagement 6% |
| 21:37.70 | 21:41.70 | 4.0s | ? | 32% | secretary 32% / check 10% / disagree 3% |
| 21:41.73 | 21:45.74 | 4.0s | ? | 15% | hit 15% / negative 5% / maybe 4% |
| 21:45.77 | 21:49.78 | 4.0s | ? | 11% | disconnect 11% / bottle 9% / illegal 3% |
| 21:49.81 | 21:53.81 | 4.0s | ? | 18% | confused 18% / tale 7% / choir 5% |
| 21:53.85 | 21:57.85 | 4.0s | ? | 10% | tale 10% / blend 3% / snow 3% |
| 21:57.88 | 22:01.89 | 4.0s | ? | 9% | accident 9% / division 5% / independent 4% |
| 22:01.92 | 22:05.92 | 4.0s | ? | 14% | rich 14% / out 10% / expensive 8% |
| 22:05.96 | 22:09.96 | 4.0s | ? | 13% | when 13% / problem 8% / sign language 4% |
| 22:09.99 | 22:14.00 | 4.0s | ? | 41% | sting 41% / judge 5% / touch 4% |
| 22:14.03 | 22:18.04 | 4.0s | ? | 6% | large 6% / assistant 6% / secretary 4% |
| 22:18.07 | 22:22.07 | 4.0s | ? | 22% | cancel 22% / sign language 9% / hit 4% |
| 22:22.11 | 22:26.11 | 4.0s | ? | 11% | remove 11% / rich 7% / impossible 5% |
| 22:26.14 | 22:30.15 | 4.0s | ? | 5% | decrease 5% / robber 4% / anatomy 3% |
| 22:30.18 | 22:34.19 | 4.0s | ? | 14% | illegal 14% / comment 7% / shine 4% |
| 22:34.22 | 22:38.22 | 4.0s | ? | 41% | problem 41% / example 7% / tale 5% |
| 22:38.26 | 22:42.26 | 4.0s | ? | 14% | classroom 14% / anatomy 3% / deduct 3% |
| 22:42.29 | 22:46.30 | 4.0s | ? | 18% | disturb 18% / stop 10% / center 6% |
| 22:46.33 | 22:50.34 | 4.0s | ? | 10% | announce 10% / diamond 3% / square 3% |
| 22:50.37 | 22:54.37 | 4.0s | ? | 10% | robber 10% / a lot 6% / pilot 4% |
| 22:54.41 | 22:58.41 | 4.0s | ? | 6% | accident 6% / secretary 5% / disturb 4% |
| 22:58.44 | 23:02.45 | 4.0s | ? | 13% | quarrel 13% / sign 11% / judge 5% |
| 23:02.48 | 23:06.48 | 4.0s | ? | 26% | balloon 26% / caption 19% / free 8% |
| 23:06.52 | 23:10.52 | 4.0s | ? | 9% | tale 9% / squeeze 3% / catch 3% |
| 23:10.56 | 23:14.56 | 4.0s | ? | 43% | secretary 43% / student 11% / debate 4% |
| 23:14.59 | 23:18.60 | 4.0s | ? | 21% | important 21% / value 10% / tale 4% |
| 23:18.63 | 23:22.63 | 4.0s | ? | 13% | graduate 13% / believe 4% / purpose 3% |
| 23:22.67 | 23:26.67 | 4.0s | ? | 9% | dismiss 9% / spoon 2% / bottle 2% |
| 23:26.70 | 23:30.71 | 4.0s | ? | 5% | spin 5% / ill 4% / final 3% |
| 23:30.74 | 23:34.75 | 4.0s | ? | 26% | complex 26% / change 7% / different 3% |
| 23:34.78 | 23:38.78 | 4.0s | ? | 26% | clock 26% / different 6% / dive 2% |
| 23:38.82 | 23:42.82 | 4.0s | ? | 7% | problem 7% / impact 4% / when 3% |
| 23:42.86 | 23:46.86 | 4.0s | ? | 17% | cancel 17% / recognize 9% / check 3% |
| 23:46.89 | 23:50.90 | 4.0s | ? | 10% | when 10% / hit 7% / cancel 4% |
| 23:50.93 | 23:54.93 | 4.0s | ? | 11% | secretary 11% / write 4% / student 4% |
| 23:54.97 | 23:58.97 | 4.0s | ? | 5% | group 5% / decrease 3% / flatter 3% |
| 23:59.00 | 24:03.01 | 4.0s | ? | 8% | office 8% / join 8% / kill 5% |
| 24:03.04 | 24:07.05 | 4.0s | ? | 13% | deduct 13% / remove 12% / graduate 5% |
| 24:07.08 | 24:11.08 | 4.0s | ? | 10% | secretary 10% / confused 9% / recognize 2% |
| 24:11.12 | 24:15.12 | 4.0s | ? | 9% | steal 9% / complex 4% / appointment 3% |
| 24:15.15 | 24:19.16 | 4.0s | ? | 18% | cancel 18% / example 7% / problem 3% |
| 24:19.19 | 24:23.19 | 4.0s | ? | 30% | above 30% / husband 7% / quit 4% |
| 24:23.23 | 24:27.23 | 4.0s | ? | 11% | anatomy 11% / student 4% / tale 3% |
| 24:27.27 | 24:31.27 | 4.0s | ? | 12% | illegal 12% / tale 11% / story 4% |
| 24:31.30 | 24:35.31 | 4.0s | accident | 85% | accident 85% / society 1% / change 1% |
| 24:35.34 | 24:39.35 | 4.0s | ? | 18% | short 18% / intersection 9% / braid 5% |
| 24:39.38 | 24:43.38 | 4.0s | ? | 12% | secretary 12% / student 8% / seldom 5% |
| 24:43.41 | 24:47.42 | 4.0s | ? | 11% | emotion 11% / maybe 11% / accident 5% |
| 24:47.45 | 24:51.46 | 4.0s | ? | 10% | correct 10% / cancel 7% / seldom 7% |
| 24:51.49 | 24:55.49 | 4.0s | ? | 13% | archery 13% / above 10% / accident 3% |
| 24:55.53 | 24:59.53 | 4.0s | ? | 24% | when 24% / square 13% / different 7% |
| 24:59.57 | 25:03.57 | 4.0s | ? | 8% | summon 8% / umbrella 7% / approve 4% |
| 25:03.60 | 25:07.61 | 4.0s | ? | 14% | remove 14% / example 9% / diarrhea 7% |
| 25:07.64 | 25:11.64 | 4.0s | ? | 30% | far 30% / there 19% / alligator 3% |
| 25:11.68 | 25:15.68 | 4.0s | ? | 15% | enormous 15% / violin 9% / avoid 8% |
| 25:15.71 | 25:19.72 | 4.0s | ? | 17% | robber 17% / expensive 16% / student 5% |
| 25:19.75 | 25:23.76 | 4.0s | ? | 26% | cancel 26% / hit 4% / build 3% |
| 25:23.79 | 25:27.79 | 4.0s | ? | 28% | recognize 28% / secretary 7% / cancel 6% |
| 25:27.83 | 25:31.83 | 4.0s | ? | 4% | explode 4% / above 3% / shirt 3% |
| 25:31.86 | 25:35.87 | 4.0s | ? | 8% | sue 8% / repeat 7% / generation 4% |
| 25:35.90 | 25:39.90 | 4.0s | ? | 11% | tie 11% / cancel 9% / triangle 3% |
| 25:39.94 | 25:43.94 | 4.0s | ? | 8% | rich 8% / above 7% / accident 4% |
| 25:43.98 | 25:47.98 | 4.0s | ? | 4% | final 4% / brother 4% / accident 2% |
| 25:48.01 | 25:52.02 | 4.0s | ? | 12% | peanut butter 12% / secretary 6% / cancel 4% |
| 25:52.05 | 25:56.05 | 4.0s | ? | 41% | when 41% / inspect 8% / gift 5% |
| 25:56.09 | 26:00.09 | 4.0s | ? | 13% | secretary 13% / disagree 10% / problem 7% |
| 26:00.12 | 26:04.13 | 4.0s | ? | 3% | tornado 3% / accident 2% / thin 2% |
| 26:04.16 | 26:08.17 | 4.0s | ? | 30% | choir 30% / appointment 10% / earthquake 4% |
| 26:08.20 | 26:12.20 | 4.0s | ? | 35% | testify 35% / sting 5% / tornado 5% |
| 26:12.24 | 26:16.24 | 4.0s | ? | 14% | all 14% / less 4% / classroom 2% |
| 26:16.28 | 26:20.28 | 4.0s | ? | 9% | double 9% / emotion 9% / reveal 6% |
| 26:20.31 | 26:24.32 | 4.0s | ? | 6% | habit 6% / appointment 5% / catch 3% |
| 26:24.35 | 26:28.35 | 4.0s | ? | 12% | sign 12% / quit 4% / resign 4% |
| 26:28.39 | 26:32.39 | 4.0s | ? | 47% | shine 47% / above 4% / evaluate 2% |
| 26:32.42 | 26:36.43 | 4.0s | ? | 15% | above 15% / detach 12% / comment 2% |
| 26:36.46 | 26:40.47 | 4.0s | ? | 18% | catch 18% / gas 7% / touch 7% |
| 26:40.50 | 26:44.50 | 4.0s | ? | 44% | above 44% / shine 4% / snow 3% |
| 26:44.54 | 26:48.54 | 4.0s | ? | 12% | accident 12% / reject 5% / land 4% |
| 26:48.57 | 26:52.58 | 4.0s | ? | 20% | robber 20% / complete 9% / anatomy 4% |
| 26:52.61 | 26:56.62 | 4.0s | ? | 12% | shine 12% / touch 7% / summon 4% |
| 26:56.65 | 27:00.65 | 4.0s | ? | 45% | judge 45% / court 28% / hope 2% |
| 27:00.69 | 27:04.69 | 4.0s | ? | 14% | sew 14% / olympics 11% / disconnect 7% |
| 27:04.72 | 27:08.73 | 4.0s | ? | 50% | above 50% / tale 3% / trade 3% |
| 27:08.76 | 27:12.76 | 4.0s | ? | 31% | flatter 31% / check 2% / large 2% |
| 27:12.80 | 27:16.80 | 4.0s | ? | 16% | example 16% / identify 4% / chemistry 4% |
| 27:16.84 | 27:20.84 | 4.0s | ? | 8% | group 8% / librarian 6% / gift 4% |
| 27:20.87 | 27:24.88 | 4.0s | ? | 12% | assistant 12% / accident 8% / match 4% |
| 27:24.91 | 27:28.91 | 4.0s | ? | 17% | boxing 17% / write 6% / dictionary 3% |
| 27:28.95 | 27:32.95 | 4.0s | ? | 42% | flatter 42% / multiply 5% / environment 3% |
| 27:32.98 | 27:36.99 | 4.0s | ? | 19% | tournament 19% / agreement 5% / testify 5% |
| 27:37.02 | 27:41.03 | 4.0s | ? | 13% | amputate 13% / spanish 10% / quit 4% |
| 27:41.06 | 27:45.06 | 4.0s | ? | 8% | last 8% / when 7% / cancel 6% |
| 27:45.10 | 27:49.10 | 4.0s | ? | 17% | above 17% / office 7% / maximum 5% |
| 27:49.13 | 27:53.14 | 4.0s | ? | 11% | determine 11% / decide 8% / judge 8% |
| 27:53.17 | 27:57.18 | 4.0s | ? | 10% | tornado 10% / dye 9% / maybe 5% |
| 27:57.21 | 28:01.21 | 4.0s | ? | 9% | grapes 9% / independent 7% / earthquake 6% |
| 28:01.25 | 28:05.25 | 4.0s | ? | 5% | there 5% / slip 4% / people 3% |
| 28:05.28 | 28:09.29 | 4.0s | ? | 6% | deduct 6% / final 5% / there 4% |
| 28:09.32 | 28:13.33 | 4.0s | ? | 6% | accident 6% / graduation 4% / bread 3% |
| 28:13.36 | 28:17.36 | 4.0s | ? | 13% | trade 13% / join 10% / wrap 6% |
| 28:17.40 | 28:21.40 | 4.0s | ? | 8% | approach 8% / category 7% / weekend 3% |
| 28:21.43 | 28:25.44 | 4.0s | ? | 29% | bottle 29% / rich 7% / seldom 5% |
| 28:25.47 | 28:29.47 | 4.0s | ? | 10% | contribute 10% / double 3% / quarrel 2% |
| 28:29.51 | 28:33.51 | 4.0s | ? | 24% | tornado 24% / laundry 15% / touch 3% |
| 28:33.55 | 28:37.55 | 4.0s | ? | 4% | join 4% / trade 4% / correct 3% |
| 28:37.58 | 28:41.59 | 4.0s | ? | 7% | secretary 7% / schedule 6% / recognize 4% |
| 28:41.62 | 28:45.62 | 4.0s | ? | 9% | singer 9% / decide 7% / student 5% |
| 28:45.66 | 28:49.66 | 4.0s | ? | 14% | tornado 14% / perfect 4% / wet 3% |
| 28:49.69 | 28:53.70 | 4.0s | ? | 5% | take turns 5% / confused 3% / appointment 3% |
| 28:53.73 | 28:57.74 | 4.0s | ? | 39% | argue 39% / gang 4% / compromise 2% |
| 28:57.77 | 29:01.77 | 4.0s | ? | 12% | center 12% / middle 11% / slip 9% |
| 29:01.81 | 29:05.81 | 4.0s | ? | 9% | choir 9% / shock 7% / testify 5% |
| 29:05.84 | 29:09.85 | 4.0s | ? | 40% | enormous 40% / judge 5% / guitar 3% |
| 29:09.88 | 29:13.88 | 4.0s | ? | 21% | complex 21% / different 7% / change 5% |
| 29:13.92 | 29:17.92 | 4.0s | ? | 19% | group 19% / catch 4% / tale 3% |
| 29:17.96 | 29:21.96 | 4.0s | ? | 15% | check 15% / cancel 14% / disagree 7% |
| 29:21.99 | 29:26.00 | 4.0s | ? | 12% | check 12% / example 5% / cost 4% |
| 29:26.03 | 29:30.04 | 4.0s | ? | 5% | resign 5% / quit 4% / sting 3% |
| 29:30.07 | 29:34.07 | 4.0s | ? | 7% | check 7% / inspect 5% / divorce 5% |
| 29:34.11 | 29:38.11 | 4.0s | ? | 4% | argue 4% / backpack 3% / recover 3% |
| 29:38.14 | 29:42.15 | 4.0s | ? | 18% | all 18% / classroom 12% / impossible 5% |
| 29:42.18 | 29:46.18 | 4.0s | ? | 11% | again 11% / final 5% / complete 4% |
| 29:46.22 | 29:50.22 | 4.0s | ? | 4% | cancel 4% / weekend 4% / graduation 3% |
| 29:50.26 | 29:54.26 | 4.0s | ? | 5% | choir 5% / confused 4% / interest 3% |
| 29:54.29 | 29:58.30 | 4.0s | ? | 9% | finish 9% / tale 5% / illegal 5% |
| 29:58.33 | 30:02.33 | 4.0s | ? | 13% | all 13% / secretary 6% / rude 4% |
| 30:02.37 | 30:06.37 | 4.0s | ? | 18% | torture 18% / above 11% / hawaii 8% |
| 30:06.40 | 30:10.41 | 4.0s | ? | 8% | close 8% / door 6% / museum 4% |
| 30:10.44 | 30:14.45 | 4.0s | ? | 15% | final 15% / accident 8% / confused 2% |
| 30:14.48 | 30:18.48 | 4.0s | ? | 13% | evaluate 13% / viewpoint 5% / people 4% |
| 30:18.52 | 30:22.52 | 4.0s | ? | 7% | accident 7% / sign language 5% / story 4% |
| 30:22.55 | 30:26.56 | 4.0s | ? | 24% | accident 24% / recognize 5% / cancel 4% |
| 30:26.59 | 30:30.60 | 4.0s | ? | 8% | cancel 8% / expensive 6% / deduct 4% |
| 30:30.63 | 30:34.63 | 4.0s | ? | 28% | remove 28% / disconnect 3% / all 3% |
| 30:34.67 | 30:38.67 | 4.0s | ? | 5% | tale 5% / accident 3% / blend 3% |
| 30:38.70 | 30:42.71 | 4.0s | ? | 21% | secretary 21% / confused 5% / accident 4% |
| 30:42.74 | 30:46.74 | 4.0s | ? | 5% | quit 5% / resign 3% / gymnastics 2% |
| 30:46.78 | 30:50.78 | 4.0s | ? | 6% | student 6% / agree 5% / compromise 5% |
| 30:50.82 | 30:54.82 | 4.0s | ? | 6% | expect 6% / tornado 4% / sauce 3% |
| 30:54.85 | 30:58.86 | 4.0s | ? | 8% | artist 8% / approve 7% / accident 5% |
| 30:58.89 | 31:02.89 | 4.0s | ? | 8% | balloon 8% / student 7% / disturb 3% |
| 31:02.93 | 31:06.93 | 4.0s | ? | 12% | accident 12% / hot 5% / divide 4% |
| 31:06.96 | 31:10.97 | 4.0s | ? | 9% | painter 9% / tornado 7% / solve 6% |
| 31:11.00 | 31:15.01 | 4.0s | ? | 6% | spanish 6% / generation 5% / sometimes 4% |
| 31:15.04 | 31:19.04 | 4.0s | ? | 5% | graduate 5% / confused 4% / accident 4% |
| 31:19.08 | 31:23.08 | 4.0s | ? | 4% | mechanic 4% / canoe 3% / care 3% |
| 31:23.12 | 31:27.12 | 4.0s | ? | 15% | dark 15% / accident 10% / schedule 8% |
| 31:27.15 | 31:31.16 | 4.0s | ? | 9% | umbrella 9% / summon 4% / rich 4% |
| 31:31.19 | 31:35.19 | 4.0s | ? | 19% | article 19% / university 4% / disturb 3% |
| 31:35.23 | 31:39.23 | 4.0s | ? | 16% | gymnastics 16% / vacant 7% / key 3% |
| 31:39.26 | 31:43.27 | 4.0s | ? | 9% | deduct 9% / schedule 6% / illegal 4% |
| 31:43.30 | 31:47.31 | 4.0s | ? | 20% | week 20% / when 5% / last week 4% |
| 31:47.34 | 31:51.34 | 4.0s | ? | 4% | divide 4% / result 3% / confused 3% |
| 31:51.38 | 31:55.38 | 4.0s | ? | 17% | quit 17% / hit 9% / from 5% |
| 31:55.41 | 31:59.42 | 4.0s | ? | 5% | balloon 5% / office 4% / resign 4% |
| 31:59.45 | 32:03.45 | 4.0s | ? | 15% | rob 15% / accident 11% / basketball 4% |
| 32:03.49 | 32:07.49 | 4.0s | ? | 38% | accident 38% / tale 6% / anatomy 4% |
| 32:07.53 | 32:11.53 | 4.0s | ? | 6% | sweater 6% / anatomy 6% / tent 5% |
| 32:11.56 | 32:15.57 | 4.0s | ? | 26% | above 26% / champion 3% / calculus 2% |
| 32:15.60 | 32:19.60 | 4.0s | ? | 8% | sculpture 8% / hit 6% / geometry 3% |
| 32:19.64 | 32:23.64 | 4.0s | ? | 6% | tiger 6% / highway 4% / garage 3% |
| 32:23.67 | 32:27.68 | 4.0s | ? | 7% | robber 7% / tornado 5% / copy 4% |
| 32:27.71 | 32:31.72 | 4.0s | ? | 17% | all 17% / interrupt 7% / disturb 5% |
| 32:31.75 | 32:35.75 | 4.0s | ? | 6% | attorney 6% / flatter 5% / accident 4% |
| 32:35.79 | 32:39.79 | 4.0s | ? | 12% | remove 12% / tale 9% / anatomy 5% |
| 32:39.83 | 32:43.83 | 4.0s | ? | 31% | expand 31% / office 5% / anniversary 3% |
| 32:43.86 | 32:47.87 | 4.0s | ? | 12% | match 12% / artist 6% / again 5% |
| 32:47.90 | 32:51.90 | 4.0s | tale | 77% | tale 77% / story 3% / number 1% |
| 32:51.94 | 32:55.94 | 4.0s | ? | 9% | information 9% / blend 5% / toast 5% |
| 32:55.97 | 32:59.98 | 4.0s | ? | 4% | slip 4% / final 4% / construct 2% |
| 33:00.01 | 33:04.02 | 4.0s | ? | 6% | reveal 6% / sculpture 4% / balloon 4% |
| 33:04.05 | 33:08.05 | 4.0s | ? | 48% | classroom 48% / group 12% / all 6% |
| 33:08.09 | 33:12.09 | 4.0s | ? | 36% | classroom 36% / tale 10% / all 7% |
| 33:12.12 | 33:16.13 | 4.0s | ? | 4% | information 4% / check 4% / sketch 3% |
| 33:16.16 | 33:20.16 | 4.0s | ? | 15% | blood 15% / toast 5% / allergy 4% |
| 33:20.20 | 33:24.20 | 4.0s | ? | 5% | sign language 5% / disturb 5% / secretary 5% |
| 33:24.24 | 33:28.24 | 4.0s | ? | 5% | today 5% / now 5% / sweep 4% |
| 33:28.27 | 33:32.28 | 4.0s | ? | 41% | accident 41% / change 4% / roommate 3% |
| 33:32.31 | 33:36.31 | 4.0s | ? | 8% | divide 8% / challenge 5% / division 5% |
| 33:36.35 | 33:40.35 | 4.0s | ? | 10% | impossible 10% / choir 6% / graduation 3% |
| 33:40.38 | 33:44.39 | 4.0s | ? | 21% | environment 21% / hour 5% / when 5% |
| 33:44.42 | 33:48.43 | 4.0s | ? | 27% | accident 27% / care 5% / sign language 5% |
| 33:48.46 | 33:52.46 | 4.0s | ? | 4% | accident 4% / workshop 3% / deduct 3% |
| 33:52.50 | 33:56.50 | 4.0s | ? | 18% | information 18% / blend 11% / disturb 5% |
| 33:56.53 | 34:00.54 | 4.0s | ? | 8% | all 8% / secretary 8% / melt 5% |
| 34:00.57 | 34:04.58 | 4.0s | ? | 20% | inform 20% / decide 12% / determine 4% |
| 34:04.61 | 34:08.61 | 4.0s | ? | 10% | all 10% / artist 8% / solve 5% |
| 34:08.65 | 34:12.65 | 4.0s | ? | 7% | information 7% / expect 6% / count 3% |
| 34:12.68 | 34:16.69 | 4.0s | ? | 12% | quarrel 12% / guitar 11% / judge 6% |
| 34:16.72 | 34:20.72 | 4.0s | ? | 24% | disconnect 24% / calm 6% / tale 3% |
| 34:20.76 | 34:24.76 | 4.0s | ? | 5% | vampire 5% / umbrella 2% / tissue 2% |
| 34:24.80 | 34:28.80 | 4.0s | ? | 12% | deduct 12% / anatomy 4% / cost 3% |
| 34:28.83 | 34:32.84 | 4.0s | ? | 38% | anatomy 38% / rise 3% / influence 2% |
| 34:32.87 | 34:36.88 | 4.0s | ? | 8% | remove 8% / divide 7% / anatomy 4% |
| 34:36.91 | 34:40.91 | 4.0s | ? | 20% | librarian 20% / awkward 5% / bush 4% |
| 34:40.95 | 34:44.95 | 4.0s | ? | 8% | umbrella 8% / secretary 5% / hippopotamus 4% |
| 34:44.98 | 34:48.99 | 4.0s | ? | 8% | spanish 8% / underwear 5% / bottle 4% |
| 34:49.02 | 34:53.02 | 4.0s | ? | 8% | group 8% / close 7% / recognize 5% |
| 34:53.06 | 34:57.06 | 4.0s | ? | 7% | dismiss 7% / chicken 5% / tornado 3% |
| 34:57.09 | 35:01.10 | 4.0s | ? | 5% | tissue 5% / vampire 4% / ill 2% |
| 35:01.13 | 35:05.14 | 4.0s | ? | 15% | college 15% / quit 5% / graduate 5% |
| 35:05.17 | 35:09.17 | 4.0s | ? | 17% | remove 17% / anatomy 7% / group 3% |
| 35:09.21 | 35:13.21 | 4.0s | ? | 8% | thousand 8% / disturb 8% / cancel 7% |
| 35:13.24 | 35:17.25 | 4.0s | ? | 4% | easter 4% / bookstore 3% / accident 3% |
| 35:17.28 | 35:21.29 | 4.0s | ? | 8% | accident 8% / champion 7% / complex 4% |
| 35:21.32 | 35:25.32 | 4.0s | ? | 18% | except 18% / unique 11% / build 7% |
| 35:25.36 | 35:29.36 | 4.0s | ? | 3% | myself 3% / expect 2% / read 2% |
| 35:29.39 | 35:33.40 | 4.0s | ? | 7% | double 7% / emotion 4% / boil 4% |
| 35:33.43 | 35:37.43 | 4.0s | ? | 6% | bar 6% / example 5% / disconnect 5% |
| 35:37.47 | 35:41.47 | 4.0s | ? | 33% | judge 33% / tornado 4% / skip 3% |
| 35:41.51 | 35:45.51 | 4.0s | ? | 5% | above 5% / viewpoint 4% / quit 4% |
| 35:45.54 | 35:49.55 | 4.0s | ? | 10% | spanish 10% / pack 6% / fun 3% |
| 35:49.58 | 35:53.59 | 4.0s | ? | 14% | tournament 14% / science 9% / star 5% |
| 35:53.62 | 35:57.62 | 4.0s | ? | 21% | disconnect 21% / quit 5% / rude 3% |
| 35:57.66 | 36:01.66 | 4.0s | ? | 36% | spanish 36% / office 6% / seldom 3% |
| 36:01.69 | 36:05.70 | 4.0s | ? | 6% | slip 6% / above 4% / graduate 2% |
| 36:05.73 | 36:09.73 | 4.0s | ? | 34% | quit 34% / sting 2% / above 2% |
| 36:09.77 | 36:13.77 | 4.0s | ? | 11% | finally 11% / court 7% / singer 6% |
| 36:13.80 | 36:17.81 | 4.0s | ? | 20% | star 20% / clock 16% / climb 14% |
| 36:17.84 | 36:21.85 | 4.0s | ? | 6% | disagree 6% / example 5% / anatomy 5% |
| 36:21.88 | 36:25.88 | 4.0s | ? | 20% | student 20% / sting 8% / spin 3% |
| 36:25.92 | 36:29.92 | 4.0s | ? | 8% | less 8% / tournament 4% / chemistry 4% |
| 36:29.95 | 36:33.96 | 4.0s | ? | 18% | sign language 18% / want 7% / allergy 3% |
| 36:33.99 | 36:38.00 | 4.0s | ? | 9% | accident 9% / pilot 8% / librarian 4% |
| 36:38.03 | 36:42.03 | 4.0s | ? | 18% | anatomy 18% / clock 15% / dive 3% |
| 36:42.07 | 36:46.07 | 4.0s | ? | 11% | sting 11% / construct 9% / sign 7% |
| 36:46.10 | 36:50.11 | 4.0s | ? | 9% | confused 9% / blend 5% / mainstream 5% |
| 36:50.14 | 36:54.14 | 4.0s | ? | 6% | group 6% / adjective 3% / tale 3% |
| 36:54.18 | 36:58.18 | 4.0s | ? | 19% | window 19% / somewhere 9% / rich 5% |
| 36:58.22 | 37:02.22 | 4.0s | ? | 33% | accident 33% / agreement 2% / approve 2% |
| 37:02.25 | 37:06.26 | 4.0s | ? | 24% | remove 24% / university 5% / deduct 3% |
| 37:06.29 | 37:10.30 | 4.0s | ? | 16% | catch 16% / balloon 5% / correct 3% |
| 37:10.33 | 37:14.33 | 4.0s | ? | 10% | confused 10% / accident 5% / secretary 3% |
| 37:14.36 | 37:18.37 | 4.0s | ? | 12% | change 12% / counselor 8% / fight 6% |
| 37:18.40 | 37:22.41 | 4.0s | ? | 26% | tale 26% / blend 6% / bookstore 3% |
| 37:22.44 | 37:26.44 | 4.0s | ? | 10% | construct 10% / husband 7% / structure 5% |
| 37:26.48 | 37:30.48 | 4.0s | ? | 6% | tale 6% / story 4% / group 4% |
| 37:30.51 | 37:34.52 | 4.0s | ? | 7% | schedule 7% / accident 6% / check 4% |
| 37:34.55 | 37:38.56 | 4.0s | ? | 17% | accident 17% / care 5% / tonight 5% |
| 37:38.59 | 37:42.59 | 4.0s | ? | 26% | problem 26% / difficult 3% / sign 3% |
| 37:42.63 | 37:46.63 | 4.0s | ? | 5% | assistant 5% / soldier 5% / address 5% |
| 37:46.66 | 37:50.67 | 4.0s | ? | 19% | emotion 19% / judge 9% / cook 8% |
| 37:50.70 | 37:54.71 | 4.0s | mainstream | 52% | mainstream 52% / accident 6% / intersection 5% |
| 37:54.74 | 37:58.74 | 4.0s | ? | 22% | office 22% / quit 16% / mainstream 4% |
| 37:58.78 | 38:02.78 | 4.0s | ? | 14% | accident 14% / approve 4% / blend 3% |
| 38:02.81 | 38:06.82 | 4.0s | ? | 27% | secretary 27% / check 6% / hit 5% |
| 38:06.85 | 38:10.86 | 4.0s | ? | 6% | bully 6% / independent 5% / assistant 3% |
| 38:10.89 | 38:14.89 | 4.0s | ? | 13% | braid 13% / golf 6% / group 4% |
| 38:14.93 | 38:18.93 | 4.0s | ? | 11% | hit 11% / different 11% / problem 6% |
| 38:18.96 | 38:22.97 | 4.0s | judge | 51% | judge 51% / singer 7% / guitar 5% |
| 38:23.00 | 38:27.01 | 4.0s | ? | 24% | complex 24% / catch 11% / change 4% |
| 38:27.04 | 38:31.04 | 4.0s | ? | 35% | rich 35% / above 5% / seldom 3% |
| 38:31.07 | 38:35.08 | 4.0s | ? | 24% | example 24% / choice 3% / pizza 2% |
| 38:35.11 | 38:39.12 | 4.0s | ? | 39% | judge 39% / argue 4% / ill 4% |
| 38:39.15 | 38:43.15 | 4.0s | ? | 10% | person 10% / quick 8% / contribute 7% |

## 不經切詞器：1 秒滑動窗口、信心 ≥ 0.5（相鄰同詞合併，共 358 個）

| 時間 | 輸出 | 最高信心 |
| --- | --- | --- |
| 00:20.82–00:20.82 | rich | 54% |
| 00:37.17–00:37.17 | quit | 53% |
| 00:42.08–00:42.08 | guitar | 50% |
| 00:43.24–00:43.48 | adverb | 60% |
| 00:47.68–00:47.68 | flirt | 64% |
| 00:56.09–00:56.09 | quit | 65% |
| 00:57.96–00:57.96 | hour | 54% |
| 01:15.47–01:15.47 | decorate | 77% |
| 01:24.35–01:24.58 | gossip | 74% |
| 01:48.41–01:48.41 | sign | 73% |
| 01:57.28–01:57.28 | come | 61% |
| 02:03.59–02:03.59 | mean | 58% |
| 02:09.66–02:09.66 | coffee | 61% |
| 02:19.24–02:19.47 | move | 81% |
| 02:23.44–02:23.68 | coat | 61% |
| 02:26.71–02:26.71 | play | 77% |
| 02:33.49–02:33.49 | intersection | 79% |
| 02:41.43–02:42.13 | continue | 86% |
| 02:58.71–02:58.71 | now | 56% |
| 03:11.56–03:11.56 | sad | 70% |
| 03:13.89–03:13.89 | push | 64% |
| 03:27.67–03:27.91 | can | 89% |
| 03:28.38–03:28.38 | balance | 58% |
| 03:31.88–03:31.88 | can | 84% |
| 03:41.69–03:41.92 | spin | 70% |
| 03:42.62–03:42.86 | can | 81% |
| 03:45.43–03:45.66 | accident | 60% |
| 03:50.80–03:50.80 | temple | 72% |
| 03:53.60–03:53.60 | then | 65% |
| 03:57.34–03:57.34 | vacant | 79% |
| 04:09.72–04:09.95 | cards | 54% |
| 04:13.69–04:13.69 | have | 56% |
| 04:23.03–04:23.03 | walk | 70% |
| 04:25.37–04:25.60 | come | 78% |
| 04:28.17–04:28.17 | improve | 51% |
| 04:30.27–04:30.27 | intersection | 63% |
| 04:34.24–04:34.24 | proper | 70% |
| 04:49.42–04:49.42 | can | 67% |
| 04:52.93–04:53.16 | sting | 55% |
| 04:57.36–04:57.36 | recognize | 68% |
| 04:58.53–04:58.53 | bookstore | 60% |
| 05:14.65–05:14.65 | sign | 63% |
| 05:25.16–05:25.16 | want | 56% |
| 05:28.66–05:28.66 | testify | 63% |
| 05:30.30–05:30.30 | above | 51% |
| 05:31.46–05:31.93 | hour | 91% |
| 05:35.67–05:35.67 | from | 66% |
| 05:51.32–05:51.32 | enormous | 60% |
| 05:58.09–05:58.32 | from | 54% |
| 06:09.07–06:09.07 | bread | 79% |
| 06:13.51–06:13.51 | near | 69% |
| 06:16.54–06:16.54 | from | 62% |
| 06:18.41–06:18.64 | hope | 68% |
| 06:22.62–06:22.85 | hope | 76% |
| 06:47.84–06:47.84 | study | 52% |
| 06:54.85–06:55.08 | joke | 73% |
| 07:06.53–07:06.53 | last | 54% |
| 07:12.83–07:13.30 | store | 64% |
| 07:15.87–07:15.87 | candle | 51% |
| 07:19.84–07:19.84 | letter | 51% |
| 07:21.47–07:21.71 | monthly | 71% |
| 07:35.96–07:35.96 | cards | 50% |
| 07:37.59–07:37.82 | soccer | 53% |
| 07:47.17–07:47.17 | delay | 51% |
| 07:52.07–07:52.31 | president | 82% |
| 07:54.87–07:55.11 | skip | 87% |
| 08:08.42–08:08.65 | sting | 74% |
| 08:09.12–08:09.12 | experiment | 62% |
| 08:17.53–08:17.76 | play | 75% |
| 08:18.23–08:18.46 | argue | 59% |
| 08:35.75–08:35.75 | above | 58% |
| 08:41.59–08:41.59 | environment | 54% |
| 08:52.33–08:52.33 | nothing | 63% |
| 08:53.03–08:53.50 | can | 83% |
| 09:04.01–09:04.01 | ready | 60% |
| 09:06.35–09:06.35 | exaggerate | 59% |
| 09:07.05–09:07.05 | summon | 65% |
| 09:15.92–09:15.92 | double | 63% |
| 09:20.13–09:20.36 | umbrella | 60% |
| 09:24.10–09:24.10 | play | 63% |
| 09:24.80–09:25.26 | maybe | 75% |
| 09:39.98–09:39.98 | conflict | 60% |
| 09:46.52–09:46.52 | car | 50% |
| 09:55.16–09:55.16 | highway | 54% |
| 09:59.37–09:59.60 | all | 87% |
| 10:22.25–10:22.25 | continue | 61% |
| 10:28.33–10:28.56 | spin | 74% |
| 10:30.43–10:30.43 | establish | 53% |
| 10:32.07–10:32.07 | letter | 79% |
| 10:37.67–10:38.84 | testify | 92% |
| 10:44.21–10:44.91 | candle | 76% |
| 11:08.97–11:08.97 | recognize | 74% |
| 11:10.14–11:10.60 | later | 87% |
| 11:14.11–11:14.11 | testify | 53% |
| 11:15.27–11:15.27 | walk | 50% |
| 11:19.95–11:19.95 | above | 56% |
| 11:42.13–11:42.13 | ill | 64% |
| 11:44.70–11:44.70 | when | 56% |
| 11:45.64–11:46.11 | want | 58% |
| 11:53.58–11:53.58 | cannot | 56% |
| 11:54.05–11:54.05 | bicycle | 63% |
| 11:56.62–11:56.62 | rain | 51% |
| 12:00.82–12:00.82 | reputation | 56% |
| 12:01.52–12:01.75 | very | 61% |
| 12:05.49–12:05.73 | from | 60% |
| 12:17.64–12:17.64 | decide | 61% |
| 12:19.74–12:19.74 | thousand | 56% |
| 12:31.65–12:31.65 | cards | 60% |
| 12:46.83–12:46.83 | ill | 53% |
| 12:54.07–12:54.07 | tie | 65% |
| 13:06.45–13:06.45 | double | 52% |
| 13:13.46–13:13.69 | establish | 89% |
| 13:21.40–13:21.40 | ill | 53% |
| 13:24.67–13:24.90 | near | 65% |
| 13:29.11–13:29.34 | different | 56% |
| 13:37.98–13:37.98 | from | 51% |
| 13:48.03–13:48.03 | learn | 61% |
| 13:48.26–13:48.96 | ill | 61% |
| 14:01.11–14:01.11 | cards | 57% |
| 14:06.01–14:06.01 | go | 55% |
| 14:06.48–14:06.48 | cannot | 86% |
| 14:16.76–14:16.76 | example | 62% |
| 14:33.11–14:33.11 | people | 59% |
| 14:35.21–14:35.21 | dye | 74% |
| 14:42.45–14:42.45 | cost | 57% |
| 14:46.65–14:46.65 | play | 79% |
| 15:00.20–15:00.20 | people | 72% |
| 15:02.77–15:02.77 | jump | 77% |
| 15:03.70–15:03.70 | week | 51% |
| 15:05.10–15:05.10 | ill | 67% |
| 15:34.30–15:34.77 | hour | 76% |
| 15:40.61–15:40.61 | shock | 52% |
| 15:44.34–15:44.58 | vacant | 69% |
| 15:45.04–15:45.04 | cannot | 67% |
| 15:49.48–15:50.18 | maybe | 77% |
| 15:54.39–15:54.39 | right | 50% |
| 15:58.36–15:58.36 | court | 50% |
| 15:59.52–15:59.52 | braid | 52% |
| 16:01.63–16:01.63 | sign | 67% |
| 16:13.07–16:13.07 | play | 65% |
| 16:15.41–16:15.64 | can | 81% |
| 16:18.21–16:18.21 | take up | 53% |
| 16:26.85–16:27.09 | court | 66% |
| 16:28.72–16:28.72 | curse | 51% |
| 16:35.73–16:35.73 | bread | 50% |
| 16:36.20–16:36.20 | near | 59% |
| 16:41.57–16:41.57 | family | 56% |
| 16:43.90–16:43.90 | serve | 61% |
| 17:02.59–17:02.59 | ill | 60% |
| 17:16.13–17:16.13 | check | 54% |
| 17:19.17–17:19.17 | car | 67% |
| 17:25.01–17:25.24 | judge | 63% |
| 17:42.76–17:42.76 | flatter | 71% |
| 17:45.33–17:46.27 | cards | 60% |
| 17:46.73–17:46.73 | joke | 61% |
| 17:56.54–17:56.54 | skinny | 52% |
| 17:57.24–17:57.24 | expect | 55% |
| 18:05.88–18:05.88 | sign | 57% |
| 18:16.16–18:16.16 | when | 66% |
| 18:16.63–18:16.63 | seldom | 53% |
| 18:33.68–18:33.68 | walk | 57% |
| 18:48.63–18:48.63 | ill | 56% |
| 18:51.43–18:51.43 | last | 55% |
| 19:05.91–19:05.91 | there | 60% |
| 19:07.08–19:07.08 | function | 51% |
| 19:07.55–19:07.78 | vacant | 72% |
| 19:09.65–19:09.65 | vacant | 63% |
| 19:11.28–19:11.28 | diarrhea | 59% |
| 19:15.95–19:15.95 | car | 59% |
| 19:20.86–19:20.86 | punish | 50% |
| 19:23.66–19:23.66 | control | 66% |
| 19:31.60–19:31.60 | rent | 55% |
| 19:50.76–19:51.22 | from | 92% |
| 19:59.16–19:59.16 | from | 83% |
| 20:04.30–20:04.30 | joke | 61% |
| 20:10.38–20:10.61 | establish | 65% |
| 20:11.31–20:11.31 | umbrella | 73% |
| 20:19.25–20:19.25 | balance | 51% |
| 20:20.19–20:20.19 | group | 55% |
| 20:23.69–20:23.92 | game | 81% |
| 20:44.01–20:44.01 | sting | 56% |
| 20:51.25–20:51.25 | graduate | 63% |
| 21:02.93–21:02.93 | letter | 60% |
| 21:12.04–21:12.27 | somewhere | 68% |
| 21:14.14–21:14.14 | conflict | 56% |
| 21:14.37–21:14.37 | cards | 55% |
| 21:20.45–21:20.45 | week | 59% |
| 21:21.15–21:21.15 | check | 52% |
| 21:26.29–21:26.52 | from | 82% |
| 21:29.09–21:29.09 | blend | 55% |
| 21:36.33–21:36.56 | grapes | 69% |
| 21:38.20–21:38.43 | letter | 81% |
| 21:41.70–21:41.70 | right | 71% |
| 21:59.45–21:59.45 | rich | 56% |
| 22:10.43–22:10.43 | decide | 53% |
| 22:16.97–22:16.97 | enormous | 60% |
| 22:19.77–22:19.77 | hit | 77% |
| 22:29.58–22:29.82 | maybe | 51% |
| 22:30.05–22:30.05 | guitar | 54% |
| 22:54.34–22:54.34 | guitar | 52% |
| 22:56.44–22:56.44 | catch | 70% |
| 22:57.38–22:57.38 | weekend | 52% |
| 23:04.85–23:05.08 | finish | 74% |
| 23:09.99–23:09.99 | change | 54% |
| 23:17.93–23:17.93 | outside | 60% |
| 23:30.54–23:30.54 | court | 55% |
| 23:46.66–23:46.66 | reject | 57% |
| 23:50.40–23:50.40 | rich | 72% |
| 23:51.80–23:52.03 | letter | 71% |
| 24:00.44–24:00.44 | intersection | 50% |
| 24:09.55–24:09.55 | quit | 56% |
| 24:17.26–24:17.49 | skip | 62% |
| 24:18.19–24:18.66 | day | 97% |
| 24:19.83–24:20.06 | monthly | 70% |
| 24:23.10–24:23.10 | trouble | 51% |
| 24:24.26–24:24.73 | flexible | 85% |
| 24:27.53–24:27.53 | group | 55% |
| 24:44.82–24:44.82 | play | 50% |
| 24:48.55–24:48.55 | recognize | 51% |
| 24:51.12–24:51.12 | proper | 57% |
| 24:56.49–24:56.73 | different | 65% |
| 24:57.20–24:57.20 | test | 62% |
| 24:57.90–24:57.90 | lightning | 51% |
| 25:09.81–25:09.81 | maybe | 51% |
| 25:14.25–25:14.25 | emotion | 55% |
| 25:15.18–25:15.18 | enormous | 70% |
| 25:28.73–25:28.73 | when | 50% |
| 25:45.08–25:45.08 | learn | 64% |
| 25:46.71–25:46.71 | touch | 53% |
| 26:05.86–26:05.86 | music | 55% |
| 26:08.67–26:08.90 | testify | 86% |
| 26:11.47–26:13.34 | testify | 87% |
| 26:13.57–26:13.57 | chemistry | 79% |
| 26:14.74–26:14.97 | sad | 93% |
| 26:15.91–26:15.91 | concern | 59% |
| 26:22.68–26:22.91 | caption | 82% |
| 26:28.29–26:28.75 | from | 90% |
| 26:31.56–26:31.79 | testify | 66% |
| 26:36.69–26:36.69 | testify | 51% |
| 26:38.56–26:38.56 | curse | 52% |
| 26:43.23–26:43.94 | tale | 76% |
| 26:46.27–26:46.27 | separate | 52% |
| 26:54.68–26:56.55 | testify | 91% |
| 27:05.89–27:06.12 | all | 75% |
| 27:15.00–27:15.47 | testify | 89% |
| 27:16.40–27:16.40 | example | 56% |
| 27:18.50–27:18.50 | letter | 56% |
| 27:19.44–27:19.44 | play | 51% |
| 27:20.37–27:20.61 | separate | 71% |
| 27:21.07–27:21.07 | have | 77% |
| 27:36.26–27:36.49 | testify | 74% |
| 27:47.93–27:47.93 | tale | 52% |
| 27:52.84–27:53.77 | maybe | 81% |
| 27:54.71–27:54.71 | quarrel | 52% |
| 27:56.81–27:56.81 | tornado | 73% |
| 28:10.12–28:10.12 | win | 58% |
| 28:11.76–28:11.76 | bread | 88% |
| 28:15.26–28:15.26 | intersection | 60% |
| 28:15.49–28:15.49 | trade | 56% |
| 28:18.76–28:18.76 | torture | 56% |
| 28:21.80–28:22.03 | concern | 56% |
| 28:23.20–28:24.84 | ill | 66% |
| 28:28.81–28:28.81 | people | 53% |
| 28:55.43–28:55.43 | bicycle | 51% |
| 28:56.37–28:56.37 | maybe | 57% |
| 28:57.07–28:57.07 | ill | 53% |
| 29:00.34–29:00.34 | tornado | 70% |
| 29:01.27–29:01.27 | solid | 54% |
| 29:08.05–29:08.51 | enormous | 89% |
| 29:12.95–29:13.42 | complex | 75% |
| 29:13.65–29:13.65 | balloon | 73% |
| 29:22.99–29:22.99 | cry | 57% |
| 29:35.14–29:35.14 | maybe | 58% |
| 29:37.48–29:37.71 | consider | 79% |
| 29:45.18–29:45.18 | weekend | 70% |
| 29:53.59–29:53.83 | finish | 84% |
| 30:02.23–30:02.23 | intersection | 68% |
| 30:21.15–30:21.39 | have | 90% |
| 30:21.85–30:22.32 | play | 90% |
| 30:23.72–30:23.72 | emotion | 53% |
| 30:36.57–30:36.57 | more | 61% |
| 30:47.31–30:47.31 | move | 73% |
| 30:48.95–30:48.95 | ill | 54% |
| 30:49.65–30:49.88 | recognize | 87% |
| 30:53.15–30:53.15 | tornado | 65% |
| 30:57.59–30:57.59 | thanksgiving | 66% |
| 31:01.79–31:02.03 | sunday | 70% |
| 31:02.73–31:02.96 | catch | 56% |
| 31:09.27–31:09.27 | toast | 68% |
| 31:14.17–31:14.17 | when | 50% |
| 31:23.28–31:23.52 | sad | 71% |
| 31:36.60–31:36.60 | candle | 51% |
| 31:37.53–31:38.00 | candle | 81% |
| 31:51.54–31:51.54 | wood | 59% |
| 32:03.69–32:03.69 | play | 55% |
| 32:11.86–32:11.86 | cards | 51% |
| 32:17.47–32:17.47 | certificate | 50% |
| 32:17.94–32:17.94 | weather | 59% |
| 32:22.14–32:22.37 | consider | 65% |
| 32:25.88–32:25.88 | dye | 62% |
| 32:33.35–32:33.35 | match | 52% |
| 32:41.99–32:41.99 | but | 70% |
| 32:47.37–32:47.60 | have | 82% |
| 32:59.28–32:59.28 | candle | 51% |
| 33:00.91–33:01.38 | candle | 77% |
| 33:02.78–33:02.78 | testify | 52% |
| 33:12.59–33:12.59 | judge | 58% |
| 33:13.29–33:13.29 | approve | 51% |
| 33:25.44–33:25.44 | maybe | 61% |
| 33:31.28–33:31.51 | roommate | 90% |
| 33:34.78–33:35.25 | shock | 68% |
| 33:36.88–33:37.12 | testify | 59% |
| 33:39.45–33:39.68 | bread | 66% |
| 33:41.55–33:41.55 | symbol | 84% |
| 33:43.19–33:43.19 | candle | 56% |
| 33:43.42–33:43.65 | right | 85% |
| 33:44.82–33:44.82 | play | 61% |
| 33:58.84–33:58.84 | melt | 50% |
| 34:03.97–34:03.97 | testify | 59% |
| 34:07.01–34:07.01 | wet | 76% |
| 34:13.32–34:13.32 | celebrate | 50% |
| 34:23.59–34:23.59 | summon | 54% |
| 34:28.97–34:28.97 | here | 64% |
| 34:34.11–34:34.11 | remove | 57% |
| 34:45.32–34:45.32 | spanish | 53% |
| 34:45.55–34:45.55 | conflict | 51% |
| 34:45.78–34:46.25 | cards | 55% |
| 34:51.16–34:51.16 | move | 59% |
| 35:16.15–35:16.15 | vacant | 59% |
| 35:20.12–35:20.59 | complex | 77% |
| 35:35.53–35:35.53 | example | 66% |
| 35:39.50–35:39.74 | ill | 52% |
| 35:40.20–35:40.44 | judge | 55% |
| 35:47.91–35:47.91 | surface | 55% |
| 35:50.72–35:50.72 | bar | 55% |
| 35:54.69–35:54.69 | caption | 56% |
| 36:07.07–36:07.07 | skip | 62% |
| 36:11.04–36:11.04 | but | 67% |
| 36:17.11–36:17.34 | star | 60% |
| 36:25.05–36:25.28 | walk | 56% |
| 36:40.93–36:40.93 | dive | 67% |
| 37:04.05–37:04.05 | cook | 58% |
| 37:07.32–37:07.32 | right | 54% |
| 37:19.70–37:19.70 | backpack | 51% |
| 37:21.81–37:21.81 | move | 71% |
| 37:25.08–37:25.08 | inform | 52% |
| 37:28.11–37:28.11 | but | 57% |
| 37:28.81–37:29.28 | group | 52% |
| 37:48.43–37:48.43 | maybe | 50% |
| 37:49.83–37:49.83 | cook | 60% |
| 37:53.34–37:53.34 | mainstream | 59% |
| 37:53.80–37:53.80 | intersection | 75% |
| 37:54.74–37:54.74 | joke | 50% |
| 37:59.64–37:59.88 | near | 71% |
| 38:13.19–38:13.19 | leave | 53% |
| 38:34.91–38:34.91 | candle | 54% |
| 38:35.85–38:35.85 | spin | 61% |
| 38:36.55–38:36.55 | guitar | 61% |
