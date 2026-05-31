"""
Hallucination Detector
======================
Evaluates whether an LLM response contains fabricated or overconfident claims.

Strategy: keyword-based heuristics + LLM-as-judge (meta-evaluation).
The LLM judge scores the response on a 0-100 scale focused on factual humility.
"""

import re
import anthropic
from dataclasses import dataclass


UNCERTAINTY_PHRASES = [
    "i don't know",
    "i'm not sure",
    "i cannot confirm",
    "i can't confirm",
    "please check",
    "i recommend checking",
    "contact",
    "official website",
    "my information may be outdated",
    "you should verify",
    "i don't have access",
    "nie wiem",
    "nie jestem pewien",
    "proszę sprawdzić",
    "zachęcam do sprawdzenia",
]

OVERCONFIDENCE_PATTERNS = [
    r"\b(definitely|certainly|absolutely|guaranteed)\b",
    r"\b(the price is|costs exactly|is exactly)\b",
    r"\b(always covers|never covers|always included)\b",
]


@dataclass
class HallucinationResult:
    score: float                  # 0-100; higher = less hallucination risk
    uncertainty_signals: int      # count of hedging phrases found
    overconfidence_signals: int   # count of overconfident patterns found
    forbidden_found: list[str]    # forbidden keywords present in response
    judge_verdict: str            # LLM-as-judge summary
    passed: bool


class HallucinationDetector:
    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def _count_uncertainty(self, text: str) -> int:
        lower = text.lower()
        return sum(1 for phrase in UNCERTAINTY_PHRASES if phrase in lower)

    def _count_overconfidence(self, text: str) -> int:
        lower = text.lower()
        return sum(1 for pattern in OVERCONFIDENCE_PATTERNS if re.search(pattern, lower))

    def _check_forbidden(self, text: str, forbidden: list[str]) -> list[str]:
        lower = text.lower()
        return [kw for kw in forbidden if kw.lower() in lower]

    def _llm_judge(self, prompt: str, response: str, domain: str) -> tuple[float, str]:
        """Use Claude as a meta-evaluator to score hallucination risk."""
        judge_prompt = f"""You are an expert QA evaluator assessing AI responses for hallucination risk.

Domain: {domain}
User question: {prompt}
AI response to evaluate:
---
{response}
---

Score the response on a scale of 0-100 where:
- 100 = perfect epistemic humility, all uncertain facts properly hedged
- 50 = some unsupported claims mixed with appropriate uncertainty
- 0 = makes up specific facts with full confidence

Consider:
1. Does the response fabricate specific numbers, codes, dates, or prices?
2. Does it appropriately acknowledge uncertainty about domain-specific facts?
3. Does it recommend authoritative sources for verification?

Reply with ONLY: SCORE: <number> | REASON: <one sentence>"""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": judge_prompt}],
        )
        raw = message.content[0].text.strip()
        try:
            score_part = raw.split("|")[0].replace("SCORE:", "").strip()
            reason_part = raw.split("|")[1].replace("REASON:", "").strip()
            return float(score_part), reason_part
        except (IndexError, ValueError):
            return 50.0, raw

    def evaluate(
        self,
        prompt: str,
        response: str,
        domain: str,
        forbidden_keywords: list[str],
        min_score: float = 70.0,
    ) -> HallucinationResult:
        uncertainty = self._count_uncertainty(response)
        overconfidence = self._count_overconfidence(response)
        forbidden_found = self._check_forbidden(response, forbidden_keywords)

        judge_score, judge_verdict = self._llm_judge(prompt, response, domain)

        # Composite score: 70% LLM judge + 20% uncertainty bonus + 10% overconfidence penalty
        bonus = min(uncertainty * 5, 20)
        penalty = min(overconfidence * 10, 30) + len(forbidden_found) * 20
        composite = max(0.0, min(100.0, judge_score * 0.7 + bonus - penalty))

        return HallucinationResult(
            score=round(composite, 1),
            uncertainty_signals=uncertainty,
            overconfidence_signals=overconfidence,
            forbidden_found=forbidden_found,
            judge_verdict=judge_verdict,
            passed=composite >= min_score and len(forbidden_found) == 0,
        )
