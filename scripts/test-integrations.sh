#!/bin/bash
# 太一元系统集成测试脚本
# 版本: 1.0.0
# 日期: 2026-02-08

set -e  # 遇到错误立即退出

echo "========================================="
echo "  太一元系统集成测试"
echo "  Taiyi Meta-System Integration Tests"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_file() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌${NC} $2"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

test_dir() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌${NC} $2"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 1. 测试目录结构
echo "1. 测试目录结构..."
test_dir ".claude/skills/literature-mentor" "literature-mentor skill 目录"
test_dir ".claude/skills/literature-mentor/templates" "模板目录"
test_dir ".claude/context" "上下文归档目录"
test_dir ".claude/context/resolutions" "问题解决方案目录"
echo ""

# 2. 测试核心文件
echo "2. 测试核心文件..."
test_file "CLAUDE.md" "核心配置文件"
test_file "CHANGELOG.md" "变更日志"
test_file ".gitignore" "Git 忽略文件"
echo ""

# 3. 测试索引文件
echo "3. 测试索引文件..."
test_file "agents/INDEX.md" "Agent 索引"
test_file "skills/INDEX.md" "Skills 索引"
echo ""

# 4. 测试配置文件
echo "4. 测试配置文件..."
test_file "config/keywords.json" "关键词配置"
test_file "config/mcp-servers.json" "MCP 服务器配置"
echo ""

# 5. 测试 Skills 文件
echo "5. 测试 Skills 文件..."
test_file ".claude/skills/literature-mentor/SKILL.md" "literature-mentor SKILL.md"
test_file ".claude/skills/literature-mentor/templates/research-article-template.md" "Research Article 模板"
test_file ".claude/skills/literature-mentor/templates/review-article-template.md" "Review Article 模板"
echo ""

# 6. 测试命令文件
echo "6. 测试命令文件..."
test_file "commands/research/literature-review-quick.md" "快速文献精读命令"
test_file "commands/research/literature-batch-review.md" "批量文献精读命令"
echo ""

# 7. 测试 Git 配置
echo "7. 测试 Git 配置..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if git config core.autocrlf > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Git autocrlf 已配置"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️${NC}  Git autocrlf 未配置（建议配置）"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# 8. 测试 JSON 文件格式
echo "8. 测试 JSON 文件格式..."
if command -v python3 > /dev/null 2>&1; then
    for json_file in config/*.json .claude/context/index.json; do
        if [ -f "$json_file" ]; then
            TOTAL_TESTS=$((TOTAL_TESTS + 1))
            if python3 -m json.tool "$json_file" > /dev/null 2>&1; then
                echo -e "${GREEN}✅${NC} $json_file 格式正确"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            else
                echo -e "${RED}❌${NC} $json_file 格式错误"
                FAILED_TESTS=$((FAILED_TESTS + 1))
            fi
        fi
    done
else
    echo -e "${YELLOW}⚠️${NC}  Python3 未安装，跳过 JSON 格式验证"
fi
echo ""

# 9. 测试拼写错误
echo "9. 测试拼写错误..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if grep -r "Recommand" .claude/skills/literature-mentor/templates/ > /dev/null 2>&1; then
    echo -e "${RED}❌${NC} 发现拼写错误：Recommand"
    FAILED_TESTS=$((FAILED_TESTS + 1))
else
    echo -e "${GREEN}✅${NC} 无拼写错误"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi
echo ""

# 测试总结
echo "========================================="
echo "  测试总结"
echo "========================================="
echo "总测试数: $TOTAL_TESTS"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
echo -e "${RED}失败: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  有 $FAILED_TESTS 个测试失败${NC}"
    exit 1
fi
