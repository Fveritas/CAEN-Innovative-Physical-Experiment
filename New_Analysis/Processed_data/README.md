# 预处理数据说明

本目录保存由 `data_processing/preprocess_root_data.py` 从原始 ROOT 文件转换得到的轻量化 NumPy 数据。后续符合计数、Rossi 曲线、能谱分析和归一化分析应优先读取这里的数据，而不是反复读取体积较大的 ROOT 文件。

## 目录结构

```text
Processed_data/
  README.md
  npz/
    5181.npz
    5182.npz
    5183.npz
    5184.npz
    51811.npz
    5185.npz
    5186.npz
    5187.npz
    5181b.npz
  summary/
    preprocess_summary.csv
    preprocess_summary.json
```

## npz 文件内容

每个 `.npz` 文件对应一个实验 run，包含逐事件数组和 run 级元数据。

默认保存的核心逐事件变量包括：

- `area`：上探测器脉冲积分，用于能谱和阈值判断。
- `area2`：下探测器脉冲积分，用于能谱和阈值判断。
- `amp`：脉冲幅度相关量。
- `base`：基线。
- `rms`：基线噪声或波形 RMS。
- `Index_minamp`：普通 ROOT 文件中的最小幅度位置。

部分文件可能还包含：

- `event_num`
- `Index_minamp1`
- `Index_minamp2`

这些字段主要存在于 `5181b.npz`，用于时间差或速度测量的附加分析。

每个 `.npz` 还包含以下 run 级元数据：

- `run`：run 编号。
- `week`：测量周次。
- `lead_plates`：铅板片数。
- `lead_thickness_mm`：铅板总厚度，单位 mm。
- `radiation_lengths`：以铅辐射长度 `X0` 表示的厚度。
- `mass_thickness_g_cm2`：质量厚度，单位 `g/cm^2`。

## 数据分组

第一周数据：

| 文件 | 铅板数 | 厚度(mm) | 说明 |
| --- | ---: | ---: | --- |
| `5181.npz` | 0 | 0 | 第一周 0 片基准 |
| `5182.npz` | 10 | 5 | 第一周 |
| `5183.npz` | 20 | 10 | 第一周 |
| `5184.npz` | 30 | 15 | 第一周 |

第二周数据：

| 文件 | 铅板数 | 厚度(mm) | 说明 |
| --- | ---: | ---: | --- |
| `51811.npz` | 0 | 0 | 第二周 0 片基准 |
| `5185.npz` | 40 | 20 | 第二周 |
| `5186.npz` | 50 | 25 | 第二周 |
| `5187.npz` | 60 | 30 | 第二周 |

特殊数据：

| 文件 | 说明 |
| --- | --- |
| `5181b.npz` | 含分通道时间字段，适合速度测量或时间差附录分析 |

## 摘要文件

`summary/preprocess_summary.csv` 和 `summary/preprocess_summary.json` 保存每个 run 的快速统计量，包括：

- 原始 ROOT 文件路径。
- 输出 `.npz` 文件路径。
- 周次、铅板片数、厚度、辐射长度、质量厚度。
- 事件数。
- 保存成功的分支和缺失分支。
- `area`、`area2` 均值。
- `area > 30` 的事件数。
- `area2 > 30` 的事件数。
- 默认符合判据 `(area > 30) & (area2 > 30)` 下的符合数。

这些摘要适合用于快速检查数据质量，也可作为报告中基础统计表的来源。

## 读取示例

```python
from pathlib import Path
import numpy as np

data_path = Path("Processed_data/npz/5181.npz")

with np.load(data_path) as data:
    area = data["area"]
    area2 = data["area2"]
    lead_plates = int(data["lead_plates"])
    thickness_mm = float(data["lead_thickness_mm"])

coincidence = (area > 30) & (area2 > 30)
n_coin = int(np.count_nonzero(coincidence))

print(lead_plates, thickness_mm, n_coin)
```

## 后续分析建议

1. 第一周数据先用 `5181.npz` 作为 0 片基准，单独分析 0、10、20、30 片。
2. 第二周数据先用 `51811.npz` 作为 0 片基准，单独分析 0、40、50、60 片。
3. 两周合并时不要直接拼接绝对符合率，应优先使用 `Coin/Up = N_coin / N_up`。
4. 同时可使用两周 0 片数据计算缩放系数，作为归一化方法的系统误差检查。
5. 所有主要分析统一使用固定阈值 `area > 30`、`area2 > 30`，不要再引入其他阈值。
