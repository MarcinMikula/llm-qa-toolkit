"""SDLC and STLC tests for public AssessmentContract construction."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from assessment.adapters import (
    ReplayExamineeAdapter,
    StubEvaluatorAdapter,
    load_assessment_request,
    load_examinee_request,
)
from assessment.contracts import AssessmentContractBuilder
from assessment.models import (
    AssessmentRequest,
    AssessmentTarget,
    EvaluationStatus,
    RuleStatus,
    TechnicalState,
    Verdict,
)
from assessment.pipeline import AssessmentPipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "testdata" / "assessment" / "ins_mixed_001.json"
GLOBAL_RULES = (
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "global_rules.json"
)
INSURANCE_RULES = (
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "insurance_rules.json"
)
RULE_FILES = (GLOBAL_RULES, INSURANCE_RULES)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def _builder() -> AssessmentContractBuilder:
    return AssessmentContractBuilder.from_rule_files(*RULE_FILES)


def _candidate():
    examinee_request = load_examinee_request(FIXTURE_PATH)
    return ReplayExamineeAdapter(FIXTURE_PATH).respond(examinee_request)


def _run(assessment_fixture: Path):
    evaluator = StubEvaluatorAdapter.from_fixture(FIXTURE_PATH)
    pipeline = AssessmentPipeline(
        examinee=ReplayExamineeAdapter(FIXTURE_PATH),
        evaluator=evaluator,
        contract_builder=_builder(),
    )
    run = pipeline.run(
        load_examinee_request(FIXTURE_PATH),
        load_assessment_request(assessment_fixture),
    )
    return run, evaluator


def _assert_definition_error(run, evaluator, error_type: str) -> None:
    assert evaluator.call_count == 0
    assert run.assessment_contract is None
    assert run.evaluator_request is None
    assert run.proposed_evaluator_result is None
    assert run.scoped_result.status is EvaluationStatus.ERROR
    assert run.scoped_result.technical_status.state is TechnicalState.ERROR
    assert run.scoped_result.technical_status.error_type == error_type
    assert run.scoped_result.accepted_findings == ()
    assert run.scoped_result.has_substantive_failure is False


def test_builder_is_the_public_contract_construction_path() -> None:
    request = load_assessment_request(FIXTURE_PATH)

    contract = _builder().build(_candidate(), request)

    assert contract.case_id == request.case_id
    assert contract.candidate_response_id == "INS-MIXED-001-SYNTHETIC-001"
    assert len(contract.allowed_targets) == 5
    assert len(contract.excluded_targets) == 3
    assert len(contract.applicable_rules) == 5


def test_empty_requested_targets_stop_pipeline_before_evaluator(
    tmp_path: Path,
) -> None:
    fixture = _load_json(FIXTURE_PATH)
    fixture["assessment_request"]["requested_targets"] = []
    fixture["assessment_request"]["required_evidence"] = {}
    fixture["assessment_request"]["allowed_verdicts"] = {}
    modified = _write_json(tmp_path / "empty_targets.json", fixture)

    run, evaluator = _run(modified)

    _assert_definition_error(run, evaluator, "ASSESSMENT_TARGETS_EMPTY")


def test_duplicate_requested_target_stops_pipeline_before_evaluator(
    tmp_path: Path,
) -> None:
    fixture = _load_json(FIXTURE_PATH)
    fixture["assessment_request"]["requested_targets"].append(
        "intent_separation"
    )
    modified = _write_json(tmp_path / "duplicate_target.json", fixture)

    run, evaluator = _run(modified)

    _assert_definition_error(run, evaluator, "DUPLICATE_ASSESSMENT_TARGET")


def test_missing_target_evidence_definition_stops_pipeline(
    tmp_path: Path,
) -> None:
    fixture = _load_json(FIXTURE_PATH)
    del fixture["assessment_request"]["required_evidence"]["intent_separation"]
    modified = _write_json(tmp_path / "missing_evidence_target.json", fixture)

    run, evaluator = _run(modified)

    _assert_definition_error(
        run,
        evaluator,
        "REQUIRED_EVIDENCE_TARGET_MISSING",
    )


def test_unrequested_verdict_target_stops_pipeline(tmp_path: Path) -> None:
    fixture = _load_json(FIXTURE_PATH)
    fixture["assessment_request"]["requested_targets"].remove(
        "actual_warsaw_weather"
    )
    del fixture["assessment_request"]["required_evidence"][
        "actual_warsaw_weather"
    ]
    modified = _write_json(tmp_path / "unexpected_verdict_target.json", fixture)

    run, evaluator = _run(modified)

    _assert_definition_error(
        run,
        evaluator,
        "ALLOWED_VERDICTS_TARGET_UNEXPECTED",
    )


def test_empty_allowed_verdicts_stop_pipeline(tmp_path: Path) -> None:
    fixture = _load_json(FIXTURE_PATH)
    fixture["assessment_request"]["allowed_verdicts"][
        "intent_separation"
    ] = []
    modified = _write_json(tmp_path / "empty_verdicts.json", fixture)

    run, evaluator = _run(modified)

    _assert_definition_error(run, evaluator, "ALLOWED_VERDICTS_EMPTY")


def test_duplicate_requested_rule_id_stops_pipeline(tmp_path: Path) -> None:
    fixture = _load_json(FIXTURE_PATH)
    fixture["assessment_request"]["requested_rule_ids"].append(
        "GLOBAL-MULTI-INTENT-01"
    )
    modified = _write_json(tmp_path / "duplicate_requested_rule.json", fixture)

    run, evaluator = _run(modified)

    _assert_definition_error(run, evaluator, "DUPLICATE_REQUESTED_RULE_ID")


def test_empty_requested_rule_id_stops_pipeline(tmp_path: Path) -> None:
    fixture = _load_json(FIXTURE_PATH)
    fixture["assessment_request"]["requested_rule_ids"].append("  ")
    modified = _write_json(tmp_path / "empty_requested_rule.json", fixture)

    run, evaluator = _run(modified)

    _assert_definition_error(run, evaluator, "EMPTY_REQUESTED_RULE_ID")


def test_rule_unrelated_to_requested_targets_stops_pipeline(
    tmp_path: Path,
) -> None:
    fixture = _load_json(FIXTURE_PATH)
    fixture["assessment_request"]["requested_targets"] = [
        "intent_separation"
    ]
    fixture["assessment_request"]["required_evidence"] = {
        "intent_separation": ["candidate_response", "stimulus_intents"]
    }
    fixture["assessment_request"]["allowed_verdicts"] = {
        "intent_separation": ["PASS", "FAIL", "REVIEW_REQUIRED"]
    }
    fixture["assessment_request"]["requested_rule_ids"] = [
        "GLOBAL-LIVE-DATA-01"
    ]
    modified = _write_json(tmp_path / "inapplicable_rule.json", fixture)

    run, evaluator = _run(modified)

    _assert_definition_error(
        run,
        evaluator,
        "RULE_NOT_APPLICABLE_TO_REQUESTED_TARGETS",
    )


def test_deprecated_status_cannot_be_authorised_by_configuration(
    tmp_path: Path,
) -> None:
    fixture = _load_json(FIXTURE_PATH)
    fixture["assessment_request"]["allowed_rule_statuses"] = [
        "DRAFT",
        "DEPRECATED",
    ]
    modified = _write_json(tmp_path / "deprecated_status.json", fixture)

    run, evaluator = _run(modified)

    _assert_definition_error(
        run,
        evaluator,
        "DEPRECATED_RULE_STATUS_NOT_ALLOWED",
    )


def test_contract_uses_defensive_read_only_mapping_copies() -> None:
    source_request = load_assessment_request(FIXTURE_PATH)
    required_evidence = dict(source_request.required_evidence)
    allowed_verdicts = dict(source_request.allowed_verdicts)
    request = AssessmentRequest(
        case_id=source_request.case_id,
        requested_targets=source_request.requested_targets,
        required_evidence=required_evidence,
        requested_rule_ids=source_request.requested_rule_ids,
        allowed_rule_statuses=frozenset({RuleStatus.DRAFT}),
        allowed_verdicts=allowed_verdicts,
        prohibited_claims=source_request.prohibited_claims,
    )

    contract = _builder().build(_candidate(), request)
    original_contract_evidence = contract.effective_required_evidence[
        AssessmentTarget.INTENT_SEPARATION
    ]
    required_evidence[AssessmentTarget.INTENT_SEPARATION] = frozenset(
        {"mutated_after_build"}
    )
    allowed_verdicts[AssessmentTarget.INTENT_SEPARATION] = frozenset(
        {Verdict.FAIL}
    )

    assert (
        contract.effective_required_evidence[AssessmentTarget.INTENT_SEPARATION]
        == original_contract_evidence
    )
    assert Verdict.PASS in contract.allowed_verdicts[
        AssessmentTarget.INTENT_SEPARATION
    ]

    with pytest.raises(TypeError):
        contract.allowed_verdicts[AssessmentTarget.INTENT_SEPARATION] = frozenset(
            {Verdict.FAIL}
        )

    with pytest.raises(TypeError):
        contract.excluded_targets[AssessmentTarget.INTENT_SEPARATION] = object()


def test_case_id_mismatch_is_process_error_before_evaluator(tmp_path: Path) -> None:
    fixture = _load_json(FIXTURE_PATH)
    fixture["case_id"] = "OTHER-CASE"
    modified = _write_json(tmp_path / "other_case.json", fixture)

    evaluator = StubEvaluatorAdapter.from_fixture(FIXTURE_PATH)
    pipeline = AssessmentPipeline(
        examinee=ReplayExamineeAdapter(FIXTURE_PATH),
        evaluator=evaluator,
        contract_builder=_builder(),
    )
    run = pipeline.run(
        load_examinee_request(FIXTURE_PATH),
        load_assessment_request(modified),
    )

    _assert_definition_error(
        run,
        evaluator,
        "ASSESSMENT_CASE_ID_MISMATCH",
    )
