"""Boundary tests for evaluator output accepted by the assessment protocol."""

from __future__ import annotations

import json
from pathlib import Path

from assessment.adapters import (
    ReplayExamineeAdapter,
    StubEvaluatorAdapter,
    load_assessment_request,
    load_examinee_request,
)
from assessment.eligibility import AssessmentEligibilityChecker
from assessment.models import (
    AssessmentContract,
    AssessmentTarget,
    EvaluationStatus,
    ProposedEvaluatorResult,
    ProposedFinding,
    RejectionReason,
    TechnicalState,
    TechnicalStatus,
    Verdict,
)
from assessment.pipeline import AssessmentPipeline
from assessment.validator import EvaluationResultValidator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "testdata" / "assessment" / "ins_mixed_001.json"
RULE_FILES = (
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "global_rules.json",
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "insurance_rules.json",
)


def _checker() -> AssessmentEligibilityChecker:
    return AssessmentEligibilityChecker.from_rule_files(*RULE_FILES)


def _build_contract(fixture_path: Path = FIXTURE_PATH) -> AssessmentContract:
    examinee_request = load_examinee_request(FIXTURE_PATH)
    assessment_request = load_assessment_request(fixture_path)
    candidate = ReplayExamineeAdapter(FIXTURE_PATH).respond(examinee_request)
    return _checker().build_contract(candidate, assessment_request)


def _finding(
    *,
    finding_id: str,
    target: AssessmentTarget = AssessmentTarget.INTENT_SEPARATION,
    verdict: Verdict = Verdict.PASS,
    rule_id: str = "GLOBAL-MULTI-INTENT-01",
    evidence_used: frozenset[str] = frozenset(
        {"candidate_response", "stimulus_intents"}
    ),
    claims: frozenset[str] = frozenset(),
) -> ProposedFinding:
    return ProposedFinding(
        finding_id=finding_id,
        target=target,
        verdict=verdict,
        rule_id=rule_id,
        evidence_used=evidence_used,
        rationale="Controlled boundary test finding.",
        claims=claims,
    )


def _validate(
    finding: ProposedFinding,
    *,
    contract: AssessmentContract | None = None,
    case_id: str = "INS-MIXED-001",
) -> tuple[AssessmentContract, object]:
    active_contract = contract or _build_contract()
    result = ProposedEvaluatorResult(
        case_id=case_id,
        technical_status=TechnicalStatus.completed(),
        findings=(finding,),
    )
    scoped = EvaluationResultValidator().validate(active_contract, result)
    return active_contract, scoped


def test_unknown_rule_reference_is_rejected() -> None:
    _, scoped = _validate(
        _finding(
            finding_id="F-UNKNOWN-RULE",
            rule_id="GLOBAL-NOT-APPLICABLE-999",
        )
    )

    assert scoped.accepted_findings == ()
    assert len(scoped.rejected_findings) == 1
    assert scoped.rejected_findings[0].reason is RejectionReason.UNKNOWN_RULE
    assert scoped.has_substantive_failure is False


def test_rule_not_applicable_to_finding_target_is_rejected() -> None:
    _, scoped = _validate(
        _finding(
            finding_id="F-WRONG-RULE-TARGET",
            rule_id="GLOBAL-LIVE-DATA-01",
        )
    )

    assert scoped.accepted_findings == ()
    assert (
        scoped.rejected_findings[0].reason
        is RejectionReason.RULE_NOT_APPLICABLE_TO_TARGET
    )
    assert scoped.has_substantive_failure is False


def test_unavailable_evidence_reference_is_rejected() -> None:
    _, scoped = _validate(
        _finding(
            finding_id="F-INVENTED-EVIDENCE",
            evidence_used=frozenset(
                {
                    "candidate_response",
                    "stimulus_intents",
                    "invented_policy_database",
                }
            ),
        )
    )

    assert scoped.accepted_findings == ()
    assert scoped.rejected_findings[0].reason is RejectionReason.EVIDENCE_NOT_AVAILABLE
    assert "invented_policy_database" in scoped.rejected_findings[0].details


def test_prohibited_claim_is_rejected() -> None:
    _, scoped = _validate(
        _finding(
            finding_id="F-PROHIBITED-CLAIM",
            target=AssessmentTarget.LIVE_DATA_HANDLING,
            rule_id="GLOBAL-LIVE-DATA-01",
            evidence_used=frozenset(
                {"candidate_response", "available_tools", "stimulus_intents"}
            ),
            claims=frozenset({"actual_weather_is_known"}),
        )
    )

    assert scoped.accepted_findings == ()
    assert scoped.rejected_findings[0].reason is RejectionReason.PROHIBITED_CLAIM
    assert "actual_weather_is_known" in scoped.rejected_findings[0].details


def test_verdict_outside_target_contract_is_rejected(tmp_path: Path) -> None:
    raw_fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    raw_fixture["assessment_request"]["allowed_verdicts"][
        "intent_separation"
    ] = ["PASS"]
    restricted_fixture = tmp_path / "restricted_verdicts.json"
    restricted_fixture.write_text(
        json.dumps(raw_fixture, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    contract = _build_contract(restricted_fixture)

    _, scoped = _validate(
        _finding(
            finding_id="F-FORBIDDEN-VERDICT",
            verdict=Verdict.FAIL,
        ),
        contract=contract,
    )

    assert scoped.accepted_findings == ()
    assert scoped.rejected_findings[0].reason is RejectionReason.VERDICT_NOT_ALLOWED
    assert scoped.has_substantive_failure is False


def test_case_id_mismatch_rejects_every_finding() -> None:
    contract = _build_contract()
    result = ProposedEvaluatorResult(
        case_id="OTHER-CASE",
        technical_status=TechnicalStatus.completed(),
        findings=(
            _finding(finding_id="F-OTHER-CASE-PASS"),
            _finding(
                finding_id="F-OTHER-CASE-FAIL",
                verdict=Verdict.FAIL,
            ),
        ),
    )

    scoped = EvaluationResultValidator().validate(contract, result)

    assert scoped.accepted_findings == ()
    assert len(scoped.rejected_findings) == 2
    assert {
        rejected.reason for rejected in scoped.rejected_findings
    } == {RejectionReason.CASE_ID_MISMATCH}
    assert len(scoped.rejected_artifacts) == 1
    assert scoped.rejected_artifacts[0].reason is RejectionReason.CASE_ID_MISMATCH
    assert scoped.has_substantive_failure is False


def test_malformed_stub_result_becomes_technical_error(tmp_path: Path) -> None:
    malformed_fixture = tmp_path / "malformed_evaluator.json"
    malformed_fixture.write_text(
        json.dumps(
            {
                "case_id": "INS-MIXED-001",
                "stub_evaluator_result": {
                    "technical_status": {"state": "COMPLETED"},
                    "findings": [
                        {
                            "finding_id": "F-MALFORMED",
                            "target": "target_that_does_not_exist",
                            "verdict": "PASS",
                            "rule_id": "GLOBAL-MULTI-INTENT-01",
                            "evidence_used": ["candidate_response"],
                            "rationale": "Invalid target should not escape parsing.",
                        }
                    ],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    evaluator = StubEvaluatorAdapter.from_fixture(
        malformed_fixture,
        expected_case_id="INS-MIXED-001",
    )
    pipeline = AssessmentPipeline(
        examinee=ReplayExamineeAdapter(FIXTURE_PATH),
        evaluator=evaluator,
        eligibility_checker=_checker(),
    )

    run = pipeline.run(
        load_examinee_request(FIXTURE_PATH),
        load_assessment_request(FIXTURE_PATH),
    )

    assert evaluator.call_count == 1
    assert run.proposed_evaluator_result is not None
    assert (
        run.proposed_evaluator_result.technical_status.state
        is TechnicalState.ERROR
    )
    assert (
        run.proposed_evaluator_result.technical_status.error_type
        == "EVALUATOR_RESULT_PARSE_ERROR"
    )
    assert run.scoped_result.status is EvaluationStatus.ERROR
    assert run.scoped_result.accepted_findings == ()
    assert run.scoped_result.has_substantive_failure is False
