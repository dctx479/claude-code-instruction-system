import json, sys

KEYWORDS_FILE = sys.argv[1]
MESSAGE = sys.argv[2].lower()

# 优先级: high > medium > low
TOOL_PRIORITY = {
	"system-cleaner": "high",
	"context-mode": "high",
	"codegraph": "high",
	"rtk": "medium",
	"claude-tap": "medium",
	"ssh-skill": "medium",
	"yakit": "medium",
	"flue-framework": "low",
	"knowledge-work-plugins": "low",
}

try:
	with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
		data = json.load(f)
except Exception:
	sys.exit(0)

external_tools = data.get("external_tools", {})
matched = None
for tool in TOOL_PRIORITY: # 按 TOOL_PRIORITY 字典插入顺序（Python 3.7+ 保证）遍历
	keywords = external_tools.get(tool, {}).get("keywords", [])
	for kw in keywords:
		if kw and kw in MESSAGE:
			matched = tool
			break
	if matched:
		break

if not matched:
	sys.exit(0)

t = external_tools.get(matched, {})
print(json.dumps({
	"tool": matched,
	"priority": t.get("priority", TOOL_PRIORITY[matched]),
	"install_cmd": t.get("install_cmd", ""),
	"verify_cmd": t.get("verify_cmd", ""),
	"expected": t.get("expected", ""),
	"doc": t.get("doc", ""),
	"matched_keyword_hint": ""
}, ensure_ascii=False))
