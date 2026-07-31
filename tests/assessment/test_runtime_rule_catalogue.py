"""SDLC and STLC tests for the controlled runtime rule catalogue."""

from __future__ import annotations

import json
from pathlib import Path

from assessment.adapters import (
    ReplayExamineeAdapter,
    StubEvaluatorAdapter,
    load_assessment_request,
    load_examinee_request,
)
from assessment.contracts import AssessmentContractBuilder
from assessment.models import (
    AssessmentTarget,
    EvaluationStatus,
    RuleStatus,
    TechnicalState,
)
from assessment.pipeline import AssessmentPipeline
from assessment.rules import RuleCatalog


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "testdata" / "assessment" / "ins_mixed_001.json"
GLOBAL_RULES = (
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "global_rules.json"
)
INSURANCE_RULES = (
    PROJECT_ROOT / "testdata" / "assessment" / "rules" / "insurance_rules.json"
)
RULE_FILES = (GLOBAL_RULES, INSURANCE_RULES)


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _pipeline(*rule_files: Path) -> tuple[AssessmentPipeline, StubEvaluatorAdapter]:
    evaluator = StubEvaluatorAdapter.from_fixture(FIXTURE_PATH)
    return (
        AssessmentPipeline(
            examinee=ReplayExamineeAdapter(FIXTURE_PATH),
            evaluator=evaluator,
            contract_builder=AssessmentContractBuilder.from_rule_files(
                *rule_files
            ),
        ),
        evaluator,
    )


def _run(
    *,
    rule_files: tuple[Path, ...] = RULE_FILES,
    assessment_fixture: Path = FIXTURE_PATH,
):
    pipeline, evaluator = _pipeline(*rule_files)
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


def test_catalog_loads_five_versioned_draft_rules() -> None:
    catalog = RuleCatalog.from_files(*RULE_FILES)

    assert len(catalog.rules) == 5
    assert catalog.rule_ids == frozenset(
        {
            "GLOBAL-MULTI-INTENT-01",
            "GLOBAL-OUT-OF-DOMAIN-01",
            "GLOBAL-LIVE-DATA-01",
            "GLOBAL-EVIDENCE-01",
            "INS-CLAIM-01",
        }
    )
    assert all(rule.version == "0.1.0" for rule in catalog.rules)
    assert all(rule.status is RuleStatus.DRAFT for rule in catalog.rules)
    assert all(rule.source.source_type == "project_evaluation_policy" for rule in catalog.rules)
    assert all(rule.source.reference for rule in catalog.rules)


def test_rule_required_evidence_participates_in_eligibility(tmp_path: Path) -> None:
    modified_global = _load_json(GLOBAL_RULES)
    multi_intent_rule = modified_global["rules"][0]
    multi_intent_rule["required_evidence"].append("rule_only_signal")
    modified_global_path = _write_json(tmp_path / "global_rules.json", modified_global)

    builder = AssessmentContractBuilder.from_rule_files(
        modified_global_path,
        INSURANCE_RULES,
    )
    examinee_request = load_examinee_request(FIXTURE_PATH)
    candidate = ReplayExamineeAdapter(FIXTURE_PATH).respond(examinee_request)
    contract = builder.build(
        candidate,
        load_assessment_request(FIXTURE_PATH),
    )

    excluded = contract.excluded_targets[AssessmentTarget.INTENT_SEPARATION]
    assert excluded.missing_evidence == frozenset({"rule_only_signal"})
    assert "rule_only_signal" in contract.effective_required_evidence[
        AssessmentTarget.INTENT_SEPARATION
    ]
    assert "GLOBAL-MULTI-INTENT-01" not in contract.rule_ids


def test_rule_for_only_excluded_target_is_not_exposed_to_evaluator(
    tmp_path: Path,
) -> None:
    modified_global = _load_json(GLOBAL_RULES)
    modified_global["rules"].append(
        {
            "id": "GLOBAL-WEATHER-FACT-01",
            "version": "0.1.0",
            "status": "DRAFT",
            "title": "Assess current weather only with authoritative forecast",
            "evaluator_instruction": (
                "Assess the actual forecast only when current authoritative "
                "forecast evidence is available."
            ),
            "applies_to_targets": ["actual_warsaw_weather"],
            "required_evidence": [
                "candidate_response",
                "current_authoritative_forecast"
            ],
            "forbidden_behaviours": ["INVENT_CURRENT_WEATHER"],
            "permitted_conclusions": [
                "The actual forecast is supported by authoritative evidence."
            ],
            "source": {
                "type": "project_evaluation_policy",
                "reference": "controlled-test-rule"
            }
        }
    )
    modified_global_path = _write_json(tmp_path / "global_rules.json", modified_global)

    modified_fixture = _load_json(FIXTURE_PATH)
    modified_fixture["assessment_request"]["requested_rule_ids"].append(
        "GLOBAL-WEATHER-FACT-01"
    )
    modified_fixture_path = _write_json(tmp_path / "case.json", modified_fixture)

    builder = AssessmentContractBuilder.from_rule_files(
        modified_global_path,
        INSURANCE_RULES,
    )
    examinee_request = load_examinee_request(FIXTURE_PATH)
    candidate = ReplayExamineeAdapter(FIXTURE_PATH).respond(examinee_request)
    contract = builder.build(
        candidate,
        load_assessment_request(modified_fixture_path),
    )

    assert AssessmentTarget.ACTUAL_WARSAW_WEATHER in contract.excluded_targets
    assert "GLOBAL-WEATHER-FACT-01" not in contract.rule_ids


def test_duplicate_rule_id_becomes_process_error_before_evaluator(
    tmp_path: Path,
) -> None:
    duplicate_rule = _load_json(INSURANCE_RULES)["rules"][0]
    duplicate_path = _write_json(
        tmp_path / "duplicate.json",
        {"catalog_id": "duplicate", "rules": [duplicate_rule]},
    )

    run, evaluator = _run(rule_files=(*RULE_FILES, duplicate_path))

    _assert_definition_error(run, evaluator, "DUPLICATE_RULE_ID")


def test_unknown_requested_rule_becomes_process_error_before_evaluator(
    tmp_path: Path,
) -> None:
    modified_fixture = _load_json(FIXTURE_PATH)
    modified_fixture["assessment_request"]["requested_rule_ids"].append(
        "GLOBAL-UNKNOWN-999"
    )
    modified_fixture_path = _write_json(tmp_path / "unknown_rule.json", modified_fixture)

    run, evaluator = _run(assessment_fixture=modified_fixture_path)

    _assert_definition_error(run, evaluator, "UNKNOWN_RULE")


def test_deprecated_rule_becomes_process_error_before_evaluator(
    tmp_path: Path,
) -> None:
    modified_global = _load_json(GLOBAL_RULES)
    modified_global["rules"][0]["status"] = "DEPRECATED"
    modified_global_path = _write_json(tmp_path / "global_rules.json", modified_global)

    run, evaluator = _run(
        rule_files=(modified_global_path, INSURANCE_RULES),
    )

    _assert_definition_error(run, evaluator, "RULE_STATUS_NOT_ALLOWED")


def test_malformed_rule_becomes_process_error_before_evaluator(
    tmp_path: Path,
) -> None:
    malformed = _load_json(GLOBAL_RULES)
    del malformed["rules"][0]["evaluator_instruction"]
    malformed_path = _write_json(tmp_path / "malformed_rules.json", malformed)

    run, evaluator = _run(
        rule_files=(malformed_path, INSURANCE_RULES),
    )

    _assert_definition_error(run, evaluator, "MALFORMED_RULE")


def test_rule_files_are_loaded_lazily_inside_pipeline(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing_rules.json"

    run, evaluator = _run(rule_files=(missing_path, INSURANCE_RULES))

    _assert_definition_error(run, evaluator, "RULE_CATALOG_FILE_NOT_FOUND")
