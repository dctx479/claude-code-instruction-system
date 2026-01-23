---
name: data-analysis
description: 通用数据分析技能，包括统计分析、数据可视化和洞察提取
version: 1.0.0
license: MIT
metadata:
  category: data-analysis
  tags: [data-analysis, statistics, visualization, insights]
  python_packages: [pandas, numpy, matplotlib, seaborn, scipy]
---

# 数据分析 Skill

## 何时使用此 Skill

当用户请求以下任务时自动激活：
- 探索性数据分析（EDA）
- 统计分析和假设检验
- 数据可视化
- 相关性分析
- 异常值检测
- 数据洞察提取

## 核心能力

### 1. 探索性数据分析（EDA）

完整的 EDA 流程：
- 数据概览和统计摘要
- 分布分析
- 相关性分析
- 缺失值和异常值检测
- 可视化探索

### 2. 统计分析

- **描述统计**: 均值、中位数、标准差、分位数
- **假设检验**: t检验、卡方检验、ANOVA
- **相关性分析**: Pearson、Spearman、Kendall
- **回归分析**: 线性回归、逻辑回归
- **时间序列分析**: 趋势、季节性、自相关

### 3. 数据可视化

- **分布图**: 直方图、密度图、箱线图
- **关系图**: 散点图、相关性热力图
- **趋势图**: 折线图、面积图
- **分类图**: 柱状图、饼图
- **高级图表**: 小提琴图、配对图、联合图

## 使用指南

### 完整 EDA 示例

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# 设置样式
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文支持

# 1. 加载数据
df = pd.read_csv('data.csv')

# 2. 数据概览
print("=" * 50)
print("数据概览")
print("=" * 50)
print(f"数据形状: {df.shape}")
print(f"\n前5行:\n{df.head()}")
print(f"\n数据类型:\n{df.dtypes}")
print(f"\n缺失值:\n{df.isnull().sum()}")

# 3. 描述统计
print("\n" + "=" * 50)
print("描述统计")
print("=" * 50)
print(df.describe())

# 数值列的详细统计
for col in df.select_dtypes(include=[np.number]).columns:
    print(f"\n{col}:")
    print(f"  均值: {df[col].mean():.2f}")
    print(f"  中位数: {df[col].median():.2f}")
    print(f"  标准差: {df[col].std():.2f}")
    print(f"  偏度: {df[col].skew():.2f}")
    print(f"  峰度: {df[col].kurtosis():.2f}")

# 4. 分布分析
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 直方图
df['value'].hist(bins=30, ax=axes[0, 0])
axes[0, 0].set_title('直方图')

# 密度图
df['value'].plot(kind='density', ax=axes[0, 1])
axes[0, 1].set_title('密度图')

# 箱线图
df.boxplot(column='value', by='category', ax=axes[1, 0])
axes[1, 0].set_title('箱线图')

# Q-Q图（正态性检验）
stats.probplot(df['value'], dist="norm", plot=axes[1, 1])
axes[1, 1].set_title('Q-Q图')

plt.tight_layout()
plt.savefig('distribution_analysis.png', dpi=300, bbox_inches='tight')

# 5. 相关性分析
numeric_cols = df.select_dtypes(include=[np.number]).columns
correlation_matrix = df[numeric_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8})
plt.title('相关性热力图')
plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')

# 6. 异常值检测
def detect_outliers_iqr(data):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return (data < lower_bound) | (data > upper_bound)

outliers = {}
for col in numeric_cols:
    outliers[col] = detect_outliers_iqr(df[col]).sum()

print("\n" + "=" * 50)
print("异常值检测（IQR方法）")
print("=" * 50)
for col, count in outliers.items():
    print(f"{col}: {count} 个异常值 ({count/len(df)*100:.2f}%)")

# 7. 分组分析
print("\n" + "=" * 50)
print("分组分析")
print("=" * 50)
group_stats = df.groupby('category').agg({
    'value': ['count', 'mean', 'median', 'std', 'min', 'max']
}).round(2)
print(group_stats)

# 8. 生成报告
report = f"""
数据分析报告
{'=' * 50}

1. 数据概况
   - 总行数: {len(df)}
   - 总列数: {len(df.columns)}
   - 缺失值总数: {df.isnull().sum().sum()}

2. 数值特征统计
{df.describe().to_string()}

3. 相关性分析
   - 最强正相关: {correlation_matrix.unstack().sort_values(ascending=False).drop_duplicates().iloc[1]}
   - 最强负相关: {correlation_matrix.unstack().sort_values().drop_duplicates().iloc[0]}

4. 异常值
   - 检测到 {sum(outliers.values())} 个异常值

5. 建议
   - 处理缺失值
   - 处理异常值
   - 特征工程
"""

with open('analysis_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print("\n✅ 分析完成！")
print("   - 分布分析图: distribution_analysis.png")
print("   - 相关性热力图: correlation_heatmap.png")
print("   - 分析报告: analysis_report.txt")
```

### 假设检验示例

```python
from scipy import stats

# t检验（两组均值比较）
group1 = df[df['category'] == 'A']['value']
group2 = df[df['category'] == 'B']['value']
t_stat, p_value = stats.ttest_ind(group1, group2)
print(f"t检验: t={t_stat:.4f}, p={p_value:.4f}")

# 卡方检验（分类变量独立性）
contingency_table = pd.crosstab(df['cat1'], df['cat2'])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
print(f"卡方检验: χ²={chi2:.4f}, p={p_value:.4f}")

# ANOVA（多组均值比较）
groups = [df[df['category'] == cat]['value'] for cat in df['category'].unique()]
f_stat, p_value = stats.f_oneway(*groups)
print(f"ANOVA: F={f_stat:.4f}, p={p_value:.4f}")

# 正态性检验
stat, p_value = stats.shapiro(df['value'])
print(f"Shapiro-Wilk检验: W={stat:.4f}, p={p_value:.4f}")
```

### 高级可视化

```python
import seaborn as sns

# 配对图（多变量关系）
sns.pairplot(df, hue='category', diag_kind='kde')
plt.savefig('pairplot.png', dpi=300, bbox_inches='tight')

# 小提琴图（分布 + 箱线图）
plt.figure(figsize=(12, 6))
sns.violinplot(data=df, x='category', y='value', hue='group')
plt.title('小提琴图')
plt.savefig('violinplot.png', dpi=300, bbox_inches='tight')

# 联合图（散点图 + 边际分布）
sns.jointplot(data=df, x='feature1', y='feature2', kind='reg')
plt.savefig('jointplot.png', dpi=300, bbox_inches='tight')

# 热力图（数据矩阵）
pivot_table = df.pivot_table(values='value', index='row', columns='col')
sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='YlOrRd')
plt.savefig('heatmap.png', dpi=300, bbox_inches='tight')
```

## 最佳实践

### 1. 数据质量检查

```python
def data_quality_report(df):
    """生成数据质量报告"""
    report = {
        '总行数': len(df),
        '总列数': len(df.columns),
        '缺失值': df.isnull().sum().sum(),
        '重复行': df.duplicated().sum(),
        '数值列': len(df.select_dtypes(include=[np.number]).columns),
        '分类列': len(df.select_dtypes(include=['object', 'category']).columns),
    }
    return pd.Series(report)
```

### 2. 自动化 EDA

```python
def auto_eda(df, target=None):
    """自动化探索性数据分析"""
    # 1. 数据概览
    print("数据概览:")
    print(df.info())

    # 2. 数值特征分析
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print("\n数值特征统计:")
        print(df[numeric_cols].describe())

        # 可视化
        df[numeric_cols].hist(bins=30, figsize=(15, 10))
        plt.tight_layout()
        plt.savefig('numeric_distributions.png')

    # 3. 分类特征分析
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(cat_cols) > 0:
        print("\n分类特征:")
        for col in cat_cols:
            print(f"\n{col}:")
            print(df[col].value_counts())

    # 4. 相关性分析
    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 8))
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm')
        plt.savefig('correlation.png')

    # 5. 目标变量分析
    if target and target in df.columns:
        print(f"\n目标变量 {target} 分析:")
        print(df[target].describe())

        # 特征与目标的关系
        for col in numeric_cols:
            if col != target:
                plt.figure(figsize=(10, 6))
                plt.scatter(df[col], df[target], alpha=0.5)
                plt.xlabel(col)
                plt.ylabel(target)
                plt.title(f'{col} vs {target}')
                plt.savefig(f'{col}_vs_{target}.png')
```

### 3. 结果解释

```python
def interpret_correlation(corr_value):
    """解释相关系数"""
    abs_corr = abs(corr_value)
    if abs_corr < 0.3:
        strength = "弱"
    elif abs_corr < 0.7:
        strength = "中等"
    else:
        strength = "强"

    direction = "正" if corr_value > 0 else "负"
    return f"{direction}相关，强度：{strength} (r={corr_value:.3f})"

def interpret_p_value(p_value, alpha=0.05):
    """解释p值"""
    if p_value < alpha:
        return f"显著 (p={p_value:.4f} < {alpha})"
    else:
        return f"不显著 (p={p_value:.4f} >= {alpha})"
```

## 参考资源

- **pandas**: https://pandas.pydata.org/
- **numpy**: https://numpy.org/
- **matplotlib**: https://matplotlib.org/
- **seaborn**: https://seaborn.pydata.org/
- **scipy**: https://scipy.org/

---

**注意**: 使用此 Skill 前请确保已安装依赖：
```bash
pip install pandas numpy matplotlib seaborn scipy
```
