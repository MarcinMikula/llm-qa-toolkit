"""Typed contracts for the first assessment-grounded vertical slice.

The models are intentionally small. They represent only the information needed
by INS-MIXED-001 and avoid committing the project to a complete future schema.
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


class ExclusionReason(StrEnum):
    """Why a requested target was excluded from substantive assessment."""

    MISSING_REQUIRED_EVIDENCE = "MISSING_REQUIRED_EVIDENCE"


class RejectionReason(StrEnum):
    """Why a proposed evaluator output was not accepted."""

    TARGET_NOT_ALLOWED = "TARGET_NOT_ALLOWED"
    VERDICT_NOT_ALLOWED = "VERDICT_NOT_ALLOWED"
    UNKNOWN_RULE = "UNKNOWN_RULE"
    EVIDENCE_NOT_AVAILABLE = "EVIDENCE_NOT_AVAILABLE"
    PROHIBITED_CLAIM = "PROHIBITED_CLAIM"
    OVERALL_SCORE_NOT_ALLOWED = "OVERALL_SCORE_NOT_ALLOWED"
    CASE_ID_MISMATCH = "CASE_ID_MISMATCH"


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
    applicable_rules: frozenset[str]
    allowed_verdicts: Mapping[AssessmentTarget, frozenset[Verdict]]
    prohibited_claims: frozenset[str]

    def __post_init__(self) -> None:
        requested = set(self.requested_targets)
        missing_requirements = requested - set(self.required_evidence)
        missing_verdicts = requested - set(self.allowed_verdicts)

        if missing_requirements:
            targets = ", ".join(sorted(target.value for target in missing_requirements))
            raise ValueError(f"Missing evidence requirements for targets: {targets}")

        if missing_verdicts:
            targets = ", ".join(sorted(target.value for target in missing_verdicts))
            raise ValueError(f"Missing allowed verdicts for targets: {targets}")


@dataclass(frozen=True)
class ExcludedTarget:
    """A requested target that cannot be substantively assessed."""

    target: AssessmentTarget
    reason: ExclusionReason
    missing_evidence: frozenset[str]


@dataclass(frozen=True)
class AssessmentContract:
    """Deterministic boundary supplied to the external evaluator."""

    case_id: str
    candidate_response_id: str
    allowed_targets: frozenset[AssessmentTarget]
    excluded_targets: Mapping[AssessmentTarget, ExcludedTarget]
    applicable_rules: frozenset[str]
    available_evidence: frozenset[str]
    allowed_verdicts: Mapping[AssessmentTarget, frozenset[Verdict]]
    prohibited_claims: frozenset[str]

    @property
    def is_partial(self) -> bool:
        return bool(self.excluded_targets)


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
