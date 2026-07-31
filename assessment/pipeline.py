"""End-to-end orchestration for the assessment-grounded runtime."""

from __future__ import annotations

from assessment.contracts import AssessmentContractBuilder
from assessment.evaluator_protocol import BoundedEvaluatorRequestBuilder
from assessment.models import (
    AssessmentDefinitionError,
    AssessmentRequest,
    AssessmentRun,
    ExamineeRequest,
    TechnicalState,
    TechnicalStatus,
)
from assessment.ports import EvaluatorPort, ExamineePort
from assessment.validator import EvaluationResultValidator


class AssessmentPipeline:
    """Run examinee access, contract construction, evaluation, and validation."""

    def __init__(
        self,
        *,
        examinee: ExamineePort,
        evaluator: EvaluatorPort,
        contract_builder: AssessmentContractBuilder | None = None,
        evaluator_request_builder: BoundedEvaluatorRequestBuilder | None = None,
        result_validator: EvaluationResultValidator | None = None,
    ) -> None:
        self._examinee = examinee
        self._evaluator = evaluator
        self._contract_builder = contract_builder or AssessmentContractBuilder()
        self._evaluator_request_builder = (
            evaluator_request_builder or BoundedEvaluatorRequestBuilder()
        )
        self._result_validator = result_validator or EvaluationResultValidator()

    def run(
        self,
        examinee_request: ExamineeRequest,
        assessment_request: AssessmentRequest,
    ) -> AssessmentRun:
        candidate_response = self._examinee.respond(examinee_request)

        if candidate_response.technical_status.state is not TechnicalState.COMPLETED:
            scoped_result = self._result_validator.technical_error_result(
                case_id=examinee_request.case_id,
                technical_status=candidate_response.technical_status,
            )
            return AssessmentRun(
                candidate_response=candidate_response,
                assessment_contract=None,
                evaluator_request=None,
                proposed_evaluator_result=None,
                scoped_result=scoped_result,
            )

        try:
            contract = self._contract_builder.build(
                candidate_response,
                assessment_request,
            )
        except AssessmentDefinitionError as exc:
            scoped_result = self._result_validator.technical_error_result(
                case_id=assessment_request.case_id,
                technical_status=TechnicalStatus.error(
                    exc.error_type,
                    str(exc),
                ),
            )
            return AssessmentRun(
                candidate_response=candidate_response,
                assessment_contract=None,
                evaluator_request=None,
                proposed_evaluator_result=None,
                scoped_result=scoped_result,
            )

        try:
            evaluator_request = self._evaluator_request_builder.build(
                examinee_request,
                candidate_response,
                contract,
            )
        except AssessmentDefinitionError as exc:
            scoped_result = self._result_validator.technical_error_result(
                case_id=assessment_request.case_id,
                technical_status=TechnicalStatus.error(
                    exc.error_type,
                    str(exc),
                ),
            )
            return AssessmentRun(
                candidate_response=candidate_response,
                assessment_contract=contract,
                evaluator_request=None,
                proposed_evaluator_result=None,
                scoped_result=scoped_result,
            )

        proposed_result = self._evaluator.evaluate(evaluator_request)
        scoped_result = self._result_validator.validate(contract, proposed_result)

        return AssessmentRun(
            candidate_response=candidate_response,
            assessment_contract=contract,
            evaluator_request=evaluator_request,
            proposed_evaluator_result=proposed_result,
            scoped_result=scoped_result,
        )
