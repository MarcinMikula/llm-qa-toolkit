"""
Response Quality Scorer
=======================
Multi-dimensional quality evaluation of LLM responses.

Dimensions (each 0-100, then weighted composite):
- Completeness  (30%): Are all relevant aspects of the question addressed?
- Precision     (25%): Is the response accurate and specific vs vague?
- Format        (20%): Is the response well-structured, readable, appropriately long?
- Actionability (25%): Does the user know what to do next?

For domain chatbots, actionability is critical — a user hitting a support bot
needs to know their next step, not just get an explanation.
"""

import anthropic
from dataclasses import dataclass


@dataclass
class QualityScore:
    completeness: float
    precision: float
    format_score: float
    actionability: float
    composite: float          # weighted average
    explanation: str
    passed: bool


SCORING_RUBRIC = """
You are a QA evaluator scoring a customer service chatbot response.

Domain: {domain}
User question: {prompt}
Chatbot response:
---
{response}
---

Score each dimension from 0 to 100:

COMPLETENESS (0-100):
- 100: All aspects of the question are addressed
- 50: Main question answered but secondary aspects ignored
- 0: Question not addressed at all

PRECISION (0-100):
- 100: Specific, accurate information; no vagueness
- 50: Mostly accurate but some vague or generic statements
- 0: Completely vague or inaccurate

FORMAT (0-100):
- 100: Well-structured, appropriate length, easy to scan, good use of lists where helpful
- 50: Readable but could be better structured or is poorly sized for the question
- 0: Wall of text, confusing structure, or one-word response to a complex question

ACTIONABILITY (0-100):
- 100: User knows exactly what to do next; clear next steps
- 50: Some guidance given but incomplete
- 0: No actionable guidance provided

Expected keywords that should appear: {expected_keywords}

Reply with ONLY this format:
COMPLETENESS: <score>
PRECISION: <score>
FORMAT: <score>
ACTIONABILITY: <score>
SUMMARY: <one sentence>
"""


class QualityScorer:
    WEIGHTS = {
        "completeness": 0.30,
        "precision": 0.25,
        "format": 0.20,
        "actionability": 0.25,
    }

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def _keyword_bonus(self, response: str, expected: list[str]) -> float:
        """Small bonus for responses hitting expected keywords."""
        if not expected:
            return 0.0
        lower = response.lower()
        hit_rate = sum(1 for kw in expected if kw.lower() in lower) / len(expected)
        return hit_rate * 10  # max +10 points bonus

    def evaluate(
        self,
        prompt: str,
        response: str,
        domain: str,
        expected_keywords: list[str],
        min_score: float = 70.0,
    ) -> QualityScore:
        judge_prompt = SCORING_RUBRIC.format(
            domain=domain,
            prompt=prompt,
            response=response,
            expected_keywords=", ".join(expected_keywords) if expected_keywords else "none specified",
        )

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": judge_prompt}],
        )
        raw = message.content[0].text.strip()

        scores: dict[str, float] = {}
        summary = ""
        for line in raw.splitlines():
            for key in ("COMPLETENESS", "PRECISION", "FORMAT", "ACTIONABILITY"):
                if line.startswith(key + ":"):
                    try:
                        scores[key.lower()] = float(line.split(":")[1].strip())
                    except ValueError:
                        scores[key.lower()] = 50.0
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()

        completeness = scores.get("completeness", 50.0)
        precision = scores.get("precision", 50.0)
        fmt = scores.get("format", 50.0)
        actionability = scores.get("actionability", 50.0)

        composite = (
            completeness * self.WEIGHTS["completeness"]
            + precision * self.WEIGHTS["precision"]
            + fmt * self.WEIGHTS["format"]
            + actionability * self.WEIGHTS["actionability"]
        ) + self._keyword_bonus(response, expected_keywords)

        composite = min(100.0, round(composite, 1))

        return QualityScore(
            completeness=completeness,
            precision=precision,
            format_score=fmt,
            actionability=actionability,
            composite=composite,
            explanation=summary,
            passed=composite >= min_score,
        )
