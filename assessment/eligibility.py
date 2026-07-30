"""Deterministic assessment eligibility, rule resolution, and scope selection."""

from __future__ import annotations

from pathlib import Path

from assessment.models import (
    AssessmentContract,
    AssessmentDefinitionError,
    AssessmentRequest,
    AssessmentTarget,
    CandidateResponse,
    ExcludedTarget,
    ExclusionReason,
    TechnicalState,
)
from assessment.rules import RuleCatalog


class AssessmentEligibilityChecker:
    """Build an assessment contract from evidence and controlled rules."""

    def __init__(
        self,
        rule_catalog: RuleCatalog | None = None,
        *,
        rule_files: tuple[Path, ...] = (),
    ) -> None:
        if rule_catalog is not None and rule_files:
            raise ValueError("Provide either rule_catalog or rule_files, not both.")

        self._rule_catalog = rule_catalog
        self._rule_files = rule_files

    @classmethod
    def from_rule_files(
        cls,
        *paths: str | Path,
    ) -> AssessmentEligibilityChecker:
        """Create a checker that loads rule files inside the assessment run."""

        return cls(rule_files=tuple(Path(path) for path in paths))

    def build_contract(
        self,
        candidate_response: CandidateResponse,
        request: AssessmentRequest,
    ) -> AssessmentContract:
        if candidate_response.technical_status.state is not TechnicalState.COMPLETED:
            raise AssessmentDefinitionError(
                "CANDIDATE_RESPONSE_NOT_AVAILABLE",
                "Cannot build an assessment contract for a technical error.",
            )

        if candidate_response.case_id != request.case_id:
            raise AssessmentDefinitionError(
                "ASSESSMENT_CASE_ID_MISMATCH",
                "Candidate response case_id does not match assessment request case_id.",
            )

        resolved_rules = self._get_rule_catalog().resolve(
            request.requested_rule_ids,
            allowed_statuses=request.allowed_rule_statuses,
        )

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
            required = request.required_evidence[target] | rule_evidence
            effective_required_evidence[target] = frozenset(required)
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
        applicable_rules = tuple(
            rule
            for rule in resolved_rules
            if rule.applies_to_targets & allowed_targets
        )

        return AssessmentContract(
            case_id=request.case_id,
            candidate_response_id=candidate_response.response_id,
            allowed_targets=frozenset(allowed_targets),
            excluded_targets=excluded_targets,
            applicable_rules=applicable_rules,
            available_evidence=candidate_response.evidence,
            effective_required_evidence=effective_required_evidence,
            allowed_verdicts=allowed_verdicts,
            prohibited_claims=request.prohibited_claims,
        )

    def _get_rule_catalog(self) -> RuleCatalog:
        if self._rule_catalog is None:
            if not self._rule_files:
                raise AssessmentDefinitionError(
                    "RULE_CATALOG_NOT_CONFIGURED",
                    "AssessmentEligibilityChecker requires a rule catalogue.",
                )
            self._rule_catalog = RuleCatalog.from_files(*self._rule_files)
        return self._rule_catalog
