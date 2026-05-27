# 工具脚本 (Utilities)

本目录包含通用工具和辅助计算脚本。

## 脚本说明

### `analyze_timing.py`
**功能**: 时间测量系统分析工具

**分析内容**:
- Index_minamp1和Index_minamp2的分布特征
- 时间分辨率评估
- 系统延迟检测
- 时间校准建议

**输出**:
- 时间分布统计
- 分辨率估计
- 异常值报告

**用法**:
```bash
python analyze_timing.py <root_file>
```

**应用场景**:
- 验证时间测量系统
- 评估时间分辨率
- 检测时间偏移
- 优化触发设置

---

### `analyze_capabilities.py`
**功能**: 探测器系统能力评估

**评估内容**:
1. **能量分辨率**
   - 从area分布计算
   - FWHM/Peak位置

2. **时间分辨率**
   - 从时间差分布计算
   - 影响速度测量精度

3. **符合效率**
   - 几何接受度
   - 触发效率

4. **动态范围**
   - ADC饱和检查
   - 线性范围

5. **噪声水平**
   - 基线涨落
   - 假触发率

**输出**:
- 系统性能报告
- 改进建议
- 限制因素分析

**用法**:
```bash
python analyze_capabilities.py
```

**典型结果**:
- 能量分辨率: ~20-30%
- 时间分辨率: ~0.5-1 ns
- 符合效率: ~60-80%
- 动态范围: 12-bit (0-4095)

---

### `calculate_required_distance.py`
**功能**: 计算达到特定测量精度所需的探测器间距

**物理模型**:
```
σ_v/v = √[(σ_d/d)² + (σ_t/t)²]
```
其中:
- σ_v/v: 速度相对误差
- σ_d/d: 距离测量相对误差
- σ_t/t: 时间测量相对误差

**输入参数**:
- 目标速度精度（如1%）
- 时间分辨率（如0.5 ns）
- 距离测量精度（如1 mm）

**输出**:
- 所需最小探测器间距
- 预期时间差
- 误差预算分析

**用法**:
```bash
python calculate_required_distance.py
```

**示例计算**:
```
目标: 1%速度精度
时间分辨率: 0.5 ns
距离精度: 1 mm

对于v = 0.99c:
时间差 = d/v ≈ d/(0.99c)
要求: σ_t/t < 1%
因此: t > 100×σ_t = 50 ns
所需距离: d > 50 ns × 0.99c ≈ 15 m
```

**结论**: 
- 短距离(~20 cm): 时间误差主导，精度受限
- 长距离(>1 m): 距离误差主导，精度提高
- 最优距离: 平衡时间和距离误差

---

### `what_can_measure.py`
**功能**: 评估当前实验装置可以测量的物理量

**可测量物理量**:

1. **宇宙射线通量**
   - 单位: counts/(cm²·s·sr)
   - 精度: ~5%（统计误差）
   - 方法: 计数率/探测器面积/立体角

2. **粒子速度**
   - 范围: 0.5c - 1.0c
   - 精度: ~5-10%（取决于距离）
   - 方法: 时间差测量

3. **能量损失**
   - 范围: 相对测量
   - 精度: ~20%（能量分辨率限制）
   - 方法: area分布分析

4. **衰减系数**
   - 范围: 0.01-0.1 cm⁻¹
   - 精度: ~10%
   - 方法: 符合率vs厚度拟合

5. **多重散射角**
   - 范围: 间接测量
   - 精度: 定性
   - 方法: 符合率几何依赖

6. **符合时间窗口**
   - 范围: 纳秒级
   - 精度: ~0.2 ns（采样间隔）
   - 方法: 时间关联分析

**不可测量**:
- 绝对能量（需要能量刻度）
- 粒子类型（需要额外探测器）
- 角度分布（需要位置灵敏探测器）
- 极化（需要极化敏感探测器）

**输出**:
- 可测量物理量列表
- 预期精度评估
- 改进建议

**用法**:
```bash
python what_can_measure.py
```

---

## 使用场景

### 实验设计阶段
1. 使用`calculate_required_distance.py`确定探测器间距
2. 使用`what_can_measure.py`明确测量目标
3. 使用`analyze_capabilities.py`评估系统性能

### 数据采集阶段
1. 使用`analyze_timing.py`验证时间系统
2. 实时监控系统性能
3. 优化触发和阈值设置

### 数据分析阶段
1. 评估测量精度
2. 识别系统限制
3. 规划改进方案

---

## 工具脚本开发指南

### 添加新工具
1. 明确功能和用途
2. 遵循现有代码风格
3. 添加详细文档字符串
4. 提供使用示例

### 代码结构
```python
#!/usr/bin/env python3
"""
简短描述

详细说明功能、输入、输出
"""

import numpy as np
import matplotlib.pyplot as plt

def main_function(params):
    """
    主函数文档
    """
  # 实现
    pass

if __name__ == "__main__":
    # 命令行接口
    main_function()
```

### 最佳实践
- 使用argparse处理命令行参数
- 提供默认值和示例
- 输出清晰的结果和建议
- 包含错误处理

---

## 物理计算参考

### 时间分辨率
```python
def time_resolution(sigma_index, sampling_rate_GHz=5.0):
    """
    计算时间分辨率
    
    sigma_index: Index的标准差（采样点）
    sampling_rate_GHz: 采样率（GHz）
    
    返回: 时间分辨率（ns）
    """
    sampling_interval_ns = 1.0 / sampling_rate_GHz
    return sigma_index * sampling_interval_ns
```

### 速度误差
```python
def velocity_error(distance_cm, time_ns, 
           sigma_distance_cm, sigma_time_ns):
    """
    计算速度测量误差
    
    返回: 速度相对误差
    """
    rel_error_d = sigma_distance_cm / distance_cm
    rel_error_t = sigma_time_ns / time_ns
    return np.sqrt(rel_error_d**2 + rel_error_t**2)
```

### 立体角
```python
def solid_angle(detector_area_cm2, distance_cm):
    """
    计算探测器立体角
    
    返回: 立体角（sr）
    """
    return detector_area_cm2 / distance_cm**2
```

### 几何接受度
```python
def geometric_acceptance(area1_cm2, area2_cm2, distance_cm):
    """
    计算符合测量的几何接受度
    
    返回: 接受度（无量纲）
    """
    # 简化模型：小角度近似
    omega = min(area1_cm2, area2_cm2) / distance_cm**2
    return omega / (4 * np.pi)
```

---

## 常用物理常数

```python
# 光速
c = 299792458  # m/s

# 铅的性质
Pb_Z = 82
Pb_A = 207.2
Pb_density = 11.34  # g/cm³
Pb_X0 = 5.6  # mm
Pb_lambda_int = 176  # mm

# 宇宙射线
cosmic_flux_sea_level = 1.0  # cm⁻²min⁻¹sr⁻¹
muon_mass = 105.7  # MeV/c²
muon_lifetime = 2.2e-6  # s

# 探测器
sampling_rate = 5.0  # GHz
sampling_interval = 0.2  # ns
waveform_length = 1024  # samples
```

---

## 参考资料
1. **粒子探测器**: Leo, W.R. *Techniques for Nuclear and Particle Physics Experiments*
2. **误差分析**: Bevington, P.R. *Data Reduction and Error Analysis*
3. **宇宙射线**: Grieder, P.K.F. *Cosmic Rays at Earth*
4. **ROOT文档**: https://root.cern.ch/doc/master/

---

## 常见问题

**Q: 如何估算测量时间？**
A: 基于预期计数率和目标统计精度，使用N = (σ_target/σ_stat)² × N_current

**Q: 探测器间距如何选择？**
A: 平衡时间分辨率和几何接受度，通常10-100 cm

**Q: 如何提高测量精度？**
A: 增加统计量、改进时间分辨率、精确测量距离、降低系统误差

**Q: 工具脚本可以修改吗？**
A: 可以，建议保留原版本并创建新版本（如_v2）
