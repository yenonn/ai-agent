#!/usr/bin/env python3
"""
Ralph Loop Agent Wrapper

Wraps agent execution with Ralph Loop verification pattern - continuously
iterating until verification confirms task completion.

This integrates with the existing agent-team-orchestrator to add verification
loops for each agent role before handoff.
"""

import sys
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import time
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import verifiers
from ralph_verifiers import get_verifier_for_agent, VerificationResult

# Import sound notifications
try:
    from sound_notifications import get_notifier

    SOUNDS_AVAILABLE = True
except ImportError:
    SOUNDS_AVAILABLE = False
    print("Warning: Sound notifications not available", file=sys.stderr)


@dataclass
class RalphLoopConfig:
    """Configuration for Ralph Loop execution"""

    agent_type: str
    max_iterations: int = 10
    max_tokens: Optional[int] = None
    max_cost: Optional[float] = None
    enable_feedback_injection: bool = True
    verbose: bool = False
    enable_sounds: bool = True  # Enable sound notifications


@dataclass
class RalphLoopResult:
    """Result from a Ralph Loop execution"""

    success: bool
    iterations: int
    final_result: Dict[str, Any]
    all_results: list
    completion_reason: str  # 'verified', 'max_iterations', 'stopped', 'error'
    verification_history: list
    total_duration_ms: int
    final_verification: Optional[VerificationResult] = None


class RalphLoopAgent:
    """
    Wraps an agent with Ralph Loop verification pattern.

    This implements the "Ralph Wiggum technique" - continuously executing
    until verification passes or limits are reached.
    """

    def __init__(self, config: RalphLoopConfig):
        self.config = config
        self.verifier = get_verifier_for_agent(config.agent_type)

        if not self.verifier:
            raise ValueError(f"No verifier found for agent type: {config.agent_type}")

        self.iteration_count = 0
        self.token_count = 0
        self.estimated_cost = 0.0
        self.verification_history = []
        self.all_results = []

        # Initialize sound notifier if available and enabled
        self.notifier = None
        if SOUNDS_AVAILABLE and config.enable_sounds:
            self.notifier = get_notifier(enabled=True)

    def should_stop(self) -> tuple[bool, str]:
        """Check if any stop condition is met"""

        if self.iteration_count >= self.config.max_iterations:
            return True, f"max_iterations ({self.config.max_iterations})"

        if self.config.max_tokens and self.token_count >= self.config.max_tokens:
            return True, f"max_tokens ({self.config.max_tokens})"

        if self.config.max_cost and self.estimated_cost >= self.config.max_cost:
            return True, f"max_cost (${self.config.max_cost})"

        return False, ""

    def execute_loop(
        self,
        task_prompt: str,
        context: Dict[str, Any],
        execute_agent_fn: Callable[[str, Dict[str, Any], int], Dict[str, Any]],
    ) -> RalphLoopResult:
        """
        Execute the Ralph Loop pattern.

        Args:
            task_prompt: The task/prompt for the agent
            context: Context dict with task info, previous results, etc.
            execute_agent_fn: Function that executes the agent and returns result
                             Should accept (prompt, context, iteration) and return result dict

        Returns:
            RalphLoopResult with execution details
        """
        start_time = time.time()
        current_prompt = task_prompt

        self.iteration_count = 0
        self.token_count = 0
        self.verification_history = []
        self.all_results = []

        if self.config.verbose:
            print(f"🔄 Starting Ralph Loop for {self.config.agent_type} agent")
            print(f"   Max iterations: {self.config.max_iterations}")

        while True:
            self.iteration_count += 1

            if self.config.verbose:
                print(f"\n--- Iteration {self.iteration_count} ---")

            # Check stop conditions BEFORE executing
            should_stop, reason = self.should_stop()
            if should_stop:
                if self.config.verbose:
                    print(f"⚠️  Stopping: {reason}")

                # Play warning sound when stopping due to limits
                if self.notifier:
                    self.notifier.play_warning()

                return RalphLoopResult(
                    success=False,
                    iterations=self.iteration_count
                    - 1,  # Don't count the stopped iteration
                    final_result=self.all_results[-1] if self.all_results else {},
                    all_results=self.all_results,
                    completion_reason=f"stopped: {reason}",
                    verification_history=self.verification_history,
                    total_duration_ms=int((time.time() - start_time) * 1000),
                    final_verification=self.verification_history[-1]
                    if self.verification_history
                    else None,
                )

            # Execute the agent
            try:
                result = execute_agent_fn(current_prompt, context, self.iteration_count)
                self.all_results.append(result)

                # Update token tracking if available
                if "usage" in result:
                    usage = result["usage"]
                    tokens_used = usage.get("totalTokens", 0)
                    self.token_count += tokens_used

                # Verify completion
                verification = self.verifier(result, context)
                self.verification_history.append(verification)

                if self.config.verbose:
                    status = "✅ COMPLETE" if verification.complete else "❌ INCOMPLETE"
                    print(f"{status}: {verification.reason}")
                    if verification.feedback:
                        print(f"   Feedback: {verification.feedback}")
                    print(f"   Confidence: {verification.confidence:.1%}")

                # Play subtle iteration sound if incomplete (attention may be needed soon)
                if not verification.complete and self.notifier:
                    self.notifier.play_iteration()

                # Check if verified complete
                if verification.complete:
                    duration_ms = int((time.time() - start_time) * 1000)

                    if self.config.verbose:
                        print(
                            f"\n🎉 Task verified complete in {self.iteration_count} iterations"
                        )
                        print(f"   Duration: {duration_ms}ms")

                    # Play success sound when task completes
                    if self.notifier:
                        self.notifier.play_success()

                    return RalphLoopResult(
                        success=True,
                        iterations=self.iteration_count,
                        final_result=result,
                        all_results=self.all_results,
                        completion_reason="verified",
                        verification_history=self.verification_history,
                        total_duration_ms=duration_ms,
                        final_verification=verification,
                    )

                # Not complete - prepare feedback for next iteration
                if self.config.enable_feedback_injection and verification.feedback:
                    feedback_prompt = f"""
Previous attempt was incomplete. Verification feedback:

{verification.feedback}

Please address the feedback and continue with the task.

Original task: {task_prompt}
"""
                    current_prompt = feedback_prompt
                else:
                    # Continue with original prompt
                    current_prompt = task_prompt

            except Exception as e:
                if self.config.verbose:
                    print(f"❌ Error during iteration {self.iteration_count}: {e}")

                # Play error sound
                if self.notifier:
                    self.notifier.play_error()

                return RalphLoopResult(
                    success=False,
                    iterations=self.iteration_count,
                    final_result=self.all_results[-1] if self.all_results else {},
                    all_results=self.all_results,
                    completion_reason=f"error: {str(e)}",
                    verification_history=self.verification_history,
                    total_duration_ms=int((time.time() - start_time) * 1000),
                )


def create_agent_prompt_with_verification(
    agent_type: str, base_prompt: str, verification_criteria: Optional[str] = None
) -> str:
    """
    Enhance agent prompts with verification requirements.

    This makes agents aware of what will be verified, improving success rate.
    """

    verification_guides = {
        "architect": """
## Verification Requirements

Your architectural specifications will be verified for:
- Complete architecture overview with system design
- Detailed component breakdown with responsibilities
- API specifications with endpoints and data models
- Security considerations (auth, data protection)
- Success criteria and quality gates
- Clear handoff readiness for implementation

**Mark completion**: End your response with "Ready for implementation" and list priority order.
""",
        "coder": """
## Verification Requirements

Your implementation will be verified for:
- Working code that meets specifications
- Comprehensive tests written and passing
- Proper error handling for edge cases
- Code documentation (docstrings, comments)
- Configuration properly externalized

**Mark completion**: End with "Ready for review" and confirm all tests pass.
""",
        "reviewer": """
## Verification Requirements

Your code review will be verified for:
- Security review (auth, input validation, vulnerabilities)
- Code quality assessment (patterns, readability, maintainability)
- Test coverage verification (>80% target)
- Performance considerations
- Clear decision: APPROVED or CHANGES REQUIRED with severity levels

**Mark completion**: Provide explicit approval or categorized change requests (CRITICAL/HIGH/MEDIUM/LOW).
""",
        "debug": """
## Verification Requirements

Your bug investigation will be verified for:
- Bug reproduction confirmed with steps
- Root cause identified (not just symptoms - explain WHY it occurs)
- Affected code paths traced with specific line numbers
- Fix strategy proposed with minimal changes
- Verification steps defined to confirm fix works

**Mark completion**: Clearly state root cause, proposed fix, and how to verify.
""",
        "docs": """
## Verification Requirements

Your documentation will be verified for:
- Clear overview/summary of the feature
- Practical usage examples with code
- API/configuration reference documentation
- Proper markdown formatting
- Up-to-date with current implementation

**Mark completion**: State "Documentation complete" and list all sections covered.
""",
        "devops": """
## Verification Requirements

Your DevOps setup will be verified for:
- Complete pipeline configuration (CI/CD)
- Deployment strategy defined with rollback plan
- Monitoring and logging configured
- Environment configurations handled (secrets, variables)
- Pipeline tested successfully end-to-end

**Mark completion**: Confirm pipeline runs successfully and provide deployment runbook.
""",
        "security": """
## Verification Requirements

Your security audit will be verified for:
- Comprehensive vulnerability scan performed
- Findings categorized by severity (CRITICAL/HIGH/MEDIUM/LOW)
- Authentication and authorization reviewed
- Input validation and injection protection checked
- Clear remediation steps for each finding

**Mark completion**: Provide categorized findings with specific remediation guidance.
""",
    }

    guide = verification_guides.get(agent_type, "")

    enhanced_prompt = f"""{base_prompt}

{guide}

{verification_criteria if verification_criteria else ""}
""".strip()

    return enhanced_prompt


def main():
    """CLI interface for Ralph Loop execution"""
    if len(sys.argv) < 3:
        print(
            "Usage: python ralph_loop_agent.py <agent_type> <task_prompt> [--max-iterations N] [--verbose] [--no-sounds]"
        )
        print(
            "\nAgent types: architect, coder, reviewer, debug, docs, devops, security"
        )
        sys.exit(1)

    agent_type = sys.argv[1]
    task_prompt = sys.argv[2]

    # Parse optional args
    max_iterations = 10
    verbose = False
    enable_sounds = True

    for i, arg in enumerate(sys.argv[3:]):
        if arg == "--max-iterations" and i + 4 < len(sys.argv):
            max_iterations = int(sys.argv[i + 4])
        elif arg == "--verbose":
            verbose = True
        elif arg == "--no-sounds":
            enable_sounds = False

    config = RalphLoopConfig(
        agent_type=agent_type,
        max_iterations=max_iterations,
        verbose=verbose,
        enable_sounds=enable_sounds,
    )

    ralph = RalphLoopAgent(config)

    # Mock execute function for testing
    def mock_execute(prompt: str, context: Dict, iteration: int) -> Dict[str, Any]:
        """Mock agent execution"""
        print(f"\n[Mock Agent Execution - Iteration {iteration}]")
        print(f"Prompt: {prompt[:100]}...")

        # Simulate some output
        return {
            "text": f"Mock output for {agent_type} agent (iteration {iteration})",
            "toolCalls": [],
            "usage": {"totalTokens": 100},
        }

    enhanced_prompt = create_agent_prompt_with_verification(agent_type, task_prompt)

    result = ralph.execute_loop(enhanced_prompt, {"task_id": "test-001"}, mock_execute)

    print("\n" + "=" * 60)
    print("RALPH LOOP RESULT")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Iterations: {result.iterations}")
    print(f"Completion: {result.completion_reason}")
    print(f"Duration: {result.total_duration_ms}ms")

    if result.final_verification:
        print(f"\nFinal Verification:")
        print(f"  Complete: {result.final_verification.complete}")
        print(f"  Reason: {result.final_verification.reason}")
        print(f"  Confidence: {result.final_verification.confidence:.1%}")


if __name__ == "__main__":
    main()
