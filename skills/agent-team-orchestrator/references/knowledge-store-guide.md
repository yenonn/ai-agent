# Knowledge Store Guide

A practical reference for using the shared team knowledge store in the agent-team-orchestrator.

---

## Overview

The knowledge store is a persistent, shared memory layer for the agent team. It outlives individual sessions and is accessible by every agent role. Its purpose is to prevent the team from repeatedly re-discovering the same patterns, making the same architectural mistakes, or reproducing known bugs.

Every piece of knowledge is stored as a structured entry with:
- A human-readable **title** and **summary** (what agents see in prompts)
- Full **content** (detailed explanation, visible only when explicitly retrieved)
- A **category** (how knowledge is classified and routed to agents)
- **Tags** (for fine-grained search)
- **Confidence** level (`high`, `medium`, `low`) reflecting how certain the insight is
- A **status** (`active`, `deprecated`, `archived`) for lifecycle management

Knowledge is stored at `~/.dev_team/knowledge.json` by default, configurable via the `DEV_TEAM_DIR` environment variable.

---

## Quick Start by Agent Role

### Architect

```bash
# Read what's already known about architecture and dependencies
python scripts/knowledge_store.py for-agent architect "microservices,api,database" --limit 5

# Record a major architectural decision after completing analysis
python scripts/knowledge_store.py add \
  "Service boundary: auth is its own microservice" \
  "architecture" \
  "We decided to extract authentication into a dedicated microservice to allow independent scaling and to enforce a single point of truth for identity. This decision was made in task_005. Coupling auth to the main API was rejected because it would require redeployment of the whole API for any auth change." \
  "Auth is a standalone microservice; do not embed auth logic in the main API service." \
  "auth,microservice,architecture,boundaries" \
  "architect" \
  "task_005" \
  "high"
```

### Coder

```bash
# Check for patterns and conventions before starting implementation
python scripts/knowledge_store.py for-agent coder "authentication,jwt,python" --limit 5

# Record a coding pattern discovered during implementation
python scripts/knowledge_store.py add \
  "Use contextlib.suppress for optional cleanup steps" \
  "pattern" \
  "When cleanup operations (e.g. removing temp files) should not block the main flow, use contextlib.suppress(Exception) rather than a bare try/except pass. This is more explicit and idiomatic." \
  "Use contextlib.suppress(Exception) for non-critical cleanup instead of bare try/except." \
  "python,patterns,error-handling,cleanup" \
  "coder" \
  "task_012" \
  "high"
```

### PR Reviewer

```bash
# Check known conventions and security patterns before reviewing
python scripts/knowledge_store.py for-agent pr_reviewer "sql,input-validation,api" --limit 5

# Record a convention violation found during review
python scripts/knowledge_store.py add \
  "Never interpolate user input into SQL strings" \
  "security" \
  "Found raw string interpolation in user search handler. All user-controlled values must use parameterised queries (cursor.execute(sql, params)). Interpolation was in search.py line 42 and was fixed in task_018." \
  "Always use parameterised queries; never interpolate user input into SQL." \
  "sql,injection,security,parameterised-queries" \
  "pr_reviewer" \
  "task_018" \
  "high"
```

### Debug Agent

```bash
# Look for known bug patterns before investigating
python scripts/knowledge_store.py for-agent debug "race-condition,async,database" --limit 5

# Record the root cause and fix after resolving a bug
python scripts/knowledge_store.py add \
  "Race condition in async task queue on shutdown" \
  "bug_fix" \
  "The task queue was not draining before the event loop closed on SIGTERM. Fixed by adding a asyncio.gather(*pending_tasks) call in the shutdown handler. Root cause was missing await in cleanup path." \
  "Ensure async task queues are drained before event loop shutdown; await pending tasks in SIGTERM handler." \
  "async,race-condition,shutdown,asyncio,event-loop" \
  "debug" \
  "task_021" \
  "high"
```

### Security Agent

```bash
# Review existing security knowledge before auditing
python scripts/knowledge_store.py for-agent security "token,session,encryption" --limit 5

# Record a security finding and its mitigation
python scripts/knowledge_store.py add \
  "Session tokens must use cryptographically secure random bytes" \
  "security" \
  "Found session IDs generated with random.random() in session.py. This is not cryptographically secure. Replaced with secrets.token_urlsafe(32). The previous implementation was vulnerable to prediction attacks." \
  "Use secrets.token_urlsafe() for session/token generation, never random.random()." \
  "session,token,cryptography,random,security" \
  "security" \
  "task_025" \
  "high"
```

### DevOps Agent

```bash
# Check for existing infrastructure and deployment knowledge
python scripts/knowledge_store.py for-agent devops "docker,ci,deployment" --limit 5

# Record a deployment lesson
python scripts/knowledge_store.py add \
  "Health check endpoint must respond before service is marked ready" \
  "devops" \
  "Kubernetes readiness probe was hitting /health before the database connection pool was initialised, causing premature traffic routing. Fixed by deferring pool init to startup event and ensuring /health waits for it." \
  "Ensure /health endpoint only returns 200 after all dependencies (DB, cache) are ready." \
  "kubernetes,health-check,readiness-probe,deployment" \
  "devops" \
  "task_030" \
  "high"
```

### Docs Agent

```bash
# Find documentation conventions before writing
python scripts/knowledge_store.py for-agent docs "api,readme,openapi" --limit 5

# Record a documentation standard
python scripts/knowledge_store.py add \
  "All public API endpoints must have OpenAPI docstrings" \
  "documentation" \
  "Convention established in task_007: every FastAPI route must have a summary, description, and response_model defined. This enables automatic OpenAPI generation. Routes without these were flagged in review." \
  "Every public API route must include summary, description, and response_model for OpenAPI generation." \
  "openapi,fastapi,documentation,convention" \
  "docs" \
  "task_007" \
  "medium"
```

### QA Tester

```bash
# Check for known testing patterns and gotchas
python scripts/knowledge_store.py for-agent qa_tester "integration,fixtures,mocking" --limit 5

# Record a testing pattern discovered during test development
python scripts/knowledge_store.py add \
  "Use factory_boy fixtures for test data, not hardcoded dicts" \
  "testing" \
  "Tests using hardcoded dict literals for model data are brittle and break on schema changes. factory_boy factories automatically generate valid model instances and adapt to schema changes. Adopted in task_015." \
  "Use factory_boy instead of hardcoded dicts for generating test model instances." \
  "testing,fixtures,factory-boy,test-data" \
  "qa_tester" \
  "task_015" \
  "high"
```

---

## Content Field Format Recommendation

The `content` field should be a full explanation that gives enough context to understand and apply the knowledge without needing to re-investigate. Use the following markdown template:

```markdown
### Problem / Context
Describe the situation or problem that led to this knowledge. Include what system, component, or file was involved, and what was happening.

### Solution / Decision
Explain clearly what was done, decided, or changed. Be specific enough that another agent can apply the same approach.

### Rationale
Explain *why* this solution was chosen over alternatives. Reference trade-offs if relevant.

### Example
Include a code snippet, command, or configuration example if applicable.

```python
# Example code demonstrating the pattern
result = some_function(param)
```
```

The `summary` field should be a single sentence that captures the core actionable insight. It is what agents see in their prompts without fetching the full entry.

---

## Search Tips and Examples

### Search by keyword across all entries
```bash
python scripts/knowledge_store.py search "jwt expiry validation"
```

### Search within a specific category
```bash
python scripts/knowledge_store.py search "" --category security --limit 10
```

### Search with tag filter
```bash
python scripts/knowledge_store.py search "database" --tags "postgresql,migration"
```

### Search entries by a specific agent author
```bash
python scripts/knowledge_store.py search "" --agent architect
```

### List everything in a category
```bash
python scripts/knowledge_store.py list --category bug_fix
```

### Paginate all active entries
```bash
python scripts/knowledge_store.py list --limit 20 --offset 0
python scripts/knowledge_store.py list --limit 20 --offset 20
```

### Get full entry including content
```bash
python scripts/knowledge_store.py get know_007
```

### View overall statistics
```bash
python scripts/knowledge_store.py stats
```

---

## CLI Reference

| Command | Arguments | Description |
|---|---|---|
| `add` | `<title> <category> <content> <summary> <tags_csv> <agent> [task_ids_csv] [confidence]` | Add a new knowledge entry |
| `update` | `<id> [--title T] [--content C] [--summary S] [--tags csv] [--confidence C] [--status S]` | Partially update an entry |
| `get` | `<id>` | Retrieve full entry (including content), increments access count |
| `search` | `<query> [--category C] [--tags csv] [--agent A] [--limit N]` | Search with relevance scoring |
| `list` | `[--category C] [--limit N] [--offset N]` | List entries (summaries only) |
| `deprecate` | `<id> [superseded_by_id]` | Mark entry as deprecated, optionally link replacement |
| `link-task` | `<id> <task_id>` | Associate a task ID with an entry |
| `tag` | `<id> <tags_csv>` | Add additional tags to an entry |
| `for-agent` | `<agent_name> [keywords_csv] [--limit N]` | Get entries relevant to an agent role |
| `stats` | | Show store statistics (counts by category, agent, confidence) |

### Confidence Levels

| Value | Meaning |
|---|---|
| `high` | Verified and well-understood; safe to apply without re-validation |
| `medium` | Likely correct but may need context-specific verification |
| `low` | Provisional or experimental; treat as a hint rather than a rule |

### Status Values

| Value | Meaning |
|---|---|
| `active` | Current and applicable |
| `deprecated` | Superseded by newer knowledge; do not apply |
| `archived` | No longer relevant but kept for historical reference |