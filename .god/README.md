# God Committee - Independent Oversight Layer

> "The Watchers at the Edge of Chaos" - Based on Aha-Loop governance model

## Overview

God Committee is an independent oversight layer for the Taiyi Meta-System. It provides:

- **Autonomous Monitoring**: Random awakening every 2-8 hours
- **Collective Decision Making**: 3-member council with consensus requirements
- **5-Level Intervention**: From housekeeping to emergency stop
- **Full Audit Trail**: All decisions and actions are logged

## Quick Start

### Automatic Operation

The God Committee operates autonomously. It will:

1. **Awaken** periodically (2-8 hours) or on triggers:
   - Milestone completion
   - Anomaly detection
   - Phase transitions

2. **Observe** system state:
   - Code quality metrics
   - Test coverage
   - Security score
   - Performance metrics
   - Resource usage

3. **Deliberate** if concerns found:
   - Present findings
   - Discuss options
   - Vote on intervention

4. **Intervene** if approved:
   - Create snapshot
   - Execute action
   - Verify result
   - Log power exercise

### Manual Invocation

Request a system review:
```
"Review the current system state with God Committee"
```

Check for pending directives:
```
"Show me the God Committee directive queue"
```

## Governance Structure

### Council Members

| Member | Focus | Bias |
|--------|-------|------|
| **Alpha** | Architecture & Design | Conservative, stability |
| **Beta** | Security & Compliance | Cautious, safety |
| **Gamma** | Performance & Resources | Pragmatic, efficiency |

### Quorum Requirements

| Scenario | Required | Notes |
|----------|----------|-------|
| Standard | 2 of 3 | Normal deliberation |
| Emergency | 1 of 3 | L5 immediate threats only |

### Intervention Levels

| Level | Name | Consensus | Examples |
|-------|------|-----------|----------|
| **L1** | Housekeeping | None | Log cleanup, cache clear |
| **L2** | Execution Control | Optional | Pause/resume execution |
| **L3** | Active Correction | Recommended | Bug fix, config update |
| **L4** | Major Intervention | **Required** | Rollback, system reset |
| **L5** | System Termination | **Required** | Emergency stop |

## File Structure

```
.god/
├── config.json              # Governance configuration
├── directives.json          # Directive queue
├── council/                 # Session transcripts
│   └── SESSION-TEMPLATE.md
├── members/                 # Member state
│   ├── alpha.json
│   ├── beta.json
│   └── gamma.json
├── observation/             # System snapshots
│   └── OBSERVATION-TEMPLATE.json
└── powers/                  # Intervention logs
    └── POWER-LOG-TEMPLATE.json

agents/god-committee/
├── god-member.md            # Member agent definition
├── god-consensus.md         # Consensus engine
└── god-intervention.md      # Intervention executor

.claude/skills/god-oversight/
└── SKILL.md                 # Oversight skill definition
```

## Integration Points

### With Orchestrator

God Committee issues directives to Orchestrator via `.god/directives.json`:

```json
{
  "priority": "high",
  "level": "L3",
  "action": "pause_execution",
  "message": "Code quality below threshold"
}
```

Orchestrator checks the directive queue before task execution.

### With Autopilot

God Committee gates Autopilot phase transitions:

- Phase completion triggers observation
- L4/L5 operations require committee approval
- Advisory directives logged for each phase

### With QA System

QA reports are fed to God Committee:

- P0/P1 issues trigger automatic review
- Quality metrics inform observations
- Committee can override QA decisions

## Directive Priorities

| Priority | Effect | Timeout |
|----------|--------|---------|
| **critical** | Pause execution | Immediate |
| **high** | Priority processing | 5 min |
| **medium** | Normal processing | 30 min |
| **low** | Advisory only | None |

## Safety Mechanisms

### Circuit Breaker

If more than 5 interventions occur within 1 hour, the system triggers a circuit breaker requiring manual review.

### Never-Do List

The intervention agent will never:
- Delete production data without snapshot
- Execute L4/L5 without consensus verification
- Reset pushed commits with `git reset --hard`
- Modify `.god/config.json` without committee approval

### Always-Do List

The intervention agent will always:
- Create snapshot before L3+ interventions
- Verify consensus before L4/L5
- Log all actions to powers/
- Run verification after intervention

## Related Documentation

- **Agent Definitions**: `agents/god-committee/`
- **Skill Definition**: `.claude/skills/god-oversight/SKILL.md`
- **Orchestrator**: `agents/orchestrator.md`
- **Autopilot**: `agents/autopilot-orchestrator.md`
- **QA System**: `agents/qa-reviewer.md`, `agents/qa-fixer.md`
