---
name: observability
description: 记录可核验的执行证据、命令退出码与简明决策摘要；不记录私密推理、提示词或凭据，不把示例和调用次数冒充性能数据。
license: MIT
metadata:
  category: system
  tags:
  - observability
  - logging
  - transparency
  - decision-tracking
  - aha-loop
  inspired_by: Aha-Loop
  version: 1.1.0
  trigger:
  - /observe
  - /thought
  - /log-decision
  - 记录思考过程
  - 思维日志
  - 决策理由
disable-model-invocation: true
---

# Execution evidence and concise decision summaries

Record observable facts from the requested task: command, environment/version where relevant, exit code, output, artifact paths and unresolved failures. Use the output artifact and format the user requested; do not mandate a second log for every task.

## Evidence contract

Run the actual verification command when authorized. Capture its real status and output; a command not run is NOT_RUN, a failed acceptance is blocked. Do not replace command evidence with the model saying it passed. Preserve failed attempts when a later fix changes the result.

A decision summary may state the choice, practical reason, tradeoff and supporting evidence. It should be concise and user-facing. Do not request, disclose or persist hidden chain-of-thought, private internal deliberation, raw prompts, secrets or credentials.

Differentiate an example/template from measurements. Invocation counts alone do not prove quality, success rate, latency or cost; report those metrics as unknown without raw evidence. Do not invent numeric confidence or log a TaskComplete success while acceptance is failing.

Read only task-relevant artifacts. Do not start continuous collection, telemetry, notifications, code changes or another Skill merely to make a report. Follow `docs/VNEXT-WORKFLOW.md` and existing authorization for any actual action.
