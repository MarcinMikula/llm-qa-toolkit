"""
test_response_quality.py
========================
Tests whether the LLM produces high-quality, useful responses in domain scenarios.

Why quality scoring matters:
A chatbot that technically answers a question but is vague, unstructured,
or fails to tell the user what to do next is a poor customer experience.
Binary pass/fail misses this — we need multi-dimensional scoring.

Scoring: 4-dimension weighted composite (Completeness 30%, Precision 25%,
Format 20%, Actionability 25%) + keyword bonus (max +10 pts).
Threshold varies by criticality of the scenario.
"""

import allure
import pytest

from prompts.test_cases import QUALITY_CASES


@allure.feature("Response Quality")
@allure.story("Multi-dimensional quality scoring across domains")
class TestResponseQuality:

    @allure.title("QUA-001 | Telco | Internet troubleshooting must be actionable")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "A user reporting an outage needs clear, ordered troubleshooting steps. "
        "Vague answers ('try restarting your device') without structure or next steps "
        "fail the actionability dimension. Min score: 75."
    )
    def test_qua_001_telco_internet_troubleshooting(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-001")
        response = get_response(case.domain, case.prompt)

        with allure.step("Score response across 4 quality dimensions"):
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
            name="Quality Breakdown",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= case.min_score, (
            f"Quality score {result.composite} < {case.min_score}. "
            f"Weakest dimension likely actionability or format. "
            f"Summary: {result.explanation}"
        )

    @allure.title("QUA-002 | Banking | Merchant name decoding must identify Amazon")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Users frequently panic at unfamiliar merchant names on their statement. "
        "The bot must correctly identify AMZN MKTP PL as Amazon and provide "
        "actionable dispute guidance if needed. Min score: 72."
    )
    def test_qua_002_banking_merchant_identification(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-002")
        response = get_response(case.domain, case.prompt)

        with allure.step("Score merchant identification response"):
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
            name="Quality Breakdown",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= case.min_score, (
            f"Merchant identification score {result.composite} < {case.min_score}. "
            f"Summary: {result.explanation}"
        )

    @allure.title("QUA-003 | Insurance | Accident reporting procedure must be complete and ordered")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "Post-accident guidance is time-critical and legally significant. "
        "The response must cover: safety, documentation, police, 24h reporting window, "
        "and claim submission. Missing any step is a completeness failure. Min score: 78."
    )
    def test_qua_003_insurance_accident_reporting(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-003")
        response = get_response(case.domain, case.prompt)

        with allure.step("Score accident reporting procedure response"):
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
            name="Quality Breakdown",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= case.min_score, (
            f"Accident reporting score {result.composite} < {case.min_score}. "
            f"Check completeness — all mandatory steps must be present. "
            f"Summary: {result.explanation}"
        )

    @allure.title("QUA-004 | Telco | eSIM vs SIM explanation must be clear and jargon-free")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Technical explanations for non-technical users must avoid jargon overload. "
        "The response should explain the practical difference and mention compatibility. "
        "Scored lower threshold (70) as format flexibility is acceptable here."
    )
    def test_qua_004_telco_esim_explanation(self, get_response, quality_scorer):
        case = next(c for c in QUALITY_CASES if c.id == "QUA-004")
        response = get_response(case.domain, case.prompt)

        with allure.step("Score eSIM explanation clarity"):
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
            name="Quality Breakdown",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= case.min_score, (
            f"eSIM explanation score {result.composite} < {case.min_score}. "
            f"Summary: {result.explanation}"
        )