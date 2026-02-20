# Resuming a Saved Session

This guide explains how to resume work after exiting an agent team orchestrator session with saved context.

**Note:** All session data is stored globally at `~/.dev_team/` - you can access it from any directory.

## Quick Resume

### List Available Checkpoints

```bash
python scripts/session_manager.py list-checkpoints
```

**Output:**
```
Available checkpoints:
  checkpoint_20240120_143000
    Timestamp: 2024-01-20T14:30:00
    Session: session_20240120_140000
    Tasks: 5
    Description: Completed architecture phase

  checkpoint_20240120_160000
    Timestamp: 2024-01-20T16:00:00
    Session: session_20240120_140000
    Tasks: 5
    Description: Implementation in progress
```

### Restore from Checkpoint

```bash
python scripts/session_manager.py restore checkpoint_20240120_160000
```

This restores:
- All task states and definitions
- Agent delegations and handoffs
- Accumulated context per task
- Delegation history

### Check Restored State

```bash
# View session status
python scripts/session_manager.py status

# View team overview
python scripts/task_tracker.py team

# Get recommended next steps
python scripts/session_manager.py next-steps
```

## Understanding Session State

### Session Files

After restoring, the following files are populated in `~/.dev_team/`:

```
~/.dev_team/
├── session.json          # Current session state
├── tasks.json            # All task definitions
├── delegations.json      # Delegation records
├── context.json          # Accumulated context
├── history.json          # Full history
└── checkpoints/          # All saved checkpoints
    ├── checkpoint_*.json
    └── session_end_*.json
```

### Session Status

View current session:

```bash
python scripts/session_manager.py status
```

**Example Output:**
```json
{
  "session_id": "session_20240120_140000",
  "started_at": "2024-01-20T14:00:00",
  "last_checkpoint": "checkpoint_20240120_160000",
  "active_agents": ["coder", "pr_reviewer"],
  "unsaved_changes": false,
  "status": "active"
}
```

## Context Restoration Workflow

### 1. Restore Checkpoint

```bash
python scripts/session_manager.py restore checkpoint_20240120_160000
```

### 2. Review Active Tasks

```bash
# Get all task statuses
python scripts/task_tracker.py team

# View specific task details
python scripts/task_tracker.py status task_001
```

**Task Status Output:**
```json
{
  "task_id": "task_001",
  "title": "User Authentication System",
  "current_state": "implementing",
  "assignee": "coder",
  "progress": 55.0,
  "pending_handoffs": [
    {
      "task_id": "task_001",
      "agent": "coder",
      "state": "implementing"
    }
  ]
}
```

### 3. Identify Last Active Agent

```bash
python scripts/agent_delegator.py current task_001
```

**Output:**
```
Current assignee: coder
```

### 4. Get Full Task Context

```bash
python scripts/agent_delegator.py context task_001
```

This shows:
- Original requirements
- Architectural decisions from Architect
- Implementation progress from Coder
- Any review feedback

### 5. View Delegation History

```bash
python scripts/agent_delegator.py history task_001
```

Shows the sequence of agent handoffs and what was accomplished at each stage.

### 6. Review Next Steps

```bash
python scripts/session_manager.py next-steps
```

**Example Output:**
```
Recommended next steps:
1. Continue implementation of 'User Authentication System' (Task: task_001, Agent: coder)
2. Complete code review for 'API Gateway' (Task: task_002)
3. Resolve blockers for 'Database Migration': Waiting for schema approval
```

## Resuming Work by Task Type

### Continuing Implementation (Coder)

```bash
# Check what was being implemented
python scripts/agent_delegator.py context task_001

# Review the architectural specs that were provided
python scripts/agent_delegator.py history task_001 | grep architect

# Continue with implementation
# ... work on code ...

# When done, delegate to reviewer
python scripts/agent_delegator.py reviewer task_001 '{
  "implementation": "Completed authentication system",
  "files_changed": ["src/auth.py", "tests/test_auth.py"],
  "test_coverage": "87%"
}'
```

### Completing Code Review (Reviewer)

```bash
# Get the implementation details
python scripts/agent_delegator.py context task_002

# Check what files were changed
python scripts/task_tracker.py status task_002

# After review, either:
# - Approve and move to QA
python scripts/task_tracker.py update task_002 testing qa_tester

# - Request changes (iteration)
python scripts/task_tracker.py update task_002 iteration coder
```

### Addressing Blocked Tasks

```bash
# List all blockers
python scripts/task_tracker.py status task_003

# Example output shows:
# "blockers": ["Waiting for API key", "Schema approval needed"]

# Once blocker is resolved:
python scripts/task_tracker.py unblock task_003 0

# If all blockers removed, task moves back to implementing
```

## Creating Checkpoints During Work

### Manual Checkpoints

Create checkpoints at key milestones:

```bash
# After completing a major phase
python scripts/session_manager.py checkpoint "auth_complete" "Completed authentication implementation"

# Before starting risky work
python scripts/session_manager.py checkpoint "pre_refactor" "Before database refactoring"

# At end of work session
python scripts/session_manager.py checkpoint "eod_20240120" "End of day checkpoint"
```

### Automatic Checkpoints

The system automatically creates checkpoints:
- When starting a session (`initial` checkpoint)
- When ending a session (`session_end_*` checkpoint)

### Checkpoint Best Practices

1. **Milestone Checkpoints:** After completing major phases (architecture done, implementation complete, review passed)
2. **Pre-Change Checkpoints:** Before major refactoring or risky changes
3. **Daily Checkpoints:** At end of each work session
4. **Pre-Handoff Checkpoints:** Before delegating to next agent

## Exporting Session Reports

Generate a markdown report with full session details:

```bash
python scripts/session_manager.py export session_report.md
```

**Report Contents:**
- Session summary (tasks, status, agents)
- Active agents and pending handoffs
- Recommended next steps
- Detailed task breakdown
- Resume instructions

Use this report to:
- Share progress with team
- Document work completed
- Plan next session
- Handoff to another developer

## Handling Edge Cases

### No Checkpoints Available

If no checkpoints exist but you have task files:

```bash
# Start new session
python scripts/session_manager.py start "Resuming previous work"

# System will use existing task files
python scripts/task_tracker.py team
```

### Corrupted Checkpoint

If a checkpoint is corrupted, try an earlier one:

```bash
# List all checkpoints
python scripts/session_manager.py list-checkpoints

# Try restoring from earlier checkpoint
python scripts/session_manager.py restore checkpoint_20240120_143000
```

### Multiple Active Tasks

If multiple tasks were in progress:

```bash
# Get list of ready tasks
python scripts/task_tracker.py ready

# Check parallel execution groups
python scripts/task_tracker.py parallel

# View dependency tree
python scripts/task_tracker.py tree task_001
```

Prioritize based on:
1. Task priority (critical > high > medium > low)
2. Dependencies (complete dependencies first)
3. Blocked status (unblock first)
4. Agent availability

## Integration with Task Tool

When using OpenCode's Task tool with sub-agents:

```bash
# Resume via Task tool passing checkpoint info
Task(
  subagent_type="general",
  description="Resume authentication implementation",
  prompt="""
  Resume the authentication system implementation from checkpoint.
  
  Context restoration:
  - Session: session_20240120_140000
  - Checkpoint: checkpoint_20240120_160000
  - Last state: implementing (Coder agent)
  - Task: task_001 - User Authentication System
  
  Review the context at scripts/agent_delegator.py context task_001
  Continue implementation based on architectural specs.
  """
)
```

## Best Practices

1. **Always create checkpoint before exit:** Even for short breaks
2. **Use descriptive checkpoint names:** Makes finding the right one easier
3. **Review context before continuing:** Don't assume you remember everything
4. **Check for unsaved changes:** Before creating new work
5. **Export reports regularly:** For documentation and handoffs
6. **Clean up old checkpoints:** Archive checkpoints older than 30 days

## Troubleshooting

### "Checkpoint not found"

```bash
# Verify checkpoint exists
ls .dev_team/checkpoints/

# Check exact name in list
python scripts/session_manager.py list-checkpoints
```

### "No active session"

```bash
# Start new session
python scripts/session_manager.py start "New session"

# Or restore from checkpoint (creates session automatically)
python scripts/session_manager.py restore checkpoint_name
```

### "Context mismatch"

If restored context doesn't match expectations:

```bash
# Check delegation history
python scripts/agent_delegator.py history task_001

# View task tree
python scripts/task_tracker.py tree task_001

# Try earlier checkpoint
python scripts/session_manager.py list-checkpoints
```

## Summary

To resume a saved session:

1. List checkpoints: `python scripts/session_manager.py list-checkpoints`
2. Restore: `python scripts/session_manager.py restore <checkpoint_id>`
3. Review status: `python scripts/session_manager.py status`
4. Check next steps: `python scripts/session_manager.py next-steps`
5. Continue work based on task state and assigned agent

The session management system ensures you can always pick up exactly where you left off, with full context preservation across agent handoffs.
