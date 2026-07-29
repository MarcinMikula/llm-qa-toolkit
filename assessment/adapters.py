"""Replay and stub adapters for the first zero-cost vertical slice."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from assessment.models import (
    AssessmentContract,
    AssessmentRequest,
    AssessmentTarget,
    CandidateResponse,
    ExamineeRequest,
    ProposedEvaluatorResult,
    ProposedFinding,
    ResponseProvenance,
    SourceType,
    TechnicalState,
    TechnicalStatus,
    Verdict,
)


class ReplayExamineeAdapter:
    """Loads a controlled candidate response from a JSON replay fixture."""

    def __init__(self, fixture_path: str | Path) -> None:
        self._fixture_path = Path(fixture_path)

    def respond(self, request: ExamineeRequest) -> CandidateResponse:
        try:
            fixture = _load_json(self._fixture_path)
        except FileNotFoundError:
            return _technical_error_response(
                request=request,
                fixture_path=self._fixture_path,
                error_type="REPLAY_FILE_NOT_FOUND",
                message=f"Replay fixture does not exist: {self._fixture_path}",
            )
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            return _technical_error_response(
                request=request,
                fixture_path=self._fixture_path,
                error_type="REPLAY_PARSE_ERROR",
                message=str(exc),
            )

        if fixture["case_id"] != request.case_id or fixture["stimulus"] != request.stimulus:
            return _technical_error_response(
                request=request,
                fixture_path=self._fixture_path,
                error_type="REPLAY_REQUEST_MISMATCH",
                message="Replay case_id or stimulus does not match the request.",
            )

        candidate = fixture["candidate_response"]
        provenance = candidate["provenance"]

        return CandidateResponse(
            response_id=str(candidate["response_id"]),
            case_id=request.case_id,
            text=str(candidate["text"]),
            evidence=frozenset(str(item) for item in candidate["evidence"]),
            metadata=dict(candidate.get("metadata", {})),
            provenance=ResponseProvenance(
                source_type=SourceType(provenance["source_type"]),
                creation_method=str(provenance["creation_method"]),
                live_model_response=bool(provenance["live_model_response"]),
                validation_purpose=str(provenance["validation_purpose"]),
            ),
            technical_status=TechnicalStatus.completed(),
        )


class StubEvaluatorAdapter:
    """Returns a controlled evaluator result without invoking a live model."""

    def __init__(self, result: ProposedEvaluatorResult) -> None:
        self._result = result
        self.call_count = 0
        self.last_contract: AssessmentContract | None = None

    def evaluate(
        self,
        candidate_response: CandidateResponse,
        contract: AssessmentContract,
    ) -> ProposedEvaluatorResult:
        self.call_count += 1
        self.last_contract = contract
        return self._result

    @classmethod
    def from_fixture(cls, fixture_path: str | Path) -> StubEvaluatorAdapter:
        fixture = _load_json(Path(fixture_path))
        raw_result = fixture["stub_evaluator_result"]
        status = raw_result.get("technical_status", {"state": "COMPLETED"})

        findings = tuple(
            ProposedFinding(
                finding_id=str(item["finding_id"]),
                target=AssessmentTarget(item["target"]),
                verdict=Verdict(item["verdict"]),
                rule_id=str(item["rule_id"]),
                evidence_used=frozenset(
                    str(evidence) for evidence in item.get("evidence_used", [])
                ),
                rationale=str(item["rationale"]),
                claims=frozenset(str(claim) for claim in item.get("claims", [])),
            )
            for item in raw_result.get("findings", [])
        )

        technical_status = TechnicalStatus(
            state=TechnicalState(status["state"]),
            error_type=status.get("error_type"),
            message=status.get("message"),
        )

        return cls(
            ProposedEvaluatorResult(
                case_id=str(fixture["case_id"]),
                technical_status=technical_status,
                findings=findings,
                overall_score=raw_result.get("overall_score"),
                raw_output=json.dumps(raw_result, ensure_ascii=False),
            )
        )


def load_examinee_request(fixture_path: str | Path) -> ExamineeRequest:
    """Load the replay request defined by a controlled fixture."""

    fixture = _load_json(Path(fixture_path))
    return ExamineeRequest(
        case_id=str(fixture["case_id"]),
        stimulus=str(fixture["stimulus"]),
    )


def load_assessment_request(fixture_path: str | Path) -> AssessmentRequest:
    """Load deterministic eligibility inputs from a controlled fixture."""

    fixture = _load_json(Path(fixture_path))
    raw_request = fixture["assessment_request"]

    requested_targets = tuple(
        AssessmentTarget(target) for target in raw_request["requested_targets"]
    )
    required_evidence = {
        AssessmentTarget(target): frozenset(str(item) for item in evidence)
        for target, evidence in raw_request["required_evidence"].items()
    }
    allowed_verdicts = {
        AssessmentTarget(target): frozenset(Verdict(item) for item in verdicts)
        for target, verdicts in raw_request["allowed_verdicts"].items()
    }

    return AssessmentRequest(
        case_id=str(fixture["case_id"]),
        requested_targets=requested_targets,
        required_evidence=required_evidence,
        applicable_rules=frozenset(
            str(rule) for rule in raw_request["applicable_rules"]
        ),
        allowed_verdicts=allowed_verdicts,
        prohibited_claims=frozenset(
            str(claim) for claim in raw_request["prohibited_claims"]
        ),
    )


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as fixture_file:
        data = json.load(fixture_file)

    if not isinstance(data, dict):
        raise TypeError("Replay fixture root must be a JSON object.")

    return data


def _technical_error_response(
    *,
    request: ExamineeRequest,
    fixture_path: Path,
    error_type: str,
    message: str,
) -> CandidateResponse:
    return CandidateResponse(
        response_id=f"{request.case_id}:technical-error",
        case_id=request.case_id,
        text="",
        evidence=frozenset(),
        metadata={"adapter_type": "replay", "fixture_path": str(fixture_path)},
        provenance=ResponseProvenance(
            source_type=SourceType.SYNTHETIC,
            creation_method="replay_adapter_error",
            live_model_response=False,
            validation_purpose="framework_pipeline",
        ),
        technical_status=TechnicalStatus.error(error_type, message),
    )
