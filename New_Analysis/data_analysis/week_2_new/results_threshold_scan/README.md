# Week 2 area2 阈值扫描

本目录检验第二周数据中，固定使用 `area2 > 30` 是否会筛掉一部分本来可能进入符合样本的事件。

## 阈值设置

- 上探测器阈值固定：`area > 30`
- 下探测器阈值扫描：`area2 > 30`、`area2 > 25`、`area2 > 20`
- 分析 run：`51811`、`5185`、`5186`、`5187`

## 主要结论

降低第二周 `area2` 阈值会恢复一部分符合事件，说明确实有事件处在 `20 < area2 <= 30` 或 `25 < area2 <= 30` 区间，在原来的 `area2 > 30` 标准下被筛掉。

- 使用 `area2 > 30` 时，第二周总符合数：6620
- 改为 `area2 > 25` 时，第二周总符合数：6622，恢复 2 个符合事件
- 改为 `area2 > 20` 时，第二周总符合数：6624，恢复 4 个符合事件

物理含义：第二周 `area2` 分布左移后，固定阈值 `area2 > 30` 会更强地压低下探测器通过率和符合率。把阈值降到 25 或 20 可以证明存在一批“被阈值筛掉”的事件，但这只是诊断探测器响应变化，不代表正式分析应随意改变阈值。

## 输出文件

### 表格

- `tables/week2_area2_threshold_scan_summary.csv`：每个 run 在三个阈值下的通过数、符合数和 Coin/Up。
- `tables/week2_area2_threshold_recovered_events.csv`：相对 `area2 > 30`，降到 25 或 20 后恢复的下探测器事件和符合事件数。

### 图像

- `figures/week2_coin_counts_area2_threshold_scan.png`：不同阈值下的符合事件数。
- `figures/week2_coin_over_up_area2_threshold_scan.png`：不同阈值下的 Coin/Up 条件符合比。
- `figures/week2_recovered_coin_events.png`：降低阈值后恢复的符合事件数。
