#!/usr/bin/env python3
"""
Agent delegation script for coordinating handoffs between Architect, Coder, PR Reviewer, and QA agents.
Manages the workflow transitions and ensures proper context transfer between team members.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from dataclasses import dataclass, asdict, field


@dataclass
class DelegationContext:
    """Stores context information for agent handoffs."""

    task_id: str
    from_agent: str
    to_agent: str
    timestamp: str
    state: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    deliverables: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    handoff_notes: str = ""
    context_accumulated: Dict[str, Any] = field(default_factory=dict)


class AgentDelegator:
    """Manages agent delegation and handoff coordination."""

    VALID_AGENTS = [
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
    VALID_STATES = [
        "new",
        "analyzing",
        "planning",
        "implementing",
        "debugging",
        "reviewing",
        "testing",
        "documenting",
        "devops",
        "security_audit",
        "iteration",
        "blocked",
        "complete",
    ]

    def __init__(self, project_root: str = "."):
        # Use global .dev_team directory (configurable via DEV_TEAM_DIR env var)
        self.project_root = Path(project_root).resolve()
        dev_team_path = os.getenv("DEV_TEAM_DIR", str(Path.home() / ".dev_team"))
        self.dev_team_dir = Path(dev_team_path).expanduser()
        self.delegations_file = self.dev_team_dir / "delegations.json"
        self.context_file = self.dev_team_dir / "context.json"
        self.history_file = self.dev_team_dir / "history.json"
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensure storage directories exist."""
        self.dev_team_dir.mkdir(exist_ok=True)

        if not self.delegations_file.exists():
            self._save_delegations({})

        if not self.context_file.exists():
            self._save_context({})

        if not self.history_file.exists():
            self._save_history([])

    def _load_delegations(self) -> Dict[str, Any]:
        """Load all delegation records."""
        try:
            with open(self.delegations_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_delegations(self, delegations: Dict[str, Any]):
        """Save all delegations."""
        with open(self.delegations_file, "w") as f:
            json.dump(delegations, f, indent=2, default=str)

    def _load_context(self) -> Dict[str, Dict]:
        """Load task context."""
        try:
            with open(self.context_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_context(self, context: Dict[str, Dict]):
        """Save task context."""
        with open(self.context_file, "w") as f:
            json.dump(context, f, indent=2, default=str)

    def _load_history(self) -> List[Dict]:
        """Load delegation history."""
        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_history(self, history: List[Dict]):
        """Save delegation history."""
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2, default=str)

    def _get_accumulated_context(self, task_id: str) -> Dict[str, Any]:
        """Get accumulated context from all previous delegations."""
        context = self._load_context()
        task_context = context.get(task_id, {})

        accumulated = {
            "original_requirements": task_context.get("original_requirements", {}),
            "architect_decisions": task_context.get("architect", {}),
            "implementation_details": task_context.get("coder", {}),
            "review_feedback": task_context.get("pr_reviewer", []),
            "test_results": task_context.get("qa_tester", {}),
        }
        return accumulated

    def delegate_to_architect(self, task_id: str, requirements: Dict) -> str:
        """Delegate task to Architect agent."""
        accumulated = self._get_accumulated_context(task_id)

        delegation = DelegationContext(
            task_id=task_id,
            from_agent="coordinator",
            to_agent="architect",
            timestamp=datetime.now().isoformat(),
            state="analyzing",
            requirements=requirements,
            deliverables=[
                "Technical specifications document",
                "System architecture design",
                "API design documentation",
                "Database schema if applicable",
                "Technology stack decisions with rationale",
                "Security considerations",
                "Performance requirements",
                "Success criteria and quality gates",
            ],
            constraints=[
                "Follow established project patterns",
                "Consider scalability and maintainability",
                "Document all architectural decisions (ADRs)",
                "Define clear interfaces between components",
            ],
            success_criteria=[
                "Complete technical specifications delivered",
                "Architecture addresses all requirements",
                "Technology choices justified and documented",
                "Security considerations addressed",
                "Performance requirements defined",
            ],
            handoff_notes="Analyze requirements and create comprehensive technical architecture. Consider existing codebase patterns and constraints.",
            context_accumulated=accumulated,
        )

        self._store_delegation(delegation)
        self._update_task_context(
            task_id,
            "architect",
            {"requirements": requirements, "started_at": datetime.now().isoformat()},
        )
        self._add_to_history(task_id, "delegated_to_architect", requirements)
        self._play_sound("play_attention_needed")

        return self._generate_architect_prompt(delegation)

    def delegate_to_coder(self, task_id: str, context: Dict) -> str:
        """Delegate task to Coder agent."""
        accumulated = self._get_accumulated_context(task_id)

        delegation = DelegationContext(
            task_id=task_id,
            from_agent=context.get("from_agent", "architect"),
            to_agent="coder",
            timestamp=datetime.now().isoformat(),
            state="implementing",
            requirements=context.get("requirements", {}),
            deliverables=[
                "Working implementation matching specifications",
                "Unit tests (>80% coverage target)",
                "Integration tests for key workflows",
                "Code documentation and comments",
                "Configuration files if needed",
            ],
            constraints=[
                "Follow architectural specifications exactly",
                "Write clean, modular, extensible code",
                "Include comprehensive error handling",
                "Follow existing codebase patterns",
                "Apply security best practices",
            ],
            success_criteria=[
                "All requirements implemented",
                "Tests pass with >80% coverage",
                "Code passes linting and type checking",
                "Documentation complete",
                "No critical security issues",
            ],
            handoff_notes="Implement features according to architectural specifications. Focus on clean code, comprehensive testing, and thorough documentation.",
            context_accumulated=accumulated,
        )

        self._store_delegation(delegation)
        self._update_task_context(
            task_id,
            "coder",
            {
                "architect_specs": context.get("architect_specs", {}),
                "started_at": datetime.now().isoformat(),
            },
        )
        self._add_to_history(task_id, "delegated_to_coder", context)
        self._play_sound("play_attention_needed")

        return self._generate_coder_prompt(delegation)

    def delegate_to_reviewer(self, task_id: str, implementation_info: Dict) -> str:
        """Delegate task to PR Reviewer agent."""
        accumulated = self._get_accumulated_context(task_id)

        delegation = DelegationContext(
            task_id=task_id,
            from_agent="coder",
            to_agent="pr_reviewer",
            timestamp=datetime.now().isoformat(),
            state="reviewing",
            requirements=implementation_info,
            deliverables=[
                "Quality assessment report",
                "Security review findings",
                "Performance analysis",
                "Improvement recommendations",
                "Approval or change requests",
            ],
            constraints=[
                "Focus on critical and high-priority issues",
                "Provide actionable, specific feedback",
                "Reference best practices and patterns",
                "Verify architectural compliance",
                "Check test coverage and quality",
            ],
            success_criteria=[
                "Zero critical security issues",
                "All high-priority issues addressed",
                "Performance benchmarks acceptable",
                "Code quality standards satisfied",
                "Architectural compliance verified",
            ],
            handoff_notes="Conduct comprehensive code review focusing on quality, security, performance, and compliance with architectural decisions.",
            context_accumulated=accumulated,
        )

        self._store_delegation(delegation)
        self._update_task_context(
            task_id,
            "pr_reviewer",
            {
                "implementation": implementation_info,
                "started_at": datetime.now().isoformat(),
            },
        )
        self._add_to_history(task_id, "delegated_to_reviewer", implementation_info)
        self._play_sound("play_attention_needed")

        return self._generate_reviewer_prompt(delegation)

    def delegate_to_qa(self, task_id: str, test_info: Dict) -> str:
        """Delegate task to QA/Tester agent."""
        accumulated = self._get_accumulated_context(task_id)

        delegation = DelegationContext(
            task_id=task_id,
            from_agent=test_info.get("from_agent", "pr_reviewer"),
            to_agent="qa_tester",
            timestamp=datetime.now().isoformat(),
            state="testing",
            requirements=test_info,
            deliverables=[
                "Test execution results",
                "Bug report (if any found)",
                "Coverage analysis",
                "Performance validation results",
                "Sign-off recommendation",
            ],
            constraints=[
                "Validate all functional requirements",
                "Test edge cases and error scenarios",
                "Perform integration testing",
                "Verify no regressions",
                "Document all test scenarios",
            ],
            success_criteria=[
                "All acceptance criteria met",
                "No critical bugs found",
                "Test coverage requirements satisfied",
                "Performance within acceptable range",
                "Integration tests passing",
            ],
            handoff_notes="Execute comprehensive testing including functional, integration, edge cases, and performance validation.",
            context_accumulated=accumulated,
        )

        self._store_delegation(delegation)
        self._update_task_context(
            task_id,
            "qa_tester",
            {"test_info": test_info, "started_at": datetime.now().isoformat()},
        )
        self._add_to_history(task_id, "delegated_to_qa", test_info)
        self._play_sound("play_attention_needed")

        return self._generate_qa_prompt(delegation)

    def delegate_to_debug(self, task_id: str, issue_info: Dict) -> str:
        """Delegate task to Debug agent for bug investigation and root-cause analysis."""
        accumulated = self._get_accumulated_context(task_id)

        delegation = DelegationContext(
            task_id=task_id,
            from_agent=issue_info.get("from_agent", "coordinator"),
            to_agent="debug",
            timestamp=datetime.now().isoformat(),
            state="debugging",
            requirements=issue_info,
            deliverables=[
                "Root cause analysis with affected files and line numbers",
                "Proposed minimal fix with rationale",
                "Verification steps to confirm the fix",
                "Regression risks and side-effects assessment",
                "Prevention recommendations",
            ],
            constraints=[
                "Prefer targeted fixes over broad refactoring",
                "Identify the exact root cause before proposing a fix",
                "Document all assumptions and evidence",
                "Do not introduce new dependencies unnecessarily",
            ],
            success_criteria=[
                "Root cause clearly identified and documented",
                "Fix proposal is minimal and targeted",
                "Verification steps confirm the bug is resolved",
                "No unintended regressions introduced",
            ],
            handoff_notes=(
                "Investigate the reported issue systematically. Reproduce it, trace the "
                "code path, and identify the exact root cause. Provide a targeted fix "
                "and clear verification steps for the Coder agent."
            ),
            context_accumulated=accumulated,
        )

        self._store_delegation(delegation)
        self._update_task_context(
            task_id,
            "debug",
            {"issue_info": issue_info, "started_at": datetime.now().isoformat()},
        )
        self._add_to_history(task_id, "delegated_to_debug", issue_info)
        self._play_sound("play_attention_needed")

        return self._generate_debug_prompt(delegation)

    def delegate_to_docs(self, task_id: str, docs_info: Dict) -> str:
        """Delegate task to Docs agent for documentation writing or review."""
        accumulated = self._get_accumulated_context(task_id)

        delegation = DelegationContext(
            task_id=task_id,
            from_agent=docs_info.get("from_agent", "coordinator"),
            to_agent="docs",
            timestamp=datetime.now().isoformat(),
            state="documenting",
            requirements=docs_info,
            deliverables=[
                "README updates (if applicable)",
                "API documentation for all public interfaces",
                "Usage examples and code snippets",
                "Configuration reference",
                "Changelog entries",
            ],
            constraints=[
                "Write for the stated target audience",
                "Keep examples accurate and runnable",
                "Use consistent terminology throughout",
                "Sync docs with the current implementation — no stale content",
            ],
            success_criteria=[
                "All public APIs and features documented",
                "Examples tested and working",
                "Documentation reviewed for clarity and accuracy",
                "No discrepancies between docs and code",
            ],
            handoff_notes=(
                "Review the codebase and existing documentation, identify gaps, then "
                "write or update documentation. Ensure all examples are accurate and "
                "that the docs match the current implementation."
            ),
            context_accumulated=accumulated,
        )

        self._store_delegation(delegation)
        self._update_task_context(
            task_id,
            "docs",
            {"docs_info": docs_info, "started_at": datetime.now().isoformat()},
        )
        self._add_to_history(task_id, "delegated_to_docs", docs_info)
        self._play_sound("play_attention_needed")

        return self._generate_docs_prompt(delegation)

    def delegate_to_devops(self, task_id: str, infra_info: Dict) -> str:
        """Delegate task to DevOps agent for CI/CD, infrastructure, or deployment work."""
        accumulated = self._get_accumulated_context(task_id)

        delegation = DelegationContext(
            task_id=task_id,
            from_agent=infra_info.get("from_agent", "coordinator"),
            to_agent="devops",
            timestamp=datetime.now().isoformat(),
            state="devops",
            requirements=infra_info,
            deliverables=[
                "CI/CD pipeline configuration files",
                "Deployment scripts and strategy documentation",
                "Infrastructure-as-code files (if applicable)",
                "Monitoring, logging, and alerting configuration",
                "Runbooks for deployment and rollback",
            ],
            constraints=[
                "Prefer automation over manual steps",
                "Handle secrets via a secrets manager — never hardcode",
                "Ensure environment parity (dev/staging/prod)",
                "Document rollback procedures for every deployment step",
            ],
            success_criteria=[
                "Pipeline builds and tests successfully on every push",
                "Automated deployment works end-to-end",
                "Monitoring and alerting configured and tested",
                "Rollback procedure documented and tested",
                "No secrets committed to source control",
            ],
            handoff_notes=(
                "Design and implement the CI/CD pipeline and infrastructure configuration. "
                "Prioritise automation, security (no hardcoded secrets), and environment "
                "parity. Test the pipeline end-to-end and document deployment and rollback "
                "procedures."
            ),
            context_accumulated=accumulated,
        )

        self._store_delegation(delegation)
        self._update_task_context(
            task_id,
            "devops",
            {"infra_info": infra_info, "started_at": datetime.now().isoformat()},
        )
        self._add_to_history(task_id, "delegated_to_devops", infra_info)
        self._play_sound("play_attention_needed")

        return self._generate_devops_prompt(delegation)

    def delegate_to_security(self, task_id: str, audit_info: Dict) -> str:
        """Delegate task to Security agent for security audits and vulnerability assessments."""
        accumulated = self._get_accumulated_context(task_id)

        delegation = DelegationContext(
            task_id=task_id,
            from_agent=audit_info.get("from_agent", "coordinator"),
            to_agent="security",
            timestamp=datetime.now().isoformat(),
            state="security_audit",
            requirements=audit_info,
            deliverables=[
                "Security findings report (CRITICAL / HIGH / MEDIUM / LOW)",
                "Remediation steps for each finding",
                "Dependency vulnerability scan results",
                "Authentication and authorisation review",
                "Data handling and encryption assessment",
            ],
            constraints=[
                "Prioritise findings by exploitability and impact",
                "Provide specific, actionable remediation steps",
                "Flag any secrets or credentials found in code",
                "Review all external inputs for injection risks",
            ],
            success_criteria=[
                "All CRITICAL findings resolved or formally accepted",
                "All HIGH findings have a remediation plan",
                "No hardcoded secrets in source control",
                "Authentication and authorisation correctly implemented",
                "Dependencies free of known high-severity CVEs",
            ],
            handoff_notes=(
                "Perform a thorough security audit of the specified scope. Use systematic "
                "checklists for auth, input validation, secrets management, and dependency "
                "scanning. Provide prioritised findings with specific remediation guidance."
            ),
            context_accumulated=accumulated,
        )

        self._store_delegation(delegation)
        self._update_task_context(
            task_id,
            "security",
            {"audit_info": audit_info, "started_at": datetime.now().isoformat()},
        )
        self._add_to_history(task_id, "delegated_to_security", audit_info)
        self._play_sound("play_attention_needed")

        return self._generate_security_prompt(delegation)

    def _store_delegation(self, delegation: DelegationContext):
        """Store delegation record."""
        delegations = self._load_delegations()
        timestamp_clean = (
            delegation.timestamp.replace("-", "")
            .replace(":", "")
            .replace(".", "")
            .replace("T", "")
        )
        delegation_id = (
            f"{delegation.task_id}_{delegation.to_agent}_{timestamp_clean[:14]}"
        )
        delegations[delegation_id] = asdict(delegation)
        self._save_delegations(delegations)

    def _update_task_context(self, task_id: str, agent: str, context: Dict):
        """Update task context for the agent."""
        all_context = self._load_context()
        if task_id not in all_context:
            all_context[task_id] = {"original_requirements": {}}

        if agent not in all_context[task_id]:
            all_context[task_id][agent] = {}

        all_context[task_id][agent].update(context)
        all_context[task_id]["last_updated"] = datetime.now().isoformat()
        all_context[task_id]["current_agent"] = agent

        self._save_context(all_context)

    def _add_to_history(self, task_id: str, action: str, details: Dict):
        """Add entry to delegation history."""
        history = self._load_history()
        history.append(
            {
                "task_id": task_id,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "details": details,
            }
        )
        self._save_history(history[-100:])

        # Mark session as having unsaved changes
        self._mark_session_changed()

    def _mark_session_changed(self):
        """Mark the current session as having unsaved changes."""
        try:
            # Import here to avoid circular dependency
            import sys
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
            # Silently fail if session manager not available
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

    def _extract_keywords(self, delegation: "DelegationContext") -> List[str]:
        """Extract meaningful keywords from delegation requirements for knowledge lookup."""
        stop_words: Set[str] = {
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
            "are",
            "was",
            "be",
            "have",
            "has",
            "do",
            "does",
            "it",
            "as",
            "by",
            "from",
        }
        keywords: List[str] = []

        def extract_from_value(v: Any) -> None:
            if isinstance(v, str):
                for word in v.lower().split():
                    word = word.strip(".,;:!?\"'()[]{}")
                    if word and len(word) > 3 and word not in stop_words:
                        keywords.append(word)
            elif isinstance(v, dict):
                for val in v.values():
                    extract_from_value(val)
            elif isinstance(v, list):
                for item in v:
                    extract_from_value(item)

        extract_from_value(delegation.requirements)
        extract_from_value(delegation.handoff_notes)  # str
        extract_from_value(delegation.deliverables)  # List[str]

        # Deduplicate preserving order, limit to 15
        seen: Set[str] = set()
        result: List[str] = []
        for k in keywords:
            if k not in seen:
                seen.add(k)
                result.append(k)
            if len(result) >= 15:
                break
        return result

    def _get_relevant_knowledge(
        self, agent: str, context_keywords: Optional[List[str]] = None
    ) -> str:
        """Fetch relevant knowledge entries and format as a markdown section for prompts."""
        try:
            import importlib.util

            ks_path = Path(__file__).parent / "knowledge_store.py"
            if not ks_path.exists():
                return ""
            spec = importlib.util.spec_from_file_location("knowledge_store", ks_path)
            if not spec or not spec.loader:
                return ""
            ks_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ks_module)
            store = ks_module.KnowledgeStore()
            entries = store.get_for_agent(agent, context_keywords, limit=5)
            if not entries:
                return ""
            lines = ["## Relevant Team Knowledge\n"]
            for e in entries:
                lines.append(
                    f"### [{e['category']}] {e['title']} (confidence: {e['confidence']})"
                )
                lines.append(f"{e['summary']}")
                if e.get("tags"):
                    lines.append(f"_Tags: {', '.join(e['tags'])}_")
                lines.append("")
            lines.append("---")
            lines.append("")
            return "\n".join(lines)
        except Exception:
            return ""

    def _generate_architect_prompt(self, delegation: DelegationContext) -> str:
        """Generate delegation prompt for Architect agent."""
        return f"""# Architecture Analysis Request

**Task ID**: {delegation.task_id}
**Assigned to**: Architect Agent
**State**: {delegation.state}

## Requirements
{json.dumps(delegation.requirements, indent=2)}

## Expected Deliverables
{self._format_list(delegation.deliverables)}

## Constraints
{self._format_list(delegation.constraints)}

## Success Criteria
{self._format_list(delegation.success_criteria)}

## Handoff Notes
{delegation.handoff_notes}

## Previous Context
{json.dumps(delegation.context_accumulated, indent=2) if delegation.context_accumulated else "No previous context"}

{self._get_relevant_knowledge("architect", self._extract_keywords(delegation))}---

Please analyze the requirements and create comprehensive technical specifications including:
1. System architecture design
2. Technology decisions with rationale
3. API specifications
4. Data models/schemas
5. Security considerations
6. Performance requirements
7. Implementation guidelines

After completion, document your architectural decisions and provide clear specifications for the Coder agent.

## Knowledge Contribution (Optional but Encouraged)
If you discover a reusable insight, pattern, fix, or decision, record it:
    python scripts/knowledge_store.py add "<title>" "<category>" "<content>" "<summary>" "<tags_csv>" "architect" "<task_id>" "high\""""

    def _generate_coder_prompt(self, delegation: DelegationContext) -> str:
        """Generate delegation prompt for Coder agent."""
        architect_decisions = delegation.context_accumulated.get(
            "architect_decisions", {}
        )

        return f"""# Implementation Request

**Task ID**: {delegation.task_id}
**Assigned to**: Coder Agent
**State**: {delegation.state}

## Architectural Specifications
{json.dumps(architect_decisions, indent=2) if architect_decisions else "See requirements below"}

## Requirements
{json.dumps(delegation.requirements, indent=2)}

## Expected Deliverables
{self._format_list(delegation.deliverables)}

## Implementation Constraints
{self._format_list(delegation.constraints)}

## Success Criteria
{self._format_list(delegation.success_criteria)}

## Handoff Notes
{delegation.handoff_notes}

## Quality Checklist
- [ ] All functions have docstrings/comments
- [ ] Error handling for all edge cases
- [ ] No hardcoded values (use config)
- [ ] Follows DRY and SOLID principles
- [ ] Security best practices applied
- [ ] Performance considerations addressed

{self._get_relevant_knowledge("coder", self._extract_keywords(delegation))}---

Please implement the features according to the architectural specifications. Focus on:
1. Clean, modular, extensible code
2. Comprehensive testing (>80% coverage)
3. Thorough documentation
4. Security best practices

After implementation, prepare the code for review by the PR Reviewer agent.

## Knowledge Contribution (Optional but Encouraged)
If you discover a reusable insight, pattern, fix, or decision, record it:
    python scripts/knowledge_store.py add "<title>" "<category>" "<content>" "<summary>" "<tags_csv>" "coder" "<task_id>" "high\""""

    def _generate_reviewer_prompt(self, delegation: DelegationContext) -> str:
        """Generate delegation prompt for PR Reviewer agent."""
        implementation = delegation.context_accumulated.get(
            "implementation_details", {}
        )

        return f"""# Code Review Request

**Task ID**: {delegation.task_id}
**Assigned to**: PR Reviewer Agent
**State**: {delegation.state}

## Implementation to Review
{json.dumps(delegation.requirements, indent=2)}

## Architectural Context
{json.dumps(delegation.context_accumulated.get("architect_decisions", {}), indent=2)}

## Review Focus Areas
{self._format_list(delegation.deliverables)}

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

### Testing
- [ ] Test coverage >80%
- [ ] Edge cases covered
- [ ] Integration tests present

### Performance
- [ ] No obvious bottlenecks
- [ ] Efficient algorithms
- [ ] Appropriate caching

{self._get_relevant_knowledge("pr_reviewer", self._extract_keywords(delegation))}
## Approval Criteria
{self._format_list(delegation.success_criteria)}

## Output Format
Provide structured feedback:
- **CRITICAL**: Must fix before merge (security, bugs)
- **HIGH**: Strongly recommended (quality, performance)
- **MEDIUM**: Suggested improvements
- **LOW**: Nice to have

---

Please conduct a thorough review. If approved, provide merge recommendation. If changes needed, list specific actionable items.

## Knowledge Contribution (Optional but Encouraged)
If you discover a reusable insight, pattern, fix, or decision, record it:
    python scripts/knowledge_store.py add "<title>" "<category>" "<content>" "<summary>" "<tags_csv>" "pr_reviewer" "<task_id>" "high\""""

    def _generate_qa_prompt(self, delegation: DelegationContext) -> str:
        """Generate delegation prompt for QA/Tester agent."""
        return f"""# Testing & Validation Request

**Task ID**: {delegation.task_id}
**Assigned to**: QA/Tester Agent
**State**: {delegation.state}

## Implementation Summary
{json.dumps(delegation.requirements, indent=2)}

## Architectural Context
{json.dumps(delegation.context_accumulated.get("architect_decisions", {}), indent=2)}

## Test Requirements
{self._format_list(delegation.deliverables)}

## Testing Constraints
{self._format_list(delegation.constraints)}

## Acceptance Criteria
{self._format_list(delegation.success_criteria)}

{self._get_relevant_knowledge("qa_tester", self._extract_keywords(delegation))}
## Test Scenarios to Execute
1. Functional testing of all requirements
2. Edge case validation
3. Error handling scenarios
4. Integration testing
5. Performance validation
6. Regression testing

## Output Required
- Test execution results (pass/fail for each scenario)
- Bug report (severity, description, steps to reproduce)
- Coverage analysis
- Performance results
- Sign-off recommendation (APPROVED / NEEDS FIXES)

---

Execute comprehensive testing and provide detailed results. Flag any issues that block release.

## Knowledge Contribution (Optional but Encouraged)
If you discover a reusable insight, pattern, fix, or decision, record it:
    python scripts/knowledge_store.py add "<title>" "<category>" "<content>" "<summary>" "<tags_csv>" "qa_tester" "<task_id>" "high\""""

    def _generate_debug_prompt(self, delegation: DelegationContext) -> str:
        """Generate delegation prompt for Debug agent."""
        return f"""# Debug Investigation Request

**Task ID**: {delegation.task_id}
**Assigned to**: Debug Agent
**State**: {delegation.state}

## Issue Description
{json.dumps(delegation.requirements, indent=2)}

## Expected Deliverables
{self._format_list(delegation.deliverables)}

## Investigation Constraints
{self._format_list(delegation.constraints)}

## Success Criteria
{self._format_list(delegation.success_criteria)}

## Handoff Notes
{delegation.handoff_notes}

## Previous Context
{json.dumps(delegation.context_accumulated, indent=2) if delegation.context_accumulated else "No previous context"}

{self._get_relevant_knowledge("debug", self._extract_keywords(delegation))}---

## Debugging Methodology
- [ ] Reproduce the issue from the provided steps
- [ ] Analyse error messages and stack traces
- [ ] Review recent code changes in affected areas
- [ ] Trace the data flow and state mutations
- [ ] Identify the exact file(s) and line(s) causing the issue
- [ ] Determine *why* the bug occurs (not just what)
- [ ] Propose a minimal, targeted fix
- [ ] Identify regression risks of the proposed fix

## Output Format
Provide structured findings:
- **Root Cause**: Clear explanation of why the bug occurs
- **Affected Code**: Specific files and lines involved
- **Proposed Fix**: Minimal changes to resolve the issue
- **Verification Steps**: How to confirm the fix works
- **Regression Risks**: Potential side effects to watch
- **Prevention**: How to prevent similar bugs in future

## Knowledge Contribution (Optional but Encouraged)
If you discover a reusable insight, pattern, fix, or decision, record it:
    python scripts/knowledge_store.py add "<title>" "<category>" "<content>" "<summary>" "<tags_csv>" "debug" "{delegation.task_id}" "high\""""

    def _generate_docs_prompt(self, delegation: DelegationContext) -> str:
        """Generate delegation prompt for Docs agent."""
        return f"""# Documentation Request

**Task ID**: {delegation.task_id}
**Assigned to**: Docs Agent
**State**: {delegation.state}

## Documentation Scope
{json.dumps(delegation.requirements, indent=2)}

## Expected Deliverables
{self._format_list(delegation.deliverables)}

## Documentation Constraints
{self._format_list(delegation.constraints)}

## Success Criteria
{self._format_list(delegation.success_criteria)}

## Handoff Notes
{delegation.handoff_notes}

## Implementation Context
{json.dumps(delegation.context_accumulated.get("implementation_details", {}), indent=2) if delegation.context_accumulated.get("implementation_details") else "See requirements above"}

{self._get_relevant_knowledge("docs", self._extract_keywords(delegation))}---

## Documentation Checklist
- [ ] All public APIs and interfaces documented
- [ ] Usage examples included and verified runnable
- [ ] Configuration options fully described
- [ ] Getting started guide updated (if needed)
- [ ] Changelog entry added
- [ ] No stale or contradictory content

## Output Format
Provide structured documentation:
- **Overview**: High-level summary of changes/features
- **API Reference**: Detailed interface documentation
- **Examples**: Practical code snippets
- **Configuration**: All configurable options described
- **Changelog**: Entry for this change

## Knowledge Contribution (Optional but Encouraged)
If you discover a reusable documentation convention or pattern, record it:
    python scripts/knowledge_store.py add "<title>" "documentation" "<content>" "<summary>" "<tags_csv>" "docs" "{delegation.task_id}" "high\""""

    def _generate_devops_prompt(self, delegation: DelegationContext) -> str:
        """Generate delegation prompt for DevOps agent."""
        return f"""# DevOps / Infrastructure Request

**Task ID**: {delegation.task_id}
**Assigned to**: DevOps Agent
**State**: {delegation.state}

## Infrastructure Requirements
{json.dumps(delegation.requirements, indent=2)}

## Expected Deliverables
{self._format_list(delegation.deliverables)}

## DevOps Constraints
{self._format_list(delegation.constraints)}

## Success Criteria
{self._format_list(delegation.success_criteria)}

## Handoff Notes
{delegation.handoff_notes}

## Previous Context
{json.dumps(delegation.context_accumulated, indent=2) if delegation.context_accumulated else "No previous context"}

{self._get_relevant_knowledge("devops", self._extract_keywords(delegation))}---

## DevOps Checklist
- [ ] Pipeline builds and tests successfully
- [ ] Automated deployment works end-to-end
- [ ] Rollback procedure documented and tested
- [ ] Secrets managed via secrets manager (not hardcoded)
- [ ] Environment parity verified (dev/staging/prod)
- [ ] Monitoring and alerting configured
- [ ] Container images scanned for vulnerabilities (if applicable)
- [ ] Infrastructure-as-code reviewed and version-controlled

## Output Format
Provide:
- **Pipeline Config**: CI/CD configuration files (inline or file paths)
- **Deploy Strategy**: How deployments and rollbacks work
- **Infrastructure**: IaC files or configuration snippets
- **Monitoring**: Logs, metrics, and alerting setup
- **Runbooks**: Step-by-step deployment and recovery procedures

## Knowledge Contribution (Optional but Encouraged)
If you discover a reusable DevOps pattern, decision, or gotcha, record it:
    python scripts/knowledge_store.py add "<title>" "devops" "<content>" "<summary>" "<tags_csv>" "devops" "{delegation.task_id}" "high\""""

    def _generate_security_prompt(self, delegation: DelegationContext) -> str:
        """Generate delegation prompt for Security agent."""
        return f"""# Security Audit Request

**Task ID**: {delegation.task_id}
**Assigned to**: Security Agent
**State**: {delegation.state}

## Audit Scope
{json.dumps(delegation.requirements, indent=2)}

## Expected Deliverables
{self._format_list(delegation.deliverables)}

## Audit Constraints
{self._format_list(delegation.constraints)}

## Success Criteria
{self._format_list(delegation.success_criteria)}

## Handoff Notes
{delegation.handoff_notes}

## Previous Context
{json.dumps(delegation.context_accumulated, indent=2) if delegation.context_accumulated else "No previous context"}

{self._get_relevant_knowledge("security", self._extract_keywords(delegation))}---

## Security Checklist
- [ ] Authentication flows reviewed
- [ ] Authorisation and access control validated
- [ ] All external inputs sanitised and validated
- [ ] SQL / NoSQL injection prevention verified
- [ ] XSS and CSRF protection in place
- [ ] Sensitive data encrypted at rest and in transit
- [ ] Secrets not committed to source control
- [ ] Dependencies scanned for known CVEs
- [ ] HTTPS enforced; insecure protocols disabled
- [ ] Rate limiting and abuse prevention considered
- [ ] Error messages do not leak sensitive information

## Output Format
Provide prioritised findings:
- **CRITICAL**: Immediate exploitable risk — block release
- **HIGH**: Significant vulnerability — fix before release
- **MEDIUM**: Security improvement — fix soon
- **LOW**: Best-practice recommendation

For each finding include:
- Description of the vulnerability
- Affected file(s) and line(s)
- Exploitation scenario
- Specific remediation steps

## Knowledge Contribution (Optional but Encouraged)
If you discover a security pattern or vulnerability worth remembering, record it:
    python scripts/knowledge_store.py add "<title>" "security" "<content>" "<summary>" "<tags_csv>" "security" "{delegation.task_id}" "high\""""

    def _format_list(self, items: List[str]) -> str:
        """Format a list for display."""
        return "\n".join(f"- {item}" for item in items)

    def get_task_delegations(self, task_id: str) -> List[Dict]:
        """Get all delegations for a specific task."""
        delegations = self._load_delegations()
        return [d for d in delegations.values() if d.get("task_id") == task_id]

    def get_current_assignee(self, task_id: str) -> Optional[str]:
        """Get current assignee for a task."""
        context = self._load_context()
        return context.get(task_id, {}).get("current_agent")

    def get_task_context(self, task_id: str) -> Dict:
        """Get full context for a task."""
        context = self._load_context()
        return context.get(task_id, {})

    def get_delegation_history(self, task_id: Optional[str] = None) -> List[Dict]:
        """Get delegation history, optionally filtered by task."""
        history = self._load_history()
        if task_id:
            return [h for h in history if h.get("task_id") == task_id]
        return history

    def create_checkpoint(
        self, checkpoint_name: Optional[str] = None, description: str = ""
    ) -> str:
        """Create a checkpoint using the session manager."""
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
                    return manager.create_checkpoint(checkpoint_name, description)
            raise FileNotFoundError("Session manager not found")
        except Exception as e:
            raise RuntimeError(f"Failed to create checkpoint: {e}")

    def generate_exit_summary(self) -> Dict:
        """Generate exit summary using session manager."""
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
                    return manager.generate_exit_summary()
            raise FileNotFoundError("Session manager not found")
        except Exception as e:
            return {"error": str(e)}

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
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
                    return manager.has_unsaved_changes()
            return False
        except Exception:
            return False


def main():
    """Command-line interface for agent delegation."""
    if len(sys.argv) < 2:
        print("Usage: agent_delegator.py <command> [args...]")
        print("Commands:")
        print("  architect <task_id> <requirements_json>  Delegate to architect")
        print("  coder <task_id> <context_json>           Delegate to coder")
        print("  reviewer <task_id> <implementation_json> Delegate to reviewer")
        print("  qa <task_id> <test_info_json>            Delegate to QA")
        print("  debug <task_id> <issue_info_json>        Delegate to debug agent")
        print("  docs <task_id> <docs_info_json>          Delegate to docs agent")
        print("  devops <task_id> <infra_info_json>       Delegate to devops agent")
        print("  security <task_id> <audit_info_json>     Delegate to security agent")
        print("  status <task_id>                         Get task delegations")
        print("  current <task_id>                        Get current assignee")
        print("  context <task_id>                        Get full task context")
        print("  history [task_id]                        Get delegation history")
        print("  checkpoint [name] [description]          Create checkpoint")
        print("  exit-summary                             Generate exit summary")
        print("  has-changes                              Check for unsaved changes")
        sys.exit(1)

    delegator = AgentDelegator()
    command = sys.argv[1]

    try:
        if command == "architect":
            if len(sys.argv) < 4:
                print(
                    "Usage: agent_delegator.py architect <task_id> <requirements_json>"
                )
                sys.exit(1)
            task_id = sys.argv[2]
            requirements = json.loads(sys.argv[3])
            prompt = delegator.delegate_to_architect(task_id, requirements)
            print("ARCHITECT DELEGATION PROMPT:")
            print("=" * 50)
            print(prompt)

        elif command == "coder":
            if len(sys.argv) < 4:
                print("Usage: agent_delegator.py coder <task_id> <context_json>")
                sys.exit(1)
            task_id = sys.argv[2]
            context = json.loads(sys.argv[3])
            prompt = delegator.delegate_to_coder(task_id, context)
            print("CODER DELEGATION PROMPT:")
            print("=" * 50)
            print(prompt)

        elif command == "reviewer":
            if len(sys.argv) < 4:
                print(
                    "Usage: agent_delegator.py reviewer <task_id> <implementation_json>"
                )
                sys.exit(1)
            task_id = sys.argv[2]
            implementation_info = json.loads(sys.argv[3])
            prompt = delegator.delegate_to_reviewer(task_id, implementation_info)
            print("PR REVIEWER DELEGATION PROMPT:")
            print("=" * 50)
            print(prompt)

        elif command == "qa":
            if len(sys.argv) < 4:
                print("Usage: agent_delegator.py qa <task_id> <test_info_json>")
                sys.exit(1)
            task_id = sys.argv[2]
            test_info = json.loads(sys.argv[3])
            prompt = delegator.delegate_to_qa(task_id, test_info)
            print("QA/TESTER DELEGATION PROMPT:")
            print("=" * 50)
            print(prompt)

        elif command == "debug":
            if len(sys.argv) < 4:
                print("Usage: agent_delegator.py debug <task_id> <issue_info_json>")
                sys.exit(1)
            task_id = sys.argv[2]
            issue_info = json.loads(sys.argv[3])
            prompt = delegator.delegate_to_debug(task_id, issue_info)
            print("DEBUG AGENT DELEGATION PROMPT:")
            print("=" * 50)
            print(prompt)

        elif command == "docs":
            if len(sys.argv) < 4:
                print("Usage: agent_delegator.py docs <task_id> <docs_info_json>")
                sys.exit(1)
            task_id = sys.argv[2]
            docs_info = json.loads(sys.argv[3])
            prompt = delegator.delegate_to_docs(task_id, docs_info)
            print("DOCS AGENT DELEGATION PROMPT:")
            print("=" * 50)
            print(prompt)

        elif command == "devops":
            if len(sys.argv) < 4:
                print("Usage: agent_delegator.py devops <task_id> <infra_info_json>")
                sys.exit(1)
            task_id = sys.argv[2]
            infra_info = json.loads(sys.argv[3])
            prompt = delegator.delegate_to_devops(task_id, infra_info)
            print("DEVOPS AGENT DELEGATION PROMPT:")
            print("=" * 50)
            print(prompt)

        elif command == "security":
            if len(sys.argv) < 4:
                print("Usage: agent_delegator.py security <task_id> <audit_info_json>")
                sys.exit(1)
            task_id = sys.argv[2]
            audit_info = json.loads(sys.argv[3])
            prompt = delegator.delegate_to_security(task_id, audit_info)
            print("SECURITY AGENT DELEGATION PROMPT:")
            print("=" * 50)
            print(prompt)

        elif command == "status":
            if len(sys.argv) < 3:
                print("Usage: agent_delegator.py status <task_id>")
                sys.exit(1)
            task_id = sys.argv[2]
            delegations = delegator.get_task_delegations(task_id)
            print(json.dumps(delegations, indent=2))

        elif command == "current":
            if len(sys.argv) < 3:
                print("Usage: agent_delegator.py current <task_id>")
                sys.exit(1)
            task_id = sys.argv[2]
            current = delegator.get_current_assignee(task_id)
            if current:
                print(f"Current assignee: {current}")
            else:
                print("No current assignee found")

        elif command == "context":
            if len(sys.argv) < 3:
                print("Usage: agent_delegator.py context <task_id>")
                sys.exit(1)
            task_id = sys.argv[2]
            context = delegator.get_task_context(task_id)
            print(json.dumps(context, indent=2))

        elif command == "history":
            task_id = sys.argv[2] if len(sys.argv) > 2 else None
            history = delegator.get_delegation_history(task_id)
            print(json.dumps(history, indent=2))

        elif command == "checkpoint":
            name = sys.argv[2] if len(sys.argv) > 2 else None
            description = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
            checkpoint_id = delegator.create_checkpoint(name, description)
            print(f"Created checkpoint: {checkpoint_id}")

        elif command == "exit-summary":
            summary = delegator.generate_exit_summary()
            print(json.dumps(summary, indent=2))

        elif command == "has-changes":
            has_changes = delegator.has_unsaved_changes()
            print(f"Unsaved changes: {'Yes' if has_changes else 'No'}")
            sys.exit(0 if not has_changes else 1)

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
