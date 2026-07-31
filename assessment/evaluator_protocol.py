"""Bounded evaluator request construction and structured result parsing.

The protocol remains provider-neutral. It renders one deterministic request for
an external semantic evaluator and parses one strict JSON result before the
existing deterministic result validator decides which findings may be accepted.
"""

from __future__ import annotations

import json
import math
from typing import Any, Mapping

from assessment.models import (
    AssessmentContract,
    AssessmentDefinitionError,
    AssessmentTarget,
    BoundedEvaluatorRequest,
    CandidateResponse,
    ExamineeRequest,
    ProposedEvaluatorResult,
    ProposedFinding,
    TechnicalStatus,
    Verdict,
)


EVALUATOR_PROTOCOL_VERSION = "0.1"
EVALUATOR_RESULT_SCHEMA_VERSION = "0.1"

_BOUNDED_EVALUATOR_INSTRUCTION = """You are a bounded external evaluator.
Evaluate only the allowed assessment targets using only the supplied stimulus,
candidate response, controlled rules, and evidence identifiers. Do not assess
excluded targets. Do not invent rules, evidence, verdicts, or factual authority.
Return one JSON object only, using exactly the required result schema. Any target
that cannot be assessed inside the supplied contract must be omitted rather than
judged outside scope."""


class BoundedEvaluatorRequestBuilder:
    """Render the deterministic contract as a provider-neutral evaluator request."""

    def build(
        self,
        examinee_request: ExamineeRequest,
        candidate_response: CandidateResponse,
        contract: AssessmentContract,
    ) -> BoundedEvaluatorRequest:
        """Create one deterministic request containing only contract-approved data."""

        self._validate_inputs(examinee_request, candidate_response, contract)

        payload = {
            "protocol_version": EVALUATOR_PROTOCOL_VERSION,
            "result_schema_version": EVALUATOR_RESULT_SCHEMA_VERSION,
            "case": {
                "case_id": contract.case_id,
                "stimulus": examinee_request.stimulus,
                "candidate_response": {
                    "response_id": candidate_response.response_id,
                    "text": candidate_response.text,
                },
            },
            "assessment_scope": {
                "allowed_targets": [
                    {
                        "target": target.value,
                        "allowed_verdicts": sorted(
                            verdict.value
                            for verdict in contract.allowed_verdicts[target]
                        ),
                        "required_evidence": sorted(
                            contract.effective_required_evidence[target]
                        ),
                    }
                    for target in sorted(
                        contract.allowed_targets,
                        key=lambda item: item.value,
                    )
                ],
                "excluded_targets": [
                    {
                        "target": excluded.target.value,
                        "reason": excluded.reason.value,
                        "missing_evidence": sorted(excluded.missing_evidence),
                    }
                    for excluded in sorted(
                        contract.excluded_targets.values(),
                        key=lambda item: item.target.value,
                    )
                ],
                "available_evidence": sorted(contract.available_evidence),
                "prohibited_claims": sorted(contract.prohibited_claims),
            },
            "applicable_rules": [
                {
                    "rule_id": rule.rule_id,
                    "version": rule.version,
                    "status": rule.status.value,
                    "title": rule.title,
                    "evaluator_instruction": rule.evaluator_instruction,
                    "applies_to_allowed_targets": sorted(
                        target.value
                        for target in rule.applies_to_targets
                        if target in contract.allowed_targets
                    ),
                    "required_evidence": sorted(rule.required_evidence),
                    "source": {
                        "source_type": rule.source.source_type,
                        "reference": rule.source.reference,
                    },
                    "forbidden_behaviours": list(rule.forbidden_behaviours),
                    "permitted_conclusions": list(rule.permitted_conclusions),
                }
                for rule in sorted(
                    contract.applicable_rules,
                    key=lambda item: item.rule_id,
                )
            ],
            "required_result_schema": {
                "type": "object",
                "additional_properties": False,
                "required": [
                    "schema_version",
                    "case_id",
                    "findings",
                    "overall_score",
                ],
                "properties": {
                    "schema_version": EVALUATOR_RESULT_SCHEMA_VERSION,
                    "case_id": contract.case_id,
                    "findings": {
                        "type": "array",
                        "item_required_fields": [
                            "finding_id",
                            "target",
                            "verdict",
                            "rule_id",
                            "evidence_used",
                            "rationale",
                            "claims",
                        ],
                    },
                    "overall_score": (
                        "must_be_null"
                        if contract.is_partial
                        else "number_or_null"
                    ),
                },
            },
        }

        payload_json = json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

        return BoundedEvaluatorRequest(
            protocol_version=EVALUATOR_PROTOCOL_VERSION,
            result_schema_version=EVALUATOR_RESULT_SCHEMA_VERSION,
            case_id=contract.case_id,
            candidate_response_id=contract.candidate_response_id,
            instruction=_BOUNDED_EVALUATOR_INSTRUCTION,
            payload_json=payload_json,
        )

    @staticmethod
    def _validate_inputs(
        examinee_request: ExamineeRequest,
        candidate_response: CandidateResponse,
        contract: AssessmentContract,
    ) -> None:
        if examinee_request.case_id != contract.case_id:
            raise AssessmentDefinitionError(
                "EVALUATOR_REQUEST_CASE_ID_MISMATCH",
                "Examinee request case_id does not match the assessment contract.",
            )

        if candidate_response.case_id != contract.case_id:
            raise AssessmentDefinitionError(
                "EVALUATOR_REQUEST_CANDIDATE_CASE_ID_MISMATCH",
                "Candidate response case_id does not match the assessment contract.",
            )

        if candidate_response.response_id != contract.candidate_response_id:
            raise AssessmentDefinitionError(
                "EVALUATOR_REQUEST_RESPONSE_ID_MISMATCH",
                "Candidate response ID does not match the assessment contract.",
            )

        if not examinee_request.stimulus.strip():
            raise AssessmentDefinitionError(
                "EVALUATOR_REQUEST_STIMULUS_EMPTY",
                "Evaluator request stimulus must be a non-empty string.",
            )


class StructuredEvaluatorResultParser:
    """Parse strict JSON output into a normalised but still untrusted result."""

    _TOP_LEVEL_FIELDS = {
        "schema_version",
        "case_id",
        "findings",
        "overall_score",
    }
    _FINDING_FIELDS = {
        "finding_id",
        "target",
        "verdict",
        "rule_id",
        "evidence_used",
        "rationale",
        "claims",
    }

    def parse(
        self,
        raw_output: str,
        request: BoundedEvaluatorRequest,
    ) -> ProposedEvaluatorResult:
        """Return a typed result or a technical parse-error result."""

        try:
            payload = json.loads(
                raw_output,
                object_pairs_hook=_reject_duplicate_object_keys,
            )
            if not isinstance(payload, dict):
                raise _SchemaError("Evaluator result root must be a JSON object.")

            self._require_exact_fields(
                payload,
                expected=self._TOP_LEVEL_FIELDS,
                location="evaluator result",
            )

            schema_version = self._required_non_empty_string(
                payload,
                "schema_version",
                location="evaluator result",
            )
            if schema_version != request.result_schema_version:
                raise _VersionError(
                    "Evaluator result schema_version "
                    f"{schema_version!r} does not match required version "
                    f"{request.result_schema_version!r}."
                )

            case_id = self._required_non_empty_string(
                payload,
                "case_id",
                location="evaluator result",
            )

            raw_findings = payload["findings"]
            if not isinstance(raw_findings, list):
                raise _SchemaError("Evaluator result findings must be a JSON array.")

            findings = tuple(
                self._parse_finding(item, index=index)
                for index, item in enumerate(raw_findings)
            )
            finding_ids = [finding.finding_id for finding in findings]
            if len(finding_ids) != len(set(finding_ids)):
                raise _SchemaError("Evaluator result contains duplicate finding IDs.")

            overall_score = self._parse_overall_score(payload["overall_score"])

            return ProposedEvaluatorResult(
                case_id=case_id,
                technical_status=TechnicalStatus.completed(),
                findings=findings,
                overall_score=overall_score,
                raw_output=raw_output,
            )
        except json.JSONDecodeError as exc:
            return self.technical_error_result(
                request=request,
                error_type="EVALUATOR_RESULT_INVALID_JSON",
                message=str(exc),
                raw_output=raw_output,
            )
        except _VersionError as exc:
            return self.technical_error_result(
                request=request,
                error_type="EVALUATOR_RESULT_SCHEMA_VERSION_MISMATCH",
                message=str(exc),
                raw_output=raw_output,
            )
        except (KeyError, TypeError, ValueError, _SchemaError) as exc:
            return self.technical_error_result(
                request=request,
                error_type="EVALUATOR_RESULT_SCHEMA_ERROR",
                message=str(exc),
                raw_output=raw_output,
            )

    @staticmethod
    def technical_error_result(
        *,
        request: BoundedEvaluatorRequest,
        error_type: str,
        message: str,
        raw_output: str | None,
    ) -> ProposedEvaluatorResult:
        """Create a process error without creating a substantive finding."""

        return ProposedEvaluatorResult(
            case_id=request.case_id,
            technical_status=TechnicalStatus.error(error_type, message),
            findings=(),
            overall_score=None,
            raw_output=raw_output,
        )

    def _parse_finding(self, raw_finding: object, *, index: int) -> ProposedFinding:
        location = f"findings[{index}]"
        if not isinstance(raw_finding, dict):
            raise _SchemaError(f"{location} must be a JSON object.")

        self._require_exact_fields(
            raw_finding,
            expected=self._FINDING_FIELDS,
            location=location,
        )

        finding_id = self._required_non_empty_string(
            raw_finding,
            "finding_id",
            location=location,
        )
        rule_id = self._required_non_empty_string(
            raw_finding,
            "rule_id",
            location=location,
        )
        rationale = self._required_non_empty_string(
            raw_finding,
            "rationale",
            location=location,
        )

        target = AssessmentTarget(
            self._required_non_empty_string(
                raw_finding,
                "target",
                location=location,
            )
        )
        verdict = Verdict(
            self._required_non_empty_string(
                raw_finding,
                "verdict",
                location=location,
            )
        )

        evidence_used = self._string_set(
            raw_finding["evidence_used"],
            location=f"{location}.evidence_used",
        )
        claims = self._string_set(
            raw_finding["claims"],
            location=f"{location}.claims",
        )

        return ProposedFinding(
            finding_id=finding_id,
            target=target,
            verdict=verdict,
            rule_id=rule_id,
            evidence_used=evidence_used,
            rationale=rationale,
            claims=claims,
        )

    @staticmethod
    def _parse_overall_score(value: object) -> float | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise _SchemaError("overall_score must be a finite number or null.")
        score = float(value)
        if not math.isfinite(score):
            raise _SchemaError("overall_score must be a finite number or null.")
        return score

    @staticmethod
    def _require_exact_fields(
        payload: Mapping[str, Any],
        *,
        expected: set[str],
        location: str,
    ) -> None:
        actual = set(payload)
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        if missing:
            raise _SchemaError(
                f"{location} is missing required fields: {', '.join(missing)}"
            )
        if unexpected:
            raise _SchemaError(
                f"{location} contains unexpected fields: {', '.join(unexpected)}"
            )

    @staticmethod
    def _required_non_empty_string(
        payload: Mapping[str, Any],
        field_name: str,
        *,
        location: str,
    ) -> str:
        value = payload[field_name]
        if not isinstance(value, str) or not value.strip():
            raise _SchemaError(
                f"{location}.{field_name} must be a non-empty string."
            )
        return value

    @staticmethod
    def _string_set(value: object, *, location: str) -> frozenset[str]:
        if not isinstance(value, list):
            raise _SchemaError(f"{location} must be a JSON array.")
        if any(not isinstance(item, str) or not item.strip() for item in value):
            raise _SchemaError(
                f"{location} must contain only non-empty strings."
            )
        if len(value) != len(set(value)):
            raise _SchemaError(f"{location} must not contain duplicates.")
        return frozenset(value)


def _reject_duplicate_object_keys(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _SchemaError(f"Duplicate JSON object key: {key!r}.")
        result[key] = value
    return result


class _SchemaError(ValueError):
    pass


class _VersionError(ValueError):
    pass
