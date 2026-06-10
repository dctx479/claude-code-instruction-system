#!/bin/bash
# Agent 自动调度测试脚本
# 测试 intent-detector.sh → intent-state.json → Agent 加载 完整流程

set -euo pipefail

INTENT_STATE="$HOME/.claude/intent-state.json"
INTENT_DETECTOR="$HOME/.claude/hooks/intent-detector.sh"

echo "=== Agent 自动调度测试 ==="
echo

# 测试用例
test_cases=(
    "debug|请帮我调试这个错误|debugger"
    "review|请审查这段代码|code-reviewer"
    "architect|设计系统架构|architect"
    "security|检查安全漏洞|security-analyst"
    "data|查询数据库|data-scientist"
    "research|文献调研|literature-manager"
    "qa-review|质量审查|qa-reviewer"
    "general|继续推进|orchestrator"
)

pass_count=0
fail_count=0

for test_case in "${test_cases[@]}"; do
    IFS='|' read -r intent message expected_agent <<< "$test_case"

    echo "测试: $intent"
    echo "输入: $message"

    # 构造 UserPromptSubmit 的 stdin JSON
    input_json=$(cat <<EOF
{"prompt":"$message"}
EOF
)

    # 执行 intent-detector
    echo "$input_json" | bash "$INTENT_DETECTOR" > /dev/null 2>&1 || true
    sleep 0.5  # 等待文件写入

    # 读取 intent-state.json
    if [[ ! -f "$INTENT_STATE" ]]; then
        echo "❌ FAIL: intent-state.json 不存在"
        ((fail_count++))
        echo
        continue
    fi

    actual_agent=$(grep -o '"agent":"[^"]*"' "$INTENT_STATE" | cut -d'"' -f4)

    if [[ "$actual_agent" == "$expected_agent" ]]; then
        echo "✅ PASS: agent=$actual_agent"
        ((pass_count++))
    else
        echo "❌ FAIL: 期望 $expected_agent，实际 $actual_agent"
        ((fail_count++))
    fi

    echo
done

echo "=== 测试结果 ==="
echo "通过: $pass_count / $((pass_count + fail_count))"
echo "失败: $fail_count / $((pass_count + fail_count))"

if [[ $fail_count -eq 0 ]]; then
    echo "✅ 所有测试通过"
    exit 0
else
    echo "❌ 部分测试失败"
    exit 1
fi
