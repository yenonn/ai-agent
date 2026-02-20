# Agent Team Orchestrator

A comprehensive skill for coordinating a multi-agent development team consisting of an Architect, Coder, PR Reviewer, and QA/Tester for software development workflows with parallel execution support.

## Overview

The Agent Team Orchestrator skill provides a structured approach to software development by leveraging specialized agents with distinct roles:

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Architect** | System design | Technical specifications, architecture decisions, technology selection |
| **Coder** | Implementation | Feature development, testing, documentation, code quality |
| **PR Reviewer** | Quality assurance | Code review, security analysis, standards compliance |
| **QA/Tester** | Validation | Test execution, edge cases, integration testing, sign-off |

## Features

- **Multi-agent coordination** with specialized roles
- **Parallel execution** support for independent tasks
- **Dependency management** between tasks
- **Context preservation** across agent handoffs
- **Quality gates** at each workflow stage
- **Iteration tracking** with configurable limits
- **Subtask support** for task decomposition
- **Blocker tracking** and resolution

## Installation

```bash
# Load the skill in OpenCode
/skill load agent-team-orchestrator
```

## Quick Start

### Create and Track Tasks

```bash
# Create a new task
python scripts/task_tracker.py create "Feature Name" "architect" high

# Check task status
python scripts/task_tracker.py status task_001

# View team overview
python scripts/task_tracker.py team
```

### Delegate to Agents

```bash
# Delegate to Architect
python scripts/agent_delegator.py architect task_001 '{"requirements": "feature description"}'

# Delegate to Coder
python scripts/agent_delegator.py coder task_001 '{"specifications": "from architect"}'

# Delegate to Reviewer
python scripts/agent_delegator.py reviewer task_001 '{"implementation": "completed code"}'

# Delegate to QA
python scripts/agent_delegator.py qa task_001 '{"test_scenarios": [...]}'
```

## Workflow States

```
NEW → ANALYZING → PLANNING → IMPLEMENTING → REVIEWING → TESTING → COMPLETE
                                    ↑              ↓           ↑
                                    └── ITERATION ←───────────┘
```

| State | Description | Agent |
|-------|-------------|-------|
| `new` | Task created, awaiting start | Coordinator |
| `analyzing` | Requirements analysis | Architect |
| `planning` | Architecture design | Architect |
| `implementing` | Code development | Coder |
| `reviewing` | Code review | PR Reviewer |
| `testing` | QA validation | QA/Tester |
| `iteration` | Addressing feedback | Coder |
| `blocked` | Has blockers | Any |
| `complete` | Finished and approved | - |

## Task Management

### Creating Tasks

```bash
# Basic task creation
python scripts/task_tracker.py create "Task Title" <task_type> [priority]

# Task types: architect, coder, pr_reviewer, qa_tester
# Priorities: low, medium, high, critical

# Examples
python scripts/task_tracker.py create "Auth System" "architect" high
python scripts/task_tracker.py create "Bug Fix" "coder" critical
```

### Subtasks and Parallel Execution

```bash
# Create subtask under parent
python scripts/task_tracker.py subtask <parent_id> "Subtask Title" <type>

# Create parallel subtasks
python scripts/task_tracker.py subtask task_001 "API Service" "coder" --parallel-group auth
python scripts/task_tracker.py subtask task_001 "DB Layer" "coder" --parallel-group auth

# View parallel groups
python scripts/task_tracker.py parallel

# Check ready tasks (all dependencies met)
python scripts/task_tracker.py ready
```

### Dependencies

```bash
# Add dependency (task_002 depends on task_001)
python scripts/task_tracker.py depend task_002 task_001

# View task tree with dependencies
python scripts/task_tracker.py tree task_001
```

### Blockers

```bash
# Add blocker
python scripts/task_tracker.py blocker task_001 "Waiting for API key"

# Remove blocker by index
python scripts/task_tracker.py unblock task_001 0
```

### Quality Gates

```bash
# Set quality gate status
python scripts/task_tracker.py gate task_001 architecture_approved true
python scripts/task_tracker.py gate task_001 tests_passing true
python scripts/task_tracker.py gate task_001 review_approved true
python scripts/task_tracker.py gate task_001 qa_validated true
```

### Session Commands

```bash
# View session status
python scripts/task_tracker.py session-status

# Create checkpoint
python scripts/task_tracker.py checkpoint "checkpoint_name" "Description"

# Generate exit summary
python scripts/task_tracker.py exit-summary
```

## Agent Delegation

### Architect

```bash
python scripts/agent_delegator.py architect <task_id> '{
  "feature": "Feature description",
  "requirements": ["req1", "req2"],
  "constraints": ["constraint1"]
}'
```

**Expected Deliverables:**
- Technical specifications document
- System architecture design
- API design documentation
- Database schema
- Technology stack decisions
- Security considerations

### Coder

```bash
python scripts/agent_delegator.py coder <task_id> '{
  "architect_specs": {...},
  "component": "Component name"
}'
```

**Expected Deliverables:**
- Working implementation
- Unit tests (>80% coverage)
- Integration tests
- Code documentation

### PR Reviewer

```bash
python scripts/agent_delegator.py reviewer <task_id> '{
  "implementation": "summary",
  "files_changed": [...],
  "test_coverage": "85%"
}'
```

**Review Checklist:**
- Security review
- Code quality
- Test coverage
- Performance
- Architectural compliance

### QA/Tester

```bash
python scripts/agent_delegator.py qa <task_id> '{
  "test_scenarios": ["scenario1", "scenario2"],
  "acceptance_criteria": ["criteria1"]
}'
```

**Expected Deliverables:**
- Test execution results
- Bug reports
- Coverage analysis
- Sign-off recommendation

### Context Management

```bash
# Get current assignee
python scripts/agent_delegator.py current task_001

# Get full task context
python scripts/agent_delegator.py context task_001

# Get delegation history
python scripts/agent_delegator.py history task_001

# Create checkpoint
python scripts/agent_delegator.py checkpoint "milestone_name" "Optional description"

# Generate exit summary
python scripts/agent_delegator.py exit-summary

# Check for unsaved changes
python scripts/agent_delegator.py has-changes
```

## Session Management

The skill includes comprehensive session management for graceful exits and context preservation.

### Starting a Session

```bash
# Start new session
python scripts/session_manager.py start "Project description"

# Check session status
python scripts/session_manager.py status
```

### Creating Checkpoints

```bash
# Create checkpoint (via session manager)
python scripts/session_manager.py checkpoint "checkpoint_name" "Description"

# Or via task tracker
python scripts/task_tracker.py checkpoint "checkpoint_name" "Description"

# Or via agent delegator
python scripts/agent_delegator.py checkpoint "checkpoint_name" "Description"
```

### Graceful Exit

Before exiting a session:

```bash
# Check for unsaved changes
python scripts/session_manager.py has-changes

# Generate exit summary
python scripts/session_manager.py summary

# Get recommended next steps
python scripts/session_manager.py next-steps

# Create final checkpoint and end session
python scripts/session_manager.py end paused  # or: complete

# Export session report
python scripts/session_manager.py export session_report.md
```

### Resuming Work

```bash
# List available checkpoints
python scripts/session_manager.py list-checkpoints

# Restore from checkpoint
python scripts/session_manager.py restore checkpoint_20240120_160000

# Check what needs to be done
python scripts/session_manager.py next-steps
```

See [references/resume-workflow.md](references/resume-workflow.md) for detailed resume instructions.

## Example Workflow

### Feature Development with Parallel Execution

```bash
# 1. Create main task
python scripts/task_tracker.py create "User Management" "architect" high

# 2. Architect analyzes and designs
python scripts/agent_delegator.py architect task_001 '{
  "features": ["registration", "authentication", "profile"],
  "constraints": ["must integrate with existing system"]
}'

# 3. Create parallel subtasks
python scripts/task_tracker.py subtask task_001 "Auth Service" "coder" --parallel-group user_mgmt
python scripts/task_tracker.py subtask task_001 "Profile Service" "coder" --parallel-group user_mgmt

# 4. Implement in parallel
python scripts/task_tracker.py update task_002 implementing coder
python scripts/agent_delegator.py coder task_002 '{"architect_specs": {...}}'

python scripts/task_tracker.py update task_003 implementing coder
python scripts/agent_delegator.py coder task_003 '{"architect_specs": {...}}'

# 5. Review each component
python scripts/agent_delegator.py reviewer task_002 '{"implementation": {...}}'

# 6. QA validates integration
python scripts/task_tracker.py update task_001 testing qa_tester
python scripts/agent_delegator.py qa task_001 '{"test_scenarios": [...]}'

# 7. Set quality gates
python scripts/task_tracker.py gate task_001 architecture_approved true
python scripts/task_tracker.py gate task_001 tests_passing true
python scripts/task_tracker.py gate task_001 review_approved true
python scripts/task_tracker.py gate task_001 qa_validated true

# 8. Complete
python scripts/task_tracker.py update task_001 complete
```

## Architecture

```
agent-team-orchestrator/
├── SKILL.md                    # Main skill definition & orchestration instructions
├── README.md                   # This file
├── scripts/
│   ├── task_tracker.py         # Task management with dependencies & parallel support
│   ├── agent_delegator.py      # Agent coordination with context preservation
│   └── session_manager.py      # Session management, checkpoints, and graceful exits
└── references/
    ├── workflow-patterns.md    # Development workflows & parallel patterns
    ├── integration-examples.md # Usage examples & command reference
    ├── sub-agent-examples.md   # Agent implementation examples
    └── resume-workflow.md      # Session resume and checkpoint restoration guide
```

## Configuration

### Task States
- `new`, `analyzing`, `planning`, `implementing`, `reviewing`, `testing`, `iteration`, `blocked`, `complete`

### Priorities
- `low`, `medium`, `high`, `critical`

### Quality Gates
- `architecture_approved`
- `tests_passing`
- `review_approved`
- `qa_validated`

### Iteration Limits
- Default: 3 maximum iterations
- Configurable per task via `max_iterations` field

## Best Practices

### Communication
- Include comprehensive context when delegating
- Document decisions at each handoff
- Use clear, actionable feedback

### Quality Assurance
- Never skip PR review
- Require >80% test coverage
- Use quality gates for checkpoints
- Always validate with QA

### Parallel Execution
- Group independent tasks in parallel groups
- Set dependencies before starting
- Monitor parallel group progress

### Iteration Management
- Track iteration count
- Escalate if >3 iterations needed
- Document iteration reasons

## Troubleshooting

### Task not found
```bash
# Verify task ID format (task_001, task_002, etc.)
python scripts/task_tracker.py team  # List all tasks
```

### Context not preserved
```bash
# Check delegation history
python scripts/agent_delegator.py history task_001

# Get current context
python scripts/agent_delegator.py context task_001
```

### Blocked tasks
```bash
# View blockers
python scripts/task_tracker.py status task_001

# Remove resolved blocker
python scripts/task_tracker.py unblock task_001 0
```

### Too many iterations
```bash
# Check iteration count
python scripts/task_tracker.py status task_001

# If stuck, escalate or decompose into smaller tasks
```

### Session recovery
```bash
# List available checkpoints
python scripts/session_manager.py list-checkpoints

# Restore from checkpoint
python scripts/session_manager.py restore <checkpoint_id>

# Check what was in progress
python scripts/session_manager.py next-steps
```

## Exit Workflow

When ending a session, follow this protocol for proper context saving:

### 1. Check Session State

```bash
# Check for unsaved changes
python scripts/session_manager.py has-changes

# Generate comprehensive summary
python scripts/session_manager.py summary
```

### 2. User Prompt

Based on the summary output, prompt the user:

**If active tasks exist:**
```
You have 3 active tasks in progress:
- task_001: User Authentication (Coder - implementing)
- task_002: API Gateway (Reviewer - reviewing)
- task_003: Database Migration (Blocked - awaiting approval)

Would you like to:
1. Save progress and exit (creates checkpoint)
2. Export session report (checkpoint + markdown report)
3. Continue working
```

**If all tasks complete:**
```
All tasks complete! Session ready to archive.

Would you like to:
1. Archive session (marks as complete)
2. Export final report
```

### 3. Save Based on User Choice

```bash
# Option 1: Quick checkpoint
python scripts/session_manager.py checkpoint "exit_checkpoint" "Session paused"
python scripts/session_manager.py end paused

# Option 2: Full export with report
python scripts/session_manager.py export session_report.md
python scripts/session_manager.py end paused

# Option 3: Archive complete session
python scripts/session_manager.py end complete
```

### 4. Show Next Steps

```bash
python scripts/session_manager.py next-steps
```

**Example Output:**
```
Recommended next steps:
1. Continue implementation of 'User Authentication' (Task: task_001, Agent: coder)
2. Complete code review for 'API Gateway' (Task: task_002)
3. Resolve blockers for 'Database Migration': Waiting for schema approval

To resume: python scripts/session_manager.py restore exit_checkpoint
```

### Exit Summary JSON Structure

The exit summary provides structured information for decision making:

```json
{
  "session_id": "session_20240120_140000",
  "has_unsaved_changes": true,
  "last_checkpoint": "checkpoint_20240120_143000",
  "total_tasks": 5,
  "active_tasks": 3,
  "blocked_tasks": 1,
  "completed_tasks": 1,
  "pending_handoffs": [
    {
      "task_id": "task_001",
      "agent": "coder",
      "state": "implementing"
    }
  ],
  "recommended_action": "SAVE_PROGRESS"
}
```

**Recommended Actions:**
- `SAVE_PROGRESS` - Active work in progress, should checkpoint
- `SAVE_WITH_BLOCKERS` - Blocked tasks exist, save for later resolution
- `SAVE_PENDING` - Pending handoffs, save agent state
- `ARCHIVE_COMPLETE` - All work done, can archive session

## Storage

Data is stored in a **global** `.dev_team/` directory (default: `~/.dev_team/`):

```
~/.dev_team/
├── tasks.json        # Task definitions and state
├── delegations.json  # Delegation records
├── context.json      # Accumulated context per task
├── history.json      # Full delegation history
├── session.json      # Current session state
└── checkpoints/      # Session checkpoints for resuming
    ├── checkpoint_*.json
    └── session_end_*.json
```

**Benefits of Global Storage:**
- ✅ Access sessions from any directory
- ✅ All orchestration work in one place
- ✅ Easy to backup (just backup ~/.dev_team)
- ✅ No per-project clutter
- ✅ Share sessions across multiple projects

**Session Management Files:**
- `session.json` - Tracks active session, unsaved changes, and current state
- `checkpoints/*.json` - Snapshots of full system state for resuming work
- Session reports (`.md` files) - Human-readable summaries for handoffs

### Configuring Storage Location

You can customize the storage location using the `DEV_TEAM_DIR` environment variable:

```bash
# Use a custom directory
export DEV_TEAM_DIR=/path/to/custom/location
python scripts/task_tracker.py team

# Use project-local storage
export DEV_TEAM_DIR=./.dev_team
python scripts/session_manager.py start "Local session"

# Relative paths are expanded from home directory
export DEV_TEAM_DIR=~/Documents/dev-team-data
```

**Default Location:** If `DEV_TEAM_DIR` is not set, the directory defaults to `~/.dev_team`

## License

This skill is provided as-is for use with OpenCode. Modify and adapt as needed for your team workflows.

---

**Agent Team Orchestrator** - Coordinating software development through specialized AI agents with parallel execution support
