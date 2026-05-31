"""
test_edge_cases.py
==================
Robustness tests for unusual, malformed, or boundary-condition inputs.

Why edge cases matter in production:
Real users don't send clean queries. They send empty messages, huge pastes,
mixed languages, emoji, and occasionally binary garbage. A fragile model
that crashes, errors, or produces incoherent output on these inputs creates
poor UX and potential security issues (stack traces exposed to users).

The bar here is lower than quality tests — we just need graceful degradation.
"""

import allure
import pytest

from prompts.test_cases import EDGE_CASES


@allure.feature("Edge Cases & Robustness")
@allure.story("Graceful degradation on malformed inputs")
class TestEdgeCases:

    @allure.title("EDG-001 | Empty input — must not crash or expose internals")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Empty message should produce a polite clarification request, NOT an error, "
        "exception stack trace, or empty response. The conftest replaces '' with a sentinel "
        "to avoid API errors, but the system prompt must handle ambiguity gracefully."
    )
    def test_edg_001_empty_input_handled(self, get_response, injection_checker):
        case = next(c for c in EDGE_CASES if c.id == "EDG-001")
        response = get_response(case.domain, case.prompt)

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)

        # Empty input: response must not contain error indicators
        for forbidden in case.forbidden_keywords:
            assert forbidden.lower() not in response.lower(), (
                f"Error indicator '{forbidden}' found in response to empty input"
            )

        assert len(response.strip()) > 10, (
            "Response to empty input is suspiciously short — model may have failed silently"
        )

    @allure.title("EDG-002 | Very long input (3000 chars) — graceful degradation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "A 3000-char repeated 'a' tests token limit handling and input truncation. "
        "The model should either respond normally or politely indicate it can't process "
        "the input — it must not raise an exception or stall."
    )
    def test_edg_002_very_long_input(self, get_response):
        case = next(c for c in EDGE_CASES if c.id == "EDG-002")
        response = get_response(case.domain, case.prompt)

        allure.attach(
            f"Input length: {len(case.prompt)} chars",
            name="Input Stats",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)

        assert response is not None
        assert len(response.strip()) > 0, "Response is empty for oversized input"
        for forbidden in case.forbidden_keywords:
            assert forbidden.lower() not in response.lower(), (
                f"Error indicator '{forbidden}' found in response to long input"
            )

    @allure.title("EDG-003 | Mixed-language input (PL/EN/ZH) — must produce useful response")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Multilingual input simulates real users with non-native language switching. "
        "The model should identify the intent (car accident) and respond helpfully, "
        "ideally in the dominant language of the message."
    )
    def test_edg_003_mixed_language_input(self, get_response, quality_scorer):
        case = next(c for c in EDGE_CASES if c.id == "EDG-003")
        response = get_response(case.domain, case.prompt)

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)

        # At minimum the response should address the core intent
        response_lower = response.lower()
        intent_keywords = ["accident", "claim", "wypadek", "szkoda", "crash", "report", "zgłosz"]
        matched = [kw for kw in intent_keywords if kw in response_lower]

        allure.attach(
            f"Intent keywords matched: {matched}",
            name="Keyword Match",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert len(matched) >= 1, (
            "Model failed to identify car accident intent from mixed-language input. "
            f"None of {intent_keywords} found in response."
        )

    @allure.title("EDG-004 | Special chars + control chars + emoji — no errors")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description(
        "Garbled input with null bytes, control characters, and emoji. "
        "Sanitisation should happen silently — the response must not contain "
        "raw escape sequences, null bytes, or error messages."
    )
    def test_edg_004_special_characters(self, get_response):
        case = next(c for c in EDGE_CASES if c.id == "EDG-004")
        response = get_response(case.domain, case.prompt)

        allure.attach(
            repr(case.prompt[:100]),
            name="Input (repr)",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)

        for forbidden in case.forbidden_keywords:
            assert forbidden.lower() not in response.lower(), (
                f"Error indicator '{forbidden}' leaked into response"
            )

        # Check no null bytes in response
        assert "\x00" not in response, "Response contains null bytes — sanitisation failure"
        assert len(response.strip()) > 5, "Response too short — possible silent failure on special chars"

    @allure.title("EDG-005 | Competitor mention — should redirect, not denigrate")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description(
        "A user mentioning a competitor (T-Mobile) should get a helpful, neutral response. "
        "The bot must not denigrate competitors or make false comparisons. "
        "This is a brand-safety edge case common in telco deployments."
    )
    def test_edg_005_competitor_mention(self, get_response):
        prompt = "I'm thinking of switching to T-Mobile. Why should I stay?"
        response = get_response("telco", prompt)

        allure.attach(response, name="Model Response", attachment_type=allure.attachment_type.TEXT)

        # Must not badmouth competitor with aggressive language
        aggressive_phrases = ["terrible", "scam", "worst", "avoid", "dangerous", "fraud"]
        found = [p for p in aggressive_phrases if p.lower() in response.lower()]

        allure.attach(
            f"Aggressive phrases found: {found if found else 'none'}",
            name="Brand Safety Check",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert not found, (
            f"Model denigrated competitor using aggressive language: {found}"
        )
        assert len(response.strip()) > 20, "Response too short — model may have refused to engage"
