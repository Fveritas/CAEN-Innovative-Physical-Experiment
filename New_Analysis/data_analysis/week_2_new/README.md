# Week 2 New: area2 左移分析

本目录专门分析第二周下探测器脉冲积分 `area2` 是否相对第一周发生明显左移。

## 分析对象

- 第一周参考基准：`5181`，0 片铅板。
- 第二周数据：`51811`、`5185`、`5186`、`5187`，分别对应 0、40、50、60 片铅板。
- 固定阈值：`area2 > 30`。

## 主要结论

第二周 `area2` 相对第一周 0 片基准存在明显左移。最直接的 0 片对比为：

- `5181` 的 `area2` 均值：34.740
- `51811` 的 `area2` 均值：17.715
- 均值差：-17.025
- 均值比例：0.510
- `5181` 的 `area2` 中位数：0.989
- `51811` 的 `area2` 中位数：-0.059
- 中位数差：-1.047
- `area2 > 30` 通过率从 0.471 下降到 0.270
- KS 检验统计量：0.202
- KS 检验 p 值：1.067e-196

这些量共同说明：第二周下探测器的脉冲积分分布不仅均值降低，而且整体分布相对第一周向低 `area2` 区域移动。因此，第二周固定阈值 `area2 > 30` 对下探测器更严格，会显著降低第二周的有效符合效率。

## 输出文件

### 表格

- `results/tables/area2_shift_summary.csv`：每个 run 的 `area2` 分布统计量。
- `results/tables/area2_shift_comparison_vs_5181.csv`：第二周各 run 相对第一周 0 片基准的差值、比例和 KS 检验。

### 图像

- `results/figures/area2_zero_lead_left_shift.png`：第一周 0 片和第二周 0 片的 `area2` 分布直接对比。
- `results/figures/area2_distribution_week2_vs_week1.png`：第一周参考和第二周全部 run 的 `area2` 分布对比。
- `results/figures/area2_ecdf_week2_vs_week1.png`：经验累积分布函数，用于观察整体分布左移。
- `results/figures/area2_boxplot_week2_vs_week1.png`：箱线图，展示中位数和四分位范围变化。
- `results/figures/area2_pass_fraction_gt30.png`：`area2 > 30` 阈值通过率对比。
