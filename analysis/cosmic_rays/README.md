# 宇宙射线分析 (Cosmic Ray Analysis)

本目录包含宇宙射线速度和时间特性分析脚本。

## 脚本说明

### `analyze_cosmic_rays.py`
**功能**: 分析宇宙射线事件的基本统计信息

**用法**:
```bash
python analyze_cosmic_rays.py <root_file> [area_threshold] [area2_threshold]
```
**参数**:
- `root_file`: ROOT数据文件路径
- `area_threshold`: 上探测器阈值（默认: 30）
- `area2_threshold`: 下探测器阈值（默认: 30）

**输出**:
- 上下探测器触发事件统计
- 符合事件数量和比例
- area和area2分布统计（最小值、最大值、均值、标准差）
- 符合效率（相对于上探测器）

**示例**:
```bash
python analyze_cosmic_rays.py ../../data/raw/5181.root 30 30
```

---

### `calculate_velocity.py`
**功能**: 从探测器时间差计算宇宙射线速度

**用法**:
```bash
python calculate_velocity.py <root_file> <distance_cm> [sampling_rate_GHz] [area_threshold] [area2_threshold]
```

**参数**:
- `root_file`: ROOT数据文件路径
- `distance_cm`: 上下探测器间距（厘米）
- `sampling_rate_GHz`: 采样率（默认: 5.0 GHz，对应DT5742）
- `area_threshold`: 上探测器阈值（默认: 30）
- `area2_threshold`: 下探测器阈值（默认: 30）

**物理原理**:
- 时间差 = (Index_minamp2 - Index_minamp1) × 采样间隔
- 速度 = 距离 / 时间差
- 结果以光速c的分数表示（期望值 ~0.99c）

**输出**:
- 符合事件统计
- 时间差分布（采样点数和纳秒）
- 速度分布（m/s和c的分数）
- 双面板图表：
  - 左图: 时间差直方图
  - 右图: 速度分布（以c为单位）

**示例**:
```bash
# 探测器间距50cm
python calculate_velocity.py ../../data/raw/5181.root 50.0

# 自定义参数
python calculate_velocity.py ../../data/raw/5181.root 50.0 5.0 30 30
```

**注意事项**:
- 采样率5 GHz对应采样间隔0.2 ns
- 自动过滤不合理的速度值（负值或>1.5c）
- 宇宙射线μ子的典型速度约为0.99c

---

### `check_time_diff.py`
**功能**: 检查和诊断探测器之间的时间差分布

**用法**:
```bash
python check_time_diff.py <root_file> [area_threshold] [area2_threshold]
```

**输出**:
- Index_minamp1和Index_minamp2的分布
- 时间差统计
- 异常值检测
- 时间差直方图

**应用场景**:
- 验证时间测量系统是否正常工作
- 检测时间偏移或系统误差
- 评估时间分辨率

---

## 相关输出

生成的图表保存在 `../../results/plots/velocity/` 目录：
- `5181b_velocity.png` - 速度分布分析
- `time_diff_analysis.png` - 时间差分析

---

## 物理背景

### 宇宙射线μ子
- 宇宙射线在大气层中产生的次级粒子
- 主要成分是μ子（muon）
- 能量范围: 几百MeV到几GeV
- 速度接近光速（β ≈ 0.99）

### 时间测量
- 使用闪烁体探测器的脉冲到达时间
- Index_minamp1/2记录波形最小值位置
- 采样率5 GHz提供0.2 ns时间分辨率
- 典型时间差: 1-3 ns（对应16-50 cm间距）

### 符合测量
- 要求上下探测器同时触发
- 符合窗口由数据采集系统定义
- 符合事件对应穿过两个探测器的同一粒子

---

## 数据质量检查

运行分析前建议检查：
1. **符合率**: 应在合理范围（通常>50%）
2. **时间差**: 应为正值且集中分布
3. **速度**: 应接近0.99c，分布宽度反映测量精度
4. **异常值**: 检查是否有大量不合理的速度值

---

## 常见问题

**Q: 为什么计算出的速度不是0.99c？**
A: 可能原因：
- 探测器间距测量不准确
- 采样率设置错误
- Index_minamp1/2记录的不是真实到达时间
- 存在电缆延迟或系统偏移

**Q: 为什么有些事件速度>c？**
A: 可能原因：
- 时间差测量误差
- 噪声触发导致的假符合
- 不同粒子触发上下探测器
- 这些事件会被自动过滤

**Q: 如何提高测量精度？**
A: 建议：
- 增加探测器间距（提高时间差）
- 提高阈值减少噪声
- 使用更精确的时间标记方法
- 校准系统延迟
