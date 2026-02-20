# Ralph Loop Integration Guide

This guide explains how the Ralph Wiggum technique has been integrated into the Agent Team Orchestrator skill.

## What is the Ralph Loop Pattern?

The Ralph Wiggum technique, created by Vercel Labs, is elegantly simple: **"Ralph is a Bash loop"**

```bash
while (!taskComplete) {
  result = agent.executeWithTools();
  taskComplete = verifyCompletion(result);
  if (!taskComplete) {
    provideFeedback();
  }
}
```

Instead of hoping an agent completes a task correctly in one shot, Ralph keeps iterating until verification confirms success.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Agent Team Orchestrator + Ralph Loop Pattern         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Architect Agent with Ralph Loop                        │ │
│  │                                                         │ │
│  │  Iteration 1: Draft architecture                      │ │
│  │  Verify: Missing API specs ❌                          │ │
│  │  Feedback: "Add API endpoint specifications"          │ │
│  │                                                         │ │
│  │  Iteration 2: Add API specs                           │ │
│  │  Verify: All sections complete ✅                      │ │
│  │  → Handoff to Coder                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Coder Agent with Ralph Loop                            │ │
│  │                                                         │ │
│  │  Iteration 1: Write implementation                     │ │
│  │  Verify: Tests failing ❌                              │ │
│  │  Feedback: "Fix test failures in auth module"         │ │
│  │                                                         │ │
│  │  Iteration 2: Fix tests                               │ │
│  │  Verify: All tests pass ✅                             │ │
│  │  → Handoff to Reviewer                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Verification Functions (`ralph_verifiers.py`)

Each agent type has a specialized verification function:

- **Architect Verifier**: Checks for complete technical specifications
- **Coder Verifier**: Ensures implementation + passing tests
- **Reviewer Verifier**: Validates thorough code review
- **Debug Verifier**: Confirms root cause identification
- **Docs Verifier**: Verifies comprehensive documentation
- **DevOps Verifier**: Checks complete CI/CD setup
- **Security Verifier**: Ensures thorough security audit

### 2. Ralph Loop Agent (`ralph_loop_agent.py`)

Core loop executor that:
- Executes agent with Task tool
- Runs verification function
- Injects feedback if incomplete
- Iterates until verified or limits reached
- Tracks iterations, tokens, cost

### 3. Enhanced Agent Prompts

Agents are given verification requirements upfront, so they know what will be checked:

```python
enhanced_prompt = create_agent_prompt_with_verification(
    agent_type='coder',
    base_prompt='Implement user authentication...'
)
# Adds verification requirements to the prompt
```

## Usage in OpenCode

When orchestrating the agent team, use Ralph Loop verification for each handoff:

### Example: Feature Development with Ralph Loop

```python
from ralph_loop_agent import RalphLoopAgent, RalphLoopConfig, create_agent_prompt_with_verification

# 1. Architect Phase with Ralph Loop
architect_config = RalphLoopConfig(
    agent_type='architect',
    max_iterations=10,
    verbose=True
)
architect_ralph = RalphLoopAgent(architect_config)

architect_prompt = create_agent_prompt_with_verification(
    'architect',
    '''
    Design a user authentication system with:
    - JWT-based authentication
    - Role-based access control
    - Password reset flow
    '''
)

def execute_architect(prompt, context, iteration):
    # Use OpenCode's Task tool to spawn architect agent
    result = task_tool.invoke({
        'subagent_type': 'general',
        'description': f'Architecture Analysis (iter {iteration})',
        'prompt': prompt
    })
    return result

architect_result = architect_ralph.execute_loop(
    architect_prompt,
    {'task_id': 'auth-001'},
    execute_architect
)

# Only proceeds when verification passes! ✅

# 2. Coder Phase with Ralph Loop
coder_config = RalphLoopConfig(
    agent_type='coder',
    max_iterations=15,
    verbose=True
)
coder_ralph = RalphLoopAgent(coder_config)

coder_prompt = create_agent_prompt_with_verification(
    'coder',
    f'''
    Implement the authentication system based on these specs:
    
    {architect_result.final_result['text']}
    '''
)

def execute_coder(prompt, context, iteration):
    result = task_tool.invoke({
        'subagent_type': 'general',
        'description': f'Implementation (iter {iteration})',
        'prompt': prompt
    })
    return result

coder_result = coder_ralph.execute_loop(
    coder_prompt,
    {'task_id': 'auth-001', 'architecture': architect_result},
    execute_coder
)

# Continues until tests pass! ✅
```

### Example: Bug Fix with Ralph Loop

```python
# Debug Agent with Ralph Loop
debug_config = RalphLoopConfig(
    agent_type='debug',
    max_iterations=8,
    verbose=True
)
debug_ralph = RalphLoopAgent(debug_config)

debug_prompt = create_agent_prompt_with_verification(
    'debug',
    '''
    Investigate authentication failure bug:
    
    Error: "Token validation fails for valid tokens"
    Reproduction: Login → Wait 5 minutes → API call fails
    Logs: [error logs here]
    '''
)

debug_result = debug_ralph.execute_loop(
    debug_prompt,
    {'task_id': 'bug-042'},
    execute_debug_agent
)

# Continues until root cause found! ✅
```

## Integration with Existing Orchestrator

The Ralph Loop pattern integrates seamlessly with your existing orchestrator:

```python
# In your orchestrator delegation logic

def delegate_to_agent_with_ralph(agent_type, task_prompt, context):
    """Delegate to an agent with Ralph Loop verification"""
    
    # Create Ralph Loop config
    config = RalphLoopConfig(
        agent_type=agent_type,
        max_iterations=get_max_iterations_for_agent(agent_type),
        verbose=True
    )
    
    ralph = RalphLoopAgent(config)
    
    # Enhance prompt with verification requirements
    enhanced_prompt = create_agent_prompt_with_verification(
        agent_type,
        task_prompt
    )
    
    # Execute with verification loop
    def execute_fn(prompt, ctx, iteration):
        return spawn_agent_via_task_tool(agent_type, prompt, ctx, iteration)
    
    result = ralph.execute_loop(enhanced_prompt, context, execute_fn)
    
    if not result.success:
        # Handle incomplete task
        raise Exception(f"Agent {agent_type} could not complete: {result.completion_reason}")
    
    return result
```

## Verification Criteria by Agent

### Architect
- ✅ Architecture overview present
- ✅ Component design detailed
- ✅ API specifications defined
- ✅ Security considerations documented
- ✅ Success criteria stated
- ✅ Handoff readiness marked

### Coder
- ✅ Implementation matches specs
- ✅ Tests executed
- ✅ All tests passing
- ✅ Error handling implemented
- ✅ Documentation added
- ✅ "Ready for review" stated

### Reviewer
- ✅ Security review completed
- ✅ Code quality assessed
- ✅ Test coverage verified
- ✅ Performance considered
- ✅ Clear approval/changes decision

### Debug
- ✅ Bug reproduced
- ✅ Root cause identified (WHY not just WHAT)
- ✅ Code path traced
- ✅ Fix strategy proposed
- ✅ Verification steps defined

### Docs
- ✅ Overview/summary present
- ✅ Usage examples included
- ✅ API/config documented
- ✅ Proper markdown formatting
- ✅ "Documentation complete" stated

### DevOps
- ✅ Pipeline configuration created
- ✅ Deployment strategy defined
- ✅ Monitoring configured
- ✅ Environment configs handled
- ✅ Pipeline tested successfully

### Security
- ✅ Vulnerability scan performed
- ✅ Findings categorized by severity
- ✅ Auth/authz reviewed
- ✅ Input validation checked
- ✅ Remediation steps provided

## Stop Conditions

Ralph Loop supports multiple stop conditions to prevent runaway execution:

```python
config = RalphLoopConfig(
    agent_type='coder',
    max_iterations=20,        # Stop after N iterations
    max_tokens=100000,        # Stop when token usage exceeds limit
    max_cost=5.0,             # Stop when cost exceeds $5
)
```

## Feedback Injection

When verification fails, feedback is automatically injected into the next iteration:

```
Iteration 1 Output:
"Implemented auth module with JWT tokens"

Verification: ❌ INCOMPLETE
Reason: Tests failing
Feedback: "Fix test failures in auth module"

Iteration 2 Prompt:
"Previous attempt was incomplete. Verification feedback:

Fix test failures in auth module

Please address the feedback and continue with the task."
```

This guides the agent toward completion without manual intervention.

## Benefits

1. **Reliability**: Tasks don't stop until verified complete
2. **Self-Correction**: Agents learn from verification feedback
3. **Quality Gates**: Each handoff meets quality standards
4. **Reduced Manual Oversight**: Automated verification loop
5. **Context Preservation**: Feedback carries forward between iterations
6. **Safety Limits**: Prevents infinite loops with stop conditions

## Best Practices

1. **Set appropriate iteration limits**: Complex tasks need more iterations
   - Architect: 10-15 iterations
   - Coder: 15-20 iterations
   - Debug: 8-12 iterations
   - Reviewer: 5-8 iterations

2. **Enable verbose mode during development**: See verification progress

3. **Customize verification for specific projects**: Add project-specific checks

4. **Monitor verification history**: Use `result.verification_history` to understand agent behavior

5. **Combine with session management**: Save Ralph Loop results to checkpoints

## Troubleshooting

### Agent never passes verification
- Check if verification criteria are too strict
- Review verification history to see what's failing
- Increase max_iterations if task is complex
- Adjust verifier patterns for your codebase style

### Agent passes too early
- Strengthen verification criteria
- Add more specific checks to the verifier
- Require explicit completion markers

### Feedback not helping
- Make verification feedback more specific
- Include examples in feedback
- Check if agent has tools needed to address feedback

## Next Steps

1. Test Ralph Loop with existing agent-team workflows
2. Tune verification criteria for your project
3. Add custom verifiers for specialized agents
4. Monitor iteration counts to optimize limits
5. Integrate with session checkpoints for long-running tasks
