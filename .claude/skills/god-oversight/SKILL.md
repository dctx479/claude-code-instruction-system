---
name: god-oversight
description: God Committee Oversight Skill - Independent monitoring and governance capability for the Taiyi Meta-System
version: 1.0.0
license: MIT
metadata:
  category: governance
  tags: [oversight, governance, monitoring, safety, intervention]
  requires: [".god/config.json", ".god/directives.json"]
trigger:
  - "/god-oversight"
  - "系统监控"
  - "治理审议"
  - "异常检测"
  - "高风险操作审批"
---

# God Committee Oversight Skill

## What (Input/Output)

**Input:**
- System state observations (code, configs, metrics)
- Anomaly detection signals
- Phase transition events from Autopilot
- Directive requests from system components

**Output:**
- Observation reports
- Intervention directives
- Consensus decisions
- Power exercise logs
- System snapshots

## When to Activate

This Skill activates automatically in the following scenarios:

1. **Periodic Awakening** - Random interval between 2-8 hours
2. **Milestone Completion** - When a major phase or task completes
3. **Anomaly Detection** - When system metrics exceed thresholds
4. **High-Risk Operations** - When L4/L5 operations are requested
5. **Autopilot Phase Transition** - At each Autopilot phase boundary
6. **Manual Invocation** - When user requests oversight review

## How (Execution Steps)

### Step 1: Observation Collection

```markdown
1. Scan system state
   - Git log (recent commits, branches)
   - Active tasks and agent states
   - Code quality metrics
   - Test coverage
   - Resource usage

2. Check anomaly indicators
   - Error rate trends
   - Performance degradation
   - Unusual file changes
   - Security scanner results

3. Build observation snapshot
   - Save to .god/observation/
   - Include all relevant metrics
```

### Step 2: Risk Assessment

```markdown
1. Evaluate observations against thresholds
   - Code quality: >= 70
   - Test coverage: >= 80%
   - Security score: >= 80
   - Error rate: < 5%

2. Classify concerns by severity
   - Critical: Immediate action needed
   - High: Prompt attention required
   - Medium: Schedule for review
   - Low: Note for future reference

3. Check for pattern matches
   - Known error patterns (from memory/error-patterns.md)
   - Previous similar incidents
   - Recurring issues
```

### Step 3: Deliberation (if needed)

```markdown
1. Convene committee (if concerns found)
   - Check quorum
   - Present findings
   - Open discussion

2. Evaluate intervention options
   - Do nothing (monitor)
   - Advisory directive
   - Active intervention
   - Emergency action

3. Reach consensus
   - Vote per governance rules
   - Record decision
   - Document dissent
```

### Step 4: Intervention (if approved)

```markdown
1. Create pre-intervention snapshot
2. Execute approved action
3. Verify results
4. Log power exercise
5. Update directive status
6. Notify Orchestrator
```

### Step 5: Reporting

```markdown
1. Generate session report
2. Update observation log
3. Archive to .god/council/
4. Sync relevant findings to memory/
```

## When Done (Acceptance Criteria)

- [ ] Observation snapshot saved to `.god/observation/`
- [ ] All concerns classified and documented
- [ ] If intervention needed: consensus recorded in `.god/council/`
- [ ] If intervention executed: power log in `.god/powers/`
- [ ] Directive queue in `.god/directives.json` updated
- [ ] Orchestrator notified of any active directives
- [ ] No orphaned or incomplete interventions

## What NOT (Guardrails)

### Boundaries

- **Do NOT** execute interventions without consensus (L4/L5)
- **Do NOT** modify production data directly
- **Do NOT** override Orchestrator without a directive
- **Do NOT** delete snapshots less than 30 days old
- **Do NOT** create more than 5 interventions per hour (circuit breaker)
- **Do NOT** modify `.god/config.json` without committee approval
- **Do NOT** skip pre-intervention snapshots for L3+

### Scope Limits

- Oversight only - not execution management (that is Orchestrator's job)
- Advisory and gate-keeping - not task assignment
- Quality and safety assurance - not feature development
- Post-hoc review - not real-time coding assistance

## Integration Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        GOD COMMITTEE LAYER                       │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────┐        │
│  │  Member   │   │  Consensus   │   │  Intervention    │        │
│  │  Agents   │──►│  Engine      │──►│  Executor        │        │
│  │ (x3)     │   │              │   │                  │        │
│  └──────────┘   └──────────────┘   └────────┬─────────┘        │
│                                              │                   │
│  .god/config.json    .god/directives.json    │ .god/powers/     │
└──────────────────────────────────────────────┼───────────────────┘
                                               │
                    ┌──────────────────────────┐│
                    │     DIRECTIVE QUEUE       ││
                    │  .god/directives.json     ││
                    └──────────┬───────────────┘│
                               │                │
          ┌────────────────────┴────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EXECUTION LAYER                             │
│  ┌──────────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │   Orchestrator   │  │   Autopilot   │  │   QA System     │  │
│  │   (checks queue) │  │   (phase gate)│  │   (reports up)  │  │
│  └──────────────────┘  └───────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Example 1: Routine Check

```markdown
User: "Review the current system state"

Skill Action:
1. Collect observation snapshot
2. Evaluate metrics
3. Generate report

Output:
---
## God Committee Observation Report
**Session:** gc-obs-20260204-001
**Type:** Routine check
**Status:** All clear

**Metrics:**
- Code Quality: 82/100
- Test Coverage: 85%
- Security Score: 92/100
- Error Rate: 0.3%

**Concerns:** None

**Recommendation:** Continue normal operations
---
```

### Example 2: Anomaly Detected

```markdown
Trigger: Error rate exceeds 5%

Skill Action:
1. Collect detailed observation
2. Convene committee
3. Deliberate on intervention
4. If approved: execute rollback
5. Generate report

Output:
---
## God Committee Emergency Session
**Session:** gc-session-20260204-002
**Type:** Anomaly response
**Trigger:** Error rate 8.5%

**Decision:** L4 Rollback approved (3/3 unanimous)
**Action:** Reverted commits abc123, def456
**Result:** Error rate restored to 0.2%
**Follow-up:** Hotfix scheduled, post-mortem pending
---
```

### Example 3: Architecture Gate

```markdown
Trigger: Autopilot Phase 2 (Specification) complete

Skill Action:
1. Review architecture decisions
2. Check for compliance
3. Gate or approve transition

Output:
---
## God Committee Phase Gate
**Phase:** Specification → Development
**Review:** Architecture compliant
**Decision:** Approved to proceed

**Advisory:**
- Consider caching strategy for auth tokens
- Database schema needs index optimization
---
```

## File Structure

```
.god/
├── config.json              # Governance configuration
├── directives.json          # Active directive queue
├── council/                 # Session transcripts and decisions
│   ├── gc-session-YYYYMMDD-NNN.md
│   └── decisions/
│       └── dec-YYYYMMDD-NNN.json
├── members/                 # Member state and availability
│   ├── alpha.json
│   ├── beta.json
│   └── gamma.json
├── observation/             # System observation snapshots
│   ├── obs-YYYYMMDD-NNN.json
│   └── snapshots/
│       └── snap-YYYYMMDD-NNN.json
├── powers/                  # Intervention exercise logs
│   └── pwr-YYYYMMDD-NNN.json
└── logs/                    # Activity logs
    └── committee.log
```

## Related Documents

- **Agent Definitions:**
  - `agents/god-committee/god-member.md` - Committee member agent
  - `agents/god-committee/god-consensus.md` - Consensus engine
  - `agents/god-committee/god-intervention.md` - Intervention executor
- **Configuration:**
  - `.god/config.json` - Governance configuration
  - `.god/directives.json` - Directive queue
- **Integration:**
  - `agents/orchestrator.md` - Orchestrator (receives directives)
  - `agents/ops/autopilot-orchestrator.md` - Autopilot (phase gates)
  - `agents/qa-reviewer.md` - QA (reports to committee)

## Metrics & Monitoring

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Session duration | < 30 min | > 45 min |
| Interventions/day | < 3 | > 5 |
| Consensus time | < 10 min | > 20 min |
| Snapshot size | < 50 MB | > 100 MB |
| Directive queue length | < 5 | > 10 |
| False positive rate | < 10% | > 20% |
