# Gaps — current validation and evidence gaps

This file tracks known gaps in the current `llm-qa-toolkit` prototype.

The purpose is not to turn every gap into an immediate implementation task.
Some gaps may be resolved through validation, documentation, tighter scope, or
an explicit design decision rather than new code.

The current foundation demonstrates a runnable evaluation pipeline, deterministic
mock execution, scoring logic, regression concepts, CI, and reporting. The gaps
below describe what is still missing before stronger claims can be made about
evaluator reliability or robustness assurance.

---

## Status legend

- **OPEN** — known gap, not yet resolved
- **PARTIAL** — some supporting mechanism exists, but the gap is not closed
- **DEFERRED** — intentionally outside the current implementation scope
- **RESOLVED** — decision or validation completed and documented

---

## Gap summary

| ID | Gap | Status | Why it matters |
|---|---|---|---|
| G-01 | Evaluator validation | OPEN | A working evaluator pipeline does not prove that evaluator verdicts are accurate |
| G-02 | Evidence / test-basis model | OPEN | A judge cannot reliably assess claims without sufficient trusted context |
| G-03 | Judge authority / gradability | OPEN | The system currently assumes that every case can be scored |
| G-04 | Threshold calibration | OPEN | Current thresholds are design assumptions, not empirically validated decision boundaries |
| G-05 | Baseline provenance | OPEN | Regression scores are difficult to interpret without full execution context |
| G-06 | Evaluation error semantics | OPEN | Technical evaluator failure must not be confused with medium-quality model behaviour |
| G-07 | Controlled live validation | OPEN | Mock consistency does not demonstrate evaluator effectiveness on real model outputs |

---

## G-01 — Evaluator validation

**Status: OPEN**

The current test suite verifies that evaluators execute, return structured results,
and behave consistently against predefined mock responses.

That does not yet demonstrate that the evaluators correctly distinguish between
good, bad, borderline, ambiguous, or insufficiently supported answers.

There is currently no human-labelled calibration or validation dataset against
which evaluator behaviour has been measured.

Missing evidence includes:

- false-positive rate
- false-negative rate
- agreement with human reviewers
- behaviour on borderline cases
- behaviour on ambiguous cases
- behaviour when available evidence is insufficient
- consistency across repeated evaluations

Until this gap is closed, the toolkit can demonstrate evaluation mechanics and
pipeline consistency, but not independently validated evaluator accuracy.

**Important distinction:**

```text
green mock suite
    != validated evaluator
    != validated model behaviour
    != demonstrated robustness
```

Possible future resolution paths include a small human-labelled validation set,
expert-reviewed domain cases, inter-rater comparison, or another deliberately
scoped calibration approach.

No specific implementation is committed yet.

---

## G-02 — Evidence / test-basis model

**Status: OPEN**

Current test cases define prompts, expected or forbidden behaviour, risk-oriented
thresholds, and evaluator logic.

They do not yet provide a formal model for the evidence required to support a
domain-specific verdict.

Depending on the claim being evaluated, a reliable test basis may require:

- trusted reference evidence
- source provenance
- applicable document, policy, or tariff version
- effective date or validity period
- business rules
- calculation inputs
- reference algorithm or deterministic oracle
- domain-specific context
- judge-only evaluation context
- intentionally missing information
- gradability prerequisites

This matters because a judge may be capable of reasoning well and still produce
an unreliable verdict when the underlying evidence is incomplete, outdated,
inapplicable, biased, or unavailable.

For example, deciding whether an insurance premium is correct may require customer
data, vehicle parameters, discounts, surcharges, tariff rules, and the applicable
calculation logic. A prompt and candidate response alone are not sufficient test
basis for that claim.

The unresolved design question is therefore not only:

> How should the judge score this response?

but first:

> What evidence must exist before this response can be judged reliably?

This gap should be addressed before the toolkit makes strong factual-correctness
or domain-authority claims.

---

## G-03 — Judge authority / gradability

**Status: OPEN**

The current evaluation flow generally assumes that an evaluator can produce a
score for every response it receives.

That assumption is too strong.

Some cases may be:

- objectively gradable
- gradable only with additional evidence
- dependent on domain expertise
- ambiguous by design
- outside the evaluator's competence
- impossible to grade reliably with the available information

The current verdict model does not formally distinguish states such as:

```text
PASS
FAIL
REVIEW
UNGRADABLE
INSUFFICIENT_EVIDENCE
ERROR
```

As a result, the system has no explicit way to say:

> I should not issue a substantive verdict for this case.

A future design may need a gradability or authority check before substantive
scoring.

Possible questions include:

```text
Do we have sufficient evidence?
Is the evidence current and applicable?
Does this decision require domain expertise?
Is the rubric precise enough?
Can the claim be objectively evaluated?
```

This is an open design direction, not yet a committed v1.0 feature.

---

## G-04 — Threshold calibration

**Status: OPEN**

Current `min_score` thresholds and score weights are manually selected design
assumptions.

They reflect intended relative risk between categories such as BLOCKER,
CRITICAL, NORMAL, and EDGE, but they have not yet been empirically calibrated
against human-labelled outcomes or another validated reference.

Open questions include:

- Why is a specific threshold 70 rather than 65 or 80?
- Does the threshold produce acceptable false-positive and false-negative rates?
- Should thresholds differ by domain, evaluator, or risk class?
- Can a composite score hide a critical failure?
- Should some conditions act as hard gates rather than weighted score inputs?

A score threshold should eventually have a documented rationale tied to the
decision it is intended to support.

Until calibration exists, current thresholds should be treated as project-level
design assumptions, not universal robustness standards.

---

## G-05 — Baseline provenance

**Status: OPEN**

Regression tests currently use baseline scores and acceptable deltas to detect
degradation.

The concept is useful, but a baseline number alone is not enough to explain what
the baseline actually represents.

A trustworthy baseline may need provenance such as:

```text
model version
model/provider configuration
system prompt version
user prompt or test-case version
judge model/version
evaluator version
temperature and relevant sampling settings
execution date
number of runs
mock or live execution mode
aggregation method
approval or acceptance basis
```

Without this context, a value such as:

```text
baseline_score = 85
```

cannot fully answer:

> 85 under which conditions, produced by what system, and approved on what basis?

This gap becomes especially important when comparing model versions, evaluator
versions, prompts, or results collected at different points in time.

---

## G-06 — Evaluation error semantics

**Status: PARTIALLY CLOSED**

Technical failure of an evaluator is not the same thing as a medium-quality model
response.

Examples of evaluator-side failure include:

- judge API failure
- malformed judge output
- parser failure
- missing expected fields
- timeout
- incompatible response format

The current implementation contains fallback behaviour that may convert some
evaluation failures into neutral-looking numeric values.

This risks collapsing two fundamentally different meanings:

```text
evaluation failed
```

and:

```text
candidate response received a medium score
```

These states should not be semantically equivalent.

A future result model should clearly separate:

```text
evaluation_status
```

from:

```text
quality_or_risk_verdict
```

For example:

```text
evaluation_status = ERROR
verdict = NOT_AVAILABLE
```

rather than inventing a substantive score when evaluation did not complete
reliably.

This is both a technical correctness gap and a reporting/traceability gap.

The assessment-grounded runtime now separates:

```text
request / adapter / parser ERROR
from
accepted substantive finding
```

`StructuredEvaluatorResultParser` preserves raw output and returns a technical
error with no findings when strict parsing fails. `EvaluationResultValidator`
continues to distinguish malformed output from well-formed evaluator overreach.

The gap remains open for the legacy score-based evaluator path until its fallback
semantics are reviewed and migrated or explicitly retained.

---

## G-07 — Controlled live validation

**Status: OPEN**

The toolkit supports live-provider execution, but no controlled validation
experiment has yet demonstrated evaluator effectiveness on a deliberately
designed set of real model responses.

Mock mode is intentionally retained because it provides:

- deterministic execution
- zero-cost CI feedback
- pipeline integration checks
- reproducible evaluator-path testing

However, mock mode cannot establish whether the evaluators perform reliably on
real, non-deterministic, previously unseen model outputs.

A meaningful live validation stage should eventually answer questions such as:

- Do evaluator results align with human-labelled expectations?
- How stable are judge verdicts across repeated runs?
- Which failure modes appear only with real model outputs?
- How sensitive are scores to model, prompt, judge, or temperature changes?
- Do current thresholds still make sense outside predefined mocks?
- Are borderline and ambiguous answers handled safely?

The goal does not need to be a large or expensive benchmark.

A small, controlled, well-documented validation experiment may provide more
useful evidence than broad but weak coverage.

---

## Cross-cutting gap — claim boundaries

The gaps above share one common principle:

> The strength of a project claim must not exceed the strength of the evidence
> supporting it.

The current toolkit can credibly claim that it demonstrates:

- a runnable LLM evaluation pipeline
- risk-oriented test-case design
- heuristic and LLM-assisted evaluation patterns
- deterministic mock execution
- scoring and regression concepts
- CI and reporting integration

It should not yet claim that it has demonstrated:

- validated evaluator accuracy
- production-grade robustness assurance
- universal threshold validity
- authoritative domain correctness
- complete AI robustness auditing

Closing a gap may require code, empirical validation, documentation, tighter
scope, or an explicit limitation.

Not every gap should automatically become a feature.

---

## Current priority

The next conceptual priority is **validation before expansion**.

Before adding broader categories such as toxicity, bias, RAG faithfulness,
agents, or multi-model benchmarking, the toolkit should first establish how much
trust can reasonably be placed in its existing evaluators and verdicts.

The immediate questions are:

1. What does each current test level actually prove?
2. How should evaluator effectiveness be validated?
3. What evidence is required for different kinds of verdicts?
4. When should the system refuse to issue an automated verdict?
5. How should thresholds and baselines be justified and traced?

These questions define the current validation gap. They do not yet define the
final implementation.
