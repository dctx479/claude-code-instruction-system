对数据文件 $ARGUMENTS 进行探索性数据分析 (EDA)。

## 分析流程

### 1. 数据加载
```python
import pandas as pd
import numpy as np

# 根据文件类型加载
df = pd.read_csv('$ARGUMENTS')  # 或 read_excel, read_json 等
```

### 2. 基础信息
```python
# 数据形状
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# 数据类型
print(df.dtypes)

# 前几行
print(df.head())
```

### 3. 数据质量
```python
# 缺失值
print(df.isnull().sum())

# 重复值
print(f"Duplicates: {df.duplicated().sum()}")

# 唯一值
print(df.nunique())
```

### 4. 统计摘要
```python
# 数值列
print(df.describe())

# 分类列
print(df.describe(include=['object']))
```

### 5. 可视化
- 分布图 (直方图、核密度图)
- 相关性热力图
- 分类变量计数图
- 时间序列图 (如适用)

## 输出报告

### 数据概览
| 属性 | 值 |
|------|-----|
| 行数 | |
| 列数 | |
| 文件大小 | |
| 时间范围 | |

### 列信息
| 列名 | 类型 | 非空数 | 唯一值 | 示例 |
|------|------|--------|--------|------|

### 数据质量问题
- 缺失值情况
- 异常值检测
- 数据一致性问题

### 关键发现
- [发现 1]
- [发现 2]

### 建议的后续分析
- [建议 1]
- [建议 2]
