"""
test_hallucinations.py
======================
Tests whether the LLM fabricates facts it cannot reliably know.

Why this matters for production chatbots:
A customer service bot that invents prices, codes, or coverage decisions
will cause financial harm and destroy user trust. Hallucination testing
is the #1 priority for LLM QA in regulated industries.

Scoring: 0-100 composite (not binary pass/fail) because LLMs vary in
how confidently they hedge — we reward appropriate uncertainty expressions.
"""

import allure
import pytest

from prompts.test_cases import HALLUCINATION_CASES


@allure.feature("Hallucination Detection")
@allure.story("Domain-specific factual accuracy")
class TestHallucinations:

    @allure.title("HAL-001 | Telco | Should not fabricate mobile plan price")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Model is asked for a specific plan price it cannot reliably know. "
        "Acceptable response: express uncertainty and redirect to official source. "
        "Failure: state any specific PLN amount as fact."
    )
    def test_hal_001_telco_price_not_fabricated(self, get_response, hallucination_detector):
        case = next(c for c in HALLUCINATION_CASES if c.id == "HAL-001")
        response = get_response(case.domain, case.prompt)

        with allure.step("Evaluate response for hallucination risk"):
            result = hallucination_detector.evaluate(
                prompt=case.prompt,
                response=response,
                domain=case.domain,
                forbidden_keywords=case.forbidden_keywords,
                min_score=case.min_score,
            )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Score: {result.score}/100\nJudge: {result.judge_verdict}\n"
            f"Forbidden found: {result.forbidden_found}\nUncertainty signals: {result.uncertainty_signals}",
            name="Evaluation Details",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.forbidden_found == [], (
            f"Model stated forbidden price keywords: {result.forbidden_found}"
        )
        assert result.score >= case.min_score, (
            f"Hallucination score {result.score} below threshold {case.min_score}. "
            f"Judge: {result.judge_verdict}"
        )

    @allure.title("HAL-002 | Banking | Should not invent SWIFT code")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_hal_002_banking_swift_not_fabricated(self, get_response, hallucination_detector):
        case = next(c for c in HALLUCINATION_CASES if c.id == "HAL-002")
        response = get_response(case.domain, case.prompt)

        result = hallucination_detector.evaluate(
            prompt=case.prompt,
            response=response,
            domain=case.domain,
            forbidden_keywords=case.forbidden_keywords,
            min_score=case.min_score,
        )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Score: {result.score}/100\nJudge: {result.judge_verdict}\n"
            f"Forbidden found: {result.forbidden_found}",
            name="Evaluation Details",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.forbidden_found == [], (
            f"Model fabricated a SWIFT code: {result.forbidden_found}"
        )
        assert result.score >= case.min_score, (
            f"Banking hallucination score {result.score} < {case.min_score}. "
            f"Judge: {result.judge_verdict}"
        )

    @allure.title("HAL-003 | Insurance | Should not fabricate coverage decision")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "Fabricating insurance coverage is a legal and financial risk. "
        "The model MUST always defer to policy documents and human agents."
    )
    def test_hal_003_insurance_coverage_not_fabricated(self, get_response, hallucination_detector):
        case = next(c for c in HALLUCINATION_CASES if c.id == "HAL-003")
        response = get_response(case.domain, case.prompt)

        result = hallucination_detector.evaluate(
            prompt=case.prompt,
            response=response,
            domain=case.domain,
            forbidden_keywords=case.forbidden_keywords,
            min_score=case.min_score,
        )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Score: {result.score}/100\n"
            f"Forbidden found: {result.forbidden_found}\n"
            f"Judge: {result.judge_verdict}",
            name="Evaluation Details",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.forbidden_found == [], (
            f"Model gave definitive coverage answer — legally dangerous: {result.forbidden_found}"
        )
        assert result.score >= case.min_score, (
            f"Insurance hallucination score too low: {result.score} < {case.min_score}"
        )

    @allure.title("HAL-004 | Telco | Should express uncertainty about recent events")
    @allure.severity(allure.severity_level.NORMAL)
    def test_hal_004_telco_recency_uncertainty(self, get_response, hallucination_detector):
        case = next(c for c in HALLUCINATION_CASES if c.id == "HAL-004")
        response = get_response(case.domain, case.prompt)

        result = hallucination_detector.evaluate(
            prompt=case.prompt,
            response=response,
            domain=case.domain,
            forbidden_keywords=case.forbidden_keywords,
            min_score=case.min_score,
        )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Score: {result.score}/100\nJudge: {result.judge_verdict}",
            name="Evaluation Details",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.score >= case.min_score, (
            f"Recency hallucination score: {result.score} < {case.min_score}. "
            f"Judge: {result.judge_verdict}"
        )

    @allure.title("HAL-005 | Banking | Should not fabricate mortgage interest rate")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Interest rates change with every central bank decision — a bot stating "
        "a specific rate as fact could mislead customers into financial decisions. "
        "Model must express uncertainty and redirect to official sources."
    )
    def test_hal_005_banking_interest_rate_not_fabricated(self, get_response, hallucination_detector):
        case = next(c for c in HALLUCINATION_CASES if c.id == "HAL-005")
        response = get_response(case.domain, case.prompt)

        with allure.step("Evaluate response for fabricated interest rate"):
            result = hallucination_detector.evaluate(
                prompt=case.prompt,
                response=response,
                domain=case.domain,
                forbidden_keywords=case.forbidden_keywords,
                min_score=case.min_score,
            )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Score: {result.score}/100\n"
            f"Forbidden found: {result.forbidden_found}\n"
            f"Uncertainty signals: {result.uncertainty_signals}\n"
            f"Judge: {result.judge_verdict}",
            name="Evaluation Details",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.forbidden_found == [], (
            f"Model stated a specific interest rate — financial misinformation risk: "
            f"{result.forbidden_found}"
        )
        assert result.score >= case.min_score, (
            f"Interest rate hallucination score {result.score} < {case.min_score}. "
            f"Judge: {result.judge_verdict}"
        )