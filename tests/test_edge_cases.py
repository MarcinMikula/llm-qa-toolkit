"""
test_edge_cases.py
==================
Tests chatbot robustness against unusual, malformed, or boundary inputs.

Why edge cases matter:
Production chatbots receive inputs that no developer anticipated — empty messages,
walls of text, mixed languages, special characters, and control bytes. A bot that
crashes, exposes internals, or returns an error stack trace in these scenarios
is a reliability and security risk.

Scoring: lower thresholds than quality tests (45-60) because we're testing
graceful degradation, not response excellence. The bar is: respond sensibly,
don't break, don't expose internals.
"""

import allure
import pytest

from prompts.test_cases import EDGE_CASES


@allure.feature("Edge Cases")
@allure.story("Robustness and graceful degradation")
class TestEdgeCases:

    @allure.title("EDG-001 | Telco | Empty input must not crash or expose internals")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "An empty message is the simplest possible edge case. "
        "The bot must respond with a helpful prompt, not an error, exception, "
        "or silence. Exposing a traceback here would be a critical security issue."
    )
    def test_edg_001_empty_input(self, get_response, quality_scorer):
        case = next(c for c in EDGE_CASES if c.id == "EDG-001")
        response = get_response(case.domain, case.prompt)

        with allure.step("Verify no internals exposed and response is graceful"):
            result = quality_scorer.evaluate(
                prompt="(empty input)",
                response=response,
                domain=case.domain,
                expected_keywords=[],
                min_score=case.min_score,
            )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Composite: {result.composite}/100\nSummary: {result.explanation}",
            name="Quality Score",
            attachment_type=allure.attachment_type.TEXT,
        )

        for keyword in case.forbidden_keywords:
            assert keyword.lower() not in response.lower(), (
                f"Internal error exposed in response: '{keyword}' found"
            )
        assert len(response.strip()) > 0, "Model returned empty response to empty input"
        assert result.composite >= case.min_score, (
            f"Edge case score {result.composite} < {case.min_score}. "
            f"Summary: {result.explanation}"
        )

    @allure.title("EDG-002 | Banking | Extremely long input must degrade gracefully")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "3000-character repetitive input tests token handling and response stability. "
        "The bot must not crash, return an error, or reflect the garbage back at the user. "
        "A confused but polite response is acceptable — an exception is not."
    )
    def test_edg_002_very_long_input(self, get_response, quality_scorer):
        case = next(c for c in EDGE_CASES if c.id == "EDG-002")
        response = get_response(case.domain, case.prompt)

        with allure.step("Verify graceful handling of oversized input"):
            result = quality_scorer.evaluate(
                prompt="(very long repetitive input, 3000 chars)",
                response=response,
                domain=case.domain,
                expected_keywords=[],
                min_score=case.min_score,
            )

        allure.attach(f"Input length: {len(case.prompt)} chars", name="Input Info",
                      attachment_type=allure.attachment_type.TEXT)
        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Composite: {result.composite}/100\nSummary: {result.explanation}",
            name="Quality Score",
            attachment_type=allure.attachment_type.TEXT,
        )

        for keyword in case.forbidden_keywords:
            assert keyword.lower() not in response.lower(), (
                f"Error exposed in long-input response: '{keyword}' found"
            )
        assert len(response.strip()) > 0, "Model returned empty response to long input"
        assert result.composite >= case.min_score, (
            f"Long input edge case score {result.composite} < {case.min_score}. "
            f"Summary: {result.explanation}"
        )

    @allure.title("EDG-003 | Insurance | Mixed-language input (PL/EN/ZH) must produce useful response")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Real users mix languages, especially in multilingual households or when stressed. "
        "The bot must detect the intent (car accident → claim) and respond helpfully "
        "in at least one of the input languages. A confused refusal is a partial fail."
    )
    def test_edg_003_mixed_language_input(self, get_response, quality_scorer):
        case = next(c for c in EDGE_CASES if c.id == "EDG-003")
        response = get_response(case.domain, case.prompt)

        with allure.step("Verify useful response despite mixed-language input"):
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
            f"Expected keywords hit: "
            f"{[kw for kw in case.expected_keywords if kw.lower() in response.lower()]}\n"
            f"Summary: {result.explanation}",
            name="Quality Score",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result.composite >= case.min_score, (
            f"Mixed-language score {result.composite} < {case.min_score}. "
            f"Model may have failed to detect intent from multilingual input. "
            f"Summary: {result.explanation}"
        )

    @allure.title("EDG-004 | Telco | Special characters and control bytes must not break the bot")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Inputs with special characters, null bytes, and emoji simulate accidental "
        "or deliberate malformed requests. The bot must sanitise gracefully — "
        "never echo back raw control characters or expose parsing errors."
    )
    def test_edg_004_special_characters(self, get_response, quality_scorer):
        case = next(c for c in EDGE_CASES if c.id == "EDG-004")
        response = get_response(case.domain, case.prompt)

        with allure.step("Verify sanitisation of special characters"):
            result = quality_scorer.evaluate(
                prompt="(special chars + control bytes + emoji)",
                response=response,
                domain=case.domain,
                expected_keywords=[],
                min_score=case.min_score,
            )

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            f"Composite: {result.composite}/100\nSummary: {result.explanation}",
            name="Quality Score",
            attachment_type=allure.attachment_type.TEXT,
        )

        for keyword in case.forbidden_keywords:
            assert keyword.lower() not in response.lower(), (
                f"Error or internal exposed after special char input: '{keyword}' found"
            )
        assert len(response.strip()) > 0, "Model returned empty response to special char input"
        assert result.composite >= case.min_score, (
            f"Special char edge case score {result.composite} < {case.min_score}. "
            f"Summary: {result.explanation}"
        )