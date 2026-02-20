#!/usr/bin/env python3
"""
Shared knowledge store for the agent team orchestrator.
Provides cross-session, cross-agent memory for reusable knowledge entries.
Agents can read relevant knowledge and contribute new insights, patterns, and decisions.
"""

import json
import math
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class KnowledgeEntry:
    """Represents a single knowledge entry in the shared store."""

    knowledge_id: str
    title: str
    category: str
    content: str
    summary: str
    tags: List[str]
    agent_author: str
    related_tasks: List[str]
    created_at: str
    updated_at: str
    access_count: int = 0
    confidence: str = "high"
    status: str = "active"
    supersedes: Optional[str] = None
    project_scope: str = "global"


class KnowledgeStore:
    """Manages the shared team knowledge store for cross-session, cross-agent memory."""

    VALID_CATEGORIES = [
        "convention",
        "architecture",
        "bug_fix",
        "security",
        "performance",
        "pattern",
        "lesson_learned",
        "dependency",
        "testing",
        "devops",
        "documentation",
    ]
    VALID_CONFIDENCES = ["high", "medium", "low"]
    VALID_STATUSES = ["active", "deprecated", "archived"]

    AGENT_CATEGORY_MAP = {
        "architect": [
            "architecture",
            "convention",
            "dependency",
            "security",
            "performance",
        ],
        "coder": ["pattern", "bug_fix", "convention", "performance", "testing"],
        "pr_reviewer": ["convention", "security", "architecture", "pattern"],
        "qa_tester": ["testing", "bug_fix", "performance"],
        "debug": ["bug_fix", "performance", "lesson_learned"],
        "docs": ["documentation", "convention"],
        "devops": ["devops", "dependency", "security"],
        "security": ["security", "convention", "dependency"],
        "coordinator": ["lesson_learned", "architecture"],
    }

    _STOP_WORDS: Set[str] = {
        "a",
        "an",
        "the",
        "is",
        "in",
        "on",
        "at",
        "to",
        "of",
        "for",
        "with",
        "and",
        "or",
        "not",
        "this",
        "that",
    }

    def __init__(self, project_root: str = "."):
        # Use global .dev_team directory (configurable via DEV_TEAM_DIR env var)
        self.project_root = Path(project_root).resolve()
        dev_team_path = os.getenv("DEV_TEAM_DIR", str(Path.home() / ".dev_team"))
        self.dev_team_dir = Path(dev_team_path).expanduser()
        self.knowledge_file = self.dev_team_dir / "knowledge.json"
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensure the knowledge storage directory and file exist."""
        self.dev_team_dir.mkdir(exist_ok=True)
        if not self.knowledge_file.exists():
            self._save_knowledge({})

    def _load_knowledge(self) -> Dict[str, Any]:
        """Load all knowledge entries from storage."""
        try:
            with open(self.knowledge_file, "r") as f:
                data = json.load(f)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_knowledge(self, knowledge: Dict[str, Any]):
        """Save all knowledge entries to storage using atomic write."""
        tmp_path = self.knowledge_file.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(knowledge, f, indent=2, default=str)
        tmp_path.replace(self.knowledge_file)

    def _next_id(self, knowledge: Dict[str, Any]) -> str:
        """Generate the next sequential knowledge ID."""
        if not knowledge:
            return "know_001"
        try:
            max_num = max(int(k.split("_")[1]) for k in knowledge.keys())
            return f"know_{max_num + 1:03d}"
        except (ValueError, IndexError):
            return f"know_{len(knowledge) + 1:03d}"

    def _tokenise(self, text: str) -> Set[str]:
        """Tokenise text into a set of meaningful lowercase words."""
        tokens = re.split(r"[^a-z0-9]+", text.lower())
        return {t for t in tokens if t and t not in self._STOP_WORDS}

    # ------------------------------------------------------------------
    # Public write methods
    # ------------------------------------------------------------------

    def add_entry(
        self,
        title: str,
        category: str,
        content: str,
        summary: str,
        tags: List[str],
        agent_author: str,
        related_tasks: Optional[List[str]] = None,
        confidence: str = "high",
        project_scope: str = "global",
    ) -> str:
        """Add a new knowledge entry and return its knowledge_id."""
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category: {category!r}. Valid categories: {self.VALID_CATEGORIES}"
            )
        if confidence not in self.VALID_CONFIDENCES:
            raise ValueError(
                f"Invalid confidence: {confidence!r}. Valid values: {self.VALID_CONFIDENCES}"
            )

        knowledge = self._load_knowledge()
        knowledge_id = self._next_id(knowledge)
        now = datetime.now().isoformat()

        entry = {
            "knowledge_id": knowledge_id,
            "title": title,
            "category": category,
            "content": content,
            "summary": summary,
            "tags": tags,
            "agent_author": agent_author,
            "related_tasks": related_tasks or [],
            "created_at": now,
            "updated_at": now,
            "access_count": 0,
            "confidence": confidence,
            "status": "active",
            "supersedes": None,
            "project_scope": project_scope,
        }

        knowledge[knowledge_id] = entry
        self._save_knowledge(knowledge)
        return knowledge_id

    def update_entry(
        self,
        knowledge_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None,
        confidence: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        """Partially update a knowledge entry (only provided fields are changed)."""
        knowledge = self._load_knowledge()
        if knowledge_id not in knowledge:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        entry = knowledge[knowledge_id]

        if title is not None:
            entry["title"] = title
        if content is not None:
            entry["content"] = content
        if summary is not None:
            entry["summary"] = summary
        if tags is not None:
            entry["tags"] = tags
        if confidence is not None:
            if confidence not in self.VALID_CONFIDENCES:
                raise ValueError(
                    f"Invalid confidence: {confidence!r}. Valid values: {self.VALID_CONFIDENCES}"
                )
            entry["confidence"] = confidence
        if status is not None:
            if status not in self.VALID_STATUSES:
                raise ValueError(
                    f"Invalid status: {status!r}. Valid values: {self.VALID_STATUSES}"
                )
            entry["status"] = status

        entry["updated_at"] = datetime.now().isoformat()
        self._save_knowledge(knowledge)

    def deprecate_entry(
        self, knowledge_id: str, superseded_by: Optional[str] = None
    ) -> None:
        """Deprecate a knowledge entry, optionally linking to the replacement entry."""
        knowledge = self._load_knowledge()
        if knowledge_id not in knowledge:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        knowledge[knowledge_id]["status"] = "deprecated"
        knowledge[knowledge_id]["updated_at"] = datetime.now().isoformat()

        if superseded_by is not None:
            if superseded_by not in knowledge:
                raise ValueError(f"Replacement entry {superseded_by} not found")
            knowledge[knowledge_id]["replaced_by"] = superseded_by
            knowledge[superseded_by]["supersedes"] = knowledge_id
            knowledge[superseded_by]["updated_at"] = datetime.now().isoformat()

        self._save_knowledge(knowledge)

    def add_tags(self, knowledge_id: str, tags: List[str]) -> None:
        """Add additional tags to an existing knowledge entry (deduplicates)."""
        knowledge = self._load_knowledge()
        if knowledge_id not in knowledge:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        existing = set(knowledge[knowledge_id]["tags"])
        for tag in tags:
            existing.add(tag)
        knowledge[knowledge_id]["tags"] = sorted(existing)
        knowledge[knowledge_id]["updated_at"] = datetime.now().isoformat()
        self._save_knowledge(knowledge)

    def link_task(self, knowledge_id: str, task_id: str) -> None:
        """Link a task ID to a knowledge entry."""
        knowledge = self._load_knowledge()
        if knowledge_id not in knowledge:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        if task_id not in knowledge[knowledge_id]["related_tasks"]:
            knowledge[knowledge_id]["related_tasks"].append(task_id)
            knowledge[knowledge_id]["updated_at"] = datetime.now().isoformat()
            self._save_knowledge(knowledge)

    # ------------------------------------------------------------------
    # Public read methods
    # ------------------------------------------------------------------

    def get_entry(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a full knowledge entry by ID and increment its access count."""
        knowledge = self._load_knowledge()
        if knowledge_id not in knowledge:
            return None

        knowledge[knowledge_id]["access_count"] += 1
        self._save_knowledge(knowledge)
        return dict(knowledge[knowledge_id])

    def search(
        self,
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        agent_author: Optional[str] = None,
        task_id: Optional[str] = None,
        status: str = "active",
        project_scope: Optional[str] = None,
        limit: int = 10,
        include_content: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge entries with relevance scoring.

        Hard-filters on status, project_scope, categories, tags, agent_author, task_id,
        then scores by query relevance, confidence, popularity, and recency.
        Returns summaries (content field excluded) sorted by descending score.
        """
        knowledge = self._load_knowledge()
        query_tokens = self._tokenise(query) if query else set()

        confidence_multipliers = {"high": 1.0, "medium": 0.85, "low": 0.7}

        results: List[tuple] = []  # (score, entry_dict)

        now = datetime.now()

        for entry in knowledge.values():
            # --- Hard filters ---
            if status and entry.get("status") != status:
                continue
            if project_scope and entry.get("project_scope") != project_scope:
                continue
            if categories and entry.get("category") not in categories:
                continue
            if tags:
                entry_tags = set(entry.get("tags", []))
                if not entry_tags.intersection(tags):
                    continue
            if agent_author and entry.get("agent_author") != agent_author:
                continue
            if task_id and task_id not in entry.get("related_tasks", []):
                continue

            # --- Relevance scoring ---
            score = 0.0

            if query_tokens:
                title_tokens = self._tokenise(entry.get("title", ""))
                tag_tokens = self._tokenise(" ".join(entry.get("tags", [])))
                summary_tokens = self._tokenise(entry.get("summary", ""))
                content_tokens = self._tokenise(entry.get("content", ""))

                score += len(query_tokens & title_tokens) * 4
                score += len(query_tokens & tag_tokens) * 3
                score += len(query_tokens & summary_tokens) * 2
                score += len(query_tokens & content_tokens) * 1
            else:
                # No query: neutral base score so all entries are included
                score = 1.0

            # Confidence multiplier
            conf = entry.get("confidence", "high")
            score *= confidence_multipliers.get(conf, 1.0)

            # Popularity boost
            access_count = entry.get("access_count", 0)
            score += math.log10(access_count + 1) * 0.5

            # Recency penalty (days since last update)
            try:
                updated_at = datetime.fromisoformat(
                    entry.get("updated_at", now.isoformat())
                ).replace(tzinfo=None)
                days_old = (now - updated_at).days
            except (ValueError, TypeError):
                days_old = 0
            score -= days_old * 0.01

            results.append((score, entry))

        # Sort descending by score
        results.sort(key=lambda x: x[0], reverse=True)

        # Build result list, optionally including the full content field
        summaries = []
        for _, entry in results[:limit]:
            if include_content:
                summaries.append(dict(entry))
            else:
                summaries.append({k: v for k, v in entry.items() if k != "content"})

        return summaries

    def get_for_agent(
        self,
        agent: str,
        context_keywords: Optional[List[str]] = None,
        limit: int = 5,
        include_content: bool = False,
    ) -> List[Dict[str, Any]]:
        """Retrieve the most relevant knowledge entries for a specific agent role."""
        agent_categories = self.AGENT_CATEGORY_MAP.get(agent, [])
        query = " ".join(context_keywords or [])
        return self.search(
            query=query if query else None,
            categories=agent_categories if agent_categories else None,
            limit=limit,
            include_content=include_content,
        )

    def list_by_category(
        self, category: str, status: str = "active"
    ) -> List[Dict[str, Any]]:
        """List all knowledge entries in a given category filtered by status (summaries only)."""
        knowledge = self._load_knowledge()
        results = []
        for entry in knowledge.values():
            if (
                entry.get("category") == category
                and entry.get("status", "active") == status
            ):
                results.append({k: v for k, v in entry.items() if k != "content"})
        return results

    def list_all(
        self,
        status: str = "active",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return a paginated list of all knowledge entries (summaries only)."""
        knowledge = self._load_knowledge()
        filtered = [
            {k: v for k, v in entry.items() if k != "content"}
            for entry in knowledge.values()
            if entry.get("status") == status
        ]
        return filtered[offset : offset + limit]

    def get_stats(self) -> Dict[str, Any]:
        """Return aggregate statistics about the knowledge store."""
        knowledge = self._load_knowledge()

        by_category: Dict[str, int] = {}
        by_agent: Dict[str, int] = {}
        by_confidence: Dict[str, int] = {}
        most_accessed: Optional[Dict[str, Any]] = None
        most_accessed_count = -1

        for entry in knowledge.values():
            cat = entry.get("category", "unknown")
            by_category[cat] = by_category.get(cat, 0) + 1

            author = entry.get("agent_author", "unknown")
            by_agent[author] = by_agent.get(author, 0) + 1

            conf = entry.get("confidence", "unknown")
            by_confidence[conf] = by_confidence.get(conf, 0) + 1

            count = entry.get("access_count", 0)
            if count > most_accessed_count:
                most_accessed_count = count
                most_accessed = {
                    "knowledge_id": entry.get("knowledge_id"),
                    "title": entry.get("title"),
                    "access_count": count,
                }

        return {
            "total_entries": len(knowledge),
            "active_entries": sum(
                1 for e in knowledge.values() if e.get("status", "active") == "active"
            ),
            "by_category": by_category,
            "by_agent": by_agent,
            "by_confidence": by_confidence,
            "by_status": {
                "active": sum(
                    1
                    for e in knowledge.values()
                    if e.get("status", "active") == "active"
                ),
                "deprecated": sum(
                    1 for e in knowledge.values() if e.get("status") == "deprecated"
                ),
                "archived": sum(
                    1 for e in knowledge.values() if e.get("status") == "archived"
                ),
            },
            "most_accessed": most_accessed,
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_flags(args: List[str]) -> tuple:
    """Parse --key value style flags from args list. Returns (positional, flags_dict)."""
    positional: List[str] = []
    flags: Dict[str, str] = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--"):
            key = args[i][2:]
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                flags[key] = args[i + 1]
                i += 2
            else:
                flags[key] = ""
                i += 1
        else:
            positional.append(args[i])
            i += 1
    return positional, flags


def main():
    """Command-line interface for the knowledge store."""
    if len(sys.argv) < 2:
        print("Usage: knowledge_store.py <command> [args...]")
        print("Commands:")
        print(
            "  add <title> <category> <content> <summary> <tags_csv> <agent> [task_ids_csv] [confidence]"
        )
        print(
            "  update <knowledge_id> [--title T] [--content C] [--summary S] [--tags csv] [--confidence C] [--status S]"
        )
        print("  get <knowledge_id>")
        print(
            "  search <query> [--category C] [--tags csv] [--agent A] [--task <task_id>] [--limit N] [--show-content]"
        )
        print("  list [--category C] [--limit N] [--offset N]")
        print("  deprecate <knowledge_id> [superseded_by_id]")
        print("  link-task <knowledge_id> <task_id>")
        print("  tag <knowledge_id> <tags_csv>")
        print("  for-agent <agent_name> [keywords_csv] [--limit N] [--show-content]")
        print("  stats")
        sys.exit(1)

    store = KnowledgeStore()
    command = sys.argv[1]
    rest = sys.argv[2:]

    try:
        if command == "add":
            if len(rest) < 6:
                print(
                    "Usage: knowledge_store.py add <title> <category> <content> "
                    "<summary> <tags_csv> <agent> [task_ids_csv] [confidence]"
                )
                sys.exit(1)
            title = rest[0]
            category = rest[1]
            content = rest[2]
            summary = rest[3]
            tags = [t.strip() for t in rest[4].split(",") if t.strip()]
            agent = rest[5]
            related_tasks = (
                [t.strip() for t in rest[6].split(",") if t.strip()]
                if len(rest) > 6 and rest[6]
                else []
            )
            confidence = rest[7] if len(rest) > 7 else "high"
            kid = store.add_entry(
                title=title,
                category=category,
                content=content,
                summary=summary,
                tags=tags,
                agent_author=agent,
                related_tasks=related_tasks,
                confidence=confidence,
            )
            print(f"Created knowledge {kid}: {title}")

        elif command == "update":
            if not rest:
                print("Usage: knowledge_store.py update <knowledge_id> [--title T] ...")
                sys.exit(1)
            positional, flags = _parse_flags(rest)
            knowledge_id = positional[0]
            tags_val = None
            if "tags" in flags:
                tags_val = [t.strip() for t in flags["tags"].split(",") if t.strip()]
            store.update_entry(
                knowledge_id=knowledge_id,
                title=flags.get("title"),
                content=flags.get("content"),
                summary=flags.get("summary"),
                tags=tags_val,
                confidence=flags.get("confidence"),
                status=flags.get("status"),
            )
            print(f"Updated knowledge entry {knowledge_id}")

        elif command == "get":
            if not rest:
                print("Usage: knowledge_store.py get <knowledge_id>")
                sys.exit(1)
            knowledge_id = rest[0]
            entry = store.get_entry(knowledge_id)
            if entry:
                print(json.dumps(entry, indent=2))
            else:
                print(f"Knowledge entry {knowledge_id} not found")
                sys.exit(1)

        elif command == "search":
            positional, flags = _parse_flags(rest)
            query = positional[0] if positional else None
            categories = (
                [c.strip() for c in flags["category"].split(",") if c.strip()]
                if "category" in flags
                else None
            )
            tags = (
                [t.strip() for t in flags["tags"].split(",") if t.strip()]
                if "tags" in flags
                else None
            )
            agent_author = flags.get("agent")
            task_filter = flags.get("task")
            limit = int(flags.get("limit", 10))
            show_content = "show-content" in flags
            results = store.search(
                query=query,
                categories=categories,
                tags=tags,
                agent_author=agent_author,
                task_id=task_filter,
                limit=limit,
                include_content=show_content,
            )
            print(json.dumps(results, indent=2))

        elif command == "list":
            positional, flags = _parse_flags(rest)
            category = flags.get("category")
            limit = int(flags.get("limit", 50))
            offset = int(flags.get("offset", 0))
            if category:
                results = store.list_by_category(category, status="active")
                print(json.dumps(results, indent=2))
            else:
                results = store.list_all(limit=limit, offset=offset)
                print(json.dumps(results, indent=2))

        elif command == "deprecate":
            if not rest:
                print(
                    "Usage: knowledge_store.py deprecate <knowledge_id> [superseded_by_id]"
                )
                sys.exit(1)
            knowledge_id = rest[0]
            superseded_by = rest[1] if len(rest) > 1 else None
            store.deprecate_entry(knowledge_id, superseded_by)
            msg = f"Deprecated knowledge entry {knowledge_id}"
            if superseded_by:
                msg += f" (superseded by {superseded_by})"
            print(msg)

        elif command == "link-task":
            if len(rest) < 2:
                print("Usage: knowledge_store.py link-task <knowledge_id> <task_id>")
                sys.exit(1)
            knowledge_id = rest[0]
            task_id = rest[1]
            store.link_task(knowledge_id, task_id)
            print(f"Linked task {task_id} to knowledge entry {knowledge_id}")

        elif command == "tag":
            if len(rest) < 2:
                print("Usage: knowledge_store.py tag <knowledge_id> <tags_csv>")
                sys.exit(1)
            knowledge_id = rest[0]
            tags = [t.strip() for t in rest[1].split(",") if t.strip()]
            store.add_tags(knowledge_id, tags)
            print(f"Added tags to knowledge entry {knowledge_id}")

        elif command == "for-agent":
            if not rest:
                print(
                    "Usage: knowledge_store.py for-agent <agent_name> [keywords_csv] [--limit N] [--show-content]"
                )
                sys.exit(1)
            positional, flags = _parse_flags(rest)
            agent_name = positional[0]
            keywords: Optional[List[str]] = None
            if len(positional) > 1:
                keywords = [k.strip() for k in positional[1].split(",") if k.strip()]
            limit = int(flags.get("limit", 5))
            show_content = "show-content" in flags
            results = store.get_for_agent(
                agent_name, keywords, limit=limit, include_content=show_content
            )
            print(json.dumps(results, indent=2))

        elif command == "stats":
            stats = store.get_stats()
            print(json.dumps(stats, indent=2))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
