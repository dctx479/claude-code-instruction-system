---
name: skill-creator
description: Skill 元创建器 - 按本项目契约（What/How/When done/What NOT）+ 第五要素 Extractable + 单一职责 + 方法论优于规则三原则，生成高质量 SKILL.md
license: MIT
metadata:
  category: system
  tags:
  - meta-skill
  - skill-authoring
  - contract
  - template
  - quality-control
  - extractable
  integration:
  - neat
  - reflection
  - knowledge-compounding
  - claude-agent-sdk
  version: 1.1.0
  trigger:
  - /skill-creator
  - 创建一个 Skill
  - 把这个流程封装成 Skill
  - 提炼成 Skill
disable-model-invocation: true
---

# Create a focused Skill

Create or update the Skill requested by the user. Keep the actual capability, its trigger and essential constraints in SKILL.md; put conditional detail in references only when it helps. Avoid generic instructions the model already knows.

## Contract
Use the requested directory. Frontmatter needs a matching kebab-case name and a concise description. Preserve supported metadata. Choose invocation policy from the user's intent; workflow commands in this repository are explicitly invoked. Do not copy invocation rules blindly to another tool or project.

Describe the useful inputs, decisions, outputs and observable completion conditions. Reuse existing resources and concrete evidence; do not prescribe a fixed document length or invented performance threshold. A simple skill needs no references folder or extra README.

In this repository, register installation groups only in config/profiles.json and regenerate the capability summary; do not manually repeat a catalog in INDEX/README/router files. In another project, follow its real discovery convention rather than imposing this repository's profile system.

## Project verification mode
When asked for a project verify Skill, derive actual commands from manifest, CI and tests. Include startup, self-check, driving the artifact, evidence and cleanup. Use isolated test data, no production data or real notifications. Run the complete applicable procedure before delivery and preserve command, exit status and output.
Return clean/changed/blocked; a real failing test is blocked, not clean. Do not fix business code when only a verification Skill was requested. If no long-running service exists, explain that startup/cleanup are not needed instead of inventing a server.

Validate naming, frontmatter, resource references and the generated procedure. Creation does not authorize global installation, commits, publishing, delegation or unrelated configuration changes. Reuse already granted authorization and ask only for genuinely missing decisions.
