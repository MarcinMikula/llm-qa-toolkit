"""
test_response_quality.py
========================
Multi-dimensional quality evaluation of chatbot responses.

Why binary pass/fail is insufficient for LLM testing:
An LLM response can be technically "correct" but fail the user in many ways —
too vague, missing next steps, wrong tone, or poorly structured.
We score four dimensions (completeness, precision, format, actionability)
and require a weighted composite above threshold.

Domain context matters: insurance/banking responses need higher actionability
than general knowledge queries.
"""

import allure
import pytest

from prompts.test_cases import QUALITY_CASES


@allure.feature("Response Quality")
@allure.story("Multi-dimensional quality scoring")
class TestResponseQuality:

    @allure.title("QUA-001 | Telco | Internet troubleshooting — actionable steps required")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "A user reporting no internet expects concrete troubleshooting steps, not generic advice. "
        "We specifically penalise vague responses that don't help the user self-resolve."
    )
    def test_qua_001_telco_internet_troubleshooting(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-001")
        response = get_response(case.domain, case.prompt)

        result = quality_scorer.evaluate(
            prompt=case.prompt,
            response=response,
            domain=case.domain,
            expected_keywords=case.expected_keywords,
            min_score=case.min_score,
        )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Composite: {result.composite}/100\n"
            f"Completeness: {result.completeness}\n"
            f"Precision: {result.precision}\n"
            f"Format: {result.format_score}\n"
            f"Actionability: {result.actionability}\n"
            f"Summary: {result.explanation}",
            name="Quality Scorecard",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.actionability >= 60, (
            f"Actionability score too low ({result.actionability}) — "
            "troubleshooting response must give clear next steps"
        )
        assert result.composite >= case.min_score, (
            f"Quality composite {result.composite} < {case.min_score}. {result.explanation}"
        )

    @allure.title("QUA-002 | Banking | Merchant name decoding — should identify Amazon")
    @allure.severity(allure.severity_level.NORMAL)
    def test_qua_002_banking_merchant_identification(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-002")
        response = get_response(case.domain, case.prompt)

        result = quality_scorer.evaluate(
            prompt=case.prompt,
            response=response,
            domain=case.domain,
            expected_keywords=case.expected_keywords,
            min_score=case.min_score,
        )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Composite: {result.composite}/100\n"
            f"Completeness: {result.completeness}\n"
            f"Precision: {result.precision}\n"
            f"Summary: {result.explanation}",
            name="Quality Scorecard",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.precision >= 65, (
            f"Precision too low ({result.precision}) — merchant 'AMZN MKTP' should be identified"
        )
        assert result.composite >= case.min_score

    @allure.title("QUA-003 | Insurance | Accident reporting — complete procedure expected")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Post-accident guidance must include documentation, timeframes, and escalation paths. "
        "Missing any critical step (e.g. police report, 24h notice) is a completeness failure."
    )
    def test_qua_003_insurance_accident_reporting(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-003")
        response = get_response(case.domain, case.prompt)

        result = quality_scorer.evaluate(
            prompt=case.prompt,
            response=response,
            domain=case.domain,
            expected_keywords=case.expected_keywords,
            min_score=case.min_score,
        )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Composite: {result.composite}/100\n"
            f"Completeness: {result.completeness}\n"
            f"Actionability: {result.actionability}\n"
            f"Summary: {result.explanation}",
            name="Quality Scorecard",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.completeness >= 65, (
            f"Completeness {result.completeness} — accident procedure must not omit key steps"
        )
        assert result.composite >= case.min_score

    @allure.title("QUA-004 | Telco | eSIM vs SIM explanation — avoid jargon overload")
    @allure.severity(allure.severity_level.MINOR)
    def test_qua_004_telco_esim_explanation(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-004")
        response = get_response(case.domain, case.prompt)

        result = quality_scorer.evaluate(
            prompt=case.prompt,
            response=response,
            domain=case.domain,
            expected_keywords=case.expected_keywords,
            min_score=case.min_score,
        )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Composite: {result.composite}/100\nSummary: {result.explanation}",
            name="Quality Scorecard",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= case.min_score, (
            f"eSIM quality score {result.composite} < {case.min_score}. {result.explanation}"
        )
