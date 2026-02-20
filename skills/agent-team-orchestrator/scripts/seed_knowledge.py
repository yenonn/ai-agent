#!/usr/bin/env python3
"""
Bootstrap seed for the shared team knowledge store.

Populates the knowledge store with project-level conventions, patterns, and
architecture decisions that all agents should be aware of from the start.

Usage:
    python scripts/seed_knowledge.py [--dry-run] [--force]

Options:
    --dry-run   Print entries that would be created without writing anything.
    --force     Re-seed even if the store already contains entries (adds new;
                does not overwrite existing entries).
"""

import importlib.util
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Seed data
# Each entry is a dict matching KnowledgeStore.add_entry() parameters.
# ---------------------------------------------------------------------------

SEED_ENTRIES = [
    # ---- Conventions -------------------------------------------------------
    {
        "title": "Atomic file writes with tmp-rename pattern",
        "category": "convention",
        "content": (
            "All JSON persistence in the agent-team-orchestrator uses an atomic "
            "write pattern: write to a .tmp file first, then rename to the target "
            "path. Example:\n\n"
            "    tmp_path = target.with_suffix('.tmp')\n"
            "    with open(tmp_path, 'w') as f:\n"
            "        json.dump(data, f, indent=2)\n"
            "    tmp_path.replace(target)\n\n"
            "Path.replace() maps to os.rename(), which is atomic on POSIX. This "
            "prevents partial reads when multiple sub-agents write simultaneously."
        ),
        "summary": "Always write JSON to a .tmp file then rename to target for atomic, corruption-safe persistence.",
        "tags": ["json", "persistence", "atomic", "concurrency", "file-io"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    {
        "title": "Monotonic ID generation with max() not len()",
        "category": "convention",
        "content": (
            "Sequential IDs (e.g. know_001, task_003) must be generated using "
            "max() over existing numeric suffixes, not len(). If any entry is "
            "deleted, len() would re-use a previous ID, silently overwriting "
            "existing data and corrupting cross-reference fields "
            "(supersedes / replaced_by).\n\n"
            "Pattern:\n"
            "    max_num = max(int(k.split('_')[1]) for k in store.keys())\n"
            "    next_id = f'prefix_{max_num + 1:03d}'"
        ),
        "summary": "Use max() over existing numeric suffixes for sequential IDs — never len() — to stay monotonic after deletions.",
        "tags": ["id-generation", "convention", "data-integrity"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    {
        "title": "Dynamic imports for optional module dependencies",
        "category": "convention",
        "content": (
            "When a module optionally depends on another script in the same "
            "directory, use importlib.util to load it dynamically rather than a "
            "top-level import. This keeps the module functional even if the "
            "dependency is absent. Always wrap in try/except and return a safe "
            "default on failure.\n\n"
            "Pattern used in agent_delegator.py for session_manager and "
            "knowledge_store:\n\n"
            "    spec = importlib.util.spec_from_file_location('mod', path)\n"
            "    mod = importlib.util.module_from_spec(spec)\n"
            "    spec.loader.exec_module(mod)\n"
            "    result = mod.SomeClass().method()\n"
        ),
        "summary": "Use importlib.util for optional same-directory dependencies; always catch exceptions and return a safe default.",
        "tags": ["importlib", "optional-dependency", "resilience", "convention"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    {
        "title": "DEV_TEAM_DIR environment variable for storage location",
        "category": "convention",
        "content": (
            "All persistent storage (tasks, delegations, context, history, "
            "knowledge, sessions) is kept in a single configurable directory. "
            "The default is ~/.dev_team/. The location is overridden with the "
            "DEV_TEAM_DIR environment variable.\n\n"
            "Every script that touches storage must resolve the path via:\n"
            "    dev_team_path = os.getenv('DEV_TEAM_DIR', str(Path.home() / '.dev_team'))\n"
            "    dev_team_dir = Path(dev_team_path).expanduser()\n\n"
            "This allows project-local storage (./.dev_team) or CI-specific paths "
            "without code changes."
        ),
        "summary": "All storage goes under DEV_TEAM_DIR (default ~/.dev_team/); always resolve via os.getenv before constructing paths.",
        "tags": ["storage", "configuration", "environment", "convention"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    # ---- Architecture ------------------------------------------------------
    {
        "title": "Agent orchestration state machine",
        "category": "architecture",
        "content": (
            "The orchestrator follows a state machine with these valid states:\n"
            "  new → analyzing → planning → implementing → reviewing → testing → complete\n"
            "  new → debugging → implementing → reviewing → complete\n"
            "  new → documenting → complete\n"
            "  new → devops → complete\n"
            "  new → security_audit → implementing → complete\n\n"
            "State is tracked in delegations.json and context.json under ~/.dev_team/. "
            "Each state transition is recorded in history.json (capped at 100 entries). "
            "Invalid state transitions should raise ValueError."
        ),
        "summary": "The orchestrator is a state machine; valid transitions are defined in AgentDelegator.VALID_STATES and must be enforced.",
        "tags": ["state-machine", "orchestration", "architecture", "workflow"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    {
        "title": "Knowledge relevance scoring formula",
        "category": "architecture",
        "content": (
            "Knowledge entries are ranked for agent prompts using:\n\n"
            "  score = (title_overlap × 4 + tag_overlap × 3\n"
            "           + summary_overlap × 2 + content_overlap × 1)\n"
            "        × confidence_multiplier  (high=1.0, medium=0.85, low=0.7)\n"
            "        + log10(access_count + 1) × 0.5\n"
            "        - days_since_updated × 0.01\n\n"
            "When no query is provided, base score = 1.0 (neutral), so all "
            "entries pass and are sorted by confidence × popularity − recency."
        ),
        "summary": "Relevance score = text-overlap weighted sum × confidence × popularity boost − recency penalty.",
        "tags": ["relevance-scoring", "knowledge-store", "architecture", "ranking"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    {
        "title": "Agent-to-knowledge-category mapping",
        "category": "architecture",
        "content": (
            "Each agent role is mapped to the knowledge categories most relevant "
            "to its work. The mapping in KnowledgeStore.AGENT_CATEGORY_MAP is:\n\n"
            "  architect:   architecture, convention, dependency, security, performance\n"
            "  coder:       pattern, bug_fix, convention, performance, testing\n"
            "  pr_reviewer: convention, security, architecture, pattern\n"
            "  qa_tester:   testing, bug_fix, performance\n"
            "  debug:       bug_fix, performance, lesson_learned\n"
            "  docs:        documentation, convention\n"
            "  devops:      devops, dependency, security\n"
            "  security:    security, convention, dependency\n"
            "  coordinator: lesson_learned, architecture\n\n"
            "Unknown agents receive no category filter (all active entries returned)."
        ),
        "summary": "AGENT_CATEGORY_MAP defines which knowledge categories each agent role receives by default in get_for_agent().",
        "tags": ["agent-roles", "knowledge-store", "architecture", "category-map"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    # ---- Patterns ----------------------------------------------------------
    {
        "title": "Bidirectional deprecation links (replaced_by / supersedes)",
        "category": "pattern",
        "content": (
            "When deprecating a knowledge entry, two pointers are written:\n"
            "  deprecated_entry['replaced_by'] = new_id   # forward: navigate to replacement\n"
            "  new_entry['supersedes'] = old_id            # backward: replacement declares origin\n\n"
            "Both are needed for bidirectional traversal. Never write only one pointer. "
            "This pattern is implemented in KnowledgeStore.deprecate_entry()."
        ),
        "summary": "Deprecation requires two pointers: replaced_by on the old entry AND supersedes on the new one — both directions.",
        "tags": ["deprecation", "knowledge-store", "pattern", "data-integrity"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    {
        "title": "Stop-word filtering for keyword extraction",
        "category": "pattern",
        "content": (
            "When extracting keywords from free-text for knowledge relevance "
            "queries, filter out common English stop words and short tokens "
            "(len <= 3). Strip punctuation before comparing. Deduplicate "
            "preserving order and cap at 15 keywords to keep queries focused.\n\n"
            "This pattern is used in AgentDelegator._extract_keywords() and "
            "KnowledgeStore._tokenise()."
        ),
        "summary": "Strip stop words, short tokens, and punctuation when extracting keywords; cap at 15 deduplicated terms.",
        "tags": ["keyword-extraction", "nlp", "pattern", "knowledge-store"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "medium",
    },
    # ---- Security ----------------------------------------------------------
    {
        "title": "Never hardcode secrets — use environment variables or a secrets manager",
        "category": "security",
        "content": (
            "No credentials, API keys, tokens, or passwords should ever appear "
            "in source code or committed JSON files. Use environment variables for "
            "local development and a secrets manager (e.g. AWS Secrets Manager, "
            "GitHub Actions Secrets, HashiCorp Vault) in CI/CD and production.\n\n"
            "The .dev_team/ directory may contain session data with task context — "
            "never put raw secrets in task requirements or handoff notes."
        ),
        "summary": "Secrets belong in environment variables or a secrets manager — never in source code, JSON files, or task context.",
        "tags": ["secrets", "security", "credentials", "best-practice"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    # ---- Testing -----------------------------------------------------------
    {
        "title": "Test isolation: restore shared state after destructive test cases",
        "category": "testing",
        "content": (
            "Tests that delete or mutate shared store entries (e.g. removing "
            "know_001 to test _next_id behaviour) must restore the original state "
            "in teardown, or run in an isolated tmp directory.\n\n"
            "Two failures in the knowledge_store test suite (2026-02-20) were "
            "caused by a deletion test that did not restore know_001 before the "
            "subsequent search test ran, causing a false failure.\n\n"
            "Pattern: use setUp/tearDown with a temp DEV_TEAM_DIR, or use "
            "unittest.mock.patch to isolate the storage path per test."
        ),
        "summary": "Destructive tests (deletes/mutations) must isolate state via tmp dirs or teardown restore — otherwise later tests get false failures.",
        "tags": ["testing", "isolation", "teardown", "test-design", "lesson-learned"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
    # ---- Lesson learned ----------------------------------------------------
    {
        "title": "Unknown agent in get_for_agent() returns all active entries (intentional)",
        "category": "lesson_learned",
        "content": (
            "KnowledgeStore.get_for_agent('unknown_agent') returns all active "
            "entries, not an empty list. This is intentional graceful fallback: "
            "unknown agents have no AGENT_CATEGORY_MAP entry → categories=None "
            "→ no category filter in search() → all active entries returned.\n\n"
            "A test that asserted an empty list for an unknown agent was written "
            "against a misunderstood expectation. The behaviour is correct. "
            "Document this clearly in any future test assertions."
        ),
        "summary": "get_for_agent('unknown') returns all active entries by design — no category filter applied for unknown roles.",
        "tags": ["knowledge-store", "unknown-agent", "fallback", "lesson-learned"],
        "agent_author": "coordinator",
        "related_tasks": [],
        "confidence": "high",
    },
]


# ---------------------------------------------------------------------------
# Seeding logic
# ---------------------------------------------------------------------------


def load_knowledge_store():
    """Dynamically load KnowledgeStore from the sibling script."""
    ks_path = Path(__file__).parent / "knowledge_store.py"
    if not ks_path.exists():
        raise FileNotFoundError(f"knowledge_store.py not found at {ks_path}")
    spec = importlib.util.spec_from_file_location("knowledge_store", ks_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load knowledge_store module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module.KnowledgeStore()


def seed(dry_run: bool = False, force: bool = False) -> int:
    """
    Seed the knowledge store with bootstrap entries.

    Returns the number of entries added (or that would be added in dry-run mode).
    """
    store = load_knowledge_store()
    existing = store.list_all(limit=1000)

    if existing and not force:
        print(
            f"Knowledge store already contains {len(existing)} entries. "
            "Use --force to seed anyway (new entries will be added alongside existing ones)."
        )
        return 0

    added = 0
    for entry in SEED_ENTRIES:
        if dry_run:
            print(f"[DRY RUN] Would add: [{entry['category']}] {entry['title']}")
        else:
            kid = store.add_entry(
                title=entry["title"],
                category=entry["category"],
                content=entry["content"],
                summary=entry["summary"],
                tags=entry["tags"],
                agent_author=entry["agent_author"],
                related_tasks=entry.get("related_tasks", []),
                confidence=entry.get("confidence", "high"),
            )
            print(f"Added {kid}: [{entry['category']}] {entry['title']}")
        added += 1

    if not dry_run:
        print(f"\nSeeded {added} knowledge entries into the store.")
    else:
        print(f"\n[DRY RUN] Would seed {added} knowledge entries.")

    return added


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    try:
        count = seed(dry_run=dry_run, force=force)
        if count == 0 and not dry_run:
            sys.exit(0)  # Store already seeded — not an error
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
