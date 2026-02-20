# How Context is Saved Before Exit

This document explains exactly how the small-agent-team-orchestrator saves context before exit.

## Overview

When you create a checkpoint before exit, the system takes a **complete snapshot** of 4 critical JSON files that contain all the context accumulated during the session. These snapshots are stored in a single checkpoint file in a **global location**: `~/.dev_team/`

## Global Storage Location

All session data is stored in your home directory:

```
~/.dev_team/
├── session.json           # Current session state
├── tasks.json             # All tasks
├── delegations.json       # Delegation records
├── context.json           # Agent context
├── history.json           # Action history
└── checkpoints/           # Checkpoint snapshots
    ├── initial.json
    ├── checkpoint_*.json
    └── session_end_*.json
```

**Benefits:**
- ✅ Access from anywhere - run scripts from any directory
- ✅ One central location for all sessions
- ✅ Easy backup: `tar -czf dev_team_backup.tar.gz ~/.dev_team`
- ✅ No per-project clutter

## What Gets Saved

### 1. Tasks Snapshot (`tasks.json`)

**Contains:**
- Every task created during the session
- Task state (new, implementing, reviewing, testing, complete, etc.)
- Current assignee (which agent is working on it)
- Priority level
- Blockers and dependencies
- Subtask relationships
- Quality gate status
- Iteration count
- All deliverables produced
- Created and updated timestamps

**Example:**
```json
{
  "task_001": {
    "task_id": "task_001",
    "title": "User Authentication System",
    "current_state": "implementing",
    "assignee": "coder",
    "priority": "high",
    "context": {
      "requirements": "Add JWT-based auth",
      "architect_specs": "..."
    },
    "handoffs": [
      {
        "from": "architect",
        "to": "coder",
        "timestamp": "2024-01-20T14:30:00",
        "notes": "Architecture approved"
      }
    ],
    "blockers": [],
    "deliverables": ["Architecture doc", "API spec"],
    "dependencies": [],
    "iteration_count": 0,
    "quality_gates": {
      "architecture_approved": true,
      "tests_passing": false,
      "review_approved": false
    }
  }
}
```

### 2. Delegations Snapshot (`delegations.json`)

**Contains:**
- Every agent delegation that occurred
- What agent received the work
- When it was delegated
- What deliverables were expected
- Success criteria
- Constraints and requirements
- Handoff notes

**Example:**
```json
{
  "task_001_coder_20240120143000": {
    "task_id": "task_001",
    "from_agent": "architect",
    "to_agent": "coder",
    "timestamp": "2024-01-20T14:30:00",
    "state": "implementing",
    "requirements": {
      "feature": "JWT authentication"
    },
    "deliverables": [
      "Working implementation",
      "Unit tests (>80% coverage)",
      "Code documentation"
    ],
    "constraints": [
      "Follow architectural specifications",
      "Use secure password hashing"
    ],
    "success_criteria": [
      "All requirements implemented",
      "Tests pass with >80% coverage"
    ],
    "handoff_notes": "Implement based on architecture doc",
    "context_accumulated": {
      "original_requirements": {...},
      "architect_decisions": {...}
    }
  }
}
```

### 3. Context Snapshot (`context.json`)

**Contains:**
- Accumulated context per task
- What each agent contributed
- Original requirements
- Architectural decisions
- Implementation details
- Review feedback
- Test results
- Current agent assignment

**Example:**
```json
{
  "task_001": {
    "original_requirements": {
      "feature": "User authentication",
      "constraints": ["Must use JWT", "Support OAuth2"]
    },
    "architect": {
      "requirements": {...},
      "started_at": "2024-01-20T14:00:00",
      "architecture": "Microservice-based auth",
      "technology_decisions": {
        "auth_library": "jsonwebtoken",
        "storage": "Redis for tokens"
      }
    },
    "coder": {
      "architect_specs": {...},
      "started_at": "2024-01-20T14:30:00",
      "files_created": ["src/auth.js", "tests/auth.test.js"],
      "progress": "60% complete"
    },
    "pr_reviewer": [],
    "qa_tester": {},
    "last_updated": "2024-01-20T15:45:00",
    "current_agent": "coder"
  }
}
```

### 4. History Snapshot (`history.json`)

**Contains:**
- Complete chronological log of all actions
- Every delegation event
- When it happened
- What was passed between agents

**Example:**
```json
[
  {
    "task_id": "task_001",
    "action": "delegated_to_architect",
    "timestamp": "2024-01-20T14:00:00",
    "details": {
      "requirements": "Add user authentication"
    }
  },
  {
    "task_id": "task_001",
    "action": "delegated_to_coder",
    "timestamp": "2024-01-20T14:30:00",
    "details": {
      "architect_specs": {...}
    }
  }
]
```

## The Checkpoint File

All four snapshots are combined into a single checkpoint file:

**File Location:**
`~/.dev_team/checkpoints/checkpoint_20240120_153000.json`

**Checkpoint Structure:**
```json
{
  "checkpoint_id": "checkpoint_20240120_153000",
  "timestamp": "2024-01-20T15:30:00",
  "session_id": "session_20240120_140000",
  "description": "End of implementation phase",
  
  "tasks_snapshot": {
    "task_001": {...},
    "task_002": {...}
  },
  
  "delegations_snapshot": {
    "task_001_architect_...": {...},
    "task_001_coder_...": {...}
  },
  
  "context_snapshot": {
    "task_001": {
      "architect": {...},
      "coder": {...}
    }
  },
  
  "history_snapshot": [
    {...},
    {...}
  ],
  
  "metadata": {
    "active_agents": ["coder", "pr_reviewer"],
    "task_count": 2
  }
}
```

## Exit Workflow Step-by-Step

### Step 1: Detect Exit Condition

```bash
# User hits Ctrl+C or session ends
# Or explicitly runs:
python scripts/session_manager.py end paused
```

### Step 2: Check for Unsaved Changes

```python
# session_manager.py internally does:
def has_unsaved_changes(self) -> bool:
    session = self._load_session()
    
    # Check if session marked as changed
    if session.unsaved_changes:
        return True
    
    # Compare current state with last checkpoint
    if session.last_checkpoint:
        checkpoint = self.load_checkpoint(session.last_checkpoint)
        current_tasks = self._load_json(self.tasks_file)
        
        # If tasks changed since checkpoint
        return current_tasks != checkpoint.tasks_snapshot
    
    return False
```

### Step 3: Generate Exit Summary

```python
def generate_exit_summary(self) -> Dict:
    # Load all current state
    tasks = self._load_json(self.tasks_file)
    context = self._load_json(self.context_file)
    
    # Analyze what's in progress
    active_tasks = [t for t in tasks.values() 
                    if t["current_state"] not in ["complete", "blocked"]]
    
    # Find pending agent handoffs
    pending_handoffs = []
    for task_id, task_context in context.items():
        if task_context.get("current_agent"):
            pending_handoffs.append({
                "task_id": task_id,
                "agent": task_context["current_agent"],
                "state": tasks[task_id]["current_state"]
            })
    
    return {
        "has_unsaved_changes": self.has_unsaved_changes(),
        "active_tasks": len(active_tasks),
        "pending_handoffs": pending_handoffs,
        "recommended_action": "SAVE_PROGRESS"
    }
```

### Step 4: Prompt User

Based on the exit summary, the orchestrator should prompt:

```python
summary = session_manager.generate_exit_summary()

if summary["has_unsaved_changes"]:
    print(f"You have {summary['active_tasks']} active tasks:")
    for handoff in summary["pending_handoffs"]:
        print(f"  - {handoff['task_id']}: {handoff['agent']} ({handoff['state']})")
    
    print("\nWould you like to save your progress?")
    print("1. Create checkpoint (quick save)")
    print("2. Export full report (checkpoint + markdown)")
    print("3. Discard changes")
```

### Step 5: Create Checkpoint

When user chooses to save:

```python
def create_checkpoint(self, checkpoint_name, description):
    # 1. Load current session
    session = self._load_session()
    
    # 2. Read all 4 state files
    tasks = self._load_json(self.tasks_file)          # Line 160
    delegations = self._load_json(self.delegations_file)  # Line 161
    context = self._load_json(self.context_file)      # Line 162
    history = self._load_json(self.history_file)      # Line 163
    
    # 3. Create checkpoint object with snapshots
    checkpoint = Checkpoint(
        checkpoint_id=checkpoint_name,
        timestamp=datetime.now().isoformat(),
        session_id=session.session_id,
        tasks_snapshot=tasks,              # Complete copy
        delegations_snapshot=delegations,  # Complete copy
        context_snapshot=context,          # Complete copy
        history_snapshot=history,          # Complete copy
        description=description,
        metadata={
            "active_agents": session.active_agents,
            "task_count": len(tasks)
        }
    )
    
    # 4. Save checkpoint to file
    checkpoint_file = self.checkpoints_dir / f"{checkpoint_name}.json"
    self._save_json(checkpoint_file, asdict(checkpoint))
    
    # 5. Update session to mark as saved
    session.last_checkpoint = checkpoint_name
    session.unsaved_changes = False
    self._save_session(session)
    
    return checkpoint_name
```

## What This Preserves

### Complete Task State
- Where each task is in the workflow
- Who's working on what
- What's been completed
- What's blocked

### Agent Context
- What the Architect decided and why
- What the Coder implemented
- What the Reviewer found
- What the QA tester validated

### Workflow History
- Sequence of agent handoffs
- When each transition happened
- What was passed between agents

### Dependencies & Relationships
- Task dependencies
- Subtask trees
- Parallel execution groups

## Restoration Process

When you restore from a checkpoint:

```python
def restore_checkpoint(self, checkpoint_id):
    # 1. Load the checkpoint file
    checkpoint = self.load_checkpoint(checkpoint_id)
    
    # 2. Overwrite all 4 state files with snapshots
    self._save_json(self.tasks_file, checkpoint.tasks_snapshot)
    self._save_json(self.delegations_file, checkpoint.delegations_snapshot)
    self._save_json(self.context_file, checkpoint.context_snapshot)
    self._save_json(self.history_file, checkpoint.history_snapshot)
    
    # 3. Update session
    session = self._load_session()
    session.last_checkpoint = checkpoint_id
    session.status = "active"
    self._save_session(session)
```

**Result:** The system is restored to the EXACT state it was in when the checkpoint was created.

## Automatic Change Tracking

Changes are tracked automatically:

### When Task is Updated

```python
# task_tracker.py
def update_task_state(self, task_id, new_state, new_assignee):
    # ... update task ...
    self._save_tasks(tasks)
    self._mark_session_changed()  # Marks session.unsaved_changes = True
```

### When Agent is Delegated

```python
# agent_delegator.py
def _add_to_history(self, task_id, action, details):
    # ... add to history ...
    self._save_history(history)
    self._mark_session_changed()  # Marks session.unsaved_changes = True
```

## Summary

**Before exit, context is saved by:**

1. **Creating a checkpoint** that contains complete snapshots of:
   - `tasks.json` - All task states and metadata
   - `delegations.json` - All agent delegation records
   - `context.json` - All accumulated agent context
   - `history.json` - Complete action history

2. **The checkpoint is a single JSON file** containing all 4 snapshots

3. **Restoration is simple** - just copy the snapshots back to the original files

4. **Nothing is lost** - Every detail about tasks, agents, context, and history is preserved

5. **Multiple restore points** - You can create checkpoints at any time, creating multiple save points

This ensures that when you resume, you have:
- ✅ All task states exactly as they were
- ✅ All context from every agent
- ✅ Complete history of what happened
- ✅ Knowledge of what needs to happen next
- ✅ Ability to continue from any agent's state

The checkpoint is a **complete time-machine snapshot** of the entire orchestration session!
