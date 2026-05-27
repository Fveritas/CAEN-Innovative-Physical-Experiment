# CAEN Cosmic Ray Detector Analysis

宇宙射线探测器数据分析项目，使用CAEN DT5742数字化仪采集数据。

## 项目结构

```
CAEN/
├── data/                      # 数据文件和处理
│   ├── raw/                # 原始ROOT数据文件
│   └── processing/                # 数据读取和诊断脚本
├── analysis/              # 分析脚本
│   ├── cosmic_rays/               # 宇宙射线速度和时间分析
│   ├── rossi/                   # Rossi转换曲线分析
│   ├── attenuation/           # 铅板衰减分析
│   └── fitting/              # 拟合质量分析
├── utilities/                     # 工具脚本
├── results/                    # 输出结果
│   ├── plots/                     # 图表输出
│   └── reports/                 # 分析报告
└── legacy/                   # 旧版本文件
```

## 实验设置

- **探测器**: 上下两个闪烁体探测器
- **数字化仪**: CAEN DT5742 (采样率: 5 GHz)
- **探测器间距**: 16.2 cm (部分实验为50 cm)
- **铅板厚度**: 0.5 mm/片
- **测量时间**: 每个数据点约1小时

## 数据文件

### 原始数据 (data/raw/)

**注意**: ROOT数据文件因体积过大未包含在Git仓库中。

数据文件列表:
- `5181.root` - 0片铅板
- `5182.root` - 10片铅板
- `5183.root` - 20片铅板
- `5184.root` - 30片铅板
- `5185.root` - 40片铅板
- `5186.root` - 50片铅板
- `5187.root` - 额外测量
- `51811.root` - 额外测量

请将ROOT数据文件放置在 `data/raw/` 目录下以运行分析脚本。

## 主要分析脚本

### 1. 宇宙射线分析 (analysis/cosmic_rays/)

#### `analyze_cosmic_rays.py`
分析宇宙射线事件的基本统计信息。

```bash
python analysis/cosmic_rays/analyze_cosmic_rays.py data/raw/5181.root [area_threshold] [area2_threshold]
```

**功能**:
- 统计上下探测器触发事件
- 计算符合事件数量
- 分析area和area2分布

#### `calculate_velocity.py`
计算宇宙射线速度。

```bash
python analysis/cosmic_rays/calculate_velocity.py data/raw/5181.root <distance_cm> [sampling_rate_GHz]
```

**功能**:
- 从时间差计算粒子速度
- 与光速比较 (期望值 ~0.99c)
- 生成速度分布图

#### `check_time_diff.py`
检查探测器之间的时间差分布。

### 2. Rossi转换曲线分析 (analysis/rossi/)

#### `rossi_analysis_v2.py`
完整的Rossi曲线分析（考虑系统偏移）。

```bash
python analysis/rossi/rossi_analysis_v2.py
```

**功能**:
- 分析不同铅板厚度下的符合率
- 检测Rossi峰位置
- 比较不同周次测量的系统差异
- 生成多面板诊断图

**物理参数**:
- 铅的辐射长度 X₀ = 5.6 mm
- 临界能量 Ec ≈ 7.4 MeV
- 铅密度 ρ = 11.34 g/cm³

#### `why_no_rossi_curve.py`
诊断为什么没有观察到Rossi峰。

### 3. 衰减分析 (analysis/attenuation/)

#### `analyze_lead_attenuation.py`
分析宇宙射线在铅中的衰减。

#### `plot_attenuation.py`
绘制衰减曲线。

### 4. 拟合分析 (analysis/fitting/)

#### `fit_analysis.py`
对数据进行拟合分析。

#### `analyze_fit_quality.py`
评估拟合质量。

### 5. 数据处理 (data/processing/)

#### `read_data.py`
基本的ROOT文件读取工具。

```bash
python data/processing/read_data.py data/raw/5181.root
```

#### `diagnostic_v4.py`
最新版本的数据诊断工具（2D分析）。

```bash
python data/processing/diagnostic_v4.py
```

## 工具脚本 (utilities/)

- `analyze_timing.py` - 时间分析工具
- `analyze_capabilities.py` - 分析探测器能力
- `calculate_required_distance.py` - 计算所需探测器间距
- `what_can_measure.py` - 评估可测量的物理量

## 结果输出

所有图表保存在 `results/plots/` 下的相应子文件夹:
- `velocity/` - 速度分析图
- `rossi/` - Rossi曲线图
- `attenuation/` - 衰减曲线图
- `diagnostics/` - 诊断图表
- `fitting/` - 拟合结果图

## 依赖环境

```bash
pip install uproot numpy matplotlib scipy
```

## 主要发现

1. **速度测量**: 宇宙射线速度约为 0.99c（符合预期）
2. **Rossi峰**: 在0-30片铅板范围内未观察到明显的Rossi峰
3. **系统偏移**: 不同周次测量存在下探测器效率差异（~下降）
4. **符合率**: 随铅板厚度增加呈线性下降趋势

## 注意事项

- 40-50片铅板数据来自不同周次，存在系统偏移
- 符合条件: area > 30 AND area2 > 30
- 采样率: 5 GHz (DT5742)
- 时间单位: 采样间隔 = 0.2 ns

## 联系方式

如有问题，请联系项目负责人。
