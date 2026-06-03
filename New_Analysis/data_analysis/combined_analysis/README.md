# 综合分析

本目录用于进行第一周和第二周数据的一致性检查，以及后续跨周合并分析。

这里的目标不是简单地把 Week 1 和 Week 2 拼接成一条曲线。两周数据在 0 片铅板基准、探测器通过率和脉冲积分分布上存在明显差异。因此，综合分析必须先量化探测器响应变化，再决定哪些归一化方法具有物理意义。

## 当前状态

目前已经完成单周分析：

```text
data_analysis/week_1/
data_analysis/week_2/
```

第一周主要输出：

```text
data_analysis/week_1/results/tables/week1_pre_fit_summary.csv
data_analysis/week_1/results/fit/week1_attenuation_fit.csv
data_analysis/week_1/results/spectrum/week1_spectrum_summary.csv
```

第二周主要输出：

```text
data_analysis/week_2/results/tables/week2_pre_fit_summary.csv
data_analysis/week_2/results/fit/week2_attenuation_fit.csv
data_analysis/week_2/results/spectrum/week2_spectrum_summary.csv
```

综合分析规划文档为：

```text
COMBINED_ANALYSIS_PLAN.md
```

当前已经实现综合分析脚本：

```text
combined_week_analysis.py
```

运行方式：

```bash
cd /home/guiyu/workspace/CAEN/New_Analysis
python3 data_analysis/combined_analysis/combined_week_analysis.py
```

## 关键观察

两周 0 片铅板基准明显不同：

```text
Week 1 zero-lead: 5181  -> N_coin = 3357 counts/hour
Week 2 zero-lead: 51811 -> N_coin = 1831 counts/hour
```

基准比值为：

```text
1831 / 3357 ≈ 0.545
```

这意味着第二周 0 片铅板的符合率只有第一周约 54.5%。这个差异过大，不能忽略，也说明两周的绝对符合率不能直接拼接。

## 主要判断

当前最可能的跨周差异来源是探测器响应漂移，尤其是下探测器通道。

证据如下：

| 物理量 | Week 1 baseline `5181` | Week 2 baseline `51811` |
| --- | ---: | ---: |
| `N_up/N_total` | 0.531 | 0.735 |
| `N_down/N_total` | 0.471 | 0.270 |
| `Coin/Up` | 0.475 | 0.267 |
| `Coin/Down` | 0.536 | 0.728 |
| `area_mean` | 36.12 | 49.06 |
| `area2_mean` | 34.74 | 17.71 |

第二周下探测器的脉冲积分分布明显偏低。在固定阈值：

```python
area2 > 30
```

不变的情况下，第二周下探测器的有效通过效率会显著降低。

## 归一化策略

综合分析至少应比较两种归一化方法。

### 1. 0 片基准缩放

定义：

```text
k = R_coin_week1(0) / R_coin_week2(0)
```

当前数值：

```text
k = 3357 / 1831 ≈ 1.833
```

然后缩放第二周符合率：

```text
R_coin_week2_scaled(x) = k * R_coin_week2(x)
```

这个方法简单，但假设第二周和第一周只差一个整体效率系数。由于两周 `area` 和 `area2` 的变化方向并不相同，这个假设较强，因此它更适合作为诊断方法，而不是唯一结论。

当前缩放后 0-60 片综合结果为：

| Run | 周次 | 铅板数 | 厚度(mm) | 缩放后 `coin/hour` | 相对 Week 1 基准透过率 | 有效阻挡率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `5181` | 1 | 0 | 0 | 3357.0 | 1.000 | 0.000 |
| `5182` | 1 | 10 | 5 | 3136.0 | 0.934 | 0.066 |
| `5183` | 1 | 20 | 10 | 3119.0 | 0.929 | 0.071 |
| `5184` | 1 | 30 | 15 | 3046.0 | 0.907 | 0.093 |
| `5185` | 2 | 40 | 20 | 2792.3 | 0.832 | 0.168 |
| `5186` | 2 | 50 | 25 | 2895.0 | 0.862 | 0.138 |
| `5187` | 2 | 60 | 30 | 3093.0 | 0.921 | 0.079 |

缩放后可以看到，第二周厚铅板点仍然不是单调下降，说明 0 片基准缩放不能完全消除第二周系统效应。

### 2. 条件符合比 `Coin/Up`

定义：

```text
Coin/Up = N_coin / N_up
```

物理意义为：

```text
P(下探测器也通过阈值 | 上探测器已通过阈值)
```

它比原始 `coin/hour` 更适合跨周比较，因为它部分消除了上探测器触发规模的变化。但它仍然会受到下探测器阈值效率影响，所以必须结合 `area2` 分布解释。

### 3. 分周透过率曲线

保守做法是分别展示：

```text
Week 1 Transmission(x)
Week 2 Transmission(x)
```

每一周都用本周自己的 0 片铅板数据归一化。这种方法不强行假设两周探测系统完全一致。

## 已完成输出

脚本：

```text
combined_week_analysis.py
```

已生成表格：

```text
results/tables/baseline_comparison.csv
results/tables/normalization_comparison.csv
results/tables/combined_scaled_summary.csv
results/tables/zero_lead_scale_factor.csv
```

已生成图像及其意义：

| 图像 | 代表的意义 |
| --- | --- |
| `results/figures/raw_coin_rate_combined.png` | 原始 `coin/hour` 随铅厚度变化的跨周拼接图。该图用于直观看出第一周和第二周绝对符合率基准不同，只能作为系统差异诊断图，不能直接用于物理拟合。 |
| `results/figures/scaled_coin_rate_combined.png` | 使用 0 片基准缩放后得到的跨周 `coin/hour` 图。该图展示如果把第二周整体缩放到第一周 0 片基准，0-60 片铅板的符合率趋势会是什么样。它用于评估“单一缩放因子”是否足以修正跨周差异。 |
| `results/figures/scaled_transmission_combined.png` | 将缩放后的符合率再除以第一周 0 片基准得到的综合透过率图。它展示 0-60 片铅板下的有效透过率趋势；当前第二周厚铅板点仍非单调，说明系统效应没有被完全消除。 |
| `results/figures/week_transmission_comparison.png` | 第一周和第二周分别以各自 0 片基准归一化后的 `Transmission` 对比图。这是最保守的跨周展示方式，不强行假设两周探测器响应一致。 |
| `results/figures/zero_lead_area_comparison.png` | 第一周 0 片 `5181` 与第二周 0 片 `51811` 的上探测器 `area` 分布对比。用于检查上探测器脉冲积分响应是否跨周变化。 |
| `results/figures/zero_lead_area2_comparison.png` | 第一周 0 片与第二周 0 片的下探测器 `area2` 分布对比。该图是判断第二周下探测器响应降低的重要证据。 |
| `results/figures/zero_lead_area_vs_area2_comparison.png` | 两周 0 片数据的 `area` vs `area2` 二维分布对比。用于同时观察上下探测器响应是否发生相对漂移。 |
| `results/figures/detector_pass_fraction_comparison.png` | `N_up/N_total` 和 `N_down/N_total` 随铅厚度变化的图。用于判断上下探测器阈值通过率是否稳定，以及第二周下探测器通过率是否异常偏低。 |
| `results/figures/conditional_coin_ratio_comparison.png` | `Coin/Up` 和 `Coin/Down` 随铅厚度变化的图。用于比较条件符合概率，判断跨周差异是否主要来自探测器效率或几何符合效率变化。 |

总结来说，`raw_coin_rate_combined.png`、`zero_lead_area*_comparison.png`、`detector_pass_fraction_comparison.png` 和 `conditional_coin_ratio_comparison.png` 主要是系统诊断图；`scaled_coin_rate_combined.png`、`scaled_transmission_combined.png` 和 `week_transmission_comparison.png` 可用于讨论归一化后的铅板阻挡趋势。

## 报告结论方向

报告中应说明：

> 第一周和第二周不能被视为同一套稳定探测条件下的连续测量。第二周的 0 片基准和下探测器响应与第一周存在明显差异，因此跨周比较必须使用归一化方法，并将探测器响应漂移作为系统误差来源。
