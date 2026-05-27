# 数据处理 (Data Processing)

本目录包含ROOT数据文件读取和初步诊断的脚本。

## 脚本说明

### `read_data.py`
**功能**: 基础ROOT文件读取工具

**用法**:
```bash
python read_data.py <root_file>
```

**输出**:
- 文件基本信息
- Tree结构
- Branch列表
- 数据条目数

**示例**:
```bash
python read_data.py ../raw/5181.root
```

---

### `diagnostic_lower.py`
**功能**: 下探测器（lower detector）数据诊断

**分析内容**:
- area2分布
- Index_minamp2分布
- 触发率统计
- 异常值检测

**输出**:
- 统计信息打印
- `diagnostic_lower_detector.png`

---

### `diagnostic_lower_v2.py`
**功能**: 改进版下探测器诊断

**新增功能**:
- 时间演化分析
- 触发效率监控
- 与上探测器对比

**输出**:
- `diagnostic_lower_v2.png`
---

### `diagnostic_v3.py`
**功能**: 综合诊断工具（v3）

**分析内容**:
- 上下探测器对比
- 符合事件分析
- 时间关联检查
- 波形质量评估

**输出**:
- `diagnostic_v3.png`

---

### `diagnostic_v4.py` ⭐ **最新版本**
**功能**: 2D诊断分析

**特点**:
- area vs area2 二维分布
- 符合区域可视化
- 阈值优化建议
- 背景噪声识别

**输出**:
- `diagnostic_v4_2d.png` - 2D散点图

**用法**:
```bash
python diagnostic_v4.py
```

---

### `Get_AllValue_Measure.C`
**功能**: ROOT宏，用于从原始波形提取测量值

**提取参数**:
- `area`: 上探测器脉冲积分
- `area2`: 下探测器脉冲积分
- `Index_minamp1`: 上探测器最小值位置
- `Index_minamp2`: 下探测器最小值位置
- `minamp1`: 上探测器最小幅度
- `minamp2`: 下探测器最小幅度

**用法**（在ROOT中）:
```cpp
root [0] .L Get_AllValue_Measure.C
root [1] Get_AllValue_Measure("input.root", "output.root")
```

---

## 数据结构

### ROOT Tree: `t1`

**Branches**:
| Branch | 类型 | 说明 |
|--------|------|------|
| `area` | Float | 上探测器脉冲积分（能量） |
| `area2` | Float | 下探测器脉冲积分（能量） |
| `Index_minamp1` | Int | 上探测器波形最小值位置（时间） |
| `Index_minamp2` | Int | 下探测器波形最小值位置（时间） |
| `minamp1` | Float | 上探测器最小幅度 |
| `minamp2` | Float | 下探测器最小幅度 |
**单位**:
- `area/area2`: 任意单位（ADC积分）
- `Index_minamp`: 采样点数（5 GHz采样率，0.2 ns/点）
- `minamp`: ADC值

---

## 诊断图表说明

### `diagnostic_lower_detector.png`
- 下探测器area2分布
- Index_minamp2分布
- 触发率时间演化

### `diagnostic_lower_v2.png`
- 多面板诊断
- 上下探测器对比
- 效率监控

### `diagnostic_v3.png`
- 综合诊断视图
- 符合事件特征
- 时间关联分析

### `diagnostic_v4_2d.png` ⭐
**2D散点图**: area vs area2
- **横轴**: area（上探测器）
- **纵轴**: area2（下探测器）
- **颜色**: 事件密度
- **区域划分**:
  - 左下角: 双低（噪声）
  - 右下角: 上高下低（单上触发）
  - 左上角: 上低下高（单下触发）
  - 右上角: 双高（符合事件）

**应用**:
- 优化阈值设置
- 识别噪声区域
- 评估符合纯度

---

## 数据质量检查

### 基本检查
1. **条目数**: 应在合理范围（几万到几十万）
2. **area分布**: 应有明显的信号峰
3. **Index范围**: 应在0-1024之间（波形长度）
4. **符合率**: 通常>50%

### 异常情况
- **area全为0**: 探测器未触发或阈值过高
- **Index集中在边界**: 触发时间设置问题
- **符合率过低**: 探测器未对准或阈值不匹配
- **area2系统性偏低**: 下探测器效率问题

---

## 阈值优化

### 方法1: 2D分布法
1. 绘制area vs area2散点图
2. 观察信号和噪声区域
3. 选择阈值使信号/噪声最大化

### 方法2: 符合率法
1. 扫描不同阈值组合
2. 计算符合率和单触发率
3. 选择符合率>70%的阈值

### 方法3: 物理动机法
1. 基于最小电离粒子能量损失
2. 考虑探测器响应
3. 留有安全余量

**推荐阈值**: area > 30, area2 > 30

---

## 常见问题

**Q: 为什么需要多个诊断版本？**
A: 逐步改进，增加新功能和更好的可视化。

**Q: 如何选择使用哪个诊断脚本？**
A: 快速检查用v1，详细分析用v4。

**Q: 2D图中的条纹是什么？**
A: 可能是ADC量化效应或特定能量的粒子。

**Q: 如何判断数据质量好坏？**
A: 看符合率、area分布清晰度和时间关联性。
