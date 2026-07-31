"""Public construction path for evaluator-facing assessment contracts."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from typing import Mapping, TypeVar

from assessment.eligibility import AssessmentEligibilityChecker
from assessment.models import (
    AssessmentContract,
    AssessmentDefinitionError,
    AssessmentRequest,
    AssessmentTarget,
    CandidateResponse,
    ExcludedTarget,
    RuleDefinition,
    RuleStatus,
    TechnicalState,
    Verdict,
)
from assessment.rules import RuleCatalog

_K = TypeVar("_K")
_V = TypeVar("_V")


class AssessmentContractBuilder:
    """Validate a test definition and build an immutable assessment contract.

    The builder is the public boundary between configurable assessment input and
    the contract trusted by the evaluator adapter. It resolves controlled rules,
    delegates evidence-based gradability to ``AssessmentEligibilityChecker``, and
    rejects inconsistent configuration before evaluator invocation.
    """

    def __init__(
        self,
        rule_catalog: RuleCatalog | None = None,
        *,
        rule_files: tuple[Path, ...] = (),
        eligibility_checker: AssessmentEligibilityChecker | None = None,
    ) -> None:
        if rule_catalog is not None and rule_files:
            raise ValueError("Provide either rule_catalog or rule_files, not both.")

        self._rule_catalog = rule_catalog
        self._rule_files = rule_files
        self._eligibility_checker = (
            eligibility_checker or AssessmentEligibilityChecker()
        )

    @classmethod
    def from_rule_files(
        cls,
        *paths: str | Path,
    ) -> AssessmentContractBuilder:
        """Create a builder that lazily loads controlled rule files."""

        return cls(rule_files=tuple(Path(path) for path in paths))

    def build(
        self,
        candidate_response: CandidateResponse,
        request: AssessmentRequest,
    ) -> AssessmentContract:
        """Build a validated, defensive, evaluator-facing contract."""

        self._validate_candidate(candidate_response)
        self._validate_request(request)

        if candidate_response.case_id != request.case_id:
            raise AssessmentDefinitionError(
                "ASSESSMENT_CASE_ID_MISMATCH",
                "Candidate response case_id does not match assessment request case_id.",
            )

        resolved_rules = self._get_rule_catalog().resolve(
            request.requested_rule_ids,
            allowed_statuses=request.allowed_rule_statuses,
        )
        self._validate_rule_applicability(request, resolved_rules)

        eligibility = self._eligibility_checker.evaluate(
            candidate_response,
            request,
            resolved_rules,
        )

        allowed_verdicts = {
            target: frozenset(request.allowed_verdicts[target])
            for target in eligibility.allowed_targets
        }

        try:
            return AssessmentContract(
                case_id=request.case_id,
                candidate_response_id=candidate_response.response_id,
                allowed_targets=frozenset(eligibility.allowed_targets),
                excluded_targets=_immutable_mapping(eligibility.excluded_targets),
                applicable_rules=tuple(eligibility.applicable_rules),
                available_evidence=frozenset(candidate_response.evidence),
                effective_required_evidence=_immutable_mapping(
                    {
                        target: frozenset(evidence)
                        for target, evidence in (
                            eligibility.effective_required_evidence.items()
                        )
                    }
                ),
                allowed_verdicts=_immutable_mapping(allowed_verdicts),
                prohibited_claims=frozenset(request.prohibited_claims),
            )
        except ValueError as exc:
            raise AssessmentDefinitionError(
                "ASSESSMENT_CONTRACT_INVARIANT_VIOLATION",
                str(exc),
            ) from exc

    def _validate_candidate(self, candidate_response: CandidateResponse) -> None:
        if candidate_response.technical_status.state is not TechnicalState.COMPLETED:
            raise AssessmentDefinitionError(
                "CANDIDATE_RESPONSE_NOT_AVAILABLE",
                "Cannot build an assessment contract for a technical error.",
            )

        if not candidate_response.case_id.strip():
            raise AssessmentDefinitionError(
                "EMPTY_CANDIDATE_CASE_ID",
                "Candidate response case_id must be a non-empty string.",
            )

        if not candidate_response.response_id.strip():
            raise AssessmentDefinitionError(
                "EMPTY_CANDIDATE_RESPONSE_ID",
                "Candidate response response_id must be a non-empty string.",
            )

        empty_evidence = sorted(
            evidence for evidence in candidate_response.evidence if not evidence.strip()
        )
        if empty_evidence:
            raise AssessmentDefinitionError(
                "EMPTY_EVIDENCE_ID",
                "Candidate response evidence identifiers must be non-empty strings.",
            )

    def _validate_request(self, request: AssessmentRequest) -> None:
        if not request.case_id.strip():
            raise AssessmentDefinitionError(
                "EMPTY_ASSESSMENT_CASE_ID",
                "Assessment request case_id must be a non-empty string.",
            )

        if not request.requested_targets:
            raise AssessmentDefinitionError(
                "ASSESSMENT_TARGETS_EMPTY",
                "Assessment request must contain at least one target.",
            )

        requested_targets = tuple(request.requested_targets)
        requested_target_set = set(requested_targets)
        if len(requested_targets) != len(requested_target_set):
            raise AssessmentDefinitionError(
                "DUPLICATE_ASSESSMENT_TARGET",
                "Assessment request contains duplicate targets.",
            )

        self._validate_target_mapping(
            mapping_name="required_evidence",
            requested_targets=requested_target_set,
            actual_targets=set(request.required_evidence),
        )
        self._validate_target_mapping(
            mapping_name="allowed_verdicts",
            requested_targets=requested_target_set,
            actual_targets=set(request.allowed_verdicts),
        )

        empty_verdict_targets = sorted(
            target.value
            for target in requested_targets
            if not request.allowed_verdicts[target]
        )
        if empty_verdict_targets:
            raise AssessmentDefinitionError(
                "ALLOWED_VERDICTS_EMPTY",
                "Allowed verdicts cannot be empty for targets: "
                + ", ".join(empty_verdict_targets),
            )

        if len(request.requested_rule_ids) != len(set(request.requested_rule_ids)):
            raise AssessmentDefinitionError(
                "DUPLICATE_REQUESTED_RULE_ID",
                "Assessment request contains duplicate rule IDs.",
            )

        empty_rule_ids = [
            rule_id for rule_id in request.requested_rule_ids if not rule_id.strip()
        ]
        if empty_rule_ids:
            raise AssessmentDefinitionError(
                "EMPTY_REQUESTED_RULE_ID",
                "Requested rule IDs must be non-empty strings.",
            )

        if request.requested_rule_ids and not request.allowed_rule_statuses:
            raise AssessmentDefinitionError(
                "RULE_STATUSES_EMPTY",
                "At least one non-deprecated rule status must be allowed.",
            )

        if (
            request.requested_rule_ids
            and RuleStatus.DEPRECATED in request.allowed_rule_statuses
        ):
            raise AssessmentDefinitionError(
                "DEPRECATED_RULE_STATUS_NOT_ALLOWED",
                "DEPRECATED rules cannot be authorised for a new assessment contract.",
            )

        empty_claims = sorted(
            claim for claim in request.prohibited_claims if not claim.strip()
        )
        if empty_claims:
            raise AssessmentDefinitionError(
                "EMPTY_PROHIBITED_CLAIM",
                "Prohibited claim identifiers must be non-empty strings.",
            )

        for target, evidence_ids in request.required_evidence.items():
            if any(not evidence.strip() for evidence in evidence_ids):
                raise AssessmentDefinitionError(
                    "EMPTY_REQUIRED_EVIDENCE_ID",
                    (
                        "Required evidence identifiers must be non-empty strings "
                        f"for target {target.value}."
                    ),
                )

    def _validate_target_mapping(
        self,
        *,
        mapping_name: str,
        requested_targets: set[AssessmentTarget],
        actual_targets: set[AssessmentTarget],
    ) -> None:
        missing = requested_targets - actual_targets
        unexpected = actual_targets - requested_targets

        if missing:
            targets = ", ".join(sorted(target.value for target in missing))
            raise AssessmentDefinitionError(
                f"{mapping_name.upper()}_TARGET_MISSING",
                f"{mapping_name} is missing requested targets: {targets}",
            )

        if unexpected:
            targets = ", ".join(sorted(target.value for target in unexpected))
            raise AssessmentDefinitionError(
                f"{mapping_name.upper()}_TARGET_UNEXPECTED",
                f"{mapping_name} contains unrequested targets: {targets}",
            )

    def _validate_rule_applicability(
        self,
        request: AssessmentRequest,
        resolved_rules: tuple[RuleDefinition, ...],
    ) -> None:
        requested_targets = set(request.requested_targets)
        inapplicable = sorted(
            rule.rule_id
            for rule in resolved_rules
            if not rule.applies_to_targets & requested_targets
        )
        if inapplicable:
            raise AssessmentDefinitionError(
                "RULE_NOT_APPLICABLE_TO_REQUESTED_TARGETS",
                (
                    "Requested rules do not apply to any requested target: "
                    + ", ".join(inapplicable)
                ),
            )

    def _get_rule_catalog(self) -> RuleCatalog:
        if self._rule_catalog is None:
            if not self._rule_files:
                raise AssessmentDefinitionError(
                    "RULE_CATALOG_NOT_CONFIGURED",
                    "AssessmentContractBuilder requires a rule catalogue.",
                )
            self._rule_catalog = RuleCatalog.from_files(*self._rule_files)
        return self._rule_catalog


def _immutable_mapping(mapping: Mapping[_K, _V]) -> Mapping[_K, _V]:
    """Return a defensive read-only copy for a public runtime contract."""

    return MappingProxyType(dict(mapping))
