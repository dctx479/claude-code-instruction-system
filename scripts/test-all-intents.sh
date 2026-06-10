#!/bin/bash
# 全量 Intent 路由验证脚本
# 覆盖 intent-detector.sh 中定义的全部 27 个 intent
# 用法: bash scripts/test-all-intents.sh

INTENT_DETECTOR="$HOME/.claude/hooks/intent-detector.sh"
INTENT_STATE="$HOME/.claude/intent-state.json"
PASS=0
FAIL=0
SKIP=0

run_test() {
    local intent_label="$1"
    local message="$2"
    local expected_agent="$3"

    echo "{\"prompt\":\"$message\"}" | bash "$INTENT_DETECTOR" >/dev/null 2>&1
    sleep 0.4

    local actual
    actual=$(tr -d '\n\r ' < "$INTENT_STATE" | grep -o '"agent":"[^"]*"' | cut -d'"' -f4 || echo "")

    if [[ "$actual" == "$expected_agent" ]]; then
        printf "  %-18s %-32s → %s ✅\n" "[$intent_label]" "\"${message:0:30}\"" "$actual"
        ((PASS++))
    else
        printf "  %-18s %-32s → got=%s, want=%s ❌\n" "[$intent_label]" "\"${message:0:30}\"" "$actual" "$expected_agent"
        ((FAIL++))
    fi
}

echo "═══════════════════════════════════════════════════════"
echo " Agent 自动调度全量测试（27 个 intent）"
echo "═══════════════════════════════════════════════════════"
echo

echo "── 代码类 ─────────────────────────────────────────────"
run_test "debug"          "帮我调试这个错误"                   "debugger"
run_test "review"         "请审查这段代码的质量"               "code-reviewer"
run_test "test"           "生成单元测试覆盖率"                 "automated-testing"
run_test "refactor"       "重构这段代码让它更清晰"             "code-reviewer"
echo

echo "── 架构类 ─────────────────────────────────────────────"
run_test "architect"      "设计一个微服务架构"                 "architect"
echo

echo "── 安全类 ─────────────────────────────────────────────"
run_test "security"       "检查XSS注入漏洞"                   "security-analyst"
run_test "security-audit" "依赖扫描CVE安全审计"               "security-audit"
echo

echo "── 数据类 ─────────────────────────────────────────────"
run_test "data"           "查询数据库SQL优化"                  "data-scientist"
run_test "analysis"       "统计分析用户行为数据"               "data-analyst"
run_test "visualization"  "绘制数据可视化图表"                 "data-visualization"
echo

echo "── AI/ML 类 ────────────────────────────────────────────"
run_test "ml"             "训练PyTorch深度学习模型"            "deep-learning"
run_test "rl"             "用PPO强化学习训练策略"              "reinforcement-learning"
run_test "timeseries"     "用ARIMA时间序列预测趋势"            "time-series-analysis"
run_test "interpretability" "SHAP解释模型可解释性"            "model-interpretability"
echo

echo "── 科研类 ─────────────────────────────────────────────"
run_test "research"       "文献综述调研论文"                   "literature-manager"
run_test "paper-writing"  "帮我撰写论文综述"                   "paper-writing-assistant"
run_test "experiment"     "记录实验配置和结果"                 "experiment-logger"
echo

echo "── 文档类 ─────────────────────────────────────────────"
run_test "document"       "编写功能规范文档"                   "spec-writer"
echo

echo "── QA 类 ───────────────────────────────────────────────"
run_test "qa-review"      "质量审查验收检查"                   "qa-reviewer"
run_test "qa-fix"         "autofix自动修复P2问题"              "qa-fixer"
echo

echo "── 运维类 ─────────────────────────────────────────────"
run_test "perf-monitor"   "性能监控报告生成"                   "performance-monitor"
run_test "optimize"       "系统配置优化token优化"              "auto-optimizer"
run_test "autopilot"      "全自主autopilot执行"                "autopilot-orchestrator"
run_test "archive"        "保存上下文归档"                     "context-archivist"
echo

echo "── 通用类 ─────────────────────────────────────────────"
run_test "general"        "继续推进任务"                       "orchestrator"
echo

echo "═══════════════════════════════════════════════════════"
printf " 结果: ✅ 通过 %d  ❌ 失败 %d  ⏭ 跳过 %d  /  总计 %d\n" \
    "$PASS" "$FAIL" "$SKIP" "$((PASS + FAIL + SKIP))"
echo "═══════════════════════════════════════════════════════"

[[ $FAIL -eq 0 ]] && exit 0 || exit 1
