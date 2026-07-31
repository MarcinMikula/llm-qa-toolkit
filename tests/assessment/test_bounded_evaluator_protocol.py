"""SDLC and STLC tests for the bounded evaluator protocol."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from assessment.adapters import (
    ReplayEvaluatorAdapter,
    ReplayExamineeAdapter,
    StubEvaluatorAdapter,
    load_assessment_request,
    load_examinee_request,
)
from assessment.contracts import AssessmentContractBuilder
from assessment.evaluator_protocol import (
    BoundedEvaluatorRequestBuilder,
    EVALUATOR_RESULT_SCHEMA_VERSION,
    StructuredEvaluatorResultParser,
)
from assessment.models import (
    BoundedEvaluatorRequest,
    EvaluationStatus,
    ExamineeRequest,
    ProposedEvaluatorResult,
    RejectionReason,
    TechnicalState,
    TechnicalStatus,
)
from assessment.pipeline import AssessmentPipeline
from assessment.validator import EvaluationResultValidator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "testdata" / "assessment" / "ins_mixed_001.json"
EVALUATOR_OUTPUT_PATH = (
    PROJECT_ROOT
    / "testdata"
    / "assessment"
    / "evaluator_outputs"
    / "ins_mixed_001.json"
)
RULE_FILES = (
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "global_rules.json",
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "insurance_rules.json",
)


def _contract_builder() -> AssessmentContractBuilder:
    return AssessmentContractBuilder.from_rule_files(*RULE_FILES)


def _protocol_inputs():
    examinee_request = load_examinee_request(FIXTURE_PATH)
    candidate = ReplayExamineeAdapter(FIXTURE_PATH).respond(examinee_request)
    contract = _contract_builder().build(
        candidate,
        load_assessment_request(FIXTURE_PATH),
    )
    return examinee_request, candidate, contract


def _bounded_request() -> BoundedEvaluatorRequest:
    examinee_request, candidate, contract = _protocol_inputs()
    return BoundedEvaluatorRequestBuilder().build(
        examinee_request,
        candidate,
        contract,
    )


def _valid_raw_output() -> str:
    return EVALUATOR_OUTPUT_PATH.read_text(encoding="utf-8")


def test_request_serializes_only_allowed_scope_and_rules() -> None:
    request = _bounded_request()
    payload = json.loads(request.payload_json)

    allowed_targets = {
        item["target"] for item in payload["assessment_scope"]["allowed_targets"]
    }
    excluded_targets = {
        item["target"] for item in payload["assessment_scope"]["excluded_targets"]
    }

    assert allowed_targets == {
        "intent_separation",
        "insurance_response_strategy",
        "domain_boundary_compliance",
        "live_data_handling",
        "unsupported_certainty",
    }
    assert excluded_targets == {
        "actual_insurance_liability",
        "actual_warsaw_weather",
        "nutritional_or_medical_correctness",
    }
    assert {
        rule["rule_id"] for rule in payload["applicable_rules"]
    } == {
        "GLOBAL-MULTI-INTENT-01",
        "GLOBAL-OUT-OF-DOMAIN-01",
        "GLOBAL-LIVE-DATA-01",
        "GLOBAL-EVIDENCE-01",
        "INS-CLAIM-01",
    }
    assert all(
        set(rule["applies_to_allowed_targets"]) <= allowed_targets
        for rule in payload["applicable_rules"]
    )


def test_request_states_missing_evidence_for_excluded_targets() -> None:
    payload = json.loads(_bounded_request().payload_json)
    excluded = {
        item["target"]: item
        for item in payload["assessment_scope"]["excluded_targets"]
    }

    assert excluded["actual_warsaw_weather"]["reason"] == (
        "MISSING_REQUIRED_EVIDENCE"
    )
    assert excluded["actual_warsaw_weather"]["missing_evidence"] == [
        "current_authoritative_forecast"
    ]
    assert "policy_wording" in excluded["actual_insurance_liability"][
        "missing_evidence"
    ]


def test_request_does_not_expose_adapter_metadata_or_provenance() -> None:
    request = _bounded_request()

    assert "adapter_type" not in request.payload_json
    assert "creation_method" not in request.payload_json
    assert "live_model_response" not in request.payload_json
    assert "approved_weather_tool" not in request.payload_json
    assert "Nie mam zatwierdzonego dostępu" in request.payload_json


def test_request_serialization_is_deterministic() -> None:
    first = _bounded_request()
    second = _bounded_request()

    assert first == second
    assert first.payload_json == second.payload_json
    assert first.rendered_prompt == second.rendered_prompt


def test_request_contains_explicit_result_schema_and_verdict_constraints() -> None:
    request = _bounded_request()
    payload = json.loads(request.payload_json)
    scope = {
        item["target"]: item
        for item in payload["assessment_scope"]["allowed_targets"]
    }

    assert payload["required_result_schema"]["additional_properties"] is False
    assert payload["required_result_schema"]["properties"][
        "schema_version"
    ] == EVALUATOR_RESULT_SCHEMA_VERSION
    assert payload["required_result_schema"]["properties"][
        "overall_score"
    ] == "must_be_null"
    assert scope["intent_separation"]["allowed_verdicts"] == [
        "FAIL",
        "PASS",
        "REVIEW_REQUIRED",
    ]
    assert "actual_warsaw_weather" not in scope


def test_parser_accepts_valid_strict_json_and_preserves_raw_output() -> None:
    request = _bounded_request()
    raw_output = _valid_raw_output()

    result = StructuredEvaluatorResultParser().parse(raw_output, request)

    assert result.technical_status.state is TechnicalState.COMPLETED
    assert result.case_id == request.case_id
    assert len(result.findings) == 6
    assert result.overall_score == 95.0
    assert result.raw_output == raw_output


def test_parser_rejects_non_json_output_as_process_error() -> None:
    request = _bounded_request()
    raw_output = "The answer is probably acceptable."

    result = StructuredEvaluatorResultParser().parse(raw_output, request)

    assert result.technical_status.state is TechnicalState.ERROR
    assert result.technical_status.error_type == "EVALUATOR_RESULT_INVALID_JSON"
    assert result.findings == ()
    assert result.raw_output == raw_output


def test_parser_rejects_markdown_fenced_json() -> None:
    request = _bounded_request()
    raw_output = f"```json\n{_valid_raw_output()}\n```"

    result = StructuredEvaluatorResultParser().parse(raw_output, request)

    assert result.technical_status.error_type == "EVALUATOR_RESULT_INVALID_JSON"
    assert result.findings == ()


def test_parser_rejects_unexpected_top_level_fields() -> None:
    request = _bounded_request()
    payload = json.loads(_valid_raw_output())
    payload["free_form_recommendation"] = "Trust me."

    result = StructuredEvaluatorResultParser().parse(
        json.dumps(payload),
        request,
    )

    assert result.technical_status.error_type == "EVALUATOR_RESULT_SCHEMA_ERROR"
    assert "unexpected fields" in (result.technical_status.message or "")


def test_parser_rejects_duplicate_json_object_keys() -> None:
    request = _bounded_request()
    raw_output = (
        '{"schema_version":"0.1","schema_version":"0.1",'
        '"case_id":"INS-MIXED-001","findings":[],"overall_score":null}'
    )

    result = StructuredEvaluatorResultParser().parse(raw_output, request)

    assert result.technical_status.error_type == "EVALUATOR_RESULT_SCHEMA_ERROR"
    assert "Duplicate JSON object key" in (result.technical_status.message or "")


def test_parser_rejects_schema_version_mismatch() -> None:
    request = _bounded_request()
    payload = json.loads(_valid_raw_output())
    payload["schema_version"] = "99.0"

    result = StructuredEvaluatorResultParser().parse(
        json.dumps(payload),
        request,
    )

    assert (
        result.technical_status.error_type
        == "EVALUATOR_RESULT_SCHEMA_VERSION_MISMATCH"
    )


def test_parser_rejects_unknown_target_as_schema_error() -> None:
    request = _bounded_request()
    payload = json.loads(_valid_raw_output())
    payload["findings"][0]["target"] = "unknown_target"

    result = StructuredEvaluatorResultParser().parse(
        json.dumps(payload),
        request,
    )

    assert result.technical_status.error_type == "EVALUATOR_RESULT_SCHEMA_ERROR"
    assert result.findings == ()


def test_parser_rejects_unknown_verdict_as_schema_error() -> None:
    request = _bounded_request()
    payload = json.loads(_valid_raw_output())
    payload["findings"][0]["verdict"] = "MAYBE"

    result = StructuredEvaluatorResultParser().parse(
        json.dumps(payload),
        request,
    )

    assert result.technical_status.error_type == "EVALUATOR_RESULT_SCHEMA_ERROR"
    assert result.findings == ()


def test_parser_rejects_duplicate_evidence_identifiers() -> None:
    request = _bounded_request()
    payload = json.loads(_valid_raw_output())
    payload["findings"][0]["evidence_used"].append("candidate_response")

    result = StructuredEvaluatorResultParser().parse(
        json.dumps(payload),
        request,
    )

    assert result.technical_status.error_type == "EVALUATOR_RESULT_SCHEMA_ERROR"
    assert "must not contain duplicates" in (
        result.technical_status.message or ""
    )


def test_parser_rejects_boolean_overall_score() -> None:
    request = _bounded_request()
    payload = json.loads(_valid_raw_output())
    payload["overall_score"] = True

    result = StructuredEvaluatorResultParser().parse(
        json.dumps(payload),
        request,
    )

    assert result.technical_status.error_type == "EVALUATOR_RESULT_SCHEMA_ERROR"
    assert result.findings == ()


def test_parser_rejects_duplicate_finding_ids() -> None:
    request = _bounded_request()
    payload = json.loads(_valid_raw_output())
    payload["findings"][1]["finding_id"] = payload["findings"][0]["finding_id"]

    result = StructuredEvaluatorResultParser().parse(
        json.dumps(payload),
        request,
    )

    assert result.technical_status.error_type == "EVALUATOR_RESULT_SCHEMA_ERROR"
    assert "duplicate finding IDs" in (result.technical_status.message or "")


def test_case_id_mismatch_remains_result_validator_responsibility() -> None:
    examinee_request, candidate, contract = _protocol_inputs()
    request = BoundedEvaluatorRequestBuilder().build(
        examinee_request,
        candidate,
        contract,
    )
    payload = json.loads(_valid_raw_output())
    payload["case_id"] = "OTHER-CASE"

    proposed = StructuredEvaluatorResultParser().parse(
        json.dumps(payload),
        request,
    )
    scoped = EvaluationResultValidator().validate(contract, proposed)

    assert proposed.technical_status.state is TechnicalState.COMPLETED
    assert scoped.accepted_findings == ()
    assert {
        item.reason for item in scoped.rejected_findings
    } == {RejectionReason.CASE_ID_MISMATCH}
    assert scoped.has_substantive_failure is False


def test_missing_replay_output_is_evaluator_process_error(tmp_path: Path) -> None:
    evaluator = ReplayEvaluatorAdapter(tmp_path / "missing-output.json")
    pipeline = AssessmentPipeline(
        examinee=ReplayExamineeAdapter(FIXTURE_PATH),
        evaluator=evaluator,
        contract_builder=_contract_builder(),
    )

    run = pipeline.run(
        load_examinee_request(FIXTURE_PATH),
        load_assessment_request(FIXTURE_PATH),
    )

    assert evaluator.call_count == 1
    assert run.assessment_contract is not None
    assert run.evaluator_request is not None
    assert run.proposed_evaluator_result is not None
    assert (
        run.proposed_evaluator_result.technical_status.error_type
        == "EVALUATOR_OUTPUT_FILE_NOT_FOUND"
    )
    assert run.scoped_result.status is EvaluationStatus.ERROR
    assert run.scoped_result.has_substantive_failure is False


class _StaticExamineeAdapter:
    def __init__(self, candidate) -> None:
        self._candidate = candidate

    def respond(self, request: ExamineeRequest):
        return self._candidate


def test_empty_stimulus_stops_pipeline_before_evaluator_request() -> None:
    examinee_request, candidate, _ = _protocol_inputs()
    empty_stimulus_request = replace(examinee_request, stimulus="   ")
    evaluator = StubEvaluatorAdapter(
        ProposedEvaluatorResult(
            case_id=examinee_request.case_id,
            technical_status=TechnicalStatus.completed(),
            findings=(),
        )
    )
    pipeline = AssessmentPipeline(
        examinee=_StaticExamineeAdapter(candidate),
        evaluator=evaluator,
        contract_builder=_contract_builder(),
    )

    run = pipeline.run(
        empty_stimulus_request,
        load_assessment_request(FIXTURE_PATH),
    )

    assert run.assessment_contract is not None
    assert run.evaluator_request is None
    assert run.proposed_evaluator_result is None
    assert evaluator.call_count == 0
    assert run.scoped_result.status is EvaluationStatus.ERROR
    assert (
        run.scoped_result.technical_status.error_type
        == "EVALUATOR_REQUEST_STIMULUS_EMPTY"
    )
    assert run.scoped_result.has_substantive_failure is False
