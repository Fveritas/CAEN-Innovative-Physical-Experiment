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

对 `Coin/Up` 归一化后再乘旧 0 片缩放因子的综合曲线，可继续运行经验指数拟合脚本：

```text
fit_normalized_scaled_analysis.py
```

运行方式：

```bash
cd /home/guiyu/workspace/CAEN/New_Analysis
python3 data_analysis/combined_analysis/combined_week_analysis.py
python3 data_analysis/combined_analysis/fit_normalized_scaled_analysis.py
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

综合分析不再使用第二周 `coin/hour` 的 0 片基准缩放作为主方法。当前采用上探测器归一化符合率：

定义：

```text
Coin/Up = N_coin / N_up
R_norm = Coin/Up * N_up(Week 1, 0 lead)
```

其中：

```text
N_up(Week 1, 0 lead) = N_up(5181) = 7064
```

物理意义为：

```text
P(下探测器也通过阈值 | 上探测器已通过阈值)
```

`R_norm` 可以理解为：把每个 run 统一到与第一周 0 片相同的上探测器候选事件规模后，估计还能形成多少双探测器符合事件。它比原始 `coin/hour` 更适合跨周比较，因为它部分消除了上探测器候选事件规模变化的影响。但它仍然会受到下探测器效率、几何接受度和阈值响应影响，因此不能解释为纯铅吸收概率。

当前 `Coin/Up` 归一化后的 0-60 片结果为：

| Run | 周次 | 铅板数 | 厚度(mm) | `Coin/Up` | `R_norm` | 相对 Week 1 0片 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `5181` | 1 | 0 | 0 | 0.4752 | 3357.0 | 1.000 |
| `5182` | 1 | 10 | 5 | 0.4455 | 3146.7 | 0.937 |
| `5183` | 1 | 20 | 10 | 0.4318 | 3049.9 | 0.909 |
| `5184` | 1 | 30 | 15 | 0.4219 | 2980.2 | 0.888 |
| `51811` | 2 | 0 | 0 | 0.2672 | 1887.7 | 0.562 |
| `5185` | 2 | 40 | 20 | 0.2324 | 1641.8 | 0.489 |
| `5186` | 2 | 50 | 25 | 0.2308 | 1630.5 | 0.486 |
| `5187` | 2 | 60 | 30 | 0.2307 | 1630.0 | 0.486 |

可以看到，第二周 40、50、60 片在 `Coin/Up` 归一化后基本表现为平台，而不是原始 `coin/hour` 中的明显回升。因此厚铅板区间的绝对符合数回升更可能来自上探测器候选事件规模变化，而不应解释为 Rossi 曲线式物理回升。

### 分周透过率曲线

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
results/tables/combined_coin_up_normalized_summary.csv
```

已生成图像及其意义：

| 图像 | 代表的意义 |
| --- | --- |
| `results/figures/raw_coin_rate_combined.png` | 原始 `coin/hour` 随铅厚度变化的跨周拼接图。该图用于直观看出第一周和第二周绝对符合率基准不同，只能作为系统差异诊断图，不能直接用于物理拟合。 |
| `results/figures/coin_up_normalized_rate_combined.png` | 使用 `Coin/Up * N_up(5181)` 得到的上探测器归一化符合率图。该图用于比较统一上探测器候选事件规模后的有效符合趋势。 |
| `results/figures/coin_up_normalized_transmission_combined.png` | 将 `Coin/Up` 归一化符合率再除以第一周 0 片基准得到的相对趋势图。第二周 40、50、60 片在该图中基本为平台。 |
| `results/figures/coin_up_normalized_then_scaled_rate_combined.png` | 在 `Coin/Up * N_up(5181)` 基础上，对第二周再乘旧 0 片符合率缩放因子 `3357/1831` 后的综合计数率图。 |
| `results/figures/coin_up_normalized_then_scaled_transmission_combined.png` | 上述“归一化后再缩放”结果相对第一周 0 片基准的透过率图。 |
| `results/figures/week_transmission_comparison.png` | 第一周和第二周分别以各自 0 片基准归一化后的 `Transmission` 对比图。这是最保守的跨周展示方式，不强行假设两周探测器响应一致。 |
| `results/figures/zero_lead_area_comparison.png` | 第一周 0 片 `5181` 与第二周 0 片 `51811` 的上探测器 `area` 分布对比。用于检查上探测器脉冲积分响应是否跨周变化。 |
| `results/figures/zero_lead_area2_comparison.png` | 第一周 0 片与第二周 0 片的下探测器 `area2` 分布对比。该图是判断第二周下探测器响应降低的重要证据。 |
| `results/figures/zero_lead_area_vs_area2_comparison.png` | 两周 0 片数据的 `area` vs `area2` 二维分布对比。用于同时观察上下探测器响应是否发生相对漂移。 |
| `results/figures/detector_pass_fraction_comparison.png` | `N_up/N_total` 和 `N_down/N_total` 随铅厚度变化的图。用于判断上下探测器阈值通过率是否稳定，以及第二周下探测器通过率是否异常偏低。 |
| `results/figures/conditional_coin_ratio_comparison.png` | `Coin/Up` 和 `Coin/Down` 随铅厚度变化的图。用于比较条件符合概率，判断跨周差异是否主要来自探测器效率或几何符合效率变化。 |

总结来说，`raw_coin_rate_combined.png`、`zero_lead_area*_comparison.png`、`detector_pass_fraction_comparison.png` 和 `conditional_coin_ratio_comparison.png` 主要是系统诊断图；`coin_up_normalized_rate_combined.png`、`coin_up_normalized_transmission_combined.png` 和 `week_transmission_comparison.png` 可用于讨论归一化后的铅板阻挡趋势。

## 归一化后再缩放的经验指数拟合

拟合对象为：

```text
R_scaled_norm = (N_coin / N_up) * N_up(5181) * k_week
```

其中 Week 1 的 `k_week = 1`，Week 2 的 `k_week = 3357 / 1831 = 1.833424`。拟合时使用第一周 0、10、20、30 片和第二周 40、50、60 片；第二周 0 片 `51811` 是定义跨周缩放的诊断点，未放入 0--60 片趋势拟合。

已生成拟合输出：

```text
results/fit_normalized_scaled/normalized_scaled_exponential_fits.csv
results/fit_normalized_scaled/normalized_scaled_exponential_fits.json
results/fit_normalized_scaled/normalized_scaled_fit_input.csv
results/fit_normalized_scaled/normalized_scaled_transmission_fit.png
results/fit_normalized_scaled/normalized_scaled_rate_fit.png
results/fit_normalized_scaled/normalized_scaled_transmission_log_fit.png
results/fit_normalized_scaled/normalized_scaled_rate_log_fit.png
results/fit_normalized_scaled/normalized_scaled_transmission_offset_exp_fit.png
results/fit_normalized_scaled/normalized_scaled_rate_offset_exp_fit.png
results/fit_normalized_scaled/normalized_scaled_transmission_offset_exp_log_fit.png
results/fit_normalized_scaled/normalized_scaled_rate_offset_exp_log_fit.png
```

经验指数模型结果为：

| 拟合对象 | 模型 | `lambda_eff` | `R^2` | `chi2/ndf` | AIC |
| --- | --- | ---: | ---: | ---: | ---: |
| 归一化透过率 | `T(x) = exp(-x/lambda_eff)` | 168.57 mm | 0.333 | 4.973 | 31.84 |
| 归一化后再缩放计数率 | `R(x) = R0 exp(-x/lambda_eff)` | 243.17 mm | 0.645 | 3.514 | 21.57 |
| 归一化透过率平台模型 | `T(x) = T_inf + A exp(-x/lambda_eff)` | 5.91 mm | 0.988 | 0.142 | 6.57 |
| 归一化后再缩放计数率平台模型 | `R(x) = R_inf + A exp(-x/lambda_eff)` | 5.91 mm | 0.988 | 0.142 | 6.57 |

单指数模型给出 `10^2 mm` 量级的有效衰减长度，但 `chi2/ndf` 明显大于 1，说明“归一化后再缩放”的跨周曲线不能被简单单指数很好描述。指数加常数的平台模型显著降低 `chi2`、AIC 和 BIC，说明它更贴近“前段下降、厚铅板区间平台”的数据形状。由于该模型参数更多且样本点较少，平台模型应作为经验描述，不应把 `lambda_eff = 5.91 mm` 解释为铅材料的真实吸收长度。

## 报告结论方向

报告中应说明：

> 第一周和第二周不能被视为同一套稳定探测条件下的连续测量。第二周的 0 片基准和下探测器响应与第一周存在明显差异，因此跨周比较必须使用归一化方法，并将探测器响应漂移作为系统误差来源。
