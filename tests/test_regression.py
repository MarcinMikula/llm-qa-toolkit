"""
test_regression.py
==================
Regression tests to detect quality degradation across model/parameter changes.

Problem this solves:
When a team updates the model version, changes temperature, or modifies the system
prompt, responses to known-good queries may silently regress. These tests act as
a safety net by comparing current scores against stored baselines.

Methodology:
- Baseline scores stored in testdata/expected_responses.json
- Acceptable delta: ±10 points by default
- Critical security responses (card fraud etc.) get tighter tolerance
- Edge cases tested with both low (0.1) and high (0.9) temperature
"""

import allure
import pytest

from conftest import get_model_response, DOMAIN_PROMPTS
from evaluators.quality_scorer import QualityScorer
from prompts.test_cases import REGRESSION_CASES
from prompts.system_prompts import BANKING_TRANSACTION_ASSISTANT, TELCO_CUSTOMER_SERVICE


@allure.feature("Regression Testing")
class TestRegression:

    @allure.title("REG-001 | Banking | Card fraud response quality stability")
    @allure.story("Banking")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Security-critical responses must remain stable. "
        "Card cloning guidance is time-sensitive and must always include card blocking and bank contact. "
        "Regression detected if score drops >10pts from baseline."
    )
    def test_reg_001_card_fraud_response_stable(
        self, get_response, quality_scorer, expected_responses
    ):
        case = next(c for c in REGRESSION_CASES if c.id == "REG-001")
        baseline = expected_responses.get("REG-001", {})
        baseline_score = baseline.get("baseline_score", 85.0)
        acceptable_delta = baseline.get("acceptable_delta", 10.0)

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
            f"Current score: {result.composite}/100\n"
            f"Baseline: {baseline_score}\n"
            f"Allowed delta: ±{acceptable_delta}\n"
            f"Actionability: {result.actionability}\n"
            f"Summary: {result.explanation}",
            name="Regression Analysis",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= (baseline_score - acceptable_delta), (
            f"REGRESSION DETECTED: score {result.composite} vs baseline {baseline_score} "
            f"(delta {baseline_score - result.composite:.1f} > {acceptable_delta})"
        )
        assert result.actionability >= 70, (
            "Card fraud response must always include actionable steps (block card, contact bank)"
        )

    @allure.title("REG-002 | Telco | Subscription cancellation response stability")
    @allure.story("Telco")
    @allure.severity(allure.severity_level.NORMAL)
    def test_reg_002_cancellation_response_stable(
        self, get_response, quality_scorer, expected_responses
    ):
        case = next(c for c in REGRESSION_CASES if c.id == "REG-002")
        baseline = expected_responses.get("REG-002", {})
        baseline_score = baseline.get("baseline_score", 78.0)
        acceptable_delta = baseline.get("acceptable_delta", 10.0)

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
            f"Current: {result.composite} | Baseline: {baseline_score} | Delta limit: {acceptable_delta}",
            name="Regression Summary",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= (baseline_score - acceptable_delta), (
            f"REGRESSION: cancellation response dropped {baseline_score - result.composite:.1f} points"
        )

    @allure.title("REG-003 | Temperature sensitivity | High temp should not break security")
    @allure.story("Unknown")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "At temperature=0.9 the model is more creative/random. "
        "Security-critical responses (fraud guidance) must still meet minimum quality. "
        "Tests that only fail at high temperature indicate temperature-sensitive system prompts."
    )
    def test_reg_003_high_temperature_security_stability(self, anthropic_client, quality_scorer):
        prompt = "What should I do if I think my card has been cloned?"

        # Run at high temperature — more random, more likely to regress
        response = get_model_response(
            client=anthropic_client,
            system_prompt=BANKING_TRANSACTION_ASSISTANT,
            user_message=prompt,
            temperature=0.9,
        )

        result = quality_scorer.evaluate(
            prompt=prompt,
            response=response,
            domain="banking",
            expected_keywords=["block", "cancel", "bank", "hotline", "report"],
            min_score=70.0,  # slightly relaxed vs default, but still critical
        )

        allure.attach(response, name="High-Temp Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Temperature: 0.9\nScore: {result.composite}/100\nSummary: {result.explanation}",
            name="Stability Check",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= 70.0, (
            f"High-temperature regression: score {result.composite} suggests "
            "security response is temperature-sensitive"
        )

    @allure.title("REG-004 | Low temperature consistency | Deterministic responses")
    @allure.story("Unknown")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "At temperature=0.1, we expect more deterministic, consistent responses. "
        "Running the same query twice should produce similar quality scores. "
        "Large score variance indicates an unstable system prompt."
    )
    def test_reg_004_low_temperature_consistency(self, anthropic_client, quality_scorer):
        prompt = "How do I cancel my subscription?"
        scores = []

        for run in range(2):
            response = get_model_response(
                client=anthropic_client,
                system_prompt=TELCO_CUSTOMER_SERVICE,
                user_message=prompt,
                temperature=0.1,
            )
            result = quality_scorer.evaluate(
                prompt=prompt,
                response=response,
                domain="telco",
                expected_keywords=["cancel", "notice", "contract", "contact"],
                min_score=72.0,
            )
            scores.append(result.composite)
            allure.attach(
                f"Run {run + 1}: {result.composite}/100",
                name=f"Run {run + 1}",
                attachment_type=allure.attachment_type.TEXT,
            )

        score_delta = abs(scores[0] - scores[1])
        allure.attach(
            f"Run 1: {scores[0]} | Run 2: {scores[1]} | Delta: {score_delta:.1f}",
            name="Consistency Analysis",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert score_delta <= 20, (
            f"Low-temp variance too high ({score_delta:.1f} pts) — "
            "system prompt may be producing inconsistent responses"
        )
        assert all(s >= 65 for s in scores), (
            f"One or more low-temp runs below threshold: {scores}"
        )

    @allure.title("REG-005 | Insurance | Storm damage response stability")
    @allure.story("Insurance")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Storm damage response must address: coverage scope, exclusions, franchise/deductible, "
        "and claims procedure — WITHOUT giving a definitive yes/no without policy context. "
        "This response must remain stable across model updates — any regression in completeness "
        "or actionability could leave a customer without critical claims guidance."
    )
    def test_reg_005_insurance_storm_damage_stable(self, get_response, quality_scorer):
        case = next(c for c in REGRESSION_CASES if c.id == "REG-005")
        baseline_score = 78.0
        acceptable_delta = 10.0

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
            f"Current: {result.composite}/100\n"
            f"Baseline: {baseline_score}\n"
            f"Floor: {baseline_score - acceptable_delta}\n"
            f"Completeness: {result.completeness}\n"
            f"Actionability: {result.actionability}\n"
            f"Summary: {result.explanation}",
            name="Regression Analysis",
            attachment_type=allure.attachment_type.TEXT,
        )

        # Must NOT give definitive yes/no
        response_lower = response.lower()
        for forbidden in case.forbidden_keywords:
            assert forbidden.lower() not in response_lower, (
                f"Model gave definitive coverage answer without policy context: '{forbidden}'"
            )

        assert result.composite >= (baseline_score - acceptable_delta), (
            f"REGRESSION: storm damage score {result.composite} vs baseline {baseline_score} "
            f"(dropped {baseline_score - result.composite:.1f} pts)"
        )
        assert result.actionability >= 65, (
            "Storm damage response must include actionable next steps (document, file claim, contact)"
        )