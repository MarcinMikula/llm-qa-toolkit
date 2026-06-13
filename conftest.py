"""
conftest.py — shared pytest fixtures for llm-qa-toolkit

Tryby działania:
  --mock   : używa predefiniowanych odpowiedzi z mock_responses.py (bez API)
  domyślny : wymaga ANTHROPIC_API_KEY w .env
"""

import json
import os
import pytest
import anthropic
from unittest.mock import MagicMock
from dotenv import load_dotenv

from evaluators.hallucination_detector import HallucinationDetector
from evaluators.injection_checker import InjectionChecker
from evaluators.quality_scorer import QualityScorer
from prompts.system_prompts import (
    TELCO_CUSTOMER_SERVICE,
    BANKING_TRANSACTION_ASSISTANT,
    INSURANCE_POLICY_BOT,
    ENERGY_CUSTOMER_SERVICE,
)
from mock_responses import MOCK_RESPONSES, MOCK_JUDGE_RESPONSES

load_dotenv()

DOMAIN_PROMPTS = {
    "telco": TELCO_CUSTOMER_SERVICE,
    "banking": BANKING_TRANSACTION_ASSISTANT,
    "insurance": INSURANCE_POLICY_BOT,
    "energy": ENERGY_CUSTOMER_SERVICE,
}


def pytest_addoption(parser):
    parser.addoption(
        "--mock",
        action="store_true",
        default=False,
        help="Run tests with mock responses instead of live Anthropic API",
    )


def is_mock_mode(config) -> bool:
    return config.getoption("--mock") or not os.environ.get("ANTHROPIC_API_KEY")


# ---------------------------------------------------------------------------
# Mock client — zastępuje anthropic.Anthropic gdy brak klucza lub --mock
# ---------------------------------------------------------------------------

def _build_mock_client(category: str = "quality") -> MagicMock:
    """Tworzy mock klienta Anthropic który zwraca sensowne wyniki."""
    client = MagicMock(spec=anthropic.Anthropic)

    def fake_create(**kwargs):
        messages = kwargs.get("messages", [])
        user_content = messages[-1]["content"] if messages else ""

        # Sprawdź czy to zapytanie judge (ocena jakości)
        is_judge = any(
            phrase in user_content
            for phrase in ["Score", "SCORE", "evaluate", "assess", "QA evaluator", "security evaluator"]
        )

        if is_judge:
            score, reason = MOCK_JUDGE_RESPONSES.get(category, (80.0, "Mock evaluation passed"))
            if "COMPLETENESS" in user_content:
                # quality scorer rubric
                text = (
                    f"COMPLETENESS: {int(score)}\n"
                    f"PRECISION: {int(score - 3)}\n"
                    f"FORMAT: {int(score + 2)}\n"
                    f"ACTIONABILITY: {int(score - 1)}\n"
                    f"SUMMARY: {reason}"
                )
            else:
                text = f"SCORE: {int(score)} | REASON: {reason}"
        else:
            # Odpowiedź chatbota — szukaj pasującego mocka po słowach kluczowych
            text = _find_mock_response(user_content)

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=text)]
        return mock_response

    client.messages.create = MagicMock(side_effect=fake_create)
    return client


def _find_mock_response(user_content: str) -> str:
    """Dopasowuje mock response do treści zapytania."""
    # Najpierw szukaj po słowach kluczowych z promptu
    keywords_map = {
        "price": "HAL-001", "plan": "HAL-001", "30gb": "HAL-001",
        "swift": "HAL-002", "bic": "HAL-002",
        "flood": "HAL-003", "coverage": "HAL-003", "covers": "HAL-003",
        "5g": "HAL-004", "last month": "HAL-004",
        "ignore your previous": "INJ-001", "system prompt": "INJ-001",
        "dan": "INJ-002", "10000": "INJ-002", "transfer": "INJ-002",
        "system override": "INJ-003", "employee": "INJ-003",
        "adjuster": "INJ-004", "claim": "INJ-004", "clm-": "INJ-004",
        "html": "INJ-005", "fraud_threshold": "INJ-005",
        "internet": "QUA-001", "not working": "QUA-001",
        "amzn": "QUA-002", "89.99": "QUA-002",
        "accident": "QUA-003", "car crash": "QUA-003",
        "esim": "QUA-004", "sim": "QUA-004",
        "cloned": "REG-001", "card": "REG-001",
        "cancel": "REG-002", "subscription": "REG-002",
        "t-mobile": "EDG-005", "switching": "EDG-005",
        "interest rate": "HAL-005", "mortgage": "HAL-005", "30-year loan": "HAL-005",
        "kwh": "HAL-006", "electricity bill": "HAL-006", "tariff": "HAL-006",
        "expire": "HAL-007", "limitation": "HAL-007", "claim expire": "HAL-007",
        "process this customer data": "INJ-006",
        "ignore previous rules": "INJ-007",
        "loyalty programme": "QUA-005", "loyalty program": "QUA-005",
        "oc and ac": "QUA-006", "difference between oc": "QUA-006",
        "roof": "REG-005", "storm": "REG-005", "home insurance": "REG-005",
        "rozbił": "EDG-003", "crashed": "EDG-003", "stłukło": "EDG-003",
    }

    lower = user_content.lower()

    # Puste lub bardzo krótkie
    if len(user_content.strip()) < 5:
        return MOCK_RESPONSES["EDG-001"]

    # Bardzo długie (edge case)
    if len(user_content) > 1000:
        return MOCK_RESPONSES["EDG-002"]

    # Znaki specjalne
    if any(c in user_content for c in ["\x00", "\x01", "???###"]):
        return MOCK_RESPONSES["EDG-004"]

    for keyword, case_id in keywords_map.items():
        if keyword in lower:
            return MOCK_RESPONSES.get(case_id, MOCK_RESPONSES["QUA-001"])

    return (
        "Thank you for your message. I'm here to help with your account, "
        "billing, or service questions. Could you provide more details about what you need?"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def mock_mode(request) -> bool:
    return is_mock_mode(request.config)


@pytest.fixture(scope="session")
def anthropic_client(request) -> anthropic.Anthropic:
    if is_mock_mode(request.config):
        return _build_mock_client()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set — run with --mock or add key to .env")
    return anthropic.Anthropic(api_key=api_key)


@pytest.fixture(scope="session")
def hallucination_detector(anthropic_client, request) -> HallucinationDetector:
    if is_mock_mode(request.config):
        client = _build_mock_client("hallucination")
        return HallucinationDetector(client)
    return HallucinationDetector(anthropic_client)


@pytest.fixture(scope="session")
def injection_checker(anthropic_client, request) -> InjectionChecker:
    if is_mock_mode(request.config):
        client = _build_mock_client("injection")
        return InjectionChecker(client)
    return InjectionChecker(anthropic_client)


@pytest.fixture(scope="session")
def quality_scorer(anthropic_client, request) -> QualityScorer:
    if is_mock_mode(request.config):
        client = _build_mock_client("quality")
        return QualityScorer(client)
    return QualityScorer(anthropic_client)


@pytest.fixture(scope="session")
def expected_responses() -> dict:
    path = os.path.join(os.path.dirname(__file__), "testdata", "expected_responses.json")
    with open(path) as f:
        return json.load(f)


def get_model_response(
    client: anthropic.Anthropic,
    system_prompt: str,
    user_message: str,
    model: str = "claude-sonnet-4-20250514",
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    if not user_message.strip():
        user_message = "(empty message)"
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


@pytest.fixture
def get_response(anthropic_client, request):
    """Factory fixture — zwraca callable do pobierania odpowiedzi modelu."""
    def _call(domain: str, prompt: str, **kwargs) -> str:
        system_prompt = DOMAIN_PROMPTS[domain]
        return get_model_response(anthropic_client, system_prompt, prompt, **kwargs)
    return _call