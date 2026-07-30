"""Deterministic validation of proposed evaluator output."""

from __future__ import annotations

from assessment.models import (
    AssessmentContract,
    EvaluationStatus,
    ProposedEvaluatorResult,
    ProposedFinding,
    RejectedArtifact,
    RejectedFinding,
    RejectionReason,
    ScopedEvaluationResult,
    TechnicalState,
    TechnicalStatus,
)


class EvaluationResultValidator:
    """Accept only findings permitted by the assessment contract."""

    def validate(
        self,
        contract: AssessmentContract,
        proposed_result: ProposedEvaluatorResult,
    ) -> ScopedEvaluationResult:
        if proposed_result.technical_status.state is not TechnicalState.COMPLETED:
            return ScopedEvaluationResult(
                case_id=contract.case_id,
                status=EvaluationStatus.ERROR,
                technical_status=proposed_result.technical_status,
                accepted_findings=(),
                rejected_findings=(),
                rejected_artifacts=(),
                not_assessed=tuple(contract.excluded_targets.values()),
            )

        accepted: list[ProposedFinding] = []
        rejected: list[RejectedFinding] = []
        artifacts: list[RejectedArtifact] = []

        if proposed_result.case_id != contract.case_id:
            mismatch_details = (
                f"Evaluator result case_id {proposed_result.case_id!r} does "
                f"not match contract case_id {contract.case_id!r}."
            )
            artifacts.append(
                RejectedArtifact(
                    artifact_type="evaluator_result",
                    reason=RejectionReason.CASE_ID_MISMATCH,
                    details=mismatch_details,
                )
            )
            rejected.extend(
                RejectedFinding(
                    finding=finding,
                    reason=RejectionReason.CASE_ID_MISMATCH,
                    details=mismatch_details,
                )
                for finding in proposed_result.findings
            )
        else:
            for finding in proposed_result.findings:
                rejection = self._validate_finding(contract, finding)
                if rejection is None:
                    accepted.append(finding)
                else:
                    rejected.append(rejection)

        if proposed_result.overall_score is not None and contract.is_partial:
            artifacts.append(
                RejectedArtifact(
                    artifact_type="overall_score",
                    reason=RejectionReason.OVERALL_SCORE_NOT_ALLOWED,
                    details=(
                        "Overall score is not allowed when one or more requested "
                        "assessment targets are excluded."
                    ),
                )
            )

        status = (
            EvaluationStatus.COMPLETED_WITH_REJECTIONS
            if rejected or artifacts
            else EvaluationStatus.COMPLETED
        )

        return ScopedEvaluationResult(
            case_id=contract.case_id,
            status=status,
            technical_status=TechnicalStatus.completed(),
            accepted_findings=tuple(accepted),
            rejected_findings=tuple(rejected),
            rejected_artifacts=tuple(artifacts),
            not_assessed=tuple(contract.excluded_targets.values()),
        )

    def technical_error_result(
        self,
        *,
        case_id: str,
        technical_status: TechnicalStatus,
    ) -> ScopedEvaluationResult:
        """Create a result for an upstream process error without a verdict."""

        return ScopedEvaluationResult(
            case_id=case_id,
            status=EvaluationStatus.ERROR,
            technical_status=technical_status,
            accepted_findings=(),
            rejected_findings=(),
            rejected_artifacts=(),
            not_assessed=(),
        )

    @staticmethod
    def _validate_finding(
        contract: AssessmentContract,
        finding: ProposedFinding,
    ) -> RejectedFinding | None:
        if finding.target not in contract.allowed_targets:
            return RejectedFinding(
                finding=finding,
                reason=RejectionReason.TARGET_NOT_ALLOWED,
                details=f"Target {finding.target.value!r} is outside allowed scope.",
            )

        if finding.verdict not in contract.allowed_verdicts[finding.target]:
            return RejectedFinding(
                finding=finding,
                reason=RejectionReason.VERDICT_NOT_ALLOWED,
                details=(
                    f"Verdict {finding.verdict.value!r} is not allowed for target "
                    f"{finding.target.value!r}."
                ),
            )

        rule = contract.rule_by_id(finding.rule_id)
        if rule is None:
            return RejectedFinding(
                finding=finding,
                reason=RejectionReason.UNKNOWN_RULE,
                details=f"Rule {finding.rule_id!r} is not applicable to this contract.",
            )

        if finding.target not in rule.applies_to_targets:
            return RejectedFinding(
                finding=finding,
                reason=RejectionReason.RULE_NOT_APPLICABLE_TO_TARGET,
                details=(
                    f"Rule {finding.rule_id!r} does not apply to target "
                    f"{finding.target.value!r}."
                ),
            )

        unavailable = finding.evidence_used - contract.available_evidence
        if unavailable:
            evidence = ", ".join(sorted(unavailable))
            return RejectedFinding(
                finding=finding,
                reason=RejectionReason.EVIDENCE_NOT_AVAILABLE,
                details=f"Finding references unavailable evidence: {evidence}.",
            )

        prohibited = finding.claims & contract.prohibited_claims
        if prohibited:
            claims = ", ".join(sorted(prohibited))
            return RejectedFinding(
                finding=finding,
                reason=RejectionReason.PROHIBITED_CLAIM,
                details=f"Finding makes prohibited claims: {claims}.",
            )

        return None
