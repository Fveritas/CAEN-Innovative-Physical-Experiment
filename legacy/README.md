# 旧版本文件 (Legacy Files)

本目录存放已被替代或不再使用的旧版本文件。

## 文件列表

### `5181b.root`
**说明**: 早期版本的0片铅板测量数据

**与5181.root的区别**:
- 可能是不同的测量时间
- 可能使用不同的数据采集设置
- 文件大小: ~165 MB

**状态**: 已被`data/raw/5181.root`替代

**保留原因**: 
- 历史记录
- 对比验证
- 备份数据

**是否可删除**: 如果确认5181.root数据质量更好，可以删除

---

### `Get_AllValue_Measure_new.C`
**说明**: ROOT宏的新版本（实际上可能是旧版本）

**功能**: 从原始波形提取测量参数
- area, area2
- Index_minamp1, Index_minamp2
- minamp1, minamp2

**与data/processing/Get_AllValue_Measure.C的关系**:
- 可能是早期开发版本
- 或者是实验性修改版本
- 功能基本相同

**状态**: 已被`data/processing/Get_AllValue_Measure.C`替代

**保留原因**:
- 可能包含不同的处理逻辑
- 用于对比验证
- 历史参考

**是否可删除**: 如果确认当前版本功能完整，可以删除

---

## 使用建议

### 何时查看Legacy文件
1. **对比验证**: 当前分析结果异常时
2. **历史追溯**: 了解分析方法演化
3. **数据恢复**: 当前数据损坏时的备份

### 何时可以删除
1. 确认当前版本数据/代码质量更好
2. 已经完成对比验证
3. 有其他备份途径
4. 磁盘空间紧张

### 最佳实践
- 定期清理不需要的旧文件
- 保留重要的历史版本
- 使用版本控制系统（Git）管理代码
- 数据文件做好备份和文档记录

---

## 文件对比

### 5181b.root vs 5181.root

**建议对比项**:
```python
import uproot

# 读取两个文件
with uproot.open('5181b.root') as f1, uproot.open('../data/raw/5181.root') as f2:
    tree1 = f1['t1']
    tree2 = f2['t1']
    
    # 对比条目数
    print(f"5181b entries: {tree1.num_entries}")
    print(f"5181 entries: {tree2.num_entries}")
    
    # 对比数据分布
    area1 = tree1['area'].array(library='np')
    area2 = tree2['area'].array(library='np')
    
    print(f"5181b area mean: {area1.mean():.2f}")
    print(f"5181 area mean: {area2.mean():.2f}")
```

**判断标准**:
- 条目数更多 → 测量时间更长 → 统计更好
- 分布更清晰 → 数据质量更好
- 符合率更高 → 系统工作更稳定

---

### Get_AllValue_Measure_new.C vs Get_AllValue_Measure.C

**建议对比**:
```bash
# 使用diff工具
diff Get_AllValue_Measure_new.C ../data/processing/Get_AllValue_Measure.C

# 或使用更友好的对比工具
meld Get_AllValue_Measure_new.C ../data/processing/Get_AllValue_Measure.C
```

**关注点**:
- 波形处理算法差异
- 阈值和参数设置
- 输出变量定义
- 注释和文档

---

## 版本历史记录

### 数据文件演化
```
初始版本 → 5181b.root (早期测量)
       ↓
当前版本 → 5181.root (改进后的测量)
```

### 代码演化
```
初始版本 → Get_AllValue_Measure.C (基础功能)
         ↓
实验版本 → Get_AllValue_Measure_new.C (尝试改进)
         ↓
当前版本 → Get_AllValue_Measure.C (稳定版本)
```

---

## 清理建议

### 安全删除流程
1. **备份**: 确保有其他备份
2. **验证**: 确认当前版本功能完整
3. **记录**: 在文档中记录删除原因
4. **删除**: 移除文件

### 保留建议
如果满足以下条件，建议保留：
- 文件大小不大（<100 MB）
- 可能用于对比验证
- 包含独特的历史信息
- 磁盘空间充足

---

## 常见问题

**Q: Legacy文件会影响分析吗？**
A: 不会，分析脚本使用data/raw/中的文件。

**Q: 如何知道哪个版本更好？**
A: 对比数据质量指标（符合率、分辨率、统计量）。

**Q: 可以恢复使用Legacy文件吗？**
A: 可以，修改分析脚本中的文件路径即可。

**Q: 为什么不直接删除？**
A: 保留一段时间以防需要回溯或对比。
