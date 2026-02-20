#!/usr/bin/env python3
"""
Task tracking script for managing development team coordination.
Tracks task states, handoffs, dependencies, and progress across the multi-agent team.
Supports parallel execution, subtasks, and dependency management.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum


class TaskStatus(Enum):
    NEW = "new"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    IMPLEMENTING = "implementing"
    REVIEWING = "reviewing"
    TESTING = "testing"
    ITERATION = "iteration"
    BLOCKED = "blocked"
    COMPLETE = "complete"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class HandoffRecord:
    """Records a handoff between agents."""

    from_agent: str
    to_agent: str
    timestamp: str
    state: str
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class TaskState:
    """Represents the current state of a development task."""

    task_id: str
    title: str
    current_state: str
    assignee: str
    created_at: str
    updated_at: str
    priority: str = "medium"
    context: Dict[str, Any] = field(default_factory=dict)
    handoffs: List[Dict[str, Any]] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    parent_task: Optional[str] = None
    parallel_group: Optional[str] = None
    iteration_count: int = 0
    max_iterations: int = 3
    quality_gates: Dict[str, bool] = field(default_factory=dict)


class TaskTracker:
    """Manages task tracking and coordination for the dev team."""

    VALID_STATES = [s.value for s in TaskStatus] + [
        "debugging",
        "documenting",
        "devops",
        "security_audit",
    ]
    VALID_PRIORITIES = [p.value for p in TaskPriority]
    VALID_ASSIGNEES = [
        "architect",
        "coder",
        "pr_reviewer",
        "qa_tester",
        "coordinator",
        "debug",
        "docs",
        "devops",
        "security",
    ]

    def __init__(self, project_root: str = "."):
        # Use global .dev_team directory (configurable via DEV_TEAM_DIR env var)
        self.project_root = Path(project_root).resolve()
        dev_team_path = os.getenv("DEV_TEAM_DIR", str(Path.home() / ".dev_team"))
        self.dev_team_dir = Path(dev_team_path).expanduser()
        self.tasks_file = self.dev_team_dir / "tasks.json"
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensure the tasks storage directory exists."""
        self.dev_team_dir.mkdir(exist_ok=True)
        if not self.tasks_file.exists():
            self._save_tasks({})

    def _load_tasks(self) -> Dict[str, Any]:
        """Load all tasks from storage."""
        try:
            with open(self.tasks_file, "r") as f:
                data = json.load(f)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_tasks(self, tasks: Dict[str, Any]):
        """Save all tasks to storage."""
        with open(self.tasks_file, "w") as f:
            json.dump(tasks, f, indent=2, default=str)

    def create_task(
        self,
        title: str,
        task_type: str,
        context: Optional[Dict[str, Any]] = None,
        priority: str = "medium",
        dependencies: Optional[List[str]] = None,
        parent_task: Optional[str] = None,
        parallel_group: Optional[str] = None,
    ) -> str:
        """Create a new task and return its ID."""
        tasks = self._load_tasks()
        task_id = f"task_{len(tasks) + 1:03d}"
        now = datetime.now().isoformat()

        initial_state = "analyzing" if task_type in ["architect"] else "new"

        task = {
            "task_id": task_id,
            "title": title,
            "current_state": initial_state,
            "assignee": task_type,
            "created_at": now,
            "updated_at": now,
            "priority": priority if priority in self.VALID_PRIORITIES else "medium",
            "context": context or {},
            "handoffs": [],
            "blockers": [],
            "deliverables": [],
            "dependencies": dependencies or [],
            "subtasks": [],
            "parent_task": parent_task,
            "parallel_group": parallel_group,
            "iteration_count": 0,
            "max_iterations": 3,
            "quality_gates": {
                "architecture_approved": False,
                "tests_passing": False,
                "review_approved": False,
                "qa_validated": False,
            },
        }

        tasks[task_id] = task

        if parent_task and parent_task in tasks:
            tasks[parent_task]["subtasks"].append(task_id)

        self._save_tasks(tasks)
        return task_id

    def create_subtask(
        self,
        parent_id: str,
        title: str,
        task_type: str,
        context: Optional[Dict[str, Any]] = None,
        parallel_group: Optional[str] = None,
    ) -> str:
        """Create a subtask under a parent task."""
        return self.create_task(
            title=title,
            task_type=task_type,
            context=context,
            parent_task=parent_id,
            parallel_group=parallel_group,
        )

    def update_task_state(
        self,
        task_id: str,
        new_state: str,
        new_assignee: Optional[str] = None,
        context_update: Optional[Dict[str, Any]] = None,
        deliverable: Optional[str] = None,
        notes: str = "",
    ):
        """Update task state and track handoff."""
        tasks = self._load_tasks()
        if task_id not in tasks:
            raise ValueError(f"Task {task_id} not found")

        task = tasks[task_id]
        now = datetime.now().isoformat()

        if new_state not in self.VALID_STATES:
            raise ValueError(
                f"Invalid state: {new_state}. Valid states: {self.VALID_STATES}"
            )

        if new_assignee and new_assignee != task["assignee"]:
            if new_assignee not in self.VALID_ASSIGNEES:
                raise ValueError(f"Invalid assignee: {new_assignee}")

            handoff = {
                "from": task["assignee"],
                "to": new_assignee,
                "timestamp": now,
                "state": task["current_state"],
                "context": task["context"].copy(),
                "notes": notes,
            }
            task["handoffs"].append(handoff)
            task["assignee"] = new_assignee

        task["current_state"] = new_state
        task["updated_at"] = now

        if context_update:
            task["context"].update(context_update)

        if deliverable:
            task["deliverables"].append(deliverable)

        if new_state == "iteration":
            task["iteration_count"] += 1
            if task["iteration_count"] > task["max_iterations"]:
                task["blockers"].append(
                    f"Max iterations ({task['max_iterations']}) exceeded"
                )

        self._save_tasks(tasks)
        self._mark_session_changed()

        # Sound notifications based on new state
        if new_state == "complete":
            self._play_sound("play_success")
        elif new_state == "blocked":
            self._play_sound("play_error")
        elif new_state == "iteration":
            self._play_sound("play_iteration")
        elif new_state in ("reviewing", "testing"):
            self._play_sound("play_completion")

    def _mark_session_changed(self):
        """Mark the current session as having unsaved changes."""
        try:
            import importlib.util

            session_manager_path = Path(__file__).parent / "session_manager.py"
            if session_manager_path.exists():
                spec = importlib.util.spec_from_file_location(
                    "session_manager", session_manager_path
                )
                if spec and spec.loader:
                    session_manager = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(session_manager)
                    manager = session_manager.SessionManager()
                    manager.update_session(unsaved_changes=True)
        except Exception:
            pass

    def _play_sound(self, method_name: str):
        """Play a sound notification via SoundNotifier (silently degrades if unavailable)."""
        try:
            import importlib.util

            sn_path = Path(__file__).parent / "sound_notifications.py"
            if not sn_path.exists():
                return
            spec = importlib.util.spec_from_file_location(
                "sound_notifications", sn_path
            )
            if spec is None or spec.loader is None:
                return
            sn_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sn_module)  # type: ignore[union-attr]
            notifier = sn_module.get_notifier()
            getattr(notifier, method_name)()
        except Exception:
            pass

    def set_quality_gate(self, task_id: str, gate: str, passed: bool):
        """Set a quality gate status."""
        tasks = self._load_tasks()
        if task_id not in tasks:
            raise ValueError(f"Task {task_id} not found")

        task = tasks[task_id]
        if "quality_gates" not in task:
            task["quality_gates"] = {}

        task["quality_gates"][gate] = passed
        task["updated_at"] = datetime.now().isoformat()
        self._save_tasks(tasks)

    def add_blocker(self, task_id: str, blocker: str):
        """Add a blocker to a task."""
        tasks = self._load_tasks()
        if task_id not in tasks:
            raise ValueError(f"Task {task_id} not found")

        tasks[task_id]["blockers"].append(blocker)
        tasks[task_id]["current_state"] = "blocked"
        tasks[task_id]["updated_at"] = datetime.now().isoformat()
        self._save_tasks(tasks)
        self._play_sound("play_error")

    def remove_blocker(self, task_id: str, blocker_index: int):
        """Remove a blocker from a task."""
        tasks = self._load_tasks()
        if task_id not in tasks:
            raise ValueError(f"Task {task_id} not found")

        task = tasks[task_id]
        if 0 <= blocker_index < len(task["blockers"]):
            task["blockers"].pop(blocker_index)
            if not task["blockers"]:
                task["current_state"] = "implementing"
            task["updated_at"] = datetime.now().isoformat()
            self._save_tasks(tasks)

    def add_dependency(self, task_id: str, depends_on: str):
        """Add a dependency to a task."""
        tasks = self._load_tasks()
        if task_id not in tasks:
            raise ValueError(f"Task {task_id} not found")
        if depends_on not in tasks:
            raise ValueError(f"Dependency task {depends_on} not found")

        if depends_on not in tasks[task_id]["dependencies"]:
            tasks[task_id]["dependencies"].append(depends_on)
            tasks[task_id]["updated_at"] = datetime.now().isoformat()
            self._save_tasks(tasks)

    def get_ready_tasks(self) -> List[Dict]:
        """Get tasks that are ready to be worked on (all dependencies met)."""
        tasks = self._load_tasks()
        ready = []

        for task_id, task in tasks.items():
            if task["current_state"] in ["complete", "blocked"]:
                continue

            dependencies_met = all(
                tasks.get(dep, {}).get("current_state") == "complete"
                for dep in task["dependencies"]
            )

            if dependencies_met:
                ready.append(task)

        return ready

    def get_parallel_groups(self) -> Dict[str, List[Dict]]:
        """Get tasks grouped by their parallel execution group."""
        tasks = self._load_tasks()
        groups: Dict[str, List[Dict]] = {}

        for task in tasks.values():
            group = task.get("parallel_group")
            if group:
                if group not in groups:
                    groups[group] = []
                groups[group].append(task)

        return groups

    def can_parallelize(self, task_ids: List[str]) -> bool:
        """Check if multiple tasks can be executed in parallel."""
        tasks = self._load_tasks()

        for task_id in task_ids:
            if task_id not in tasks:
                return False

            task = tasks[task_id]
            for dep in task.get("dependencies", []):
                if dep in task_ids:
                    return False

        return True

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get comprehensive task status."""
        tasks = self._load_tasks()
        if task_id not in tasks:
            return None

        task = tasks[task_id]
        return {
            "task_id": task["task_id"],
            "title": task["title"],
            "current_state": task["current_state"],
            "assignee": task["assignee"],
            "priority": task["priority"],
            "progress": self._calculate_progress(task),
            "handoffs": len(task["handoffs"]),
            "blockers": task["blockers"],
            "deliverables": task["deliverables"],
            "dependencies": task["dependencies"],
            "subtasks": task["subtasks"],
            "iteration_count": task["iteration_count"],
            "quality_gates": task.get("quality_gates", {}),
            "created_at": task["created_at"],
            "updated_at": task["updated_at"],
        }

    def _calculate_progress(self, task: Dict) -> float:
        """Calculate task progress percentage."""
        state_weights = {
            "new": 0,
            "analyzing": 10,
            "planning": 20,
            "implementing": 50,
            "reviewing": 70,
            "testing": 85,
            "iteration": 75,
            "blocked": 50,
            "complete": 100,
        }
        base_progress = state_weights.get(task["current_state"], 0)

        quality_gates = task.get("quality_gates", {})
        gates_passed = sum(1 for v in quality_gates.values() if v)
        total_gates = len(quality_gates) if quality_gates else 1

        gate_bonus = (gates_passed / total_gates) * 10 if base_progress > 0 else 0

        return min(100, base_progress + gate_bonus)

    def get_team_status(self) -> Dict:
        """Get overall team status and task summary."""
        tasks = self._load_tasks()
        status = {
            "total_tasks": len(tasks),
            "by_state": {},
            "by_assignee": {},
            "by_priority": {},
            "active_blockers": 0,
            "completed_tasks": 0,
            "in_progress": 0,
            "ready_to_start": len(self.get_ready_tasks()),
            "parallel_groups": len(self.get_parallel_groups()),
        }

        for task in tasks.values():
            status["by_state"][task["current_state"]] = (
                status["by_state"].get(task["current_state"], 0) + 1
            )

            status["by_assignee"][task["assignee"]] = (
                status["by_assignee"].get(task["assignee"], 0) + 1
            )

            status["by_priority"][task["priority"]] = (
                status["by_priority"].get(task["priority"], 0) + 1
            )

            status["active_blockers"] += len(task["blockers"])

            if task["current_state"] == "complete":
                status["completed_tasks"] += 1
            elif task["current_state"] in ["implementing", "reviewing", "testing"]:
                status["in_progress"] += 1

        return status

    def get_task_tree(self, task_id: str) -> Dict:
        """Get task with all subtasks as a tree structure."""
        tasks = self._load_tasks()
        if task_id not in tasks:
            return {}

        def build_tree(tid: str) -> Dict:
            task = tasks.get(tid, {})
            tree = {
                "task_id": tid,
                "title": task.get("title", ""),
                "state": task.get("current_state", ""),
                "assignee": task.get("assignee", ""),
                "subtasks": [],
            }
            for subtask_id in task.get("subtasks", []):
                tree["subtasks"].append(build_tree(subtask_id))
            return tree

        return build_tree(task_id)


def main():
    """Command-line interface for task tracking."""
    if len(sys.argv) < 2:
        print("Usage: task_tracker.py <command> [args...]")
        print("Commands:")
        print("  create <title> <type> [priority]     Create a new task")
        print("  subtask <parent_id> <title> <type>   Create a subtask")
        print("  status <task_id>                     Get task status")
        print("  update <task_id> <state> [assignee]  Update task state")
        print("  team                                 Get team status")
        print("  blocker <task_id> <desc>             Add blocker to task")
        print("  unblock <task_id> <index>            Remove blocker")
        print("  depend <task_id> <depends_on>        Add dependency")
        print("  ready                                List ready tasks")
        print("  parallel                             Show parallel groups")
        print("  gate <task_id> <gate> <true|false>   Set quality gate")
        print("  tree <task_id>                       Show task tree")
        print("  session-status                       Show session status")
        print("  checkpoint [name] [desc]             Create checkpoint")
        print("  exit-summary                         Generate exit summary")
        sys.exit(1)

    tracker = TaskTracker()
    command = sys.argv[1]

    try:
        if command == "create":
            if len(sys.argv) < 4:
                print("Usage: task_tracker.py create <title> <type> [priority]")
                sys.exit(1)
            title = sys.argv[2]
            task_type = sys.argv[3]
            priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
            task_id = tracker.create_task(title, task_type, priority=priority)
            print(f"Created task {task_id}: {title}")

        elif command == "subtask":
            if len(sys.argv) < 5:
                print("Usage: task_tracker.py subtask <parent_id> <title> <type>")
                sys.exit(1)
            parent_id = sys.argv[2]
            title = sys.argv[3]
            task_type = sys.argv[4]
            task_id = tracker.create_subtask(parent_id, title, task_type)
            print(f"Created subtask {task_id}: {title} under {parent_id}")

        elif command == "status":
            if len(sys.argv) < 3:
                print("Usage: task_tracker.py status <task_id>")
                sys.exit(1)
            task_id = sys.argv[2]
            status = tracker.get_task_status(task_id)
            if status:
                print(json.dumps(status, indent=2))
            else:
                print(f"Task {task_id} not found")

        elif command == "update":
            if len(sys.argv) < 4:
                print("Usage: task_tracker.py update <task_id> <state> [assignee]")
                sys.exit(1)
            task_id = sys.argv[2]
            new_state = sys.argv[3]
            new_assignee = sys.argv[4] if len(sys.argv) > 4 else None
            tracker.update_task_state(task_id, new_state, new_assignee)
            print(f"Updated task {task_id} to {new_state}")

        elif command == "team":
            status = tracker.get_team_status()
            print(json.dumps(status, indent=2))

        elif command == "blocker":
            if len(sys.argv) < 4:
                print("Usage: task_tracker.py blocker <task_id> <description>")
                sys.exit(1)
            task_id = sys.argv[2]
            blocker = " ".join(sys.argv[3:])
            tracker.add_blocker(task_id, blocker)
            print(f"Added blocker to task {task_id}")

        elif command == "unblock":
            if len(sys.argv) < 4:
                print("Usage: task_tracker.py unblock <task_id> <index>")
                sys.exit(1)
            task_id = sys.argv[2]
            index = int(sys.argv[3])
            tracker.remove_blocker(task_id, index)
            print(f"Removed blocker {index} from task {task_id}")

        elif command == "depend":
            if len(sys.argv) < 4:
                print("Usage: task_tracker.py depend <task_id> <depends_on>")
                sys.exit(1)
            task_id = sys.argv[2]
            depends_on = sys.argv[3]
            tracker.add_dependency(task_id, depends_on)
            print(f"Added dependency: {task_id} depends on {depends_on}")

        elif command == "ready":
            ready = tracker.get_ready_tasks()
            if ready:
                print("Ready tasks:")
                for task in ready:
                    print(
                        f"  {task['task_id']}: {task['title']} ({task['current_state']})"
                    )
            else:
                print("No tasks ready to start")

        elif command == "parallel":
            groups = tracker.get_parallel_groups()
            if groups:
                print("Parallel execution groups:")
                for group, tasks in groups.items():
                    print(f"\n{group}:")
                    for task in tasks:
                        print(f"  {task['task_id']}: {task['title']}")
            else:
                print("No parallel groups defined")

        elif command == "gate":
            if len(sys.argv) < 5:
                print("Usage: task_tracker.py gate <task_id> <gate> <true|false>")
                sys.exit(1)
            task_id = sys.argv[2]
            gate = sys.argv[3]
            passed = sys.argv[4].lower() == "true"
            tracker.set_quality_gate(task_id, gate, passed)
            print(f"Set quality gate '{gate}' to {passed} for task {task_id}")

        elif command == "tree":
            if len(sys.argv) < 3:
                print("Usage: task_tracker.py tree <task_id>")
                sys.exit(1)
            task_id = sys.argv[2]
            tree = tracker.get_task_tree(task_id)
            print(json.dumps(tree, indent=2))

        elif command == "session-status":
            try:
                import importlib.util

                session_manager_path = Path(__file__).parent / "session_manager.py"
                if session_manager_path.exists():
                    spec = importlib.util.spec_from_file_location(
                        "session_manager", session_manager_path
                    )
                    if spec and spec.loader:
                        session_manager = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(session_manager)
                        manager = session_manager.SessionManager()
                        session = manager.get_current_session()
                        if session:
                            print(json.dumps(asdict(session), indent=2))
                        else:
                            print("No active session")
                else:
                    print("Session manager not found")
            except Exception as e:
                print(f"Error: {e}")

        elif command == "checkpoint":
            try:
                import importlib.util

                session_manager_path = Path(__file__).parent / "session_manager.py"
                if session_manager_path.exists():
                    spec = importlib.util.spec_from_file_location(
                        "session_manager", session_manager_path
                    )
                    if spec and spec.loader:
                        session_manager = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(session_manager)
                        manager = session_manager.SessionManager()
                        name = sys.argv[2] if len(sys.argv) > 2 else None
                        description = (
                            " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
                        )
                        checkpoint_id = manager.create_checkpoint(name, description)
                        print(f"Created checkpoint: {checkpoint_id}")
                else:
                    print("Session manager not found")
            except Exception as e:
                print(f"Error: {e}")

        elif command == "exit-summary":
            try:
                import importlib.util

                session_manager_path = Path(__file__).parent / "session_manager.py"
                if session_manager_path.exists():
                    spec = importlib.util.spec_from_file_location(
                        "session_manager", session_manager_path
                    )
                    if spec and spec.loader:
                        session_manager = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(session_manager)
                        manager = session_manager.SessionManager()
                        summary = manager.generate_exit_summary()
                        print(json.dumps(summary, indent=2))
                else:
                    print("Session manager not found")
            except Exception as e:
                print(f"Error: {e}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
