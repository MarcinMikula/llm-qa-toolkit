# LLM QA Toolkit — Testing Strategy

This is the test strategy for **LLM QA Toolkit itself** — the evaluation
framework as a product — not for any particular chatbot or LLM. The
toolkit's purpose is to assess the reliability, safety and quality of
production LLM systems, so this document describes how the toolkit's own
correctness and credibility are validated.

This is a **living document**: each section describes both the intended
strategy and the current implementation state, with architectural
reasoning documented separately in `LEARNINGS.md` and
`docs/architecture-decisions.md`.

## Why this document exists

Most LLM evaluation projects stop at "the evaluator runs and produces a
score." This document exists to show a different approach: the
evaluation framework itself should be treated as production software,
with multiple validation layers ensuring that scoring logic,
integration, and real-model behaviour remain trustworthy as the project
evolves.

---

## 1. Evaluator validation

**Scope:** deterministic scoring logic that can be validated without
calling an external LLM.

This layer focuses on validating the behaviour of the evaluators
themselves rather than the quality of any specific language model.

Typical responsibilities include:

- composite score calculations
- keyword detection
- regex-based heuristics
- penalty and bonus application
- threshold validation
- typed result models

**Plan:** every evaluator should be deterministic when given identical
input. The same response should always produce the same score and
verdict.

**Current state:** HallucinationDetector, InjectionChecker and
QualityScorer are covered through deterministic pytest tests and mock
responses.

**Known gap:** LLM-as-judge behaviour itself cannot be unit tested,
since judge quality depends on an external model whose behaviour may
change over time.

---

## 2. Pipeline integration

**Scope:** verifies that the complete evaluation pipeline works
correctly once individual components are connected together.

Rather than validating scoring algorithms in isolation, this layer
ensures that prompts, providers, fixtures, evaluators and reports
exchange data correctly.

Typical flow:

Prompt

↓

Provider (live or mock)

↓

Evaluator

↓

Composite score

↓

pytest assertion

↓

Allure report

**Current state:** fully operational in both mock mode and live API
mode.

Mock mode validates evaluator behaviour without external dependencies.

Live mode validates the complete integration with Anthropic's API.

**Known gap:** currently only Anthropic is supported as a live provider.
Cross-provider consistency testing is planned for future versions.

---

## 3. Live model evaluation

**Scope:** validates real LLM behaviour rather than evaluator logic.

Unlike deterministic mock runs, this layer measures whether production
models actually satisfy the quality and safety expectations encoded in
the evaluation suite.

Typical scenarios include:

- hallucination resistance
- prompt injection resistance
- response quality
- regression against previous baselines

**Current state:** supported through live Anthropic API execution.

Mock mode remains the default for CI to provide deterministic results,
while live runs are intended for manual execution and scheduled
regression checks.

**Known gap:** live evaluations currently execute against a single model.
Future versions will compare multiple providers using the same dataset.

---

## 4. Regression benchmark

**Scope:** verifies that model quality does not degrade over time.

Unlike traditional regression testing, the objective is not exact output
reproduction but maintaining acceptable quality relative to historical
baselines.

Evaluation focuses on:

- baseline preservation
- acceptable score deltas
- stability across model updates
- consistency between repeated executions

**Current state:** baseline regression tests are implemented for
selected scenarios using tolerance bands.

**Future direction:** evolve this layer into a complete benchmark system
supporting historical trend analysis, model comparison and prompt
comparison.

---

## 5. Non-functional evaluation

**Scope:** properties of the evaluation framework that are independent
of response correctness.

This includes:

- retry behaviour
- timeout handling
- deterministic mock execution
- API failure recovery
- token usage
- execution cost
- result reproducibility

**Current state:** retry handling, mock mode and timeout protection are
implemented.

**Known gap:** cost-at-scale measurements, concurrent evaluation and
provider failover have not yet been implemented.

---

## Summary table

| Layer | Status | Current evidence |
|---|---|---|
| Evaluator validation | 🟢 Substantial | Deterministic evaluator tests |
| Pipeline integration | 🟢 Implemented | Mock mode + live Anthropic execution |
| Live model evaluation | 🟡 Available | Manual live API execution |
| Regression benchmark | 🟡 Foundation complete | Baseline regression tests |
| Non-functional evaluation | 🟡 Partial | Retry, timeout and deterministic mock mode |

## Where to read more

- `LEARNINGS.md` — implementation lessons discovered while building the toolkit
- `docs/architecture-decisions.md` — rationale behind major design decisions
- `docs/known-limitations.md` — current boundaries of the framework
- `docs/gaps.md` — architectural improvements planned for future versions
- `docs/future-ideas.md` — longer-term evolution beyond the current roadmap