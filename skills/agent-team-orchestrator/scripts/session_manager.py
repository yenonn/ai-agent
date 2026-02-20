#!/usr/bin/env python3
"""
Session management for agent team orchestrator.
Handles checkpoints, context saving, exit prompts, and session resumption.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict, field


@dataclass
class SessionState:
    """Represents the current orchestration session state."""

    session_id: str
    started_at: str
    last_checkpoint: Optional[str]
    active_agents: List[str]
    unsaved_changes: bool
    context_summary: Dict[str, Any]
    status: str  # "active", "paused", "complete"


@dataclass
class Checkpoint:
    """Represents a context checkpoint for resuming later."""

    checkpoint_id: str
    timestamp: str
    session_id: str
    tasks_snapshot: Dict[str, Any]
    delegations_snapshot: Dict[str, Any]
    context_snapshot: Dict[str, Any]
    history_snapshot: List[Dict]
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Manages orchestration sessions, checkpoints, and graceful exits."""

    def __init__(self, project_root: str = "."):
        # Use global .dev_team directory (configurable via DEV_TEAM_DIR env var)
        self.project_root = Path(project_root).resolve()
        dev_team_path = os.getenv("DEV_TEAM_DIR", str(Path.home() / ".dev_team"))
        self.dev_team_dir = Path(dev_team_path).expanduser()
        self.session_file = self.dev_team_dir / "session.json"
        self.checkpoints_dir = self.dev_team_dir / "checkpoints"
        self.tasks_file = self.dev_team_dir / "tasks.json"
        self.delegations_file = self.dev_team_dir / "delegations.json"
        self.context_file = self.dev_team_dir / "context.json"
        self.history_file = self.dev_team_dir / "history.json"
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensure storage directories exist."""
        self.dev_team_dir.mkdir(exist_ok=True)
        self.checkpoints_dir.mkdir(exist_ok=True)

        if not self.session_file.exists():
            self._save_session(None)

    def _load_json(self, file_path: Path) -> Any:
        """Load JSON from file."""
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if file_path.suffix == ".json" else []

    def _save_json(self, file_path: Path, data: Any):
        """Save JSON to file."""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _load_session(self) -> Optional[SessionState]:
        """Load current session state."""
        data = self._load_json(self.session_file)
        if data and "session_id" in data:
            return SessionState(**data)
        return None

    def _save_session(self, session: Optional[SessionState]):
        """Save session state."""
        data = asdict(session) if session else {}
        self._save_json(self.session_file, data)

    def start_session(self, description: str = "") -> str:
        """Start a new orchestration session."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = SessionState(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
            last_checkpoint=None,
            active_agents=[],
            unsaved_changes=False,
            context_summary={"description": description},
            status="active",
        )
        self._save_session(session)
        
        # Also create initial checkpoint
        self.create_checkpoint("initial", "Session started")
        
        return session_id

    def get_current_session(self) -> Optional[SessionState]:
        """Get the current active session."""
        return self._load_session()

    def update_session(
        self,
        active_agents: Optional[List[str]] = None,
        unsaved_changes: Optional[bool] = None,
        context_update: Optional[Dict] = None,
    ):
        """Update the current session state."""
        session = self._load_session()
        if not session:
            return

        if active_agents is not None:
            session.active_agents = active_agents
        if unsaved_changes is not None:
            session.unsaved_changes = unsaved_changes
        if context_update:
            session.context_summary.update(context_update)

        self._save_session(session)

    def create_checkpoint(
        self, checkpoint_name: Optional[str] = None, description: str = ""
    ) -> str:
        """Create a context checkpoint for resuming later."""
        session = self._load_session()
        if not session:
            # Create session without checkpoint to avoid recursion
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session = SessionState(
                session_id=session_id,
                started_at=datetime.now().isoformat(),
                last_checkpoint=None,
                active_agents=[],
                unsaved_changes=False,
                context_summary={"description": "Auto-created session"},
                status="active",
            )
            self._save_session(session)

        timestamp = datetime.now()
        if not checkpoint_name:
            checkpoint_name = f"checkpoint_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_name,
            timestamp=timestamp.isoformat(),
            session_id=session.session_id,
            tasks_snapshot=self._load_json(self.tasks_file),
            delegations_snapshot=self._load_json(self.delegations_file),
            context_snapshot=self._load_json(self.context_file),
            history_snapshot=self._load_json(self.history_file),
            description=description,
            metadata={
                "active_agents": session.active_agents,
                "task_count": len(self._load_json(self.tasks_file)),
            },
        )

        checkpoint_file = self.checkpoints_dir / f"{checkpoint_name}.json"
        self._save_json(checkpoint_file, asdict(checkpoint))

        # Update session with checkpoint info
        session.last_checkpoint = checkpoint_name
        session.unsaved_changes = False
        self._save_session(session)

        return checkpoint_name

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints."""
        checkpoints = []
        for checkpoint_file in sorted(self.checkpoints_dir.glob("*.json")):
            try:
                data = self._load_json(checkpoint_file)
                checkpoints.append(
                    {
                        "checkpoint_id": data.get("checkpoint_id"),
                        "timestamp": data.get("timestamp"),
                        "session_id": data.get("session_id"),
                        "description": data.get("description", ""),
                        "task_count": data.get("metadata", {}).get("task_count", 0),
                    }
                )
            except Exception:
                continue
        return checkpoints

    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load a specific checkpoint."""
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        if not checkpoint_file.exists():
            return None

        data = self._load_json(checkpoint_file)
        return Checkpoint(**data)

    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """Restore system state from a checkpoint."""
        checkpoint = self.load_checkpoint(checkpoint_id)
        if not checkpoint:
            return False

        # Restore all state files
        self._save_json(self.tasks_file, checkpoint.tasks_snapshot)
        self._save_json(self.delegations_file, checkpoint.delegations_snapshot)
        self._save_json(self.context_file, checkpoint.context_snapshot)
        self._save_json(self.history_file, checkpoint.history_snapshot)

        # Update session
        session = self._load_session()
        if session:
            session.last_checkpoint = checkpoint_id
            session.status = "active"
            self._save_session(session)

        return True

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes since last checkpoint."""
        session = self._load_session()
        if not session:
            return False

        if session.unsaved_changes:
            return True

        # Check if files have been modified since last checkpoint
        if not session.last_checkpoint:
            # No checkpoint yet, check if any tasks exist
            tasks = self._load_json(self.tasks_file)
            return len(tasks) > 0

        checkpoint = self.load_checkpoint(session.last_checkpoint)
        if not checkpoint:
            return True

        # Compare current state with checkpoint
        current_tasks = self._load_json(self.tasks_file)
        current_delegations = self._load_json(self.delegations_file)

        return (
            current_tasks != checkpoint.tasks_snapshot
            or current_delegations != checkpoint.delegations_snapshot
        )

    def generate_exit_summary(self) -> Dict[str, Any]:
        """Generate a summary of current state for exit prompt."""
        session = self._load_session()
        tasks = self._load_json(self.tasks_file)
        delegations = self._load_json(self.delegations_file)
        context = self._load_json(self.context_file)

        active_tasks = [
            t
            for t in tasks.values()
            if t.get("current_state")
            not in ["complete", "blocked", "cancelled"]
        ]
        blocked_tasks = [
            t for t in tasks.values() if t.get("current_state") == "blocked"
        ]
        completed_tasks = [
            t for t in tasks.values() if t.get("current_state") == "complete"
        ]

        pending_handoffs = []
        for task_id, task_context in context.items():
            current_agent = task_context.get("current_agent")
            if current_agent and task_id in tasks:
                task = tasks[task_id]
                if task.get("current_state") not in ["complete"]:
                    pending_handoffs.append(
                        {
                            "task_id": task_id,
                            "agent": current_agent,
                            "state": task.get("current_state"),
                        }
                    )

        return {
            "session_id": session.session_id if session else "unknown",
            "has_unsaved_changes": self.has_unsaved_changes(),
            "last_checkpoint": session.last_checkpoint if session else None,
            "total_tasks": len(tasks),
            "active_tasks": len(active_tasks),
            "blocked_tasks": len(blocked_tasks),
            "completed_tasks": len(completed_tasks),
            "pending_handoffs": pending_handoffs,
            "active_agents": session.active_agents if session else [],
            "recommended_action": self._recommend_exit_action(
                active_tasks, blocked_tasks, pending_handoffs
            ),
        }

    def _recommend_exit_action(
        self, active_tasks: List, blocked_tasks: List, pending_handoffs: List
    ) -> str:
        """Recommend what action to take on exit."""
        if len(active_tasks) > 0:
            return "SAVE_PROGRESS"
        elif len(blocked_tasks) > 0:
            return "SAVE_WITH_BLOCKERS"
        elif len(pending_handoffs) > 0:
            return "SAVE_PENDING"
        else:
            return "ARCHIVE_COMPLETE"

    def generate_next_steps(self) -> List[str]:
        """Generate recommended next steps for resuming."""
        tasks = self._load_json(self.tasks_file)
        context = self._load_json(self.context_file)

        next_steps = []

        # Find tasks ready to work on
        for task_id, task in tasks.items():
            state = task.get("current_state")
            assignee = task.get("assignee")

            if state == "implementing":
                next_steps.append(
                    f"Continue implementation of '{task.get('title')}' (Task: {task_id}, Agent: {assignee})"
                )
            elif state == "reviewing":
                next_steps.append(
                    f"Complete code review for '{task.get('title')}' (Task: {task_id})"
                )
            elif state == "testing":
                next_steps.append(
                    f"Finish testing '{task.get('title')}' (Task: {task_id})"
                )
            elif state == "blocked":
                blockers = task.get("blockers", [])
                next_steps.append(
                    f"Resolve blockers for '{task.get('title')}': {', '.join(blockers)}"
                )

        if not next_steps:
            next_steps.append("All tasks complete or no active tasks")

        return next_steps[:5]  # Return top 5

    def end_session(self, status: str = "paused", create_final_checkpoint: bool = True):
        """End the current session gracefully."""
        session = self._load_session()
        if not session:
            return

        if create_final_checkpoint:
            self.create_checkpoint(
                checkpoint_name=f"session_end_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=f"Session ended with status: {status}",
            )

        session.status = status
        session.unsaved_changes = False
        self._save_session(session)

    def export_session_report(self, output_file: Optional[str] = None) -> str:
        """Export a markdown report of the current session."""
        summary = self.generate_exit_summary()
        next_steps = self.generate_next_steps()
        tasks = self._load_json(self.tasks_file)

        output_path: Path
        if not output_file:
            output_path = (
                self.dev_team_dir / f"session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )
        else:
            output_path = Path(output_file)

        report_lines = [
            f"# Session Report: {summary['session_id']}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Last Checkpoint:** {summary['last_checkpoint'] or 'None'}",
            "",
            "## Summary",
            "",
            f"- Total Tasks: {summary['total_tasks']}",
            f"- Active Tasks: {summary['active_tasks']}",
            f"- Completed Tasks: {summary['completed_tasks']}",
            f"- Blocked Tasks: {summary['blocked_tasks']}",
            f"- Unsaved Changes: {'Yes' if summary['has_unsaved_changes'] else 'No'}",
            "",
            "## Active Agents",
            "",
        ]

        if summary["active_agents"]:
            for agent in summary["active_agents"]:
                report_lines.append(f"- {agent}")
        else:
            report_lines.append("- None")

        report_lines.extend(
            [
                "",
                "## Pending Handoffs",
                "",
            ]
        )

        if summary["pending_handoffs"]:
            for handoff in summary["pending_handoffs"]:
                report_lines.append(
                    f"- Task {handoff['task_id']}: {handoff['agent']} ({handoff['state']})"
                )
        else:
            report_lines.append("- None")

        report_lines.extend(
            [
                "",
                "## Recommended Next Steps",
                "",
            ]
        )

        for i, step in enumerate(next_steps, 1):
            report_lines.append(f"{i}. {step}")

        report_lines.extend(
            [
                "",
                "## Task Details",
                "",
            ]
        )

        for task_id, task in tasks.items():
            report_lines.extend(
                [
                    f"### {task_id}: {task.get('title')}",
                    "",
                    f"- **State:** {task.get('current_state')}",
                    f"- **Assignee:** {task.get('assignee')}",
                    f"- **Priority:** {task.get('priority')}",
                    f"- **Created:** {task.get('created_at')}",
                    f"- **Updated:** {task.get('updated_at')}",
                ]
            )

            if task.get("blockers"):
                report_lines.append("- **Blockers:**")
                for blocker in task["blockers"]:
                    report_lines.append(f"  - {blocker}")

            if task.get("dependencies"):
                report_lines.append(
                    f"- **Dependencies:** {', '.join(task['dependencies'])}"
                )

            report_lines.append("")

        report_lines.extend(
            [
                "",
                "## Resume Instructions",
                "",
                "To resume this session:",
                "",
                "```bash",
                f"python scripts/session_manager.py resume {summary['session_id']}",
                "",
                "# Or restore from last checkpoint",
                f"python scripts/session_manager.py restore {summary['last_checkpoint'] or 'checkpoint_name'}",
                "```",
            ]
        )

        with open(output_path, "w") as f:
            f.write("\n".join(report_lines))

        return str(output_path)


def main():
    """Command-line interface for session management."""
    if len(sys.argv) < 2:
        print("Usage: session_manager.py <command> [args...]")
        print("Commands:")
        print("  start [description]              Start a new session")
        print("  status                           Show current session status")
        print("  checkpoint [name] [description]  Create a checkpoint")
        print("  list-checkpoints                 List all checkpoints")
        print("  restore <checkpoint_id>          Restore from checkpoint")
        print("  has-changes                      Check for unsaved changes")
        print("  summary                          Show exit summary")
        print("  next-steps                       Show recommended next steps")
        print("  end [status]                     End session (status: paused/complete)")
        print("  export [output_file]             Export session report")
        sys.exit(1)

    manager = SessionManager()
    command = sys.argv[1]

    try:
        if command == "start":
            description = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            session_id = manager.start_session(description)
            print(f"Started session: {session_id}")

        elif command == "status":
            session = manager.get_current_session()
            if session:
                print(json.dumps(asdict(session), indent=2))
            else:
                print("No active session")

        elif command == "checkpoint":
            name = sys.argv[2] if len(sys.argv) > 2 else None
            description = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
            checkpoint_id = manager.create_checkpoint(name, description)
            print(f"Created checkpoint: {checkpoint_id}")

        elif command == "list-checkpoints":
            checkpoints = manager.list_checkpoints()
            if checkpoints:
                print("Available checkpoints:")
                for cp in checkpoints:
                    print(f"\n  {cp['checkpoint_id']}")
                    print(f"    Timestamp: {cp['timestamp']}")
                    print(f"    Session: {cp['session_id']}")
                    print(f"    Tasks: {cp['task_count']}")
                    if cp["description"]:
                        print(f"    Description: {cp['description']}")
            else:
                print("No checkpoints found")

        elif command == "restore":
            if len(sys.argv) < 3:
                print("Usage: session_manager.py restore <checkpoint_id>")
                sys.exit(1)
            checkpoint_id = sys.argv[2]
            if manager.restore_checkpoint(checkpoint_id):
                print(f"Restored from checkpoint: {checkpoint_id}")
            else:
                print(f"Failed to restore checkpoint: {checkpoint_id}")
                sys.exit(1)

        elif command == "has-changes":
            has_changes = manager.has_unsaved_changes()
            print(f"Unsaved changes: {'Yes' if has_changes else 'No'}")
            sys.exit(0 if not has_changes else 1)

        elif command == "summary":
            summary = manager.generate_exit_summary()
            print(json.dumps(summary, indent=2))

        elif command == "next-steps":
            steps = manager.generate_next_steps()
            print("Recommended next steps:")
            for i, step in enumerate(steps, 1):
                print(f"{i}. {step}")

        elif command == "end":
            status = sys.argv[2] if len(sys.argv) > 2 else "paused"
            manager.end_session(status)
            print(f"Session ended with status: {status}")

        elif command == "export":
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            report_path = manager.export_session_report(output_file)
            print(f"Session report exported to: {report_path}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
