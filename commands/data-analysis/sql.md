为分析需求生成 SQL 查询: $ARGUMENTS

## 查询生成流程

### 1. 需求理解
- 解析自然语言需求
- 识别目标表和列
- 确定过滤条件和聚合逻辑

### 2. Schema 分析
```sql
-- 查看表结构
DESCRIBE table_name;
SHOW TABLES;
```

### 3. 查询构建
根据需求类型生成:

**聚合查询:**
```sql
SELECT
    dimension_column,
    COUNT(*) as count,
    SUM(metric) as total,
    AVG(metric) as average
FROM table_name
WHERE conditions
GROUP BY dimension_column
ORDER BY count DESC;
```

**连接查询:**
```sql
SELECT
    t1.column1,
    t2.column2
FROM table1 t1
JOIN table2 t2 ON t1.id = t2.foreign_id
WHERE conditions;
```

**窗口函数:**
```sql
SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY date) as row_num,
    SUM(amount) OVER (PARTITION BY category ORDER BY date ROWS UNBOUNDED PRECEDING) as cumsum
FROM table_name;
```

### 4. 查询优化
- 使用索引列进行过滤
- 避免 SELECT *
- 合理使用 LIMIT
- 考虑查询计划 (EXPLAIN)

## 输出格式

### 生成的查询
```sql
[SQL 查询]
```

### 查询说明
- 目的: [查询目的]
- 使用的表: [表列表]
- 关键逻辑: [逻辑说明]

### 性能考虑
- 预估数据量
- 建议的索引
- 潜在优化点

### 验证建议
- 如何验证结果正确性
- 边界情况测试
