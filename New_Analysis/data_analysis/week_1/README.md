# 第一周数据分析说明

本目录用于分析第一周宇宙线铅板阻挡实验数据。当前已经完成固定阈值计数、符合率、相对透过率、有效阻挡能力、归一化符合比、基础诊断图、指数衰减拟合以及脉冲积分分布分析。

## 已完成内容

### 1. 分析规划

规划文档：

```text
WEEK_1_ANALYSIS_PLAN.md
```

该文档说明了第一周分析的物理目标、数据范围、固定阈值、主要物理量、误差传播、衰减拟合和后续脚本设计。

### 2. 拟合前分析脚本

脚本：

```text
week1_pre_fit_analysis.py
```

该脚本完成以下工作：

- 读取第一周预处理数据：
  - `Processed_data/npz/5181.npz`
  - `Processed_data/npz/5182.npz`
  - `Processed_data/npz/5183.npz`
  - `Processed_data/npz/5184.npz`
- 使用固定阈值：

```python
coincidence = (area > 30) & (area2 > 30)
```

- 计算基础计数：
  - `N_total`
  - `N_up`
  - `N_down`
  - `N_coin`
- 计算符合率：

```text
R_coin = N_coin / T
```

其中：

```text
T = 3600 s
sigma_T = 60 s
```

- 计算归一化符合比：

```text
Coin/Up = N_coin / N_up
Coin/Down = N_coin / N_down
```

- 计算相对透过率和有效阻挡能力：

```text
Transmission(x) = R_coin(x) / R_coin(0)
Blocking(x) = 1 - Transmission(x)
```

- 生成统计表和基础诊断图。

### 3. 衰减拟合与脉冲积分分析脚本

脚本：

```text
week1_fit_spectrum_analysis.py
```

该脚本完成以下工作：

- 读取 `results/tables/week1_pre_fit_summary.csv`。
- 使用 `Transmission(x) = exp(-x / lambda_eff)` 做带误差指数拟合。
- 使用 `R_coin(x) = R0 * exp(-x / lambda_eff)` 对 `coin/hour` 做带误差指数拟合。
- 输出 `lambda_eff`、`sigma_lambda`、`chi2`、`chi2/ndf`。
- 统计全事件和符合事件中的 `area`、`area2` 分布。
- 绘制衰减拟合图、拟合残差图、符合事件 `area/area2` 脉冲积分分布。

注意：`lambda_eff` 是当前实验几何和阈值条件下的有效衰减长度，不是 μ 子在铅中的纯吸收长度。

## 如何运行

从项目根目录运行：

```bash
cd /home/guiyu/workspace/CAEN/New_Analysis
python3 data_analysis/week_1/week1_pre_fit_analysis.py
python3 data_analysis/week_1/week1_fit_spectrum_analysis.py
```

如果需要指定输入或输出目录：

```bash
python3 data_analysis/week_1/week1_pre_fit_analysis.py \
  --input-dir Processed_data/npz \
  --output-dir data_analysis/week_1/results

python3 data_analysis/week_1/week1_fit_spectrum_analysis.py \
  --input-dir Processed_data/npz \
  --results-dir data_analysis/week_1/results
```

## 输出文件

脚本默认输出到：

```text
data_analysis/week_1/results/
```

### 1. 统计表

```text
results/tables/week1_pre_fit_summary.csv
```

主要字段包括：

| 字段 | 含义 |
| --- | --- |
| `run` | 数据 run 编号 |
| `lead_plates` | 铅板片数 |
| `lead_thickness_mm` | 铅板厚度，单位 mm |
| `radiation_lengths` | 以铅辐射长度表示的厚度 |
| `n_total` | 总事件数 |
| `n_up` | 满足 `area > 30` 的事件数 |
| `n_down` | 满足 `area2 > 30` 的事件数 |
| `n_coin` | 同时满足上下阈值的符合数 |
| `r_coin_per_hour` | 每小时符合计数率 |
| `r_coin_hz` | Hz 单位符合率 |
| `sigma_r_coin_per_hour` | 包含计数误差和 1 min 时间误差的每小时符合率误差 |
| `coin_over_up` | `N_coin / N_up` |
| `coin_over_down` | `N_coin / N_down` |
| `transmission` | 相对 0 片铅板的有效透过率 |
| `blocking` | 有效阻挡能力，`1 - transmission` |

### 2. 图像

```text
results/figures/week1_coin_rate.png
```

第一周符合率随铅板厚度变化图。

```text
results/figures/week1_transmission_blocking.png
```

第一周有效透过率和有效阻挡能力图。

```text
results/figures/week1_normalized_coin_ratios.png
```

第一周 `Coin/Up` 与 `Coin/Down` 归一化符合比。

```text
results/figures/week1_area_distribution.png
results/figures/week1_area2_distribution.png
```

第一周 `area` 和 `area2` 脉冲积分分布。

```text
results/figures/week1_area_vs_area2_5181.png
results/figures/week1_area_vs_area2_5182.png
results/figures/week1_area_vs_area2_5183.png
results/figures/week1_area_vs_area2_5184.png
```

每个 run 的 `area` vs `area2` 二维分布图。

### 3. 拟合结果

```text
results/fit/week1_attenuation_fit.csv
results/fit/week1_attenuation_fit.json
results/fit/week1_attenuation_fit.png
results/fit/week1_coin_rate_fit.png
```

当前第一周相对透过率指数拟合结果：

| 参数 | 数值 |
| --- | ---: |
| `lambda_eff_mm` | 137.45 mm |
| `sigma_lambda_eff_mm` | 34.85 mm |
| `chi2/ndf` | 0.335 |

拟合模型为：

```text
Transmission(x) = exp(-x / lambda_eff)
```

当前第一周绝对符合率拟合结果：

| 参数 | 数值 |
| --- | ---: |
| `R0` | 3306.04 counts/hour |
| `sigma_R0` | 67.14 counts/hour |
| `lambda_eff_mm` | 168.09 mm |
| `sigma_lambda_eff_mm` | 62.02 mm |
| `chi2/ndf` | 0.701 |

拟合模型为：

```text
R_coin(x) = R0 * exp(-x / lambda_eff)
```

### 4. 脉冲积分分布结果

```text
results/spectrum/week1_spectrum_summary.csv
results/spectrum/week1_area_coin_spectrum.png
results/spectrum/week1_area2_coin_spectrum.png
```

`week1_spectrum_summary.csv` 统计了每个 run 的全事件和符合事件 `area`、`area2` 分布，包括 `count`、`mean`、`median`、`std`、`p10`、`p90`。

## 当前基础结果概览

按固定阈值 `(area > 30) & (area2 > 30)`，第一周符合数为：

| Run | 铅板数 | 厚度(mm) | `N_coin` |
| --- | ---: | ---: | ---: |
| `5181` | 0 | 0 | 3357 |
| `5182` | 10 | 5 | 3136 |
| `5183` | 20 | 10 | 3119 |
| `5184` | 30 | 15 | 3046 |

相对 0 片铅板的有效透过率约为：

| Run | 铅板数 | `Transmission` | `Blocking` |
| --- | ---: | ---: | ---: |
| `5181` | 0 | 1.000 | 0.000 |
| `5182` | 10 | 0.934 | 0.066 |
| `5183` | 20 | 0.929 | 0.071 |
| `5184` | 30 | 0.907 | 0.093 |

这些数值说明第一周数据中，随着铅板厚度从 0 增加到 15 mm，双探测器有效符合率整体下降。该下降应解释为当前实验几何和阈值条件下的有效衰减，不能直接解释为 μ 子被铅板吸收的比例。

## 后续工作

第一周内部的基础统计、拟合和脉冲积分分布分析已经完成。后续可做：

1. 把第一周表格和图整理进实验报告。
2. 与第二周结果做跨周归一化比较。
3. 在报告中强调第一周只有 4 个厚度点，拟合自由度较少。
4. 说明 `lambda_eff` 是有效衰减长度，不是 μ 子在铅中的纯吸收长度。
