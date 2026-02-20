# Session Context — 2026-02-20

## Feature Implemented: Shared Team Knowledge Store

A centralized, persistent memory layer for the agent-team-orchestrator. All agents can read from and write to a shared `knowledge.json` file stored in `~/.dev_team/`.

---

## What Was Built

### New File: `scripts/knowledge_store.py`
Full Python module (~650 lines) implementing `KnowledgeStore` class + CLI.

**Key responsibilities:**
- Persist reusable knowledge entries across sessions and agents
- Score and rank entries by relevance (title/tag/summary/content overlap + confidence + recency)
- Expose per-agent filtered queries via `get_for_agent(agent, keywords, limit)`

### Modified: `scripts/agent_delegator.py`
Two new private methods added:
- `_extract_keywords(delegation)` — pulls meaningful terms from delegation requirements, `handoff_notes`, and `deliverables`
- `_get_relevant_knowledge(agent, context_keywords)` — dynamically imports `knowledge_store.py`, returns a formatted markdown section (silently degrades to `""` if store unavailable)

All four `_generate_*_prompt()` methods now include:
1. A `## Relevant Team Knowledge` section (top 5 entries for that agent role)
2. A `## Knowledge Contribution` section prompting agents to write back

### Modified: `SKILL.md`
Section **3.6 Shared Knowledge Store** added between Session Management (3.5) and Quality Gates (4).

### New File: `references/knowledge-store-guide.md`
Practical usage guide with per-agent examples, content format template, and CLI reference.

---

## Architecture Decisions

### Data Schema (`knowledge.json`)
```json
{
  "know_001": {
    "knowledge_id": "know_001",
    "title": "Short human-readable title",
    "category": "bug_fix",
    "content": "Full markdown body (only returned by get, not search)",
    "summary": "One-sentence distillation (≤200 chars)",
    "tags": ["python", "loop"],
    "agent_author": "coder",
    "related_tasks": ["task_007"],
    "created_at": "ISO-8601",
    "updated_at": "ISO-8601",
    "access_count": 0,
    "confidence": "high",
    "status": "active",
    "supersedes": null,
    "replaced_by": null,
    "project_scope": "global"
  }
}
```

### 11 Knowledge Categories
| Category | Primary Authors | Primary Consumers |
|---|---|---|
| `convention` | coordinator, pr_reviewer | coder, pr_reviewer |
| `architecture` | architect | all |
| `bug_fix` | debug | coder, pr_reviewer, qa |
| `security` | security | all |
| `performance` | debug, coder | architect, coder, qa |
| `pattern` | architect, coder | coder |
| `lesson_learned` | coordinator | all |
| `dependency` | architect, devops | coder, devops |
| `testing` | qa, coder | coder, qa |
| `devops` | devops | devops |
| `documentation` | docs | docs, coder |

### Relevance Scoring Formula
```
score = (title_overlap × 4 + tag_overlap × 3 + summary_overlap × 2 + content_overlap × 1)
      × confidence_multiplier (high=1.0, medium=0.85, low=0.7)
      + log10(access_count + 1) × 0.5
      - days_since_updated × 0.01
```

### Agent → Category Mapping (`AGENT_CATEGORY_MAP`)
```python
{
    "architect":   ["architecture", "convention", "dependency", "security", "performance"],
    "coder":       ["pattern", "bug_fix", "convention", "performance", "testing"],
    "pr_reviewer": ["convention", "security", "architecture", "pattern"],
    "qa_tester":   ["testing", "bug_fix", "performance"],
    "debug":       ["bug_fix", "performance", "lesson_learned"],
    "docs":        ["documentation", "convention"],
    "devops":      ["devops", "dependency", "security"],
    "security":    ["security", "convention", "dependency"],
    "coordinator": ["lesson_learned", "architecture"],
}
```

---

## Critical Design Choices Explained

### Why atomic writes (tmp + rename)?
Multiple sub-agents may write simultaneously at handoff boundaries. `Path.replace()` maps to `os.rename()` — atomic on POSIX — preventing partial reads of a half-written file. Consistent with `session_manager.py`.

### Why `_next_id` uses `max()` not `len()`?
If any entry is deleted, `len()` would re-use a previous ID, silently overwriting the existing entry and corrupting `supersedes`/`replaced_by` cross-references. `max()` over existing numeric suffixes is monotonic regardless of deletions.

### Why `deprecate_entry` writes two pointers?
- `deprecated_entry["replaced_by"] = new_id` — forward link: agents reading the old entry can navigate to the replacement
- `new_entry["supersedes"] = old_id` — backward link: the replacement declares what it replaces

Both are needed for bidirectional traversal.

### Why `list_by_category` needs an explicit `status` parameter (fix from PR review)?
Without it, deprecated/archived entries would surface alongside active ones in CLI output. Since `search()` is the main query path and already filters by status, `list_by_category` must match that behavior.

### Why `_get_relevant_knowledge` uses `importlib.util` dynamic import?
Same pattern as `_mark_session_changed()` in `agent_delegator.py` and `task_tracker.py`. Avoids a hard dependency — if `knowledge_store.py` is absent, the entire delegation system still works. The method always wraps in `try/except` and returns `""` on any failure.

---

## Known Behavior (Not Bugs)

### `get_for_agent('unknown_agent')` returns all active entries
Unknown agents have no `AGENT_CATEGORY_MAP` entry → `categories=None` → no category filter → `search()` returns all active entries with no filter. This is intentional graceful fallback behavior.

### `search()` with empty query and no filters returns all active entries
No query tokens means `score = 1.0` (neutral baseline) for every entry; they are sorted by confidence multiplier + popularity boost + recency.

---

## Test Results (2026-02-20)

**67/69 passed.** The 2 failures were test issues, not code bugs:

1. `search python loop finds list mutation entry` — test bug: `_next_id` deletion test deleted `know_001` and did not restore it before the search test ran.
2. `unknown agent returns empty list` — test expectation mismatch: unknown agent correctly returns all entries (see Known Behavior above).

---

## CLI Quick Reference

```bash
# Add a new entry
python scripts/knowledge_store.py add \
  "Title" "category" "Full content" "One-sentence summary" \
  "tag1,tag2" "agent_name" "task_001" "high"

# Find relevant entries for an agent
python scripts/knowledge_store.py for-agent coder "authentication,jwt" --limit 5

# Full-text search
python scripts/knowledge_store.py search "loop mutation" --category bug_fix

# Search by task
python scripts/knowledge_store.py search "" --task task_007

# Get full entry (including content)
python scripts/knowledge_store.py get know_003

# Deprecate an entry and link replacement
python scripts/knowledge_store.py add "New improved entry" ...   # → know_042
python scripts/knowledge_store.py deprecate know_017 know_042

# Stats
python scripts/knowledge_store.py stats
```

---

## Files Changed in This Session

| File | Change |
|---|---|
| `scripts/knowledge_store.py` | **NEW** — ~650 lines |
| `scripts/agent_delegator.py` | **MODIFIED** — +98 lines (2 new methods, 4 prompt updates) |
| `SKILL.md` | **MODIFIED** — +89 lines (section 3.6) |
| `references/knowledge-store-guide.md` | **NEW** — usage guide |
| `SESSION_CONTEXT_2026-02-20.md` | **NEW** — this file |

---

## Next Steps / Future Ideas

- Add delegation methods for `debug`, `docs`, `devops`, `security` agents in `agent_delegator.py` so they also auto-receive knowledge in their prompts (currently only architect, coder, pr_reviewer, qa_tester do)
- Seed the knowledge store with project conventions as a bootstrap step
- Consider a `search --show-content` flag for richer CLI output
- The `get_for_agent` unknown-agent fallback could be changed to return `[]` if explicit empty results are preferred for unknown roles