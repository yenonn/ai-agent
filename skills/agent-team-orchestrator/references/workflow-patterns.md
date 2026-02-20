# Development Workflow Patterns

## Standard Development Workflow

### Feature Development Flow
1. **Requirements Analysis** (Architect)
   - Analyze user requirements
   - Create technical specifications
   - Design system architecture
   - Select technology stack
   - Define success criteria

2. **Implementation Planning** (Coder)
   - Review architectural specifications
   - Break down into implementation tasks
   - Create development plan
   - Set up development environment

3. **Code Implementation** (Coder)
   - Write clean, maintainable code
   - Create comprehensive tests
   - Document code and APIs
   - Follow coding standards

4. **Code Review** (PR Reviewer)
   - Review code quality and architecture compliance
   - Check security and performance
   - Validate test coverage
   - Provide actionable feedback

5. **QA Testing** (QA/Tester)
   - Execute test scenarios
   - Validate edge cases
   - Performance testing
   - Sign-off or report issues

6. **Iteration Cycle** (All)
   - Address review/QA feedback
   - Re-review as needed
   - Approve final implementation

### Bug Fix Workflow
1. **Root Cause Analysis** (Architect)
   - Identify issue scope and impact
   - Design fix strategy
   - Plan testing approach

2. **Implementation** (Coder)
   - Implement targeted fix
   - Add regression tests
   - Update documentation

3. **Verification** (PR Reviewer + QA)
   - Review fix approach
   - Validate testing strategy
   - Confirm no regressions

### Refactoring Workflow
1. **Analysis** (Architect)
   - Identify refactoring goals
   - Plan refactoring strategy
   - Define success criteria

2. **Implementation** (Coder)
   - Implement refactoring in steps
   - Maintain functionality
   - Update tests accordingly

3. **Validation** (PR Reviewer + QA)
   - Verify no functionality broken
   - Check performance improvements
   - Validate code quality improvements

## Parallel Execution Patterns

### Pattern 1: Independent Components
When multiple components can be developed independently with no shared state:

```
┌─────────────────────────────────────────────────────────┐
│                    ARCHITECT PHASE                       │
│  (Single architect designs all components together)      │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  IMPLEMENTATION PHASE                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Coder A   │  │   Coder B   │  │   Coder C   │     │
│  │  (Auth)     │  │  (API)      │  │  (DB)       │     │
│  │  Task_002   │  │  Task_003   │  │  Task_004   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│        │                │                │               │
│        ▼                ▼                ▼               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Reviewer A │  │  Reviewer B │  │  Reviewer C │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     INTEGRATION                          │
│  (Final review of combined components)                   │
└─────────────────────────────────────────────────────────┘
```

**When to use:**
- Components have well-defined interfaces
- No shared mutable state
- Clear separation of concerns
- Each component can be tested independently

**Example:**
```bash
# Create main task
python scripts/task_tracker.py create "User Management System" "architect"

# Create parallel subtasks
python scripts/task_tracker.py subtask task_001 "Auth Service" "coder" --parallel-group auth_system
python scripts/task_tracker.py subtask task_001 "User Profile Service" "coder" --parallel-group auth_system
python scripts/task_tracker.py subtask task_001 "Permission Service" "coder" --parallel-group auth_system
```

### Pattern 2: Staggered Handoff
For components with dependencies:

```
┌─────────────┐
│  Architect  │ (Plans all components)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Coder A    │ → Reviewer A → APPROVED
│ (Core API)  │
└──────┬──────┘
       │ (passes interface contract)
       ▼
┌─────────────┐
│  Coder B    │ → Reviewer B → APPROVED
│ (Client A)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Coder C    │ → Reviewer C → APPROVED
│ (Client B)  │
└─────────────┘
```

**When to use:**
- Components depend on interfaces from others
- API contracts need to be established first
- Sequential dependencies between modules

### Pattern 3: Fan-Out/Fan-In
For processing pipelines:

```
                    ┌─────────────┐
                    │  Architect  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Coder     │
                    │ (Framework) │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │   Coder A   │  │   Coder B   │  │   Coder C   │
  │ (Plugin 1)  │  │ (Plugin 2)  │  │ (Plugin 3)  │
  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │     QA      │
                    │ (Integration)│
                    └─────────────┘
```

## Handoff Protocols

### Architect → Coder Handoff
**Required Information:**
- Technical specifications document
- Architecture diagrams
- API design documentation
- Database schema (if applicable)
- Technology stack decisions with rationale
- Security considerations
- Performance requirements
- Success criteria and quality gates

**Success Criteria:**
- Coder has complete understanding of requirements
- All technical decisions documented
- Implementation constraints clearly defined
- Success metrics established
- Dependencies identified

**Context to Preserve:**
```json
{
  "architect_decisions": {
    "tech_stack": "...",
    "patterns": "...",
    "security_model": "...",
    "performance_targets": "..."
  },
  "constraints": [...],
  "risks": [...]
}
```

### Coder → PR Reviewer Handoff
**Required Information:**
- Complete implementation
- Test results and coverage report
- Performance benchmarks (if applicable)
- Security checklist completion
- Documentation updates
- Self-review notes

**Success Criteria:**
- All requirements implemented and tested
- Code passes linting/type checking
- Documentation complete
- Ready for production deployment

**Context to Preserve:**
```json
{
  "implementation_details": {
    "files_changed": [...],
    "patterns_used": [...],
    "deviations_from_spec": [...],
    "known_limitations": [...]
  },
  "test_coverage": {...}
}
```

### PR Reviewer → Coder Iteration
**Required Information:**
- Detailed review findings with severity
- Priority classification of issues
- Specific improvement suggestions
- Code examples for fixes
- Timeline expectations

**Success Criteria:**
- All critical issues resolved
- High-priority issues addressed
- Code quality standards met
- Ready for re-review

**Feedback Format:**
```
CRITICAL: [Description] 
  - File: path/to/file.py:123
  - Fix: [Specific action]
  - Reason: [Why it matters]

HIGH: [Description]
  - File: path/to/file.py:456
  - Suggestion: [Recommended fix]
```

### PR Reviewer → QA Handoff
**Required Information:**
- Review approval status
- Test coverage summary
- Known edge cases
- Areas needing manual testing
- Performance expectations

**Success Criteria:**
- Code review approved
- Automated tests passing
- Ready for validation testing

## Quality Gates

### Architecture Gate
- [ ] Requirements fully analyzed
- [ ] Technical specifications complete
- [ ] Architecture approved
- [ ] Technology stack justified
- [ ] Success criteria defined
- [ ] Risks identified and mitigated
- [ ] Security model documented

### Implementation Gate
- [ ] All features implemented
- [ ] Tests cover >80% of code
- [ ] Performance benchmarks met
- [ ] Security checklist passed
- [ ] Documentation complete
- [ ] Code follows style guide
- [ ] No linting errors

### Review Gate
- [ ] No critical security issues
- [ ] No critical performance issues
- [ ] Architectural compliance verified
- [ ] Code quality standards met
- [ ] All high-priority feedback addressed
- [ ] Tests are meaningful and robust

### QA Gate
- [ ] All functional requirements validated
- [ ] Edge cases tested
- [ ] Integration tests passing
- [ ] Performance within bounds
- [ ] No regressions detected
- [ ] Documentation accurate

## Error Recovery Patterns

### Blocked Task Recovery
```
1. Identify blocker source
2. Create resolution subtask
3. Assign to appropriate agent
4. Track resolution progress
5. Resume original task
```

### Failed Review Recovery
```
1. Document all issues with severity
2. Prioritize by impact
3. Create fix plan
4. Implement fixes incrementally
5. Re-review only changed areas
6. Track iteration count
7. Escalate if max iterations exceeded
```

### Context Loss Recovery
```
1. Review task history
2. Check delegation records
3. Summarize known state
4. Re-delegate with summary
5. Get user confirmation if critical
```

## Task Decomposition Patterns

### Vertical Slice Decomposition
Break by feature (each subtask is a complete feature):

```
Task: User Management
├── Subtask: User Registration (full stack)
├── Subtask: User Authentication (full stack)
├── Subtask: User Profile (full stack)
└── Subtask: User Permissions (full stack)
```

**Pros:** Each subtask is independently deployable
**Cons:** May duplicate effort across layers

### Horizontal Layer Decomposition
Break by technical layer:

```
Task: User Management
├── Subtask: Database Schema (DB layer)
├── Subtask: API Endpoints (API layer)
├── Subtask: Business Logic (Service layer)
└── Subtask: UI Components (Frontend layer)
```

**Pros:** Clear technical separation
**Cons:** Higher coordination overhead, must be sequential

### Hybrid Decomposition
Combine both approaches:

```
Task: User Management
├── Subtask: Auth (vertical slice)
│   ├── DB: Users table
│   ├── API: /auth/*
│   └── UI: Login form
├── Subtask: Profile (vertical slice)
│   ├── DB: Profiles table
│   ├── API: /profile/*
│   └── UI: Profile page
└── Subtask: Shared Components (horizontal)
    ├── Auth middleware
    └── User model
```

## Metrics to Track

### Per Task
- Time in each state
- Iteration count
- Number of blockers
- Review pass rate
- Test coverage achieved

### Team Level
- Average cycle time
- Throughput (tasks/week)
- WIP (work in progress) count
- Bottleneck identification
- Quality gate pass rates

### Agent Performance
- Average time per delegation
- Context preservation score
- Handoff success rate
- Feedback quality score
