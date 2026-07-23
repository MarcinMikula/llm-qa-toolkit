# Architecture decisions

Key architectural and scope decisions for `llm-qa-toolkit`.

This document records decisions that shape the project across multiple files or
future changes. It is intentionally shorter than `LEARNINGS.md`: detailed
reasoning and chronological discovery remain there, while this file captures the
current decision and its consequences.

See also:

- [`../LEARNINGS.md`](../LEARNINGS.md) — chronological reasoning and lessons
- [`gaps.md`](gaps.md) — unresolved validation and evidence gaps
- [`known-limitations.md`](known-limitations.md) — concise current-state boundaries
- [`testing-strategy.md`](testing-strategy.md) — validation levels and claim boundaries
- [`future-ideas.md`](future-ideas.md) — deliberately deferred research directions

---

## Decision summary

| ID | Decision | Status |
|---|---|---|
| AD-01 | Separate test-case data, evaluator logic, and test orchestration | Active |
| AD-02 | Use scoring and thresholds instead of exact-output assertions | Active |
| AD-03 | Combine deterministic heuristics with LLM-assisted evaluation | Active |
| AD-04 | Keep mock mode as an intentional permanent validation layer | Active |
| AD-05 | Treat regression baselines as comparison references, not ground truth | Active |
| AD-06 | Keep project scope as an LLM evaluation toolkit, not a full AI robustness audit platform | Active |
| AD-07 | Validate evaluator behaviour before expanding to multi-provider benchmarking | Active |

---

# AD-01 — Separate test-case data, evaluator logic, and test orchestration

## Decision

Keep the core concerns separated:

```text
prompts/test_cases.py
    → test data, prompts, thresholds, domain/risk assumptions

evaluators/
    → evaluation logic

tests/
    → orchestration and assertions
```

## Why

LLM evaluation scenarios evolve independently from evaluator implementation.

Mixing all three concerns into test files would make it harder to:

- review test cases separately from evaluator code
- reuse evaluator logic
- change thresholds without rewriting tests
- compare evaluator behaviour across scenarios
- reason about whether a failure comes from test data, evaluator logic, or wiring

## Consequence

Adding or changing a test case may still require coordinated updates across test
data, mocks, and tests, but the responsibilities remain explicit.

---

# AD-02 — Use scoring and thresholds instead of exact-output assertions

## Decision

Do not treat LLM responses like deterministic API responses.

Avoid:

```python
assert response == expected_response
```

Use:

- multidimensional scoring
- heuristics
- thresholds
- explicit forbidden behaviour
- regression tolerances

where appropriate.

## Why

LLM outputs are non-deterministic and semantically variable.

Two acceptable answers may differ substantially in wording while expressing the
same useful behaviour.

## Consequence

The toolkit uses composite scores and category-specific thresholds.

However:

> Current thresholds and weights are design assumptions, not yet empirically
> calibrated standards.

See `gaps.md` G-04.

Scoring flexibility must not be interpreted as evidence that every weighted
formula is already validated.

---

# AD-03 — Combine deterministic heuristics with LLM-assisted evaluation

## Decision

Use layered evaluation rather than relying on a single mechanism.

Current patterns include:

```text
deterministic keyword / regex checks
        +
LLM-as-judge reasoning
        +
composite scoring / threshold logic
```

## Why

Deterministic checks are strong for narrow, explicit conditions such as:

- forbidden identifiers
- known attack-compliance phrases
- required uncertainty signals

LLM-assisted evaluation is useful for dimensions that require semantic judgement,
such as:

- completeness
- nuanced refusal behaviour
- contextual quality
- unsupported certainty

Neither mechanism is universally sufficient alone.

## Consequence

The evaluator architecture intentionally mixes deterministic and probabilistic
signals.

This does **not** mean the LLM judge is treated as a source of truth.

Its judgement remains dependent on:

- rubric quality
- available evidence
- domain context
- prompt design
- model behaviour

Evaluator validation remains a separate requirement.

---

# AD-04 — Mock mode remains intentional

## Decision

Keep mock mode as a permanent validation layer.

Mock mode is not temporary scaffolding to be removed once live API access exists.

Its purpose is:

```text
cheap
deterministic
fast
reproducible
CI-friendly
```

pipeline feedback.

## Why

Live LLM calls are:

- non-deterministic
- slower
- cost-bearing
- provider-dependent
- vulnerable to model/version drift
- harder to debug reproducibly

A deterministic layer is necessary for software-level feedback on every change.

Mock mode provides evidence that:

- test routing works
- evaluator paths execute
- scoring integration works
- deterministic expectations remain stable
- CI and reporting remain functional

## Claim boundary

Mock mode does **not** prove:

```text
evaluator accuracy
real-model behaviour
production robustness
formal audit assurance
```

The architectural decision is therefore:

> Keep mock mode, but explicitly limit the claims made from it.

This is consistent with the validation model in `testing-strategy.md`:

```text
Unit / deterministic tests
        ↓
Mock pipeline tests
        ↓
Evaluator validation
        ↓
Controlled live-model validation
        ↓
Regression evaluation
```

A later live-validation layer complements mock mode.

It does not replace it.

---

# AD-05 — Regression baselines are comparison references, not ground truth

## Decision

Use baselines to detect degradation, not to define correctness.

Conceptually:

```text
baseline
    ↓
current comparable run
    ↓
difference
    ↓
investigation if outside tolerance
```

## Why

A model can regress relative to a previously accepted state even when exact output
reproduction is impossible.

However, matching a baseline does not prove that the baseline itself was correct.

## Consequence

The current regression approach uses scores and acceptable deltas.

Future maturity requires stronger provenance for baselines, including relevant
context such as:

- model/provider
- prompt version
- judge/evaluator version
- run date
- mock/live mode
- number of runs
- approval basis

See `gaps.md` G-05.

---

# AD-06 — Scope remains an LLM evaluation toolkit, not a full AI robustness audit platform

## Decision

Keep the project scoped as an **LLM evaluation toolkit and experimental
evaluation framework**.

Do not expand it into a complete enterprise AI robustness auditing platform.

## Context

A recent review against broader AI robustness auditing meta-requirements surfaced
valuable concerns around:

- governance
- stakeholder involvement
- audit access
- auditor independence
- MLOps integration
- monitoring
- evidence provenance
- human participation
- documentation
- scalability
- domain adaptability

These ideas are useful for evaluating the quality and limits of this project.

They are **not automatically project requirements**.

## Explicit non-scope

The project is not currently intended to become an integrated platform for:

```text
enterprise governance
MLOps orchestration
auditor independence workflows
legal/compliance workflow management
real-time production monitoring
organization-wide dashboards
enterprise risk management
formal audit certification
```

Some individual concepts from those areas may still influence design.

Examples:

- evidence provenance
- human review
- gradability
- domain-expert escalation
- traceable baselines

But influence does not imply full platform scope.

## Why

Trying to implement every robustness meta-requirement would:

- destroy the project's vertical focus
- create large amounts of infrastructure unrelated to the core research question
- make validation harder, not easier
- encourage breadth before evidence
- blur the difference between evaluation tooling and organizational governance

The current priority is to understand whether the existing evaluation approach
can be trusted within a defined scope.

## Consequence

Meta-requirements are treated as:

> **a source of design questions and quality criteria, not a backlog.**

The project keeps the right to resolve an identified gap through:

- validation
- documentation
- narrower scope
- explicit limitation
- design change
- or deliberate deferral

Not every gap becomes a feature.

---

# AD-07 — Validate evaluator behaviour before expanding provider breadth

## Decision

Evaluator validation comes before multi-provider / multi-judge benchmarking.

The order is:

```text
FIRST
Does the evaluator work for its intended scope?

THEN
How does Claude compare with GPT, Gemini, Ollama, or an ensemble?
```

## Why

Provider agreement is not ground truth.

For example:

```text
Claude agrees with GPT
GPT agrees with Gemini
```

does not establish correctness if all three are using the same weak evidence,
rubric, or unsupported assumption.

Before provider comparison has real meaning, the project needs an external basis
for evaluating evaluator quality.

Possible evidence includes:

- human-labelled known-good cases
- human-labelled known-bad cases
- borderline cases
- ambiguous cases
- insufficient-evidence cases
- deterministic reference outcomes where available

## Consequence

Multi-provider support remains a valid future direction.

It is deliberately sequenced after evaluator validation rather than treated as
the next proof of maturity.

See `future-ideas.md`.

---

# Current architectural principle — validation before expansion

The project currently prioritizes:

```text
validate existing evaluator behaviour
        ↓
understand evidence/test-basis requirements
        ↓
review thresholds and decision boundaries
        ↓
perform controlled live validation
        ↓
only then expand providers, models, and evaluation breadth
```

This protects the project from a common failure mode:

```text
more features
more dashboards
more providers
more scores

without stronger evidence
```

The architecture should optimize for trustworthy learning, not feature count.

---

# Decision boundary: evidence-grounded judge authority is not yet architecture

Ideas such as:

```text
PASS
FAIL
REVIEW
UNGRADABLE

gradability checks
evidence authority
domain-expert escalation
human-review requirements
```

are intentionally documented in `future-ideas.md`.

They are promising research directions, but they are **not yet committed
architecture for v1.0**.

This distinction matters.

An idea moves from future direction to architecture only after:

- its problem is sufficiently understood
- its scope is clear
- its value can be tested
- implementation cost is justified
- it does not expand the project beyond its intended role

---

# What these decisions do not claim

These decisions define how the toolkit is structured and scoped.

They do not claim that the project has already demonstrated:

- validated evaluator accuracy
- production-grade LLM robustness
- formal audit assurance
- universal threshold validity
- authoritative domain correctness

Those remain validation questions.

The project's testing principle applies here as well:

> **Never make a stronger claim than the validation level can support.**
