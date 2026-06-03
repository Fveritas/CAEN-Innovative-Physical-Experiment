# 宇宙线铅板阻挡实验小论文大纲

## 题目建议

**基于双闪烁体符合探测的宇宙线铅板阻挡实验分析**

可选英文题目：

**Effective Attenuation of Cosmic-Ray Coincidence Events in Lead Absorbers**

## 摘要

摘要应控制在 150-250 字，包含以下内容：

1. 实验目的：研究宇宙线穿过不同厚度铅板后的双探测器符合率变化。
2. 实验方法：使用上下两个闪烁体探测器和 CAEN DT5742 数字化仪，固定阈值 `(area > 30) & (area2 > 30)` 选择符合事件。
3. 数据范围：第一周 0-30 片铅板，第二周 0、40、50、60 片铅板。
4. 主要结果：第一周符合率随铅厚整体下降；第二周存在明显系统效应；跨周绝对符合率不能直接拼接。
5. 结论：铅板导致的是实验几何和探测阈值条件下的有效符合率衰减，不能直接解释为 μ 子纯吸收。

## 1. 引言

### 1.1 宇宙线背景

应说明：

- 原初宇宙线主要来自地球大气层外，成分以质子和原子核为主。
- 原初宇宙线进入大气后产生强子簇射，进而产生 π、K 等介子。
- π/K 衰变产生 μ 子，μ 子是海平面附近最重要的穿透性带电粒子。
- 海平面 μ 子通常具有 GeV 量级能量，因此几厘米铅板不能简单地完全吸收 μ 子。

可用公式：

```text
pi/K -> muon + neutrino
tau_lab = gamma * tau_mu
```

### 1.2 宇宙线角分布

可写：

```text
I(theta) ≈ I(0) cos^2(theta)
```

上下两个探测器构成几何望远镜，因此实验更敏感于接近垂直入射的宇宙线。

### 1.3 本实验物理问题

核心问题：

> 铅板厚度增加后，双探测器符合率如何变化？这种变化来自铅板阻挡、多重散射、低能成分削弱，还是探测器效率变化？

注意避免说：

```text
本实验直接测量 μ 子在铅中的吸收长度。
```

推荐说：

```text
本实验测量的是固定几何和固定阈值条件下，宇宙线事件仍能形成双探测器符合的有效概率。
```

## 2. 实验原理

### 2.1 双探测器符合

定义：

```text
N_up   = count(area > 30)
N_down = count(area2 > 30)
N_coin = count((area > 30) & (area2 > 30))
```

符合率：

```text
R_coin = N_coin / T
```

本实验：

```text
T = 3600 s
sigma_T = 60 s
```

误差：

```text
sigma_R / R_coin = sqrt(1/N_coin + (sigma_T/T)^2)
```

### 2.2 归一化符合比

定义：

```text
Coin/Up = N_coin / N_up
Coin/Down = N_coin / N_down
```

物理意义：

```text
Coin/Up ≈ P(下探测器也通过阈值 | 上探测器已通过阈值)
```

应说明 `Coin/Up` 不是纯吸收概率，而是受铅板阻挡、多重散射、几何接受度和下探测器效率共同影响的条件符合概率。

### 2.3 铅板有效阻挡能力

定义透过率：

```text
Transmission(x) = R_coin(x) / R_coin(0)
```

定义有效阻挡率：

```text
Blocking(x) = 1 - Transmission(x)
```

注意：

```text
Blocking 不等于 μ 子被吸收比例。
```

### 2.4 多重散射和能量损失

能量损失估算：

```text
dE/dx ≈ 1-2 MeV/(g/cm^2)
```

30 mm 铅对应：

```text
X_mass = 3.0 cm * 11.34 g/cm^3 = 34.02 g/cm^2
Delta E ≈ 68 MeV
```

对 GeV μ 子而言，该能损不足以解释全部符合率下降，因此多重散射和几何符合效率很重要。

多重散射 Highland 公式：

```text
theta0 ≈ (13.6 MeV / beta p c) z sqrt(x/X0) [1 + 0.038 ln(x/X0)]
```

## 3. 实验装置与数据

### 3.1 实验装置

应写明：

- 上下两个闪烁体探测器。
- 铅板放置在两个探测器之间。
- CAEN DT5742 数字化仪。
- 采样率 5 GS/s。
- 固定阈值 `(area > 30) & (area2 > 30)`。

### 3.2 数据分组

第一周：

| Run | 铅板数 | 厚度(mm) |
| --- | ---: | ---: |
| `5181` | 0 | 0 |
| `5182` | 10 | 5 |
| `5183` | 20 | 10 |
| `5184` | 30 | 15 |

第二周：

| Run | 铅板数 | 厚度(mm) |
| --- | ---: | ---: |
| `51811` | 0 | 0 |
| `5185` | 40 | 20 |
| `5186` | 50 | 25 |
| `5187` | 60 | 30 |

强调：

```text
两周数据必须先分开讨论，不能直接拼接绝对符合率。
```

## 4. 数据处理方法

### 4.1 预处理

说明使用 `uproot` 读取 ROOT 文件，保存关键分支到 `.npz`：

- `area`
- `area2`
- `amp`
- `base`
- `rms`
- `Index_minamp`

对应脚本：

```text
data_processing/preprocess_root_data.py
```

### 4.2 单周分析

第一周脚本：

```text
data_analysis/week_1/week1_pre_fit_analysis.py
data_analysis/week_1/week1_fit_spectrum_analysis.py
```

第二周脚本：

```text
data_analysis/week_2/week2_pre_fit_analysis.py
data_analysis/week_2/week2_fit_spectrum_analysis.py
```

### 4.3 拟合模型

相对透过率拟合：

```text
Transmission(x) = exp(-x/lambda_eff)
```

绝对符合率拟合：

```text
R_coin(x) = R0 exp(-x/lambda_eff)
```

说明：

- `lambda_eff` 是有效衰减长度。
- 它包含多重散射、几何接受度、能量损失、探测效率和阈值响应。

## 5. 第一周结果

### 5.1 基础结果

| Run | 铅板数 | `N_coin` | `Transmission` | `Blocking` |
| --- | ---: | ---: | ---: | ---: |
| `5181` | 0 | 3357 | 1.000 | 0.000 |
| `5182` | 10 | 3136 | 0.934 | 0.066 |
| `5183` | 20 | 3119 | 0.929 | 0.071 |
| `5184` | 30 | 3046 | 0.907 | 0.093 |

应插入图：

```text
data_analysis/week_1/results/figures/week1_coin_rate.png
data_analysis/week_1/results/figures/week1_transmission_blocking.png
```

### 5.2 第一周拟合

| 拟合对象 | `lambda_eff` | `chi2/ndf` |
| --- | ---: | ---: |
| `Transmission` | 137.45 ± 34.85 mm | 0.335 |
| `coin/hour` | 168.09 ± 62.02 mm | 0.701 |

应插入图：

```text
data_analysis/week_1/results/fit/week1_attenuation_fit.png
data_analysis/week_1/results/fit/week1_coin_rate_fit.png
```

### 5.3 第一周物理解释

第一周整体呈下降趋势，说明铅板增加后，有效符合概率下降。该下降可能来自：

- 多重散射导致粒子偏离下探测器。
- 低能成分被铅板削弱。
- 粒子能量损失后低于阈值。
- 几何符合效率降低。

## 6. 第二周结果

### 6.1 基础结果

| Run | 铅板数 | `N_coin` | `Transmission` | `Blocking` |
| --- | ---: | ---: | ---: | ---: |
| `51811` | 0 | 1831 | 1.000 | 0.000 |
| `5185` | 40 | 1523 | 0.832 | 0.168 |
| `5186` | 50 | 1579 | 0.862 | 0.138 |
| `5187` | 60 | 1687 | 0.921 | 0.079 |

应插入图：

```text
data_analysis/week_2/results/figures/week2_coin_rate.png
data_analysis/week_2/results/figures/week2_transmission_blocking.png
```

### 6.2 第二周拟合

| 拟合对象 | `lambda_eff` | `chi2/ndf` |
| --- | ---: | ---: |
| `Transmission` | 188.23 ± 33.90 mm | 2.384 |
| `coin/hour` | 239.47 ± 75.59 mm | 6.364 |

应插入图：

```text
data_analysis/week_2/results/fit/week2_attenuation_fit.png
data_analysis/week_2/results/fit/week2_coin_rate_fit.png
```

### 6.3 第二周物理解释

第二周厚铅板点不是单调下降，尤其 40、50、60 片之间出现回升趋势。因此第二周不能简单解释为干净的铅板衰减曲线。

应重点讨论：

- 第二周可能存在探测器响应漂移。
- 下探测器 `area2` 分布偏低。
- 固定 `area2 > 30` 阈值在第二周更严格。
- 第二周拟合只能作为经验趋势。

## 7. 跨周综合分析

### 7.1 0 片基准差异

```text
Week 1: N_coin(5181) = 3357 counts/hour
Week 2: N_coin(51811) = 1831 counts/hour
```

比值：

```text
1831 / 3357 ≈ 0.545
```

这说明第二周绝对符合率基准显著低于第一周。

### 7.2 探测器响应漂移

| 物理量 | Week 1 `5181` | Week 2 `51811` |
| --- | ---: | ---: |
| `N_up/N_total` | 0.531 | 0.735 |
| `N_down/N_total` | 0.471 | 0.270 |
| `Coin/Up` | 0.475 | 0.267 |
| `Coin/Down` | 0.536 | 0.728 |
| `area_mean` | 36.12 | 49.06 |
| `area2_mean` | 34.74 | 17.71 |

应插入图：

```text
data_analysis/combined_analysis/results/figures/zero_lead_area_comparison.png
data_analysis/combined_analysis/results/figures/zero_lead_area2_comparison.png
data_analysis/combined_analysis/results/figures/detector_pass_fraction_comparison.png
data_analysis/combined_analysis/results/figures/conditional_coin_ratio_comparison.png
```

### 7.3 0 片基准缩放

定义：

```text
k = R_coin_week1(0) / R_coin_week2(0) = 3357 / 1831 = 1.833
```

缩放结果：

| Run | 铅板数 | 缩放后 `coin/hour` | 透过率 |
| --- | ---: | ---: | ---: |
| `5181` | 0 | 3357.0 | 1.000 |
| `5182` | 10 | 3136.0 | 0.934 |
| `5183` | 20 | 3119.0 | 0.929 |
| `5184` | 30 | 3046.0 | 0.907 |
| `5185` | 40 | 2792.3 | 0.832 |
| `5186` | 50 | 2895.0 | 0.862 |
| `5187` | 60 | 3093.0 | 0.921 |

应插入图：

```text
data_analysis/combined_analysis/results/figures/scaled_coin_rate_combined.png
data_analysis/combined_analysis/results/figures/scaled_transmission_combined.png
data_analysis/combined_analysis/results/figures/week_transmission_comparison.png
```

### 7.4 综合结论

0 片缩放后，第二周厚铅板点仍然非单调。这说明单一缩放因子不能完全消除第二周系统效应。因此最终报告应给出：

1. 第一周作为较可靠的低厚度区间结果。
2. 第二周作为厚铅板区间和系统误差讨论。
3. 跨周缩放结果作为趋势参考，而不是唯一物理拟合。

## 8. 结论

建议结论包括：

1. 第一周数据表明铅板厚度增加会降低双探测器有效符合率。
2. 第一周有效衰减长度约为 100-200 mm 量级，取决于拟合对象。
3. 第二周数据存在明显系统效应，尤其下探测器响应降低。
4. 两周绝对符合率不能直接拼接。
5. 0 片基准缩放后可以得到 0-60 片的趋势图，但第二周厚铅板点仍非单调。
6. 本实验测得的是有效符合率衰减，不是 μ 子在铅中的纯吸收长度。

## 9. 图表清单

建议正文主要图：

1. 第一周 `Transmission` 和 `Blocking`。
2. 第一周衰减拟合。
3. 第二周 `Transmission` 和 `Blocking`。
4. 第二周衰减拟合。
5. 两周 0 片 `area2` 对比。
6. 条件符合比 `Coin/Up`、`Coin/Down` 对比。
7. 0 片缩放后的 0-60 片综合透过率。

建议正文主要表：

1. 数据 run 和铅板厚度表。
2. 第一周统计表。
3. 第二周统计表。
4. 两周 0 片基准对比表。
5. 衰减拟合参数表。

## 10. 参考文献

可引用：

1. Particle Data Group, *Cosmic Rays*, Review of Particle Physics 2024.
2. Particle Data Group, *Passage of Particles Through Matter*, Review of Particle Physics 2024.
3. B. Rossi, *High-Energy Particles*, Prentice-Hall.
4. B. Rossi, "Interaction between Cosmic Rays and Matter", Nature 132, 173 (1933).
5. CAEN DT5742 documentation.

