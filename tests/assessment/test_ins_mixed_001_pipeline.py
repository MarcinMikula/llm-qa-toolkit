"""Executable proof of the assessment-grounded runtime slice."""

from __future__ import annotations

from pathlib import Path

from assessment.adapters import (
    ReplayExamineeAdapter,
    StubEvaluatorAdapter,
    load_assessment_request,
    load_examinee_request,
)
from assessment.eligibility import AssessmentEligibilityChecker
from assessment.models import (
    AssessmentTarget,
    EvaluationStatus,
    RejectionReason,
    RuleStatus,
    SourceType,
    TechnicalState,
)
from assessment.pipeline import AssessmentPipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "testdata" / "assessment" / "ins_mixed_001.json"
RULE_FILES = (
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "global_rules.json",
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "insurance_rules.json",
)


def _checker() -> AssessmentEligibilityChecker:
    return AssessmentEligibilityChecker.from_rule_files(*RULE_FILES)


def _build_pipeline(
    *,
    fixture_path: Path = FIXTURE_PATH,
) -> tuple[AssessmentPipeline, StubEvaluatorAdapter]:
    evaluator = StubEvaluatorAdapter.from_fixture(FIXTURE_PATH)
    pipeline = AssessmentPipeline(
        examinee=ReplayExamineeAdapter(fixture_path),
        evaluator=evaluator,
        eligibility_checker=_checker(),
    )
    return pipeline, evaluator


def test_replay_returns_normalised_synthetic_candidate_response() -> None:
    request = load_examinee_request(FIXTURE_PATH)

    response = ReplayExamineeAdapter(FIXTURE_PATH).respond(request)

    assert response.technical_status.state is TechnicalState.COMPLETED
    assert response.case_id == "INS-MIXED-001"
    assert response.response_id == "INS-MIXED-001-SYNTHETIC-001"
    assert response.provenance.source_type is SourceType.SYNTHETIC
    assert response.provenance.live_model_response is False
    assert response.provenance.validation_purpose == "framework_pipeline"
    assert "Nie mam zatwierdzonego dostępu" in response.text


def test_missing_evidence_excludes_factual_targets() -> None:
    examinee_request = load_examinee_request(FIXTURE_PATH)
    assessment_request = load_assessment_request(FIXTURE_PATH)
    candidate = ReplayExamineeAdapter(FIXTURE_PATH).respond(examinee_request)

    contract = _checker().build_contract(candidate, assessment_request)

    assert set(contract.excluded_targets) == {
        AssessmentTarget.ACTUAL_INSURANCE_LIABILITY,
        AssessmentTarget.ACTUAL_WARSAW_WEATHER,
        AssessmentTarget.NUTRITIONAL_OR_MEDICAL_CORRECTNESS,
    }
    assert contract.excluded_targets[
        AssessmentTarget.ACTUAL_WARSAW_WEATHER
    ].missing_evidence == frozenset({"current_authoritative_forecast"})
    assert "policy_wording" in contract.excluded_targets[
        AssessmentTarget.ACTUAL_INSURANCE_LIABILITY
    ].missing_evidence


def test_behavioural_targets_remain_allowed() -> None:
    examinee_request = load_examinee_request(FIXTURE_PATH)
    assessment_request = load_assessment_request(FIXTURE_PATH)
    candidate = ReplayExamineeAdapter(FIXTURE_PATH).respond(examinee_request)

    contract = _checker().build_contract(candidate, assessment_request)

    assert contract.allowed_targets == frozenset(
        {
            AssessmentTarget.INTENT_SEPARATION,
            AssessmentTarget.INSURANCE_RESPONSE_STRATEGY,
            AssessmentTarget.DOMAIN_BOUNDARY_COMPLIANCE,
            AssessmentTarget.LIVE_DATA_HANDLING,
            AssessmentTarget.UNSUPPORTED_CERTAINTY,
        }
    )
    assert contract.is_partial is True


def test_contract_contains_controlled_rule_definitions() -> None:
    examinee_request = load_examinee_request(FIXTURE_PATH)
    assessment_request = load_assessment_request(FIXTURE_PATH)
    candidate = ReplayExamineeAdapter(FIXTURE_PATH).respond(examinee_request)

    contract = _checker().build_contract(candidate, assessment_request)

    assert tuple(rule.rule_id for rule in contract.applicable_rules) == (
        "GLOBAL-MULTI-INTENT-01",
        "GLOBAL-OUT-OF-DOMAIN-01",
        "GLOBAL-LIVE-DATA-01",
        "GLOBAL-EVIDENCE-01",
        "INS-CLAIM-01",
    )
    assert all(rule.status is RuleStatus.DRAFT for rule in contract.applicable_rules)
    assert all(rule.version == "0.1.0" for rule in contract.applicable_rules)
    assert contract.rule_ids == frozenset(
        {
            "GLOBAL-MULTI-INTENT-01",
            "GLOBAL-OUT-OF-DOMAIN-01",
            "GLOBAL-LIVE-DATA-01",
            "GLOBAL-EVIDENCE-01",
            "INS-CLAIM-01",
        }
    )


def test_end_to_end_accepts_scoped_findings_and_rejects_overreach() -> None:
    pipeline, evaluator = _build_pipeline()

    run = pipeline.run(
        load_examinee_request(FIXTURE_PATH),
        load_assessment_request(FIXTURE_PATH),
    )

    assert evaluator.call_count == 1
    assert evaluator.last_contract == run.assessment_contract
    assert run.scoped_result.status is EvaluationStatus.COMPLETED_WITH_REJECTIONS
    assert {finding.finding_id for finding in run.scoped_result.accepted_findings} == {
        "F-001",
        "F-002",
        "F-003",
        "F-004",
        "F-005",
    }
    assert len(run.scoped_result.rejected_findings) == 1
    assert (
        run.scoped_result.rejected_findings[0].finding.finding_id
        == "F-OVERREACH-001"
    )
    assert (
        run.scoped_result.rejected_findings[0].reason
        is RejectionReason.TARGET_NOT_ALLOWED
    )


def test_partial_scope_rejects_overall_score() -> None:
    pipeline, _ = _build_pipeline()

    run = pipeline.run(
        load_examinee_request(FIXTURE_PATH),
        load_assessment_request(FIXTURE_PATH),
    )

    assert len(run.scoped_result.rejected_artifacts) == 1
    rejected_score = run.scoped_result.rejected_artifacts[0]
    assert rejected_score.artifact_type == "overall_score"
    assert rejected_score.reason is RejectionReason.OVERALL_SCORE_NOT_ALLOWED


def test_rejected_out_of_scope_fail_does_not_fail_examinee() -> None:
    pipeline, _ = _build_pipeline()

    run = pipeline.run(
        load_examinee_request(FIXTURE_PATH),
        load_assessment_request(FIXTURE_PATH),
    )

    assert any(
        rejected.finding.verdict.value == "FAIL"
        for rejected in run.scoped_result.rejected_findings
    )
    assert run.scoped_result.has_substantive_failure is False


def test_adapter_error_is_not_a_substantive_failure(tmp_path: Path) -> None:
    missing_fixture = tmp_path / "missing.json"
    pipeline, evaluator = _build_pipeline(fixture_path=missing_fixture)

    run = pipeline.run(
        load_examinee_request(FIXTURE_PATH),
        load_assessment_request(FIXTURE_PATH),
    )

    assert run.candidate_response.technical_status.state is TechnicalState.ERROR
    assert run.candidate_response.technical_status.error_type == "REPLAY_FILE_NOT_FOUND"
    assert run.assessment_contract is None
    assert run.proposed_evaluator_result is None
    assert evaluator.call_count == 0
    assert run.scoped_result.status is EvaluationStatus.ERROR
    assert run.scoped_result.has_substantive_failure is False
