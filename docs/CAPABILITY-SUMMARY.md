# 能力安装清单

由 `python scripts/check-doc-facts.py --write` 生成。profile 唯一来源为 `config/profiles.json`。

| Profile | Skills | Agents | 自动 Skill 描述字符 |
|---|---:|---:|---:|
| core | 23 | 20 | 672 |
| ctf | 13 | 0 | 0 |
| research | 7 | 4 | 0 |
| ecommerce | 4 | 0 | 0 |
| media | 2 | 0 | 0 |
| data | 3 | 7 | 148 |
| frontend | 3 | 2 | 286 |
| multi-model | 4 | 3 | 0 |

总计：59 个顶层 Skill、36 个 Agent、33 个命令。

字符数来自描述静态统计，不等于 token 数或真实会话 /context 实测。
新目标默认 core。切换 profile 不删除旧目标文件；旧全量安装需先审阅多余文件。
Java/PHP 顶层 Skill 通过路径读取嵌套参考，嵌套文件不计为独立注册 Skill。
