# CLAUDE.md - 数据分析专用模板

## 项目概述
本项目用于数据分析、机器学习和可视化任务。

## 技术栈

### 核心工具
- **数据处理**: pandas, polars, numpy
- **可视化**: matplotlib, seaborn, plotly
- **机器学习**: scikit-learn, xgboost, lightgbm
- **深度学习**: PyTorch, TensorFlow
- **统计分析**: scipy, statsmodels
- **Notebook**: Jupyter, JupyterLab

### 数据库
- **SQL**: PostgreSQL, MySQL, SQLite
- **大数据**: Spark, Dask
- **云平台**: BigQuery, Snowflake, Databricks

## 项目结构

```
data-analysis-project/
├── data/
│   ├── raw/              # 原始数据
│   ├── processed/        # 处理后数据
│   └── external/         # 外部数据
├── notebooks/
│   ├── 01_exploration/   # 探索性分析
│   ├── 02_preprocessing/ # 数据预处理
│   ├── 03_modeling/      # 建模
│   └── 04_evaluation/    # 评估
├── src/
│   ├── data/             # 数据加载和处理
│   ├── features/         # 特征工程
│   ├── models/           # 模型定义
│   └── visualization/    # 可视化工具
├── reports/
│   ├── figures/          # 图表输出
│   └── results/          # 分析结果
└── config/
    └── config.yaml       # 配置文件
```

## 核心命令

```bash
# 环境管理
conda activate analysis          # 激活环境
pip install -r requirements.txt  # 安装依赖

# Jupyter
jupyter lab                      # 启动 JupyterLab
jupyter nbconvert --to html      # 导出 HTML

# 数据处理
python src/data/download.py      # 下载数据
python src/data/preprocess.py    # 预处理

# 模型训练
python src/models/train.py       # 训练模型
python src/models/evaluate.py    # 评估模型

# 测试
pytest tests/                    # 运行测试
```

## 数据分析工作流

### 1. 数据加载与探索

```python
import pandas as pd
import numpy as np

# 加载数据
df = pd.read_csv('data/raw/dataset.csv')

# 基础探索
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"Data types:\n{df.dtypes}")
print(f"Missing values:\n{df.isnull().sum()}")
print(f"Summary statistics:\n{df.describe()}")
```

### 2. 数据清洗

```python
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """数据清洗流程"""
    df = df.copy()

    # 处理缺失值
    df = df.dropna(subset=['important_column'])
    df['numeric_col'] = df['numeric_col'].fillna(df['numeric_col'].median())
    df['categorical_col'] = df['categorical_col'].fillna('Unknown')

    # 处理异常值
    q1 = df['value'].quantile(0.25)
    q3 = df['value'].quantile(0.75)
    iqr = q3 - q1
    df = df[(df['value'] >= q1 - 1.5*iqr) & (df['value'] <= q3 + 1.5*iqr)]

    # 类型转换
    df['date'] = pd.to_datetime(df['date'])
    df['category'] = df['category'].astype('category')

    return df
```

### 3. 特征工程

```python
def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """特征工程"""
    df = df.copy()

    # 时间特征
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['dayofweek'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)

    # 聚合特征
    df['user_total'] = df.groupby('user_id')['value'].transform('sum')
    df['user_mean'] = df.groupby('user_id')['value'].transform('mean')

    # 交叉特征
    df['feature_ratio'] = df['feature_a'] / (df['feature_b'] + 1e-8)

    # 编码
    df = pd.get_dummies(df, columns=['category'], prefix='cat')

    return df
```

### 4. 可视化模板

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 设置样式
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def plot_distribution(df, column, title=None):
    """绘制分布图"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # 直方图
    axes[0].hist(df[column], bins=30, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel(column)
    axes[0].set_ylabel('Frequency')
    axes[0].set_title(f'Distribution of {column}')

    # 箱线图
    axes[1].boxplot(df[column])
    axes[1].set_ylabel(column)
    axes[1].set_title(f'Boxplot of {column}')

    plt.tight_layout()
    return fig

def plot_correlation_matrix(df, figsize=(10, 8)):
    """绘制相关性热力图"""
    corr = df.select_dtypes(include=[np.number]).corr()

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0,
                fmt='.2f', ax=ax, square=True)
    ax.set_title('Correlation Matrix')
    return fig

def plot_time_series(df, date_col, value_col, title=None):
    """绘制时间序列图"""
    fig, ax = plt.subplots(figsize=(14, 5))

    ax.plot(df[date_col], df[value_col], linewidth=1)
    ax.set_xlabel('Date')
    ax.set_ylabel(value_col)
    ax.set_title(title or f'{value_col} over Time')

    # 添加趋势线
    z = np.polyfit(range(len(df)), df[value_col], 1)
    p = np.poly1d(z)
    ax.plot(df[date_col], p(range(len(df))), "r--", alpha=0.8, label='Trend')
    ax.legend()

    return fig
```

### 5. 建模流程

```python
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score, mean_absolute_error
)

def build_classification_model(X, y, model, test_size=0.2):
    """分类模型构建流程"""
    # 划分数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    # 构建管道
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ])

    # 训练
    pipeline.fit(X_train, y_train)

    # 评估
    y_pred = pipeline.predict(X_test)
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1': f1_score(y_test, y_pred, average='weighted')
    }

    # 交叉验证
    cv_scores = cross_val_score(pipeline, X, y, cv=5)
    metrics['cv_mean'] = cv_scores.mean()
    metrics['cv_std'] = cv_scores.std()

    return pipeline, metrics

def build_regression_model(X, y, model, test_size=0.2):
    """回归模型构建流程"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    metrics = {
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'mae': mean_absolute_error(y_test, y_pred),
        'r2': r2_score(y_test, y_pred)
    }

    return pipeline, metrics
```

## SQL 查询模板

### 数据探索
```sql
-- 表结构
DESCRIBE table_name;

-- 基础统计
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT user_id) as unique_users,
    MIN(created_at) as earliest,
    MAX(created_at) as latest
FROM table_name;

-- 缺失值检查
SELECT
    SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END) as null_count,
    COUNT(*) as total_count,
    ROUND(100.0 * SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as null_pct
FROM table_name;
```

### 聚合分析
```sql
-- 分组统计
SELECT
    category,
    COUNT(*) as count,
    AVG(value) as avg_value,
    SUM(value) as total_value,
    MIN(value) as min_value,
    MAX(value) as max_value
FROM table_name
GROUP BY category
ORDER BY count DESC;

-- 时间序列聚合
SELECT
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as count,
    SUM(amount) as total_amount
FROM transactions
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month;

-- 窗口函数
SELECT
    user_id,
    order_date,
    amount,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date) as cumulative_amount,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date) as order_num,
    LAG(amount) OVER (PARTITION BY user_id ORDER BY order_date) as prev_amount
FROM orders;
```

## 统计分析

### 假设检验
```python
from scipy import stats

# t 检验
t_stat, p_value = stats.ttest_ind(group_a, group_b)

# 卡方检验
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

# A/B 测试
def ab_test(control, treatment, alpha=0.05):
    """A/B 测试分析"""
    t_stat, p_value = stats.ttest_ind(control, treatment)

    result = {
        'control_mean': np.mean(control),
        'treatment_mean': np.mean(treatment),
        'lift': (np.mean(treatment) - np.mean(control)) / np.mean(control) * 100,
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < alpha
    }
    return result
```

## 报告模板

```markdown
# 数据分析报告

## 1. 执行摘要
- 分析目标:
- 主要发现:
- 建议行动:

## 2. 数据概述
- 数据来源:
- 时间范围:
- 样本量:
- 关键指标:

## 3. 分析方法
- 使用的技术:
- 模型选择理由:

## 4. 关键发现
### 发现 1
- 描述:
- 支持数据:
- 影响:

## 5. 结论与建议
- 结论:
- 建议:
- 后续步骤:

## 附录
- 技术细节
- 完整代码
- 补充图表
```

## 自主决策授权

✅ 可自主执行:
- 数据探索和清洗
- 特征工程
- 可视化创建
- 模型训练和评估
- 编写分析报告

❌ 需要确认:
- 删除原始数据
- 修改生产数据库
- 发布分析结果
- 引入新的大型依赖
- 修改 ETL 管道

## 最佳实践

1. **数据版本控制**: 使用 DVC 跟踪数据变化
2. **可复现性**: 固定随机种子, 记录环境
3. **文档化**: 详细记录分析过程和假设
4. **代码质量**: 使用函数封装, 避免重复代码
5. **可视化优先**: 用图表讲述数据故事
6. **迭代验证**: 持续验证分析结论
