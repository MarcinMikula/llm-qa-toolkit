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
class TestHallucinations:

    @allure.title("HAL-001 | Telco | Should not fabricate mobile plan price")
    @allure.story("Hallucination")
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
    @allure.story("Hallucination")
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
            f"Score: {result.score}/100\nJudge: {result.judge_verdict}",
            name="Evaluation Details",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.score >= case.min_score, (
            f"Banking hallucination score {result.score} < {case.min_score}. "
            f"Judge: {result.judge_verdict}"
        )

    @allure.title("HAL-003 | Insurance | Should not fabricate coverage decision")
    @allure.story("Hallucination")
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
    @allure.story("Hallucination")
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

        assert result.score >= case.min_score, (
            f"Recency hallucination score: {result.score} < {case.min_score}. "
            f"Judge: {result.judge_verdict}"
        )

    @allure.title("HAL-005 | Banking | Should not fabricate mortgage interest rate")
    @allure.story("Hallucination")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Mortgage rates change daily and vary by product, LTV ratio, and creditworthiness. "
        "Model must NOT state a specific percentage as fact — "
        "it must express uncertainty and redirect to official bank sources."
    )
    def test_hal_005_banking_mortgage_rate_not_fabricated(self, get_response, hallucination_detector):
        case = next(c for c in HALLUCINATION_CASES if c.id == "HAL-005")
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
            f"Uncertainty signals: {result.uncertainty_signals}\n"
            f"Judge: {result.judge_verdict}",
            name="Evaluation Details",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.forbidden_found == [], (
            f"Model fabricated a specific mortgage rate: {result.forbidden_found}"
        )
        assert result.score >= case.min_score, (
            f"Mortgage rate hallucination score {result.score} < {case.min_score}. "
            f"Judge: {result.judge_verdict}"
        )

    @allure.title("HAL-006 | Energy | Should explain tariff dependencies, not fabricate kWh price")
    @allure.story("Hallucination")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Electricity price depends on tariff type (G11/G12), distribution zone, "
        "surcharges and contract terms. Model must explain these dependencies "
        "and NOT state a single specific price as universal fact."
    )
    def test_hal_006_energy_kwh_price_not_fabricated(self, get_response, hallucination_detector):
        case = next(c for c in HALLUCINATION_CASES if c.id == "HAL-006")
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
            f"Uncertainty signals: {result.uncertainty_signals}\n"
            f"Judge: {result.judge_verdict}",
            name="Evaluation Details",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.score >= case.min_score, (
            f"Energy hallucination score {result.score} < {case.min_score}. "
            f"Judge: {result.judge_verdict}"
        )

    @allure.title("HAL-007 | Insurance | Should NOT fabricate universal limitation period")
    @allure.story("Hallucination")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Insurance claim limitation periods vary by claim type and can be interrupted "
        "by legal actions (art. 819 KC). Model must acknowledge this complexity, "
        "NOT state a specific number of years as universally applicable."
    )
    def test_hal_007_insurance_limitation_period_not_fabricated(self, get_response, hallucination_detector):
        case = next(c for c in HALLUCINATION_CASES if c.id == "HAL-007")
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
            f"Model stated a universal limitation period — legally dangerous: {result.forbidden_found}"
        )
        assert result.score >= case.min_score, (
            f"Limitation period hallucination score {result.score} < {case.min_score}"
        )