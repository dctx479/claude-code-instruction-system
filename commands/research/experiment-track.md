# /experiment-track - 实验追踪

## 功能描述
结构化记录实验配置、结果和分析，支持实验复现。

## 使用方法
```bash
/experiment-track <操作> [参数]
```

## 操作

### 1. 创建实验
```bash
/experiment-track create --name "实验名称" --description "实验描述"
```

### 2. 记录配置
```bash
/experiment-track config --exp-id <ID> --file config.yaml
```

### 3. 记录结果
```bash
/experiment-track result --exp-id <ID> --metrics metrics.json
```

### 4. 生成报告
```bash
/experiment-track report --exp-id <ID> --output report.md
```

### 5. 对比实验
```bash
/experiment-track compare --exp-ids <ID1,ID2,ID3>
```

## 实验记录结构
```
.research/experiments/
├── exp-001/
│   ├── metadata.json       # 实验元信息
│   ├── config.yaml         # 实验配置
│   ├── code/               # 代码快照
│   ├── data/               # 数据信息
│   ├── results/            # 结果文件
│   │   ├── metrics.json
│   │   ├── figures/
│   │   └── logs/
│   ├── analysis.md         # 分析报告
│   └── reproduction.md     # 复现指南
```

## 自动记录
- Git commit hash
- 环境依赖（requirements.txt）
- 随机种子
- 硬件信息
- 执行时间

## 集成
- Jupyter Notebook: 自动保存 notebook
- TensorBoard: 链接训练日志
- MLflow: 可选集成
