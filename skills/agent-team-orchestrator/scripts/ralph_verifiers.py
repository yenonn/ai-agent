#!/usr/bin/env python3
"""
Ralph Loop Verification Functions for Agent-Team Orchestrator

Each agent role has a verification function that determines if their task
is truly complete before handing off to the next agent.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
import re


@dataclass
class VerificationResult:
    """Result of a verification check"""
    complete: bool
    reason: str
    feedback: Optional[str] = None  # Feedback for next iteration if incomplete
    confidence: float = 1.0  # 0.0 to 1.0


class AgentVerifiers:
    """Verification functions for each agent role"""
    
    @staticmethod
    def architect_verifier(result: Dict[str, Any], context: Dict[str, Any]) -> VerificationResult:
        """
        Verify Architect agent has completed comprehensive technical specifications.
        
        Required deliverables:
        - Architecture overview
        - Component design with responsibilities
        - API specifications (endpoints, data models)
        - Database schema (if applicable)
        - Security considerations
        - Performance requirements
        - Success criteria and quality gates
        """
        output = result.get('text', '')
        
        # Check for required sections
        required_sections = [
            ('architecture overview', r'(?i)(architecture\s+overview|system\s+design|high-level\s+design)'),
            ('component design', r'(?i)(component|module|service)\s+(design|breakdown|architecture)'),
            ('api specifications', r'(?i)(api|endpoint|interface)\s+(spec|design|documentation)'),
            ('security', r'(?i)(security|authentication|authorization)'),
            ('success criteria', r'(?i)(success\s+criteria|quality\s+gates|acceptance\s+criteria)')
        ]
        
        missing_sections = []
        for section_name, pattern in required_sections:
            if not re.search(pattern, output):
                missing_sections.append(section_name)
        
        # Check for completeness markers
        has_handoff_ready = 'handoff' in output.lower() or 'ready for implementation' in output.lower()
        
        if not missing_sections and has_handoff_ready:
            return VerificationResult(
                complete=True,
                reason="All architectural specifications provided with clear implementation guidance",
                confidence=0.95
            )
        
        feedback_parts = []
        if missing_sections:
            feedback_parts.append(f"Missing sections: {', '.join(missing_sections)}")
        if not has_handoff_ready:
            feedback_parts.append("Include explicit handoff readiness statement with implementation priorities")
        
        return VerificationResult(
            complete=False,
            reason="Architectural specifications incomplete",
            feedback=" | ".join(feedback_parts),
            confidence=0.7
        )
    
    @staticmethod
    def coder_verifier(result: Dict[str, Any], context: Dict[str, Any]) -> VerificationResult:
        """
        Verify Coder agent has completed implementation with tests.
        
        Verification checks:
        - Code implementation present
        - Tests written and passing
        - Error handling implemented
        - Documentation added
        - Matches architectural specifications
        """
        output = result.get('text', '')
        tool_calls = result.get('toolCalls', [])
        
        # Check if tests were run
        test_executed = any('test' in str(call).lower() or 'pytest' in str(call).lower() 
                           for call in tool_calls)
        
        # Check for test success indicators
        tests_passing = bool(re.search(r'(?i)(all\s+tests?\s+pass|tests?\s+successful|\d+\s+passed)', output))
        
        # Check for implementation completeness
        has_error_handling = bool(re.search(r'(?i)(error\s+handling|try\s*[/{]|except|catch)', output))
        has_documentation = bool(re.search(r'(?i)(docstring|documentation|commented|readme)', output))
        
        # Check for "ready for review" marker
        ready_for_review = bool(re.search(r'(?i)(ready\s+for\s+review|implementation\s+complete)', output))
        
        checks = {
            'tests_executed': test_executed,
            'tests_passing': tests_passing,
            'error_handling': has_error_handling,
            'documentation': has_documentation,
            'ready': ready_for_review
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        if passed == total:
            return VerificationResult(
                complete=True,
                reason="Implementation complete with passing tests and documentation",
                confidence=0.9
            )
        
        missing = [k.replace('_', ' ') for k, v in checks.items() if not v]
        return VerificationResult(
            complete=False,
            reason=f"Implementation incomplete: {passed}/{total} checks passed",
            feedback=f"Required: {', '.join(missing)}",
            confidence=passed / total
        )
    
    @staticmethod
    def reviewer_verifier(result: Dict[str, Any], context: Dict[str, Any]) -> VerificationResult:
        """
        Verify PR Reviewer agent has completed thorough code review.
        
        Verification checks:
        - Security review completed
        - Code quality assessment done
        - Test coverage verified
        - Performance considerations noted
        - Clear approval or change requests
        """
        output = result.get('text', '')
        
        # Check for review sections
        review_sections = [
            ('security', r'(?i)(security|vulnerabilities|auth|sanitization)'),
            ('code quality', r'(?i)(code\s+quality|readability|maintainability|patterns)'),
            ('testing', r'(?i)(test\s+coverage|tests?|testing)'),
            ('performance', r'(?i)(performance|optimization|efficiency)')
        ]
        
        completed_sections = []
        for section_name, pattern in review_sections:
            if re.search(pattern, output):
                completed_sections.append(section_name)
        
        # Check for explicit decision
        has_approval = bool(re.search(r'(?i)(approved|lgtm|looks\s+good|ready\s+to\s+merge)', output))
        has_changes_requested = bool(re.search(r'(?i)(changes?\s+required|must\s+fix|critical|blocking)', output))
        has_decision = has_approval or has_changes_requested
        
        # Count critical/high/medium/low issues if present
        critical_issues = len(re.findall(r'(?i)critical', output))
        high_issues = len(re.findall(r'(?i)high\s+priority', output))
        
        if len(completed_sections) >= 3 and has_decision:
            if has_approval or (critical_issues == 0 and high_issues == 0):
                return VerificationResult(
                    complete=True,
                    reason="Comprehensive review completed with clear decision",
                    confidence=0.95
                )
        
        feedback_parts = []
        if len(completed_sections) < 3:
            missing = set(dict(review_sections).keys()) - set(completed_sections)
            feedback_parts.append(f"Complete review sections: {', '.join(missing)}")
        if not has_decision:
            feedback_parts.append("Provide explicit approval or change request decision")
        
        return VerificationResult(
            complete=False,
            reason="Review incomplete or decision unclear",
            feedback=" | ".join(feedback_parts) if feedback_parts else None,
            confidence=len(completed_sections) / len(review_sections)
        )
    
    @staticmethod
    def debug_verifier(result: Dict[str, Any], context: Dict[str, Any]) -> VerificationResult:
        """
        Verify Debug agent has identified root cause and validated fix strategy.
        
        Verification checks:
        - Bug reproduced and confirmed
        - Root cause identified (not just symptoms)
        - Affected code paths traced
        - Fix strategy proposed
        - Verification steps defined
        """
        output = result.get('text', '')
        
        # Check for debugging completeness
        checks = {
            'reproduced': bool(re.search(r'(?i)(reproduced|confirmed|verified\s+issue)', output)),
            'root_cause': bool(re.search(r'(?i)(root\s+cause|underlying\s+(issue|problem)|why\s+.+\s+occurs)', output)),
            'code_path': bool(re.search(r'(?i)(code\s+path|stack\s+trace|call\s+stack|line\s+\d+)', output)),
            'fix_strategy': bool(re.search(r'(?i)(fix|solution|resolve|proposed\s+change)', output)),
            'verification': bool(re.search(r'(?i)(verification|test\s+plan|how\s+to\s+verify)', output))
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        # Extra check: ensure it's not just symptom description
        has_deep_analysis = bool(re.search(r'(?i)(because|due\s+to|caused\s+by|reason)', output))
        
        if passed >= 4 and has_deep_analysis:
            return VerificationResult(
                complete=True,
                reason="Root cause identified with clear fix strategy and verification plan",
                confidence=0.9
            )
        
        missing = [k.replace('_', ' ') for k, v in checks.items() if not v]
        feedback = f"Debug analysis incomplete. Required: {', '.join(missing)}"
        
        if not has_deep_analysis:
            feedback += " | Explain WHY the bug occurs, not just WHAT is happening"
        
        return VerificationResult(
            complete=False,
            reason=f"Debug investigation incomplete: {passed}/{total} checks passed",
            feedback=feedback,
            confidence=passed / total
        )
    
    @staticmethod
    def docs_verifier(result: Dict[str, Any], context: Dict[str, Any]) -> VerificationResult:
        """
        Verify Docs agent has created comprehensive, accurate documentation.
        
        Verification checks:
        - Clear overview/summary present
        - Usage examples included
        - API/configuration documented
        - Properly formatted (markdown)
        - Up-to-date with implementation
        """
        output = result.get('text', '')
        
        checks = {
            'overview': bool(re.search(r'(?i)(overview|summary|introduction|about)', output)),
            'examples': bool(re.search(r'(?i)(example|usage|how\s+to|getting\s+started)', output)),
            'api_docs': bool(re.search(r'(?i)(api|endpoint|function|method|parameter)', output)),
            'formatting': bool(re.search(r'(```|#\s+\w+|\*\*\w+\*\*)', output)),  # Markdown indicators
            'complete_marker': bool(re.search(r'(?i)(documentation\s+complete|docs\s+updated)', output))
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        if passed >= 4:
            return VerificationResult(
                complete=True,
                reason="Documentation comprehensive and properly formatted",
                confidence=0.85
            )
        
        missing = [k.replace('_', ' ') for k, v in checks.items() if not v]
        return VerificationResult(
            complete=False,
            reason=f"Documentation incomplete: {passed}/{total} checks passed",
            feedback=f"Required: {', '.join(missing)}",
            confidence=passed / total
        )
    
    @staticmethod
    def devops_verifier(result: Dict[str, Any], context: Dict[str, Any]) -> VerificationResult:
        """
        Verify DevOps agent has configured complete CI/CD and infrastructure.
        
        Verification checks:
        - Pipeline configuration present
        - Deployment strategy defined
        - Monitoring/logging configured
        - Environment configs handled
        - Pipeline tested successfully
        """
        output = result.get('text', '')
        tool_calls = result.get('toolCalls', [])
        
        # Check for config files created
        config_files = ['yml', 'yaml', 'json', 'tf', 'dockerfile']
        files_created = any(ext in str(tool_calls).lower() for ext in config_files)
        
        checks = {
            'pipeline': bool(re.search(r'(?i)(pipeline|ci/cd|workflow|actions)', output)),
            'deployment': bool(re.search(r'(?i)(deploy|deployment|rollout|release)', output)),
            'monitoring': bool(re.search(r'(?i)(monitoring|logging|metrics|alerts)', output)),
            'config': bool(re.search(r'(?i)(environment|config|secrets|variables)', output)),
            'tested': bool(re.search(r'(?i)(tested|verified|validated|successful)', output)),
            'files_created': files_created
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        if passed >= 5:
            return VerificationResult(
                complete=True,
                reason="DevOps infrastructure complete and tested",
                confidence=0.9
            )
        
        missing = [k.replace('_', ' ') for k, v in checks.items() if not v]
        return VerificationResult(
            complete=False,
            reason=f"DevOps setup incomplete: {passed}/{total} checks passed",
            feedback=f"Required: {', '.join(missing)}",
            confidence=passed / total
        )
    
    @staticmethod
    def security_verifier(result: Dict[str, Any], context: Dict[str, Any]) -> VerificationResult:
        """
        Verify Security agent has completed thorough security audit.
        
        Verification checks:
        - Vulnerability scan performed
        - Findings categorized by severity
        - Authentication/authorization reviewed
        - Input validation checked
        - Remediation steps provided
        """
        output = result.get('text', '')
        
        # Check for severity classifications
        has_critical = 'critical' in output.lower()
        has_high = 'high' in output.lower()
        has_medium = 'medium' in output.lower()
        has_low = 'low' in output.lower()
        has_severity = has_critical or has_high or has_medium or has_low
        
        checks = {
            'vulnerability_scan': bool(re.search(r'(?i)(vulnerabilit|security\s+scan|audit|assessment)', output)),
            'severity_classification': has_severity,
            'auth_review': bool(re.search(r'(?i)(authentication|authorization|access\s+control)', output)),
            'input_validation': bool(re.search(r'(?i)(input\s+validation|sanitization|injection)', output)),
            'remediation': bool(re.search(r'(?i)(remediation|fix|recommendation|mitigation)', output))
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        # Security audits should be thorough
        if passed == total:
            return VerificationResult(
                complete=True,
                reason="Comprehensive security audit completed with remediation guidance",
                confidence=0.95
            )
        
        missing = [k.replace('_', ' ') for k, v in checks.items() if not v]
        return VerificationResult(
            complete=False,
            reason=f"Security audit incomplete: {passed}/{total} checks passed",
            feedback=f"Required: {', '.join(missing)}",
            confidence=passed / total
        )


def get_verifier_for_agent(agent_type: str):
    """Get the appropriate verification function for an agent type"""
    verifier_map = {
        'architect': AgentVerifiers.architect_verifier,
        'coder': AgentVerifiers.coder_verifier,
        'reviewer': AgentVerifiers.reviewer_verifier,
        'debug': AgentVerifiers.debug_verifier,
        'docs': AgentVerifiers.docs_verifier,
        'devops': AgentVerifiers.devops_verifier,
        'security': AgentVerifiers.security_verifier
    }
    return verifier_map.get(agent_type.lower())


if __name__ == '__main__':
    # Test verification functions
    print("Ralph Loop Verifiers loaded successfully")
    print("\nAvailable verifiers:")
    for agent_type in ['architect', 'coder', 'reviewer', 'debug', 'docs', 'devops', 'security']:
        print(f"  - {agent_type}")
