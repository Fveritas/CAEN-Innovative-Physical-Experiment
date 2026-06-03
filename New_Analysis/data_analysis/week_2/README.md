# 第二周数据分析说明

本目录用于分析第二周宇宙线铅板阻挡实验数据。当前已经完成固定阈值计数、符合率、相对透过率、有效阻挡能力、归一化符合比、基础诊断图、经验指数拟合以及脉冲积分分布分析。

第二周数据只用于周内分析。由于第二周与第一周之间存在探测效率、增益或实验条件差异，不能把第二周绝对符合率直接拼接到第一周曲线上。跨周合并应在后续单独进行归一化分析。

## 已完成内容

### 1. 分析规划

规划文档：

```text
WEEK_2_ANALYSIS_PLAN.md
```

该文档说明了第二周数据范围、固定阈值、主要统计量、误差传播、系统效应检查和后续拟合注意事项。

### 2. 拟合前分析脚本

脚本：

```text
week2_pre_fit_analysis.py
```

该脚本完成以下工作：

- 读取第二周预处理数据：
  - `Processed_data/npz/51811.npz`
  - `Processed_data/npz/5185.npz`
  - `Processed_data/npz/5186.npz`
  - `Processed_data/npz/5187.npz`
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

- 以 `51811.npz` 作为第二周 0 片基准，计算：

```text
Transmission_week2(x) = R_coin_week2(x) / R_coin_week2(0)
Blocking_week2(x) = 1 - Transmission_week2(x)
```

- 生成统计表和基础诊断图。

### 3. 衰减拟合与脉冲积分分析脚本

脚本：

```text
week2_fit_spectrum_analysis.py
```

该脚本完成以下工作：

- 读取 `results/tables/week2_pre_fit_summary.csv`。
- 使用 `Transmission_week2(x) = exp(-x / lambda_eff_week2)` 做带误差经验拟合。
- 使用 `R_coin(x) = R0 * exp(-x / lambda_eff)` 对 `coin/hour` 做带误差经验拟合。
- 输出 `lambda_eff`、`sigma_lambda`、`chi2`、`chi2/ndf`。
- 统计全事件和符合事件中的 `area`、`area2` 分布。
- 绘制衰减拟合图、拟合残差图、符合事件 `area/area2` 脉冲积分分布。

注意：第二周数据存在明显系统效应可能，拟合结果只作为经验趋势参考，不应直接解释为铅中 μ 子吸收长度。

## 如何运行

从项目根目录运行：

```bash
cd /home/guiyu/workspace/CAEN/New_Analysis
python3 data_analysis/week_2/week2_pre_fit_analysis.py
python3 data_analysis/week_2/week2_fit_spectrum_analysis.py
```

如果需要指定输入或输出目录：

```bash
python3 data_analysis/week_2/week2_pre_fit_analysis.py \
  --input-dir Processed_data/npz \
  --output-dir data_analysis/week_2/results

python3 data_analysis/week_2/week2_fit_spectrum_analysis.py \
  --input-dir Processed_data/npz \
  --results-dir data_analysis/week_2/results
```

## 输出文件

脚本默认输出到：

```text
data_analysis/week_2/results/
```

### 1. 统计表

```text
results/tables/week2_pre_fit_summary.csv
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
| `transmission` | 相对第二周 0 片铅板的有效透过率 |
| `blocking` | 有效阻挡能力，`1 - transmission` |

### 2. 图像

```text
results/figures/week2_coin_rate.png
```

第二周符合率随铅板厚度变化图。

```text
results/figures/week2_transmission_blocking.png
```

第二周有效透过率和有效阻挡能力图。

```text
results/figures/week2_normalized_coin_ratios.png
```

第二周 `Coin/Up` 与 `Coin/Down` 归一化符合比。

```text
results/figures/week2_area_distribution.png
results/figures/week2_area2_distribution.png
```

第二周 `area` 和 `area2` 脉冲积分分布。

```text
results/figures/week2_area_vs_area2_51811.png
results/figures/week2_area_vs_area2_5185.png
results/figures/week2_area_vs_area2_5186.png
results/figures/week2_area_vs_area2_5187.png
```

每个 run 的 `area` vs `area2` 二维分布图。

### 3. 拟合结果

```text
results/fit/week2_attenuation_fit.csv
results/fit/week2_attenuation_fit.json
results/fit/week2_attenuation_fit.png
results/fit/week2_coin_rate_fit.png
```

当前第二周相对透过率经验指数拟合结果：

| 参数 | 数值 |
| --- | ---: |
| `lambda_eff_mm` | 188.23 mm |
| `sigma_lambda_eff_mm` | 33.90 mm |
| `chi2/ndf` | 2.384 |

拟合模型为：

```text
Transmission_week2(x) = exp(-x / lambda_eff_week2)
```

当前第二周绝对符合率经验拟合结果：

| 参数 | 数值 |
| --- | ---: |
| `R0` | 1781.19 counts/hour |
| `sigma_R0` | 50.63 counts/hour |
| `lambda_eff_mm` | 239.47 mm |
| `sigma_lambda_eff_mm` | 75.59 mm |
| `chi2/ndf` | 6.364 |

拟合模型为：

```text
R_coin(x) = R0 * exp(-x / lambda_eff)
```

第二周厚铅板点存在回升趋势，尤其 `coin/hour` 拟合的 `chi2/ndf` 明显偏大。因此这些拟合主要用于量化经验趋势，不能作为可靠的纯衰减模型。

### 4. 脉冲积分分布结果

```text
results/spectrum/week2_spectrum_summary.csv
results/spectrum/week2_area_coin_spectrum.png
results/spectrum/week2_area2_coin_spectrum.png
```

`week2_spectrum_summary.csv` 统计了每个 run 的全事件和符合事件 `area`、`area2` 分布，包括 `count`、`mean`、`median`、`std`、`p10`、`p90`。

## 当前基础结果概览

按固定阈值 `(area > 30) & (area2 > 30)`，第二周符合数为：

| Run | 铅板数 | 厚度(mm) | `N_coin` |
| --- | ---: | ---: | ---: |
| `51811` | 0 | 0 | 1831 |
| `5185` | 40 | 20 | 1523 |
| `5186` | 50 | 25 | 1579 |
| `5187` | 60 | 30 | 1687 |

相对第二周 0 片铅板的有效透过率约为：

| Run | 铅板数 | `Transmission` | `Blocking` |
| --- | ---: | ---: | ---: |
| `51811` | 0 | 1.000 | 0.000 |
| `5185` | 40 | 0.832 | 0.168 |
| `5186` | 50 | 0.862 | 0.138 |
| `5187` | 60 | 0.921 | 0.079 |

第二周结果与理想的单调衰减趋势并不完全一致，尤其是 40、50、60 片之间出现回升趋势。因此第二周需要重点作为系统效应讨论对象，而不能简单解释为铅板越厚阻挡越弱。可能原因包括：

- 第二周探测器效率或增益变化。
- 下探测器 `area2` 分布偏移。
- 厚铅板测量之间实验条件不完全一致。
- 统计误差和 1 min 时间误差之外仍存在系统误差。

## 后续工作

第二周基础统计、经验拟合和脉冲积分分布分析已经完成。后续分析应优先做系统效应检查，而不是直接把拟合结果解释为衰减长度：

1. 比较 `51811` 与厚铅板数据的 `area`、`area2` 分布。
2. 检查 `N_up/N_total`、`N_down/N_total`、`Coin/Up`、`Coin/Down` 的变化。
3. 在跨周合并时使用 `Coin/Up` 或 0 片基准缩放，不直接拼接绝对符合率。
4. 在报告中明确 `lambda_eff_week2` 是第二周实验条件下的经验有效参数，不是 μ 子在铅中的纯吸收长度。
