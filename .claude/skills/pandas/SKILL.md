---
name: pandas
description: pandas 数据分析库，用于数据处理、清洗和分析
version: 1.0.0
license: MIT
metadata:
  category: data-analysis
  tags: [pandas, data-analysis, dataframe, data-processing]
  python_package: pandas
---

# pandas Skill

## 何时使用此 Skill

当用户请求以下任务时自动激活：
- 读取和写入数据文件（CSV, Excel, JSON 等）
- 数据清洗和预处理
- 数据转换和重塑
- 数据分组和聚合
- 时间序列分析
- 数据可视化（配合 matplotlib）

## 核心能力

### 1. 数据读取和写入

支持多种数据格式：
- **CSV**: `pd.read_csv()`, `df.to_csv()`
- **Excel**: `pd.read_excel()`, `df.to_excel()`
- **JSON**: `pd.read_json()`, `df.to_json()`
- **SQL**: `pd.read_sql()`, `df.to_sql()`
- **Parquet**: `pd.read_parquet()`, `df.to_parquet()`

### 2. 数据探索

```python
import pandas as pd

# 读取数据
df = pd.read_csv('data.csv')

# 基本信息
df.head()          # 前 5 行
df.tail()          # 后 5 行
df.info()          # 数据类型和缺失值
df.describe()      # 统计摘要
df.shape           # 形状 (行数, 列数)
df.columns         # 列名
df.dtypes          # 数据类型
```

### 3. 数据清洗

```python
# 处理缺失值
df.isnull().sum()              # 统计缺失值
df.dropna()                    # 删除缺失值
df.fillna(value)               # 填充缺失值
df.fillna(df.mean())           # 用均值填充

# 处理重复值
df.duplicated().sum()          # 统计重复行
df.drop_duplicates()           # 删除重复行

# 数据类型转换
df['column'] = df['column'].astype('int')
df['date'] = pd.to_datetime(df['date'])
```

### 4. 数据选择和过滤

```python
# 选择列
df['column']                   # 单列
df[['col1', 'col2']]          # 多列

# 选择行
df.loc[0]                      # 按标签
df.iloc[0]                     # 按位置
df.loc[0:5, 'column']         # 行列组合

# 条件过滤
df[df['age'] > 30]            # 单条件
df[(df['age'] > 30) & (df['city'] == 'Beijing')]  # 多条件
df.query('age > 30 and city == "Beijing"')        # 查询语法
```

### 5. 数据转换

```python
# 添加新列
df['new_col'] = df['col1'] + df['col2']

# 应用函数
df['col'].apply(lambda x: x * 2)
df.apply(func, axis=1)         # 按行应用

# 重命名
df.rename(columns={'old': 'new'})

# 排序
df.sort_values('column')
df.sort_values(['col1', 'col2'], ascending=[True, False])
```

### 6. 分组和聚合

```python
# 分组聚合
df.groupby('category')['value'].sum()
df.groupby('category').agg({
    'value': ['sum', 'mean', 'count'],
    'price': 'max'
})

# 透视表
pd.pivot_table(df, values='value', index='row', columns='col', aggfunc='sum')

# 交叉表
pd.crosstab(df['row'], df['col'])
```

## 使用指南

### 完整示例：数据分析流程

```python
import pandas as pd
import numpy as np

# 1. 读取数据
df = pd.read_csv('sales_data.csv')

# 2. 数据探索
print(f"数据形状: {df.shape}")
print(f"\n数据类型:\n{df.dtypes}")
print(f"\n缺失值:\n{df.isnull().sum()}")
print(f"\n统计摘要:\n{df.describe()}")

# 3. 数据清洗
# 处理缺失值
df['price'].fillna(df['price'].median(), inplace=True)
df.dropna(subset=['customer_id'], inplace=True)

# 处理重复值
df.drop_duplicates(inplace=True)

# 数据类型转换
df['date'] = pd.to_datetime(df['date'])
df['quantity'] = df['quantity'].astype('int')

# 4. 特征工程
df['total'] = df['price'] * df['quantity']
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# 5. 数据分析
# 按类别统计
category_stats = df.groupby('category').agg({
    'total': ['sum', 'mean', 'count'],
    'quantity': 'sum'
}).round(2)

# 时间序列分析
monthly_sales = df.groupby(df['date'].dt.to_period('M'))['total'].sum()

# 6. 数据导出
df.to_csv('cleaned_data.csv', index=False)
category_stats.to_excel('category_report.xlsx')
```

### 时间序列分析

```python
# 设置日期索引
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# 重采样
df.resample('D').sum()         # 按天
df.resample('W').mean()        # 按周
df.resample('M').sum()         # 按月

# 滚动窗口
df['rolling_mean'] = df['value'].rolling(window=7).mean()
df['rolling_std'] = df['value'].rolling(window=7).std()

# 移动
df['prev_value'] = df['value'].shift(1)
df['next_value'] = df['value'].shift(-1)
```

### 数据合并

```python
# 合并（类似 SQL JOIN）
pd.merge(df1, df2, on='key')                    # 内连接
pd.merge(df1, df2, on='key', how='left')        # 左连接
pd.merge(df1, df2, on='key', how='outer')       # 外连接

# 拼接
pd.concat([df1, df2], axis=0)                   # 垂直拼接
pd.concat([df1, df2], axis=1)                   # 水平拼接
```

## 最佳实践

### 1. 性能优化

```python
# 使用合适的数据类型
df['category'] = df['category'].astype('category')  # 分类数据
df['id'] = df['id'].astype('int32')                 # 整数

# 分块读取大文件
chunks = pd.read_csv('large_file.csv', chunksize=10000)
for chunk in chunks:
    process(chunk)

# 使用 query 而非布尔索引（更快）
df.query('age > 30')  # 快
df[df['age'] > 30]    # 慢
```

### 2. 链式操作

```python
result = (df
    .query('age > 30')
    .groupby('city')['salary']
    .mean()
    .sort_values(ascending=False)
    .head(10)
)
```

### 3. 避免循环

```python
# ❌ 慢
for i in range(len(df)):
    df.loc[i, 'new_col'] = df.loc[i, 'col1'] * 2

# ✅ 快
df['new_col'] = df['col1'] * 2
```

## 常见问题

### SettingWithCopyWarning

**原因**: 在 DataFrame 的副本上修改数据

**解决方案**:
```python
# 使用 .loc
df.loc[df['age'] > 30, 'category'] = 'senior'

# 或显式复制
df_copy = df[df['age'] > 30].copy()
```

### 内存不足

**解决方案**:
```python
# 1. 优化数据类型
df = df.astype({
    'int_col': 'int32',
    'float_col': 'float32',
    'cat_col': 'category'
})

# 2. 分块处理
for chunk in pd.read_csv('file.csv', chunksize=10000):
    process(chunk)

# 3. 使用 Dask（大数据）
import dask.dataframe as dd
ddf = dd.read_csv('large_file.csv')
```

## 参考资源

- **官方文档**: https://pandas.pydata.org/docs/
- **用户指南**: https://pandas.pydata.org/docs/user_guide/
- **API 参考**: https://pandas.pydata.org/docs/reference/
- **教程**: https://pandas.pydata.org/docs/getting_started/tutorials.html

---

**注意**: 使用此 Skill 前请确保已安装 pandas：
```bash
pip install pandas
```
