"""Deterministic assessment eligibility and scope selection."""

from __future__ import annotations

from assessment.models import (
    AssessmentContract,
    AssessmentRequest,
    CandidateResponse,
    ExcludedTarget,
    ExclusionReason,
    TechnicalState,
)


class AssessmentEligibilityChecker:
    """Build an assessment contract from explicit evidence requirements."""

    def build_contract(
        self,
        candidate_response: CandidateResponse,
        request: AssessmentRequest,
    ) -> AssessmentContract:
        if candidate_response.technical_status.state is not TechnicalState.COMPLETED:
            raise ValueError("Cannot build an assessment contract for a technical error.")

        if candidate_response.case_id != request.case_id:
            raise ValueError(
                "Candidate response case_id does not match assessment request case_id."
            )

        allowed_targets = set()
        excluded_targets = {}

        for target in request.requested_targets:
            required = request.required_evidence[target]
            missing = required - candidate_response.evidence

            if missing:
                excluded_targets[target] = ExcludedTarget(
                    target=target,
                    reason=ExclusionReason.MISSING_REQUIRED_EVIDENCE,
                    missing_evidence=frozenset(missing),
                )
            else:
                allowed_targets.add(target)

        allowed_verdicts = {
            target: request.allowed_verdicts[target] for target in allowed_targets
        }

        return AssessmentContract(
            case_id=request.case_id,
            candidate_response_id=candidate_response.response_id,
            allowed_targets=frozenset(allowed_targets),
            excluded_targets=excluded_targets,
            applicable_rules=request.applicable_rules,
            available_evidence=candidate_response.evidence,
            allowed_verdicts=allowed_verdicts,
            prohibited_claims=request.prohibited_claims,
        )
