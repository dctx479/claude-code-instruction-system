# 集成 claude-scientific-skills

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/K-Dense-AI/claude-scientific-skills.git

# 2. 集成到太一元系统
cp -r claude-scientific-skills/scientific-skills/* .claude/skills/

# 3. 验证
ls .claude/skills/
# 应看到: machine-learning/, data-analysis/, bioinformatics/ 等
```

## 包含的 Skills (140+)

### Machine Learning & AI
- 机器学习算法
- 模型训练和评估
- 超参数优化
- 特征工程

### Deep Learning
- CNN (卷积神经网络)
- RNN (循环神经网络)
- Transformer
- GAN (生成对抗网络)

### Reinforcement Learning
- DQN (Deep Q-Network)
- PPO (Proximal Policy Optimization)
- SAC (Soft Actor-Critic)
- MADDPG (Multi-Agent DDPG)

### Time Series Analysis
- ARIMA
- Prophet
- LSTM
- 异常检测

### Model Interpretability
- SHAP
- LIME
- Captum
- Fairlearn

### Data Analysis & Visualization
- pandas
- numpy
- matplotlib
- plotly
- seaborn

### Python Packages (55+)
- PyTorch
- TensorFlow
- scikit-learn
- Hugging Face Transformers
- Stable-Baselines3
- RLlib
- OpenAI Gym
- statsmodels
- scipy
- ...

## 使用示例

### 深度学习
```markdown
"帮我设计一个图像分类模型，使用 PyTorch"
→ 自动激活 PyTorch Skill
→ 生成模型架构、训练代码、评估脚本
```

### 数据分析
```markdown
"分析这个 CSV 文件的统计特征"
→ 自动激活 pandas Skill
→ 生成数据探索、可视化、统计分析代码
```

### 时间序列预测
```markdown
"预测未来 30 天的销售额"
→ 自动激活 Prophet/LSTM Skill
→ 生成预测模型、训练代码、结果可视化
```

### 模型可解释性
```markdown
"使用 SHAP 解释模型预测结果"
→ 自动激活 SHAP Skill
→ 生成 SHAP 分析代码、可视化图表
```

## 预期效果

- **科研能力提升**: 10-20 倍
- **支持库数量**: 55+ Python 包
- **Token 节省**: 70-90% (渐进式披露)
- **配置成本**: 零（开箱即用）

## 注意事项

1. **仓库大小**: ~50MB，包含大量文档和示例
2. **依赖管理**: Skills 不包含实际的 Python 包，需要单独安装
3. **更新频率**: 社区持续更新，建议定期 `git pull`

## 故障排查

### Skills 未被激活
- 确认 Skills 已正确复制到 `.claude/skills/` 目录
- 检查 SKILL.md 文件格式是否正确
- 尝试显式提及 Skill 名称（如 "使用 PyTorch Skill"）

### Token 消耗过高
- 检查是否加载了过多 Skills
- 考虑只复制需要的 Skills 子集
- 使用渐进式披露机制

## 相关资源

- **GitHub**: https://github.com/K-Dense-AI/claude-scientific-skills
- **文档**: https://github.com/K-Dense-AI/claude-scientific-skills/blob/main/README.md
- **Skills 市场**: https://skillsmp.com/
- **Awesome Agent Skills**: https://github.com/heilcheng/awesome-agent-skills
