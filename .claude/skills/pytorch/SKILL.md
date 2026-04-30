---
name: pytorch
description: PyTorch 深度学习参考库 - 提供模型定义、训练循环、迁移学习、设备管理的惯用写法和常见陷阱
version: 1.1.0
license: MIT
metadata:
  category: ai-ml
  tags: [pytorch, deep-learning, neural-networks, ai]
  python_package: torch
trigger:
  - "pytorch"
  - "torch"
  - "神经网络"
  - "深度学习"
  - "训练模型"
---

# PyTorch Skill

> 提供 PyTorch 惯用写法，避免常见的梯度管理错误和 CUDA OOM 问题。

## What（输入/输出）

**输入**：用户描述的深度学习任务（模型设计/训练/推理/部署）

**输出**：可直接运行的 PyTorch 代码片段，附带关键注意事项

## How（判断框架）

编写 PyTorch 代码时，优先考虑：
1. **训练/推理模式分离**：`model.train()` vs `model.eval()` + `torch.no_grad()`
2. **设备一致性**：模型和数据必须在同一设备
3. **梯度清零时机**：`optimizer.zero_grad()` 在每个 batch 开始前
4. **检查点保存**：保存 `state_dict` 而非整个模型（跨版本兼容）

## When Done（验收标准）

- 推理代码有 `model.eval()` + `torch.no_grad()`
- 训练循环有 `optimizer.zero_grad()` → `loss.backward()` → `optimizer.step()` 顺序
- 模型保存使用 `state_dict`，不直接 `torch.save(model)`

## What NOT（边界约束）

🚫 不做的事：
1. 不替代 `deep-learning` Agent（本 Skill 只提供 API 参考，复杂架构设计用 Agent）
2. 不处理分布式训练细节（DDP 配置复杂，需专项指导）
3. 不做模型选型建议（用 `architect` Agent）

---

## 核心参考

### 何时使用此 Skill

当用户请求以下任务时自动激活：
- 设计或实现神经网络模型
- 训练深度学习模型
- 使用 PyTorch 进行张量操作
- 实现自定义损失函数或优化器
- 模型推理和部署

## 核心能力

### 1. 模型架构设计

支持常见的神经网络架构：
- **CNN**（卷积神经网络）：图像分类、目标检测
- **RNN/LSTM/GRU**：序列建模、时间序列预测
- **Transformer**：NLP 任务、注意力机制
- **GAN**：生成对抗网络
- **自定义架构**：灵活组合各种层

### 2. 训练流程

完整的训练流程支持：
- 数据加载和预处理（DataLoader, Dataset）
- 模型定义（nn.Module）
- 损失函数选择（CrossEntropyLoss, MSELoss 等）
- 优化器配置（Adam, SGD, AdamW 等）
- 训练循环（前向传播、反向传播、参数更新）
- 验证和测试
- 模型保存和加载

### 3. 高级功能

- **迁移学习**：使用预训练模型（torchvision.models）
- **混合精度训练**：torch.cuda.amp
- **分布式训练**：torch.nn.parallel.DistributedDataParallel
- **模型量化**：torch.quantization
- **ONNX 导出**：模型部署

## 使用指南

### 基本示例：图像分类

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# 1. 定义模型
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 64 * 8 * 8)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

# 2. 准备数据
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

train_dataset = datasets.CIFAR10(root='./data', train=True,
                                  download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

# 3. 训练设置
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SimpleCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 4. 训练循环
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        # 前向传播
        outputs = model(images)
        loss = criterion(outputs, labels)

        # 反向传播和优化
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss/len(train_loader):.4f}')

# 5. 保存模型
torch.save(model.state_dict(), 'model.pth')
```

### 迁移学习示例

```python
import torchvision.models as models

# 加载预训练模型
model = models.resnet50(pretrained=True)

# 冻结预训练层
for param in model.parameters():
    param.requires_grad = False

# 替换最后一层
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, num_classes)

# 只训练最后一层
optimizer = optim.Adam(model.fc.parameters(), lr=0.001)
```

## 最佳实践

### 1. 设备管理

```python
# 自动选择设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 将模型和数据移到设备
model = model.to(device)
data = data.to(device)
```

### 2. 梯度管理

```python
# 训练模式
model.train()

# 推理模式（禁用梯度计算）
model.eval()
with torch.no_grad():
    outputs = model(inputs)
```

### 3. 学习率调度

```python
from torch.optim.lr_scheduler import StepLR, ReduceLROnPlateau

# 固定步长衰减
scheduler = StepLR(optimizer, step_size=10, gamma=0.1)

# 自适应衰减
scheduler = ReduceLROnPlateau(optimizer, mode='min', patience=5)

# 在训练循环中
for epoch in range(num_epochs):
    train(...)
    val_loss = validate(...)
    scheduler.step(val_loss)  # ReduceLROnPlateau
    # scheduler.step()  # StepLR
```

### 4. 模型检查点

```python
# 保存检查点
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}
torch.save(checkpoint, 'checkpoint.pth')

# 加载检查点
checkpoint = torch.load('checkpoint.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
epoch = checkpoint['epoch']
loss = checkpoint['loss']
```

## 常见问题

### CUDA Out of Memory

**解决方案**：
- 减小 batch size
- 使用梯度累积
- 使用混合精度训练
- 清理不需要的张量

```python
# 梯度累积
accumulation_steps = 4
for i, (images, labels) in enumerate(train_loader):
    outputs = model(images)
    loss = criterion(outputs, labels) / accumulation_steps
    loss.backward()

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### 训练不收敛

**检查清单**：
- 学习率是否合适（尝试 1e-3, 1e-4）
- 数据是否正确归一化
- 损失函数是否正确
- 梯度是否爆炸/消失（使用梯度裁剪）

```python
# 梯度裁剪
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

## 参考资源

- **官方文档**: https://pytorch.org/docs/
- **教程**: https://pytorch.org/tutorials/
- **论坛**: https://discuss.pytorch.org/
- **GitHub**: https://github.com/pytorch/pytorch

---

**注意**: 使用此 Skill 前请确保已安装 PyTorch：
```bash
pip install torch torchvision torchaudio
```
