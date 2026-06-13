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
class TestResponseQuality:

    @allure.title("QUA-001 | Telco | Internet troubleshooting — actionable steps required")
    @allure.story("Telco")
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
    @allure.story("Banking")
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
    @allure.story("Insurance")
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
    @allure.story("Telco")
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

    @allure.title("QUA-005 | Energy | Loyalty programme — specific steps required")
    @allure.story("Energy")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Loyalty programme response must include specific conditions (eligibility) "
        "AND required customer actions. A generic description of benefits without "
        "actionable steps is a quality failure for this domain."
    )
    def test_qua_005_energy_loyalty_programme(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-005")
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

        assert result.actionability >= 65, (
            f"Actionability {result.actionability} too low — loyalty response must include "
            "steps the customer must take, not just programme description"
        )
        assert result.composite >= case.min_score, (
            f"Loyalty programme quality score {result.composite} < {case.min_score}. "
            f"{result.explanation}"
        )

    @allure.title("QUA-006 | Insurance | OC vs AC — must distinguish legal basis and coverage")
    @allure.story("Insurance")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "OC is mandatory third-party liability (regulated by Motor Insurance Act). "
        "AC is voluntary own-damage insurance (regulated by OWU — insurer's general terms). "
        "Response must clearly distinguish: mandatory vs voluntary, legal basis, coverage scope."
    )
    def test_qua_006_insurance_oc_vs_ac(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-006")
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

        assert result.completeness >= 65, (
            f"Completeness {result.completeness} — OC vs AC explanation must cover "
            "both mandatory/voluntary distinction and legal basis"
        )
        assert result.composite >= case.min_score, (
            f"OC vs AC quality score {result.composite} < {case.min_score}. {result.explanation}"
        )