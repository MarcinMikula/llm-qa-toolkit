"""Deterministic assessment eligibility and scoped gradability decisions."""

from __future__ import annotations

from assessment.models import (
    AssessmentEligibility,
    AssessmentRequest,
    AssessmentTarget,
    CandidateResponse,
    ExcludedTarget,
    ExclusionReason,
    RuleDefinition,
)


class AssessmentEligibilityChecker:
    """Calculate gradability from evidence and already-resolved rules.

    This class intentionally does not load rules, validate the complete test
    definition, or construct the evaluator-facing contract. Those responsibilities
    belong to :class:`AssessmentContractBuilder`.
    """

    def evaluate(
        self,
        candidate_response: CandidateResponse,
        request: AssessmentRequest,
        resolved_rules: tuple[RuleDefinition, ...],
    ) -> AssessmentEligibility:
        allowed_targets: set[AssessmentTarget] = set()
        excluded_targets: dict[AssessmentTarget, ExcludedTarget] = {}
        effective_required_evidence: dict[AssessmentTarget, frozenset[str]] = {}

        for target in request.requested_targets:
            rule_evidence = frozenset(
                evidence
                for rule in resolved_rules
                if target in rule.applies_to_targets
                for evidence in rule.required_evidence
            )
            required = frozenset(request.required_evidence[target] | rule_evidence)
            effective_required_evidence[target] = required
            missing = required - candidate_response.evidence

            if missing:
                excluded_targets[target] = ExcludedTarget(
                    target=target,
                    reason=ExclusionReason.MISSING_REQUIRED_EVIDENCE,
                    missing_evidence=frozenset(missing),
                )
            else:
                allowed_targets.add(target)

        applicable_rules = tuple(
            rule
            for rule in resolved_rules
            if rule.applies_to_targets & allowed_targets
        )

        return AssessmentEligibility(
            allowed_targets=frozenset(allowed_targets),
            excluded_targets=excluded_targets,
            effective_required_evidence=effective_required_evidence,
            applicable_rules=applicable_rules,
        )
