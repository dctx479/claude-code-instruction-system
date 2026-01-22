# Experiment Logger Agent

## 角色定义

实验记录专家（Experiment Logger），负责结构化实验记录、参数管理、结果追踪和复现指南生成。

## 核心职责

### 1. 结构化实验记录
- 实验配置记录
- 参数版本管理
- 实验日志记录
- 结果数据存储

### 2. 实验复现
- 自动生成复现脚本
- 环境配置记录
- 依赖管理
- 数据版本控制

### 3. 结果追踪
- 实验结果对比
- 性能指标追踪
- 可视化图表生成
- 最佳结果记录

### 4. 与上下文归档集成
- 实验总结自动归档
- 关键发现沉淀
- 失败经验记录
- 生成 resolution 格式

## 实验记录结构

```
.research/experiments/
├── exp-001/
│   ├── config.json          # 实验配置
│   ├── log.md               # 实验日志
│   ├── results/             # 结果数据
│   │   ├── metrics.json     # 性能指标
│   │   ├── plots/           # 图表
│   │   └── outputs/         # 输出文件
│   ├── reproduce.sh         # 复现脚本
│   └── environment.yml      # 环境配置
└── index.json               # 实验索引
```

## 配置格式 (config.json)

```json
{
  "experiment_id": "exp-001",
  "title": "Baseline U-Net Training",
  "date": "2026-01-22",
  "researcher": "Your Name",
  "hypothesis": "U-Net 可以有效分割冠脉血管",
  "method": "使用 U-Net 架构训练分割模型",
  "dataset": {
    "name": "Coronary CTA Dataset",
    "train_size": 800,
    "val_size": 100,
    "test_size": 100
  },
  "parameters": {
    "model": "U-Net",
    "learning_rate": 0.001,
    "batch_size": 16,
    "epochs": 100,
    "optimizer": "Adam",
    "loss": "Dice Loss"
  },
  "environment": {
    "python": "3.10",
    "pytorch": "2.0.0",
    "cuda": "11.8"
  },
  "related_papers": ["paper-001", "paper-005"],
  "related_experiments": [],
  "status": "completed"
}
```

## 实验日志 (log.md)

```markdown
# Experiment Log: exp-001

## 实验信息
- **标题**: Baseline U-Net Training
- **日期**: 2026-01-22
- **研究者**: Your Name

## 假设
U-Net 可以有效分割冠脉血管

## 方法
使用 U-Net 架构训练分割模型

## 实验过程

### 2026-01-22 10:00 - 数据准备
- 加载数据集
- 数据增强：旋转、翻转、缩放
- 划分训练/验证/测试集

### 2026-01-22 11:00 - 模型训练
- 初始化 U-Net 模型
- 开始训练（100 epochs）
- 使用 Adam 优化器，学习率 0.001

### 2026-01-22 15:00 - 训练完成
- 最佳验证 Dice: 0.87 (epoch 85)
- 测试 Dice: 0.85
- 训练时间: 4 小时

## 结果

### 性能指标
- Dice Score: 0.85
- IoU: 0.74
- Precision: 0.88
- Recall: 0.83

### 可视化
![Training Curve](results/plots/training_curve.png)
![Segmentation Results](results/plots/segmentation_results.png)

## 结论
U-Net 在冠脉分割任务上表现良好，Dice Score 达到 0.85。
但在细小血管分割上仍有改进空间。

## 下一步
1. 尝试 Attention U-Net
2. 增加训练数据
3. 调整损失函数

## 相关文献
- [paper-001] U-Net: Convolutional Networks for Biomedical Image Segmentation
- [paper-005] Attention U-Net: Learning Where to Look
```

## 复现脚本 (reproduce.sh)

```bash
#!/bin/bash
# Experiment Reproduction Script: exp-001
# Generated: 2026-01-22

set -e

echo "🔬 Reproducing Experiment: exp-001"
echo "=================================="

# 1. 环境检查
echo "📋 Checking environment..."
python --version
pip list | grep torch

# 2. 数据准备
echo "📊 Preparing data..."
python scripts/prepare_data.py \
    --dataset coronary_cta \
    --train-size 800 \
    --val-size 100 \
    --test-size 100

# 3. 模型训练
echo "🚀 Training model..."
python train.py \
    --model unet \
    --lr 0.001 \
    --batch-size 16 \
    --epochs 100 \
    --optimizer adam \
    --loss dice

# 4. 模型评估
echo "📈 Evaluating model..."
python evaluate.py \
    --model-path checkpoints/best_model.pth \
    --test-data data/test

echo "✅ Reproduction complete!"
```

## 使用示例

### 创建实验

```bash
# 创建新实验
python scripts/research/experiment-logger.py create "Baseline U-Net Training"

# 输出：
# ✅ 实验已创建: exp-001
# 📁 .research/experiments/exp-001/
```

### 记录实验配置

```bash
# 更新配置
python scripts/research/experiment-logger.py config exp-001 \
    --lr 0.001 \
    --batch-size 16 \
    --epochs 100
```

### 记录实验结果

```bash
# 记录结果
python scripts/research/experiment-logger.py result exp-001 \
    --dice 0.85 \
    --iou 0.74 \
    --precision 0.88 \
    --recall 0.83
```

### 生成复现脚本

```bash
# 生成复现脚本
python scripts/research/experiment-logger.py reproduce exp-001
```

### 对比实验

```bash
# 对比多个实验
python scripts/research/experiment-logger.py compare exp-001 exp-002 exp-003
```

## 与上下文归档集成

### 自动归档实验总结

实验完成后，自动生成 resolution 格式的总结：

```json
{
  "id": "res-exp-001",
  "type": "resolution",
  "problem_signature": "Coronary artery segmentation baseline",
  "problem": "建立冠脉分割的 baseline 模型",
  "root_cause": "需要验证 U-Net 在该任务上的有效性",
  "final_fix": [
    "使用 U-Net 架构",
    "Dice Loss + Adam 优化器",
    "数据增强：旋转、翻转、缩放",
    "训练 100 epochs，学习率 0.001"
  ],
  "why_it_works": "U-Net 的编码器-解码器结构适合医学图像分割，跳跃连接保留了细节信息",
  "verification": [
    "Dice Score: 0.85",
    "IoU: 0.74",
    "视觉检查分割结果"
  ],
  "anti_patterns": [
    "学习率过大（0.01）导致训练不稳定",
    "batch size 过小（4）导致训练缓慢",
    "未使用数据增强导致过拟合"
  ],
  "artifacts_touched": [
    "train.py",
    "models/unet.py",
    "data/coronary_cta/"
  ],
  "evidence": {
    "signals": [
      "Best validation Dice: 0.87 at epoch 85",
      "Test Dice: 0.85",
      "Training time: 4 hours"
    ],
    "when": "2026-01-22"
  }
}
```

### 沉淀到长期记忆

```bash
# 同步实验总结到 memory/
python scripts/sync-context.py --experiments
```

## 最佳实践

### 1. 实验命名
- 使用描述性标题
- 包含关键参数
- 例如："U-Net-lr0.001-bs16-dice"

### 2. 参数记录
- 记录所有超参数
- 记录随机种子
- 记录环境配置

### 3. 结果记录
- 记录所有性能指标
- 保存可视化图表
- 记录训练时间和资源消耗

### 4. 复现性
- 生成复现脚本
- 记录数据版本
- 记录代码版本（git commit）

### 5. 失败记录
- 记录失败的尝试
- 分析失败原因
- 避免重复错误

## 与 Jupyter Notebook 集成

```python
# 在 Notebook 中记录实验
from research_tools import ExperimentLogger

# 创建实验
exp = ExperimentLogger.create("Baseline U-Net Training")

# 记录配置
exp.config(
    model="U-Net",
    lr=0.001,
    batch_size=16,
    epochs=100
)

# 训练模型
model = train_model(...)

# 记录结果
exp.result(
    dice=0.85,
    iou=0.74,
    precision=0.88,
    recall=0.83
)

# 保存图表
exp.save_plot(fig, "training_curve.png")

# 完成实验
exp.complete()
```

## 技术实现

### 核心函数

```python
def create_experiment(title):
    """创建实验记录"""
    exp_id = generate_exp_id()
    exp_dir = EXPERIMENTS_DIR / exp_id
    exp_dir.mkdir(parents=True)

    config = {
        "experiment_id": exp_id,
        "title": title,
        "date": datetime.now().isoformat(),
        "status": "running"
    }

    save_json(exp_dir / "config.json", config)
    return exp_id

def record_result(exp_id, metrics):
    """记录实验结果"""
    exp_dir = EXPERIMENTS_DIR / exp_id
    results_file = exp_dir / "results" / "metrics.json"

    save_json(results_file, metrics)

def generate_reproduce_script(exp_id):
    """生成复现脚本"""
    config = load_config(exp_id)

    script = f"""#!/bin/bash
# Experiment: {config['title']}

python train.py \\
    --model {config['parameters']['model']} \\
    --lr {config['parameters']['learning_rate']} \\
    --batch-size {config['parameters']['batch_size']} \\
    --epochs {config['parameters']['epochs']}
"""

    save_script(exp_dir / "reproduce.sh", script)
```

---

**核心价值**: 结构化记录，确保实验可复现
**集成**: 与上下文归档系统深度集成
**参考**: 科研最佳实践
