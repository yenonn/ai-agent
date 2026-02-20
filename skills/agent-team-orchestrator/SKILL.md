---
name: agent-team-orchestrator
description: Coordinates a multi-agent team consisting of Architect, PR Reviewer, Coder, Debug Agent, Docs Agent, DevOps Agent, and Security Agent for software development workflows. Use when you need architectural planning, code review, implementation coordination, bug investigation, documentation, CI/CD setup, or security audits. Triggers when user requests team-based development with role specialization.
---

# Agent Team Orchestrator

Coordinates a multi-agent team for comprehensive software development workflows with parallel execution support and intelligent task decomposition.

## Team Roles

### Architect Agent
- Analyzes requirements and creates technical architecture
- Designs system components and data flow
- Makes technology stack decisions
- Creates technical specifications and blueprints
- Considers security, performance, and scalability
- Defines success criteria and quality gates

### Coder Agent
- Implements features based on architectural specifications
- Writes clean, maintainable, modular code
- Creates comprehensive tests (unit, integration, e2e)
- Documents code and APIs thoroughly
- Addresses review feedback iteratively
- Follows software design patterns (SOLID, DRY, KISS)
- Ensures code is extensible and human-readable

### PR Reviewer Agent
- Reviews code for quality, security, and best practices
- Validates architectural compliance
- Checks test coverage (>80% target)
- Provides actionable, prioritized feedback
- Security vulnerability assessment
- Performance and scalability review

### Debug Agent
- Investigates and diagnoses bugs and issues
- Analyzes error logs, stack traces, and reproduction steps
- Identifies root causes using systematic debugging approaches
- Proposes targeted fixes with minimal code changes
- Verifies fixes resolve the issue without regressions
- Documents bug causes and prevention strategies
- Collaborates with Coder on complex fixes

### Docs Agent
- Writes and maintains project documentation
- Creates comprehensive README files and getting started guides
- Documents APIs, endpoints, and data models
- Writes tutorials and usage examples
- Maintains changelogs and release notes
- Ensures documentation stays in sync with code
- Reviews documentation for clarity and completeness

### DevOps Agent
- Designs and implements CI/CD pipelines
- Manages deployment configurations and strategies
- Creates infrastructure as code (Terraform, CloudFormation, etc.)
- Configures monitoring, logging, and alerting
- Optimizes build processes and deployment speed
- Manages environment configurations
- Handles container orchestration (Docker, Kubernetes)

### Security Agent
- Performs security audits and vulnerability assessments
- Reviews authentication and authorization implementations
- Scans dependencies for known vulnerabilities
- Identifies security anti-patterns and risks
- Reviews data handling and encryption practices
- Validates input sanitization and output encoding
- Creates security reports with remediation steps

### QA/Tester Agent (Optional)
- Creates comprehensive test strategies
- Validates edge cases and error handling
- Performs integration and regression testing
- Documents test scenarios and results

## Workflow Orchestration

### State Machine

```
[NEW] → [ANALYZING] → [PLANNING] → [IMPLEMENTING] → [REVIEWING] → [TESTING] → [COMPLETE]
           ↓              ↓              ↓               ↓            ↓
        (Architect)   (Architect)   (Coder)        (Reviewer)    (QA)
                          ↓              ↓               ↓
                       [ITERATION] ← ← ← ← ← ← ← ← ← ← ←

[NEW] → [DEBUGGING] → [IMPLEMENTING] → [REVIEWING] → [COMPLETE]
           ↓              ↓               ↓
        (Debug)        (Coder)        (Reviewer)

[NEW] → [DOCUMENTING] → [COMPLETE]
           ↓
        (Docs)

[NEW] → [DEVOPS] → [COMPLETE]
           ↓
        (DevOps)

[NEW] → [SECURITY_AUDIT] → [IMPLEMENTING] → [COMPLETE]
           ↓                  ↓
        (Security)          (Coder)
```

### Task States
- `new`: Task created, awaiting analysis
- `analyzing`: Architect analyzing requirements
- `planning`: Architecture and specifications being created
- `implementing`: Coder implementing features
- `debugging`: Debug Agent investigating issues
- `reviewing`: PR Reviewer examining code
- `testing`: QA validation in progress
- `documenting`: Docs Agent writing documentation
- `devops`: DevOps Agent configuring infrastructure
- `security_audit`: Security Agent performing audit
- `iteration`: Addressing feedback
- `blocked`: Task has blockers
- `complete`: Task finished and approved

### Parallel Execution Patterns

**Pattern 1: Independent Components**
When multiple components can be developed independently:
```
┌─────────────┐
│  Architect  │ (Plans all components)
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────┐
│         Parallel Implementation       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │ Coder A │ │ Coder B │ │ Coder C │ │
│  │(Auth)   │ │(API)    │ │(DB)     │ │
│  └─────────┘ └─────────┘ └─────────┘ │
└──────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│  Reviewer   │ (Reviews combined PR)
└─────────────┘
```

**Pattern 2: Staggered Handoff**
For dependent components:
```
Architect → Coder(Component A) → Reviewer(A)
                  ↓ (passes context)
            Coder(Component B) → Reviewer(B)
                  ↓
            Coder(Component C) → Reviewer(C)
```

**Pattern 3: Debug Flow**
For bug fixes and issue resolution:
```
┌─────────────┐
│    Debug    │ (Investigates & diagnoses)
└──────┬──────┘
       │ (passes root cause & fix strategy)
       ▼
┌─────────────┐
│    Coder    │ (Implements targeted fix)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Reviewer  │ (Validates fix)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Debug    │ (Verifies fix resolves issue)
└─────────────┘
```

**Pattern 4: Documentation Flow**
For documentation tasks:
```
┌─────────────┐     ┌─────────────┐
│    Coder    │ ──→ │    Docs     │
│ (implements)│     │(documents)  │
└─────────────┘     └─────────────┘

Or standalone:
┌─────────────┐
│    Docs     │ (Reviews existing code, writes docs)
└─────────────┘
```

**Pattern 5: Security Audit Flow**
For security reviews:
```
┌─────────────┐
│  Security   │ (Audits codebase)
└──────┬──────┘
       │ (findings with severity)
       ▼
┌─────────────┐
│    Coder    │ (Fixes critical/high issues)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Security   │ (Verifies fixes)
└─────────────┘
```

**Pattern 6: DevOps Flow**
For infrastructure tasks:
```
┌─────────────┐
│   DevOps    │ (Sets up CI/CD, deployment)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   DevOps    │ (Verifies pipeline works)
└─────────────┘
```

## Agent Delegation Prompts

### Architect Prompt Template

When delegating to the Architect agent, use:

```
# Architecture Analysis Request

**Task ID**: {task_id}
**Priority**: {priority}

## Requirements
{detailed_requirements}

## Context
- Project: {project_name}
- Existing Codebase: {codebase_summary}
- Constraints: {constraints}

## Deliverables Required
1. Technical specifications document
2. System architecture design (include diagrams if helpful)
3. API design documentation
4. Database schema (if applicable)
5. Technology stack decisions with rationale
6. Security considerations
7. Performance requirements
8. Success criteria and quality gates

## Output Format
Provide a structured response with:
- **Architecture Overview**: High-level design
- **Component Design**: Detailed component breakdown
- **Data Flow**: How data moves through the system
- **API Specifications**: Endpoints, request/response formats
- **Security Plan**: Authentication, authorization, data protection
- **Performance Strategy**: Caching, optimization, scaling
- **Implementation Guidance**: Priority order, dependencies, risks

After analysis, prepare handoff context for the Coder agent.
```

### Coder Prompt Template

When delegating to the Coder agent:

```
# Implementation Request

**Task ID**: {task_id}
**Assigned to**: Coder Agent
**State**: implementing

## Architectural Specifications
{architect_specs}

## Implementation Requirements
- Follow architectural specifications exactly
- Write clean, modular, extensible code
- Include comprehensive error handling
- Add inline documentation for complex logic
- Follow existing codebase patterns and conventions

## Required Deliverables
1. Working implementation matching specifications
2. Unit tests (>80% coverage target)
3. Integration tests for key workflows
4. Code documentation
5. Configuration files if needed

## Quality Standards
- [ ] All functions have docstrings/comments
- [ ] Error handling for all edge cases
- [ ] No hardcoded values (use config)
- [ ] Follows DRY and SOLID principles
- [ ] Security best practices applied
- [ ] Performance considerations addressed

## Context from Previous Agents
{previous_context}

After implementation, prepare code for PR Review.
```

### PR Reviewer Prompt Template

When delegating to the PR Reviewer:

```
# Code Review Request

**Task ID**: {task_id}
**Reviewer**: PR Reviewer Agent

## Implementation to Review
{implementation_summary}

## Files Changed
{file_list_with_descriptions}

## Review Checklist

### Security Review
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] Authentication/authorization correctness
- [ ] Sensitive data handling
- [ ] Dependencies security audit

### Code Quality
- [ ] Follows architectural specifications
- [ ] Clean, readable, maintainable code
- [ ] Proper error handling
- [ ] No code duplication
- [ ] Appropriate abstractions
- [ ] Consistent naming conventions

### Testing
- [ ] Test coverage >80%
- [ ] Edge cases covered
- [ ] Integration tests present
- [ ] Tests are meaningful (not just coverage)

### Performance
- [ ] No obvious bottlenecks
- [ ] Efficient algorithms/data structures
- [ ] Appropriate caching strategy
- [ ] Database query optimization

## Output Format
Provide structured feedback:
- **CRITICAL**: Must fix before merge (security, bugs)
- **HIGH**: Strongly recommended (quality, performance)
- **MEDIUM**: Suggested improvements
- **LOW**: Nice to have (style, minor optimizations)

If approved, provide merge recommendation.
If changes needed, list specific actionable items for iteration.
```

### QA/Tester Prompt Template

```
# Testing & Validation Request

**Task ID**: {task_id}
**QA Agent**: Tester

## Implementation Summary
{implementation_summary}

## Test Requirements
1. Validate all functional requirements met
2. Test edge cases and error scenarios
3. Integration testing across components
4. Performance validation
5. Security testing checklist

## Test Scenarios to Execute
{test_scenarios}

## Acceptance Criteria
{acceptance_criteria}

## Output Required
- Test execution results
- Bug report (if any found)
- Coverage analysis
- Sign-off recommendation
```

### Debug Agent Prompt Template

```
# Debug Investigation Request

**Task ID**: {task_id}
**Debug Agent**: Debugger
**State**: debugging

## Issue Description
{issue_description}

## Reproduction Steps
{reproduction_steps}

## Available Context
- Error logs: {error_logs}
- Stack traces: {stack_traces}
- Environment: {environment_info}
- Recent changes: {recent_changes}

## Debugging Requirements
1. Reproduce and confirm the issue
2. Identify root cause through systematic analysis
3. Trace the bug through the code path
4. Determine affected components and scope
5. Propose minimal, targeted fix
6. Identify potential side effects of fix
7. Recommend prevention strategies

## Debugging Methodology
- [ ] Verify reproduction steps work
- [ ] Analyze error messages and stack traces
- [ ] Review recent code changes in affected areas
- [ ] Check data flow and state mutations
- [ ] Identify the exact line(s) causing the issue
- [ ] Determine why the bug occurs (not just what)

## Output Format
Provide structured findings:
- **Root Cause**: Clear explanation of why the bug occurs
- **Affected Code**: Specific files and lines involved
- **Proposed Fix**: Minimal changes to resolve the issue
- **Verification Steps**: How to confirm the fix works
- **Regression Risks**: Potential side effects to watch
- **Prevention**: How to prevent similar bugs in the future

After diagnosis, prepare handoff context for the Coder agent.
```

### Docs Agent Prompt Template

```
# Documentation Request

**Task ID**: {task_id}
**Docs Agent**: Documenter
**State**: documenting

## Documentation Scope
{documentation_scope}

## Available Context
- Codebase summary: {codebase_summary}
- Recent changes: {recent_changes}
- Target audience: {target_audience}

## Documentation Requirements
1. Clear and concise writing
2. Proper formatting (markdown, structure)
3. Code examples with explanations
4. Up-to-date with current implementation
5. Covers all relevant features/APIs

## Required Deliverables
- [ ] README updates (if applicable)
- [ ] API documentation
- [ ] Usage examples and tutorials
- [ ] Configuration documentation
- [ ] Changelog entries

## Quality Standards
- [ ] Accurate and up-to-date
- [ ] Clear for target audience
- [ ] Includes practical examples
- [ ] Properly formatted
- [ ] Links to related docs

## Output Format
Provide structured documentation:
- **Overview**: High-level summary
- **Quick Start**: Getting started guide
- **Detailed Docs**: Comprehensive reference
- **Examples**: Code snippets and use cases
- **Configuration**: All configurable options
```

### DevOps Agent Prompt Template

```
# DevOps/Infrastructure Request

**Task ID**: {task_id}
**DevOps Agent**: DevOps Engineer
**State**: devops

## Infrastructure Requirements
{infrastructure_requirements}

## Current State
- Existing CI/CD: {existing_cicd}
- Deployment target: {deployment_target}
- Environments: {environments}

## Deliverables Required
1. CI/CD pipeline configuration
2. Deployment scripts and configs
3. Infrastructure as code (if needed)
4. Monitoring and logging setup
5. Environment configuration

## DevOps Checklist
- [ ] Pipeline builds successfully
- [ ] Automated tests run in pipeline
- [ ] Deployment strategy defined
- [ ] Rollback plan documented
- [ ] Monitoring configured
- [ ] Secrets management handled
- [ ] Environment parity verified

## Output Format
Provide complete DevOps setup:
- **Pipeline Config**: CI/CD configuration files
- **Deploy Strategy**: How deployments work
- **Infrastructure**: IaC files or configs
- **Monitoring**: Logs, metrics, alerts setup
- **Runbooks**: Deployment and recovery procedures
```

### Security Agent Prompt Template

```
# Security Audit Request

**Task ID**: {task_id}
**Security Agent**: Security Analyst
**State**: security_audit

## Audit Scope
{audit_scope}

## Areas to Review
- Authentication mechanisms
- Authorization and access control
- Input validation and sanitization
- Data encryption (at rest and in transit)
- Dependency vulnerabilities
- API security
- Secrets management

## Security Checklist
- [ ] Auth flows reviewed
- [ ] Input validation verified
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Secrets not exposed
- [ ] Dependencies scanned
- [ ] HTTPS enforced
- [ ] Rate limiting considered

## Output Format
Provide security assessment:
- **CRITICAL**: Immediate security risks
- **HIGH**: Significant vulnerabilities
- **MEDIUM**: Security improvements needed
- **LOW**: Best practice recommendations
- **Remediation**: Specific fix instructions for each finding
```

## Coordination Instructions

### 1. Task Intake
When receiving a new task:
1. Analyze complexity to determine if team orchestration is needed
2. Create task in tracker with appropriate type
3. Determine if task can be parallelized
4. Identify dependencies between subtasks

### 2. Agent Spawning
Use the Task tool to spawn specialized agents:

```
For architectural analysis:
Task(subagent_type="general", description="Architecture Analysis", prompt=architect_prompt)

For implementation:
Task(subagent_type="general", description="Feature Implementation", prompt=coder_prompt)

For review:
Task(subagent_type="general", description="Code Review", prompt=reviewer_prompt)

For debugging:
Task(subagent_type="general", description="Bug Investigation", prompt=debug_prompt)

For documentation:
Task(subagent_type="general", description="Documentation", prompt=docs_prompt)

For DevOps/infrastructure:
Task(subagent_type="general", description="DevOps Setup", prompt=devops_prompt)

For security audit:
Task(subagent_type="general", description="Security Audit", prompt=security_prompt)
```

### 3. Context Preservation
Between agent handoffs, preserve:
- Original requirements
- Architectural decisions and rationale
- Implementation details and patterns used
- Review feedback and changes made
- Test results and coverage data
- Debug findings and root cause analysis
- Security findings and remediation status
- Documentation changes

### 3.5 Session Management and Exit Handling

The orchestrator uses a session management system to track progress and enable graceful exits with context saving.

**Storage Location:** Session data is stored globally (default: `~/.dev_team/` in your home directory). You can customize this location using the `DEV_TEAM_DIR` environment variable:

```bash
# Use custom location
export DEV_TEAM_DIR=/path/to/storage
# Or for project-local storage
export DEV_TEAM_DIR=./.dev_team
```

**Starting a Session:**
```bash
python scripts/session_manager.py start "Project description"
```

**During Execution:**
- Session automatically tracks all task changes and delegations
- All data stored in configured directory (tasks, delegations, context, history)
- Unsaved changes are detected automatically
- Create checkpoints at key milestones:
  ```bash
  python scripts/session_manager.py checkpoint "milestone_name" "Description"
  # Or via delegator/tracker:
  python scripts/agent_delegator.py checkpoint "milestone_name" "Description"
  python scripts/task_tracker.py checkpoint "milestone_name" "Description"
  ```

**Before Exiting:**
When the orchestrator session needs to end (completion, interruption, or error), follow this protocol:

1. **Check for Unsaved Changes:**
   ```bash
   python scripts/session_manager.py has-changes
   # Or: python scripts/agent_delegator.py has-changes
   ```

2. **Generate Exit Summary:**
   ```bash
   python scripts/session_manager.py summary
   ```
   This provides:
   - Active task count
   - Pending agent handoffs
   - Blocked tasks
   - Recommended action (SAVE_PROGRESS, SAVE_WITH_BLOCKERS, SAVE_PENDING, ARCHIVE_COMPLETE)

3. **Prompt User Based on State:**
   - **Active tasks exist:** "You have N active tasks. Would you like to save your progress before exiting?"
   - **Pending handoffs:** "Agent X is awaiting input. Save context for resuming later?"
   - **All complete:** "All tasks complete. Archive this session?"
   - **Blocked tasks:** "You have N blocked tasks. Save session state?"

4. **Save Options:**
   - **Create Checkpoint:** Quick save of current state
     ```bash
     python scripts/session_manager.py checkpoint "exit_checkpoint" "Session paused"
     ```
   - **Export Report:** Generate detailed markdown report + checkpoint
     ```bash
     python scripts/session_manager.py export [output_file]
     ```
   - **End Session:** Mark session as paused or complete
     ```bash
     python scripts/session_manager.py end paused  # or: complete
     ```

5. **Show Next Steps:**
   ```bash
   python scripts/session_manager.py next-steps
   ```
   Displays recommended actions for resuming work.

**Resuming a Session:**
```bash
# List available checkpoints
python scripts/session_manager.py list-checkpoints

# Restore from specific checkpoint
python scripts/session_manager.py restore checkpoint_20240101_123000

# Check session status after restore
python scripts/session_manager.py status
```

### 3.6 Shared Knowledge Store

The orchestrator maintains a shared knowledge store that persists reusable insights, patterns, decisions, and lessons across sessions and agents. Agents automatically receive relevant entries in their prompts and can contribute new knowledge after completing tasks.

**Storage Location:** Knowledge data is stored alongside other team state (default: `~/.dev_team/knowledge.json`). Configurable via the `DEV_TEAM_DIR` environment variable, same as sessions and tasks.

#### Purpose

The knowledge store provides cross-session, cross-agent memory for:
- Architectural decisions that apply to future work
- Coding patterns standardised by the team
- Bug fixes and lessons learned from past issues
- Security mitigations and conventions
- Performance optimisations that have been validated

#### Reading Knowledge

Agents receive relevant knowledge entries automatically in their delegation prompts. They can also query the store directly:

```bash
# Get entries relevant to a specific agent role and context
python scripts/knowledge_store.py for-agent coder "authentication,jwt" --limit 5

# Search by keyword across all entries
python scripts/knowledge_store.py search "" --category security --limit 10

# Retrieve a specific entry by ID
python scripts/knowledge_store.py get know_003
```

#### Writing Knowledge

After completing a task, agents should contribute if they discovered anything reusable:

```bash
python scripts/knowledge_store.py add "title" "category" "content" "summary" "tags" "agent_name" "task_id" "high"
```

Example:

```bash
python scripts/knowledge_store.py add \
  "Always validate JWT expiry before processing requests" \
  "security" \
  "Discovered that the auth middleware was not checking exp claim. Added explicit expiry validation using datetime.utcnow(). This prevents replay attacks with expired tokens." \
  "Validate JWT exp claim explicitly in middleware; do not rely on library defaults alone." \
  "jwt,auth,security,middleware" \
  "coder" \
  "task_014" \
  "high"
```

#### When to Write

Contribute a knowledge entry when you discover:
- A non-obvious bug and its root cause
- An architectural decision with lasting impact on the codebase
- A security issue that was mitigated and should not recur
- A performance optimisation that was validated with measurement
- A coding pattern that should be standardised across the team

#### Categories

| Category | Description |
|---|---|
| `convention` | Code style, naming, and structural conventions the team follows |
| `architecture` | High-level design decisions and system structure choices |
| `bug_fix` | Root causes of bugs and the fixes applied |
| `security` | Vulnerabilities found, mitigations applied, and security patterns |
| `performance` | Bottlenecks identified and optimisations validated |
| `pattern` | Reusable implementation patterns and idioms |
| `lesson_learned` | Retrospective insights and process improvements |
| `dependency` | Third-party library decisions, version constraints, and gotchas |
| `testing` | Test strategies, coverage patterns, and testing conventions |
| `devops` | CI/CD, deployment, and infrastructure decisions |
| `documentation` | Documentation standards and conventions |

#### Deprecating Stale Knowledge

When a knowledge entry becomes outdated, add a corrected version first, then deprecate the old one:

```bash
# Add corrected version first
python scripts/knowledge_store.py add "Updated JWT validation approach" "security" "..." "..." "jwt,auth" "architect" "task_042" "high"

# Deprecate the old entry, linking to the replacement
python scripts/knowledge_store.py deprecate know_017 know_042
```

### 4. Quality Gates
Before transitioning between states:
- Debug → Coder: Root cause identified, fix strategy documented
- Security → Coder: Vulnerabilities prioritized, fix requirements clear
- Architect → Coder: Architecture must be approved
- Coder → Reviewer: All tests passing, basic self-review done
- Reviewer → Complete: No critical issues, all high-priority addressed
- Coder → Docs: Implementation complete, ready for documentation

### 5. Iteration Handling
When review requires changes:
1. Document specific issues clearly
2. Prioritize by severity
3. Coder addresses in priority order
4. Re-review only changed areas
5. Track iteration count (max 3 recommended)

## Usage Patterns

### Complex Feature Development
```
1. Create task → delegate to Architect
2. Review architecture → approve or iterate
3. Parallelize implementation if possible
4. Sequential review with integration focus
5. QA validation
6. Final approval and merge
```

### Bug Fix Workflow
```
1. Create task with reproduction steps
2. Debug Agent investigates and identifies root cause
3. Coder implements targeted fix based on diagnosis
4. Reviewer validates fix approach
5. QA confirms fix and no regressions
```

### Complex Bug Workflow
```
1. Create task with reproduction steps and context
2. Debug Agent investigates root cause
3. Architect reviews fix strategy (if architectural impact)
4. Coder implements fix
5. Reviewer validates fix
6. Debug Agent verifies fix resolves issue
7. QA confirms no regressions
```

### Refactoring Workflow
```
1. Architect analyzes current state and target state
2. Define migration strategy with rollback plan
3. Incremental implementation with tests
4. Review each increment
5. Full regression testing
6. Docs Agent updates documentation
```

### Documentation Workflow
```
1. Docs Agent reviews codebase
2. Identify documentation gaps
3. Write/update documentation
4. Coder reviews for accuracy
5. Final approval
```

### Security Audit Workflow
```
1. Security Agent scans codebase
2. Identify vulnerabilities by severity
3. Coder addresses critical/high issues
4. Security Agent verifies fixes
5. Document security posture
```

### DevOps Setup Workflow
```
1. DevOps Agent analyzes deployment needs
2. Design CI/CD pipeline
3. Create infrastructure configs
4. Test pipeline end-to-end
5. Document deployment process
```

## Task Delegation Guidelines

| Task Type | Primary Agent | Support Agents | Parallel Safe |
|-----------|---------------|----------------|---------------|
| New Feature | Architect → Coder | Reviewer, QA, Docs | Partial |
| Bug Fix | Debug → Coder | Reviewer | No |
| Complex Bug | Debug → Architect → Coder | Reviewer | No |
| Refactoring | Architect → Coder | Reviewer, Docs | Partial |
| Performance | Debug → Architect → Coder | Reviewer, QA | No |
| Security | Security → Coder | Reviewer | No |
| Documentation | Docs | Reviewer | Yes |
| DevOps/CI-CD | DevOps | Reviewer | Partial |
| Security Audit | Security | Coder (if fixes needed) | Yes |

## Error Recovery

### Blocked Tasks
1. Identify blocker source
2. Escalate to user if external dependency
3. Create subtask to resolve blocker
4. Resume when resolved

### Failed Reviews
1. Document all issues clearly
2. Provide code examples for fixes
3. Set priority for each issue
4. Track iteration count
5. Escalate if >3 iterations

### Context Loss
1. Review task history
2. Check delegation records
3. Re-delegate with summary context
4. User confirmation if critical context missing

## Metrics Tracking

Track for continuous improvement:
- Average time per state transition
- Iteration count per task type
- Review pass rate
- Test coverage trends
- Blocker frequency
- Debug accuracy rate (fixes that resolve issues on first attempt)
- Average debug investigation time
- Security vulnerability count by severity
- Documentation freshness (time since last update)
- Deployment success rate
- Pipeline build times

## Best Practices

1. **Start with Architecture**: Never skip planning phase
2. **Preserve Context**: Always pass full context between agents
3. **Parallelize Wisely**: Only parallelize independent components
4. **Review Thoroughly**: Never skip code review
5. **Test Continuously**: Tests should be written with code
6. **Document Decisions**: Keep architectural decision records
7. **Limit Iterations**: Set max iteration count to prevent loops
8. **Escalate Early**: Don't hesitate to ask user for clarification
9. **Debug Before Fixing**: Always investigate root cause before implementing fixes
10. **Minimal Bug Fixes**: Prefer targeted fixes over broad refactoring for bugs
11. **Docs With Code**: Document features as they're implemented
12. **Security First**: Run security audits on authentication/authorization changes
13. **Automate DevOps**: Prefer automated pipelines over manual deployments
