# Agent Team Integration Examples

## Example 1: New Feature Development with Parallel Execution

### Scenario: User Authentication System

**User Request**: "I need to implement a JWT-based user authentication system with role-based access control"

**Team Workflow:**

1. **Architect Analysis**:
   ```bash
   # Create main task
   python scripts/task_tracker.py create "JWT Authentication System" "architect" high

   # Delegate to architect
   python scripts/agent_delegator.py architect task_001 '{
     "feature": "JWT auth with RBAC",
     "requirements": ["login", "logout", "role management", "token refresh"],
     "constraints": ["must work with existing user database"]
   }'
   ```

2. **Create Parallel Subtasks** (after architecture approved):
   ```bash
   # Create subtasks for parallel implementation
   python scripts/task_tracker.py subtask task_001 "Auth API Endpoints" "coder" --parallel-group auth_impl
   python scripts/task_tracker.py subtask task_001 "JWT Middleware" "coder" --parallel-group auth_impl
   python scripts/task_tracker.py subtask task_001 "Role Management" "coder" --parallel-group auth_impl
   ```

3. **Coder Implementation** (parallel):
   ```bash
   # Delegate to coders in parallel
   python scripts/task_tracker.py update task_002 "implementing" "coder"
   python scripts/agent_delegator.py coder task_002 '{
     "architect_specs": "from architect analysis",
     "component": "Auth API Endpoints"
   }'

   python scripts/task_tracker.py update task_003 "implementing" "coder"
   python scripts/agent_delegator.py coder task_003 '{
     "architect_specs": "from architect analysis",
     "component": "JWT Middleware"
   }'
   ```

4. **PR Review** (per component):
   ```bash
   python scripts/agent_delegator.py reviewer task_002 '{
     "implementation": "completed auth API",
     "tests": "test coverage report"
   }'
   ```

5. **QA Validation**:
   ```bash
   python scripts/task_tracker.py update task_001 "testing" "qa_tester"
   python scripts/agent_delegator.py qa task_001 '{
     "implementation": "completed all components",
     "test_scenarios": ["login flow", "token refresh", "role checks"],
     "acceptance_criteria": ["secure auth", "proper role enforcement"]
   }'
   ```

6. **Quality Gates**:
   ```bash
   # Set quality gates as they pass
   python scripts/task_tracker.py gate task_001 architecture_approved true
   python scripts/task_tracker.py gate task_001 tests_passing true
   python scripts/task_tracker.py gate task_001 review_approved true
   python scripts/task_tracker.py gate task_001 qa_validated true
   ```

## Example 2: Bug Fix Workflow

### Scenario: Performance Issue in Data Processing

**User Request**: "The data export function is timing out with large datasets"

**Team Workflow:**

1. **Architect Analysis**:
   ```bash
   python scripts/task_tracker.py create "Data Export Performance Fix" "architect" critical
   python scripts/agent_delegator.py architect task_002 '{
     "issue": "timeout on large datasets",
     "scope": "export function",
     "impact": "high - blocking users",
     "current_behavior": "times out after 30 seconds with >10k records"
   }'
   ```

2. **Fix Strategy** (Architect):
   - Identify bottleneck (likely memory usage or inefficient queries)
   - Design solution: streaming, pagination, or optimization
   - Plan testing approach with large datasets
   - Define performance targets

3. **Implementation** (Coder):
   ```bash
   python scripts/task_tracker.py update task_002 "implementing" "coder"
   python scripts/agent_delegator.py coder task_002 '{
     "strategy": "streaming export with chunked processing",
     "approach": "process in batches of 1000 records",
     "performance_target": "<5 seconds for 100k records"
   }'
   ```

4. **Review** (PR Reviewer):
   ```bash
   python scripts/agent_delegator.py reviewer task_002 '{
     "fix": "implemented streaming solution",
     "changes": "modified export.py, added chunk_processor.py",
     "performance_test": "passes with 100k records in 3.2 seconds"
   }'
   ```

5. **QA Validation**:
   ```bash
   python scripts/agent_delegator.py qa task_002 '{
     "test_scenarios": ["1k records", "10k records", "100k records", "1M records"],
     "regression_tests": "all existing export tests pass"
   }'
   ```

## Example 3: Technical Debt Reduction

### Scenario: Legacy Code Refactoring

**User Request**: "Refactor the authentication module to use modern patterns"

**Team Workflow:**

1. **Analysis** (Architect):
   ```bash
   python scripts/task_tracker.py create "Auth Module Refactor" "architect" medium
   python scripts/agent_delegator.py architect task_003 '{
     "refactor": "auth module",
     "goal": "modern patterns",
     "constraints": ["backward compatibility", "no API changes", "gradual migration"],
     "current_issues": ["callback hell", "no error handling", "hard to test"]
   }'
   ```

2. **Planning** (Architect):
   - Identify legacy patterns to replace
   - Design target architecture
   - Plan migration strategy with phases
   - Define success criteria
   - Create rollback plan

3. **Phased Implementation** (Coder):
   ```bash
   # Phase 1: Refactor to async/await
   python scripts/task_tracker.py subtask task_003 "Phase 1: Async Conversion" "coder"
   python scripts/agent_delegator.py coder task_004 '{
     "phase": 1,
     "changes": "convert callbacks to async/await",
     "testing": "maintain existing test coverage"
   }'

   # Phase 2: Add proper error handling
   python scripts/task_tracker.py subtask task_003 "Phase 2: Error Handling" "coder"
   
   # Phase 3: Improve testability
   python scripts/task_tracker.py subtask task_003 "Phase 3: Dependency Injection" "coder"
   ```

4. **Verification** (PR Reviewer + QA):
   ```bash
   python scripts/agent_delegator.py reviewer task_003 '{
     "refactor": "completed all phases",
     "migration": "backward compatible",
     "tests": "improved coverage from 60% to 90%"
   }'
   
   python scripts/agent_delegator.py qa task_003 '{
     "regression_tests": "all existing functionality works",
     "performance_tests": "no degradation"
   }'
   ```

## Example 4: Full Integration Test

### Scenario: E-commerce Checkout Flow

**User Request**: "Build a complete checkout flow with cart, payment, and order processing"

**Complete Workflow:**

```bash
# 1. Create main task
python scripts/task_tracker.py create "E-commerce Checkout Flow" "architect" high

# 2. Architect designs the system
python scripts/agent_delegator.py architect task_005 '{
  "features": ["shopping cart", "payment processing", "order management", "inventory sync"],
  "integrations": ["Stripe API", "Inventory Service", "Email Service"],
  "requirements": ["secure payment", "real-time inventory", "order confirmation emails"]
}'

# 3. Create parallel implementation tasks
python scripts/task_tracker.py subtask task_005 "Cart Service" "coder" --parallel-group checkout
python scripts/task_tracker.py subtask task_005 "Payment Integration" "coder" --parallel-group checkout
python scripts/task_tracker.py subtask task_005 "Order Service" "coder" --parallel-group checkout

# 4. Check what tasks are ready
python scripts/task_tracker.py ready

# 5. Set dependencies (Order Service depends on Cart)
python scripts/task_tracker.py depend task_008 task_006

# 6. View parallel groups
python scripts/task_tracker.py parallel

# 7. Implementation with context passing
python scripts/agent_delegator.py coder task_006 '{
  "architect_specs": {...},
  "component": "Cart Service",
  "interfaces": ["ICartRepository", "ICartCalculator"]
}'

# 8. Review cycle
python scripts/agent_delegator.py reviewer task_006 '{...}'

# 9. If iteration needed
python scripts/task_tracker.py update task_006 "iteration" "coder"
python scripts/task_tracker.py update task_006 "reviewing" "pr_reviewer"

# 10. Final QA
python scripts/task_tracker.py update task_005 "testing" "qa_tester"
python scripts/agent_delegator.py qa task_005 '{
  "test_scenarios": [
    "add to cart",
    "update quantity",
    "remove item",
    "apply discount",
    "checkout flow",
    "payment success",
    "payment failure",
    "order confirmation"
  ],
  "integration_tests": ["Stripe integration", "Inventory sync", "Email delivery"]
}'

# 11. Set all quality gates
python scripts/task_tracker.py gate task_005 architecture_approved true
python scripts/task_tracker.py gate task_005 tests_passing true
python scripts/task_tracker.py gate task_005 review_approved true
python scripts/task_tracker.py gate task_005 qa_validated true

# 12. Complete
python scripts/task_tracker.py update task_005 "complete"

# 13. View final status
python scripts/task_tracker.py status task_005
python scripts/task_tracker.py team
```

## Command Reference Quick Guide

### Task Management
```bash
# Create tasks
python scripts/task_tracker.py create "Task Title" "architect" high
python scripts/task_tracker.py subtask task_001 "Subtask" "coder" --parallel-group group1

# View status
python scripts/task_tracker.py status task_001
python scripts/task_tracker.py team
python scripts/task_tracker.py tree task_001
python scripts/task_tracker.py ready
python scripts/task_tracker.py parallel

# Update tasks
python scripts/task_tracker.py update task_001 implementing coder
python scripts/task_tracker.py gate task_001 tests_passing true
python scripts/task_tracker.py blocker task_001 "Waiting for API key"
python scripts/task_tracker.py depend task_002 task_001
```

### Agent Delegation
```bash
# Delegate to agents
python scripts/agent_delegator.py architect task_001 '{"requirements": {...}}'
python scripts/agent_delegator.py coder task_001 '{"specs": {...}}'
python scripts/agent_delegator.py reviewer task_001 '{"implementation": {...}}'
python scripts/agent_delegator.py qa task_001 '{"test_info": {...}}'

# View delegation info
python scripts/agent_delegator.py status task_001
python scripts/agent_delegator.py current task_001
python scripts/agent_delegator.py context task_001
python scripts/agent_delegator.py history task_001
```

## Best Practices Summary

### Communication
- Always include comprehensive context when delegating
- Document decisions at each handoff
- Use clear, actionable feedback in reviews
- Preserve context across all handoffs

### Quality Assurance
- Never skip the PR review step
- Require test coverage >80%
- Use quality gates for critical checkpoints
- Always validate with QA before completion

### Parallel Execution
- Group independent tasks in parallel groups
- Set up dependencies before starting
- Check readiness before delegating
- Monitor parallel group progress

### Iteration Management
- Track iteration count
- Set max iterations (default: 3)
- Escalate if stuck in iteration loop
- Document why iterations are needed

### Error Handling
- Add blockers as soon as identified
- Create resolution subtasks
- Track blocker resolution
- Update status when unblocked
