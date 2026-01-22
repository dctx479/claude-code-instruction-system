# CLAUDE.md - 网络安全/CTF 专用模板

## 安全研究声明
本配置仅用于:
- 授权的安全测试和渗透测试
- CTF 竞赛和安全挑战
- 安全研究和教育目的
- 防御性安全实践

**重要**: 始终在授权环境中进行安全测试。

## 环境配置

### 工具集
```bash
# 信息收集
nmap                   # 端口扫描
gobuster               # 目录枚举
ffuf                   # Web 模糊测试
subfinder              # 子域名发现

# 漏洞分析
sqlmap                 # SQL 注入
burpsuite              # Web 代理
nikto                  # Web 漏洞扫描
nuclei                 # 漏洞扫描器

# 利用工具
metasploit             # 渗透测试框架
john                   # 密码破解
hashcat                # GPU 密码破解

# 逆向分析
ghidra                 # 反编译
gdb                    # 调试器
radare2                # 逆向框架
```

### 常用命令

```bash
# 信息收集
nmap -sC -sV -oN scan.txt <target>           # 服务版本扫描
gobuster dir -u <url> -w <wordlist>          # 目录枚举
ffuf -w <wordlist> -u <url>/FUZZ             # 模糊测试

# Web 测试
curl -X POST -d "data" <url>                  # POST 请求
sqlmap -u "<url>?id=1" --dbs                 # SQL 注入测试

# 密码学
openssl enc -aes-256-cbc -d -in file         # AES 解密
echo "base64" | base64 -d                     # Base64 解码
xxd -r -p hexfile                            # Hex 转二进制

# 二进制分析
file <binary>                                 # 文件类型
strings <binary>                              # 提取字符串
checksec <binary>                            # 安全机制检查
```

## CTF 方法论

### 1. Web 安全

#### 常见漏洞类型
- **SQL 注入**: UNION, 盲注, 时间盲注
- **XSS**: 反射型, 存储型, DOM-based
- **SSRF**: 服务端请求伪造
- **XXE**: XML 外部实体注入
- **文件上传**: 绕过检查, WebShell
- **认证绕过**: JWT 漏洞, Session 劫持
- **反序列化**: PHP, Java, Python

#### 测试清单
```markdown
- [ ] 输入点识别 (表单, URL参数, Headers)
- [ ] SQL 注入测试
- [ ] XSS 测试 (反射/存储)
- [ ] 目录遍历
- [ ] 文件包含 (LFI/RFI)
- [ ] IDOR (不安全的直接对象引用)
- [ ] 认证/授权绕过
- [ ] 敏感信息泄露
```

### 2. 密码学

#### 常见类型识别
```python
# 哈希识别
MD5:    32 位十六进制
SHA1:   40 位十六进制
SHA256: 64 位十六进制

# 编码识别
Base64: [A-Za-z0-9+/=]
Hex:    [0-9A-Fa-f]
URL:    %XX 格式
```

#### 攻击思路
- 弱密钥/已知密钥
- 填充预言机攻击
- 哈希长度扩展攻击
- CBC 位翻转攻击

### 3. 逆向工程

#### 分析流程
1. **静态分析**: 反编译, 字符串提取
2. **动态分析**: 调试, 行为监控
3. **混淆分析**: 反混淆, 脱壳

#### 常用技巧
```bash
# 反编译
objdump -d <binary>
ghidra <binary>

# 动态调试
gdb <binary>
ltrace <binary>
strace <binary>
```

### 4. PWN (二进制漏洞利用)

#### 漏洞类型
- 栈溢出 (Stack Overflow)
- 堆溢出 (Heap Overflow)
- 格式化字符串
- Use After Free
- 整数溢出

#### 保护机制
```bash
# 检查保护
checksec --file=<binary>

# 常见保护
ASLR:    地址空间随机化
NX:      不可执行栈
Canary:  栈保护
PIE:     位置无关可执行
RELRO:   只读重定位
```

### 5. 取证分析

#### 工具集
```bash
# 内存取证
volatility -f <dump> imageinfo
volatility -f <dump> pslist

# 文件取证
binwalk <file>
foremost <file>
exiftool <file>

# 流量分析
wireshark <pcap>
tshark -r <pcap>
```

## 安全代码审计框架

### SAST 检查点
```markdown
## 输入验证
- [ ] 用户输入是否经过验证和清洗
- [ ] 是否使用参数化查询
- [ ] 是否有适当的输入长度限制

## 认证授权
- [ ] 密码存储是否安全 (bcrypt/argon2)
- [ ] Session 管理是否安全
- [ ] 权限检查是否完整

## 数据保护
- [ ] 敏感数据是否加密存储
- [ ] 是否使用 HTTPS
- [ ] 是否有数据泄露风险

## 错误处理
- [ ] 错误信息是否暴露敏感信息
- [ ] 是否有适当的日志记录
```

### 代码模式识别
```python
# 危险函数 (各语言)
# Python
eval(), exec(), os.system(), subprocess.call()

# PHP
eval(), system(), exec(), shell_exec(), include()

# Java
Runtime.exec(), ProcessBuilder

# JavaScript
eval(), Function(), innerHTML, document.write()
```

## 报告模板

```markdown
# 安全测试报告

## 概述
- 测试目标:
- 测试范围:
- 测试时间:
- 授权信息:

## 发现汇总
| 漏洞 | 严重程度 | 状态 |
|------|---------|------|
|      |         |      |

## 详细发现

### 漏洞 1: [名称]
- **严重程度**: Critical/High/Medium/Low
- **位置**: [URL/文件位置]
- **描述**: [详细描述]
- **复现步骤**:
  1.
  2.
- **影响**: [潜在影响]
- **修复建议**: [如何修复]
- **参考**: [CVE/CWE 编号]

## 修复建议优先级
1. [Critical 级别漏洞]
2. [High 级别漏洞]
...
```

## 自主决策授权

✅ 可自主执行:
- 信息收集和侦察
- 漏洞识别和分析
- CTF 挑战求解
- 安全代码审计
- 编写 PoC 脚本

❌ 需要确认:
- 实际漏洞利用
- 任何可能造成破坏的操作
- 涉及生产环境的测试
- 社会工程相关活动

## 伦理准则
1. 仅在授权范围内进行测试
2. 发现漏洞后负责任披露
3. 不进行任何破坏性操作
4. 保护测试过程中获取的数据
5. 遵守相关法律法规
