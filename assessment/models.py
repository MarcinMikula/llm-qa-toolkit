"""Typed contracts for the assessment-grounded runtime.

The models remain intentionally small. They cover the controlled rule-catalogue
slice and the INS-MIXED-001 scenario without pretending to be a complete future
schema for every domain or evaluator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class TechnicalState(StrEnum):
    """Technical execution status, separate from substantive findings."""

    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class EvaluationStatus(StrEnum):
    """Status of the assessment process itself."""

    COMPLETED = "COMPLETED"
    COMPLETED_WITH_REJECTIONS = "COMPLETED_WITH_REJECTIONS"
    ERROR = "ERROR"


class SourceType(StrEnum):
    """Origin of a candidate response."""

    SYNTHETIC = "synthetic"
    LIVE_CAPTURE = "live_capture"
    MANUAL_CAPTURE = "manual_capture"


class Verdict(StrEnum):
    """Substantive verdicts proposed for gradable targets."""

    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class AssessmentTarget(StrEnum):
    """Targets used by the first mixed-domain assessment case."""

    INTENT_SEPARATION = "intent_separation"
    INSURANCE_RESPONSE_STRATEGY = "insurance_response_strategy"
    DOMAIN_BOUNDARY_COMPLIANCE = "domain_boundary_compliance"
    LIVE_DATA_HANDLING = "live_data_handling"
    UNSUPPORTED_CERTAINTY = "unsupported_certainty"
    ACTUAL_INSURANCE_LIABILITY = "actual_insurance_liability"
    ACTUAL_WARSAW_WEATHER = "actual_warsaw_weather"
    NUTRITIONAL_OR_MEDICAL_CORRECTNESS = "nutritional_or_medical_correctness"


class RuleStatus(StrEnum):
    """Controlled lifecycle or authority status of a rule definition."""

    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    VALIDATED = "VALIDATED"
    DEPRECATED = "DEPRECATED"


class ExclusionReason(StrEnum):
    """Why a requested target was excluded from substantive assessment."""

    MISSING_REQUIRED_EVIDENCE = "MISSING_REQUIRED_EVIDENCE"


class RejectionReason(StrEnum):
    """Why a proposed evaluator output was not accepted."""

    TARGET_NOT_ALLOWED = "TARGET_NOT_ALLOWED"
    VERDICT_NOT_ALLOWED = "VERDICT_NOT_ALLOWED"
    UNKNOWN_RULE = "UNKNOWN_RULE"
    RULE_NOT_APPLICABLE_TO_TARGET = "RULE_NOT_APPLICABLE_TO_TARGET"
    EVIDENCE_NOT_AVAILABLE = "EVIDENCE_NOT_AVAILABLE"
    PROHIBITED_CLAIM = "PROHIBITED_CLAIM"
    OVERALL_SCORE_NOT_ALLOWED = "OVERALL_SCORE_NOT_ALLOWED"
    CASE_ID_MISMATCH = "CASE_ID_MISMATCH"


class AssessmentDefinitionError(ValueError):
    """Invalid assessment configuration or Test Basis, not examinee failure."""

    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type


@dataclass(frozen=True)
class TechnicalStatus:
    """Technical status carried by adapters and evaluation results."""

    state: TechnicalState
    error_type: str | None = None
    message: str | None = None

    @classmethod
    def completed(cls) -> TechnicalStatus:
        return cls(state=TechnicalState.COMPLETED)

    @classmethod
    def error(cls, error_type: str, message: str) -> TechnicalStatus:
        return cls(
            state=TechnicalState.ERROR,
            error_type=error_type,
            message=message,
        )


@dataclass(frozen=True)
class ResponseProvenance:
    """Traceability metadata for a replayed candidate response."""

    source_type: SourceType
    creation_method: str
    live_model_response: bool
    validation_purpose: str


@dataclass(frozen=True)
class RuleSource:
    """Declared authority source for a controlled rule definition."""

    source_type: str
    reference: str


@dataclass(frozen=True)
class RuleDefinition:
    """Versioned rule content supplied to assessment-contract construction."""

    rule_id: str
    version: str
    status: RuleStatus
    title: str
    evaluator_instruction: str
    applies_to_targets: frozenset[AssessmentTarget]
    required_evidence: frozenset[str]
    source: RuleSource
    forbidden_behaviours: tuple[str, ...] = ()
    permitted_conclusions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        text_fields = {
            "rule_id": self.rule_id,
            "version": self.version,
            "title": self.title,
            "evaluator_instruction": self.evaluator_instruction,
            "source.source_type": self.source.source_type,
            "source.reference": self.source.reference,
        }
        empty_fields = [name for name, value in text_fields.items() if not value.strip()]
        if empty_fields:
            joined = ", ".join(empty_fields)
            raise ValueError(f"Rule definition contains empty fields: {joined}")

        if not self.applies_to_targets:
            raise ValueError("Rule definition must apply to at least one target.")


@dataclass(frozen=True)
class ExamineeRequest:
    """Input sent through an examinee port."""

    case_id: str
    stimulus: str


@dataclass(frozen=True)
class CandidateResponse:
    """Normalised response returned by any examinee adapter."""

    response_id: str
    case_id: str
    text: str
    evidence: frozenset[str]
    metadata: Mapping[str, Any]
    provenance: ResponseProvenance
    technical_status: TechnicalStatus


@dataclass(frozen=True)
class AssessmentRequest:
    """Supplied basis for deterministic eligibility and scope selection."""

    case_id: str
    requested_targets: tuple[AssessmentTarget, ...]
    required_evidence: Mapping[AssessmentTarget, frozenset[str]]
    requested_rule_ids: tuple[str, ...]
    allowed_rule_statuses: frozenset[RuleStatus]
    allowed_verdicts: Mapping[AssessmentTarget, frozenset[Verdict]]
    prohibited_claims: frozenset[str]




@dataclass(frozen=True)
class ExcludedTarget:
    """A requested target that cannot be substantively assessed."""

    target: AssessmentTarget
    reason: ExclusionReason
    missing_evidence: frozenset[str]


@dataclass(frozen=True)
class AssessmentEligibility:
    """Evidence-based gradability decision before contract construction."""

    allowed_targets: frozenset[AssessmentTarget]
    excluded_targets: Mapping[AssessmentTarget, ExcludedTarget]
    effective_required_evidence: Mapping[AssessmentTarget, frozenset[str]]
    applicable_rules: tuple[RuleDefinition, ...]


@dataclass(frozen=True)
class AssessmentContract:
    """Deterministic boundary supplied to the external evaluator."""

    case_id: str
    candidate_response_id: str
    allowed_targets: frozenset[AssessmentTarget]
    excluded_targets: Mapping[AssessmentTarget, ExcludedTarget]
    applicable_rules: tuple[RuleDefinition, ...]
    available_evidence: frozenset[str]
    effective_required_evidence: Mapping[AssessmentTarget, frozenset[str]]
    allowed_verdicts: Mapping[AssessmentTarget, frozenset[Verdict]]
    prohibited_claims: frozenset[str]

    def __post_init__(self) -> None:
        rule_ids = [rule.rule_id for rule in self.applicable_rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("Assessment contract contains duplicate rule IDs.")

        if self.allowed_targets & set(self.excluded_targets):
            raise ValueError(
                "Allowed and excluded assessment targets must be disjoint."
            )

        all_targets = self.allowed_targets | set(self.excluded_targets)
        if set(self.effective_required_evidence) != all_targets:
            raise ValueError(
                "Effective evidence requirements must cover every requested target."
            )

        if set(self.allowed_verdicts) != set(self.allowed_targets):
            raise ValueError(
                "Allowed verdicts must exist exactly for allowed assessment targets."
            )

        if any(
            not rule.applies_to_targets & self.allowed_targets
            for rule in self.applicable_rules
        ):
            raise ValueError(
                "Every rule in the contract must apply to an allowed target."
            )

    @property
    def is_partial(self) -> bool:
        return bool(self.excluded_targets)

    @property
    def rule_ids(self) -> frozenset[str]:
        """IDs available to the evaluator-result validator."""

        return frozenset(rule.rule_id for rule in self.applicable_rules)

    def rule_by_id(self, rule_id: str) -> RuleDefinition | None:
        """Return a resolved rule definition from this exact contract."""

        return next(
            (rule for rule in self.applicable_rules if rule.rule_id == rule_id),
            None,
        )


@dataclass(frozen=True)
class ProposedFinding:
    """Finding proposed by an evaluator before deterministic validation."""

    finding_id: str
    target: AssessmentTarget
    verdict: Verdict
    rule_id: str
    evidence_used: frozenset[str]
    rationale: str
    claims: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class ProposedEvaluatorResult:
    """Normalised but not yet trusted evaluator output."""

    case_id: str
    technical_status: TechnicalStatus
    findings: tuple[ProposedFinding, ...]
    overall_score: float | None = None
    raw_output: str | None = None


@dataclass(frozen=True)
class RejectedFinding:
    """Evaluator finding retained for traceability but not accepted."""

    finding: ProposedFinding
    reason: RejectionReason
    details: str


@dataclass(frozen=True)
class RejectedArtifact:
    """Non-finding evaluator output rejected by the protocol."""

    artifact_type: str
    reason: RejectionReason
    details: str


@dataclass(frozen=True)
class ScopedEvaluationResult:
    """Final result after deterministic validation of evaluator output."""

    case_id: str
    status: EvaluationStatus
    technical_status: TechnicalStatus
    accepted_findings: tuple[ProposedFinding, ...]
    rejected_findings: tuple[RejectedFinding, ...]
    rejected_artifacts: tuple[RejectedArtifact, ...]
    not_assessed: tuple[ExcludedTarget, ...]

    @property
    def has_substantive_failure(self) -> bool:
        """Only accepted FAIL findings count as substantive failures."""

        return any(
            finding.verdict is Verdict.FAIL for finding in self.accepted_findings
        )


@dataclass(frozen=True)
class AssessmentRun:
    """Traceable output of the complete assessment pipeline."""

    candidate_response: CandidateResponse
    assessment_contract: AssessmentContract | None
    proposed_evaluator_result: ProposedEvaluatorResult | None
    scoped_result: ScopedEvaluationResult
