"""
test_regression.py
==================
Tests whether response quality remains stable across model/parameter changes.

Why regression testing matters for LLMs:
Unlike deterministic software, LLM responses change when you update the model,
adjust temperature, or modify the system prompt. A response that scored 85
last week might score 60 after a model update — regression tests catch this.

Strategy: compare live quality score against a baseline stored in
testdata/expected_responses.json. Test fails if score drops more than
acceptable_delta below baseline.

This is the QA equivalent of performance benchmarking for AI systems.
"""

import allure
import pytest

from prompts.test_cases import REGRESSION_CASES


@allure.feature("Regression Testing")
@allure.story("Response quality stability across model changes")
class TestRegression:

    @allure.title("REG-001 | Banking | Card cloning response must not regress")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "Security-critical response: user reporting a cloned card needs immediate, "
        "clear guidance (block card, contact bank, police report). "
        "Baseline score: 85.0. Acceptable delta: ±10 pts. "
        "Any regression here has real financial safety implications."
    )
    def test_reg_001_banking_card_cloning_stable(self, get_response, quality_scorer, expected_responses):
        case = next(c for c in REGRESSION_CASES if c.id == "REG-001")
        baseline = expected_responses["REG-001"]
        response = get_response(case.domain, case.prompt)

        with allure.step("Score current response and compare to baseline"):
            result = quality_scorer.evaluate(
                prompt=case.prompt,
                response=response,
                domain=case.domain,
                expected_keywords=case.expected_keywords,
                min_score=case.min_score,
            )

        baseline_score = baseline["baseline_score"]
        acceptable_delta = baseline["acceptable_delta"]
        lower_bound = baseline_score - acceptable_delta

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Current score:    {result.composite}/100\n"
            f"Baseline score:   {baseline_score}/100\n"
            f"Acceptable floor: {lower_bound}/100\n"
            f"Delta:            {round(result.composite - baseline_score, 1)}\n\n"
            f"Completeness:  {result.completeness}\n"
            f"Precision:     {result.precision}\n"
            f"Format:        {result.format_score}\n"
            f"Actionability: {result.actionability}\n\n"
            f"Summary: {result.explanation}",
            name="Regression Analysis",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            f"Acceptable behavior: {baseline['acceptable_behavior']}\n"
            f"Unacceptable behavior: {baseline['unacceptable_behavior']}",
            name="Baseline Criteria",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= lower_bound, (
            f"REGRESSION DETECTED: score {result.composite} dropped more than "
            f"{acceptable_delta} pts below baseline {baseline_score}. "
            f"Floor was {lower_bound}. Summary: {result.explanation}"
        )
        assert result.composite >= case.min_score, (
            f"Score {result.composite} below absolute minimum {case.min_score}. "
            f"Summary: {result.explanation}"
        )

    @allure.title("REG-002 | Telco | Subscription cancellation response must not regress")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "High-frequency user query: subscription cancellation. "
        "Response must mention notice period, cancellation channels, and contract obligations. "
        "Baseline score: 78.0. Acceptable delta: ±10 pts. "
        "Regression here affects large numbers of users daily."
    )
    def test_reg_002_telco_cancellation_stable(self, get_response, quality_scorer, expected_responses):
        case = next(c for c in REGRESSION_CASES if c.id == "REG-002")
        baseline = expected_responses["REG-002"]
        response = get_response(case.domain, case.prompt)

        with allure.step("Score current response and compare to baseline"):
            result = quality_scorer.evaluate(
                prompt=case.prompt,
                response=response,
                domain=case.domain,
                expected_keywords=case.expected_keywords,
                min_score=case.min_score,
            )

        baseline_score = baseline["baseline_score"]
        acceptable_delta = baseline["acceptable_delta"]
        lower_bound = baseline_score - acceptable_delta

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Current score:    {result.composite}/100\n"
            f"Baseline score:   {baseline_score}/100\n"
            f"Acceptable floor: {lower_bound}/100\n"
            f"Delta:            {round(result.composite - baseline_score, 1)}\n\n"
            f"Completeness:  {result.completeness}\n"
            f"Precision:     {result.precision}\n"
            f"Format:        {result.format_score}\n"
            f"Actionability: {result.actionability}\n\n"
            f"Summary: {result.explanation}",
            name="Regression Analysis",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            f"Acceptable behavior: {baseline['acceptable_behavior']}\n"
            f"Unacceptable behavior: {baseline['unacceptable_behavior']}",
            name="Baseline Criteria",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= lower_bound, (
            f"REGRESSION DETECTED: score {result.composite} dropped more than "
            f"{acceptable_delta} pts below baseline {baseline_score}. "
            f"Floor was {lower_bound}. Summary: {result.explanation}"
        )
        assert result.composite >= case.min_score, (
            f"Score {result.composite} below absolute minimum {case.min_score}. "
            f"Summary: {result.explanation}"
        )