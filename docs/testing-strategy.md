# Testing strategy — validation levels and claim boundaries

This document defines how `llm-qa-toolkit` is tested and, equally important,
**what each test level is allowed to prove**.

The project evaluates probabilistic systems through heuristics, thresholds,
regression baselines, and LLM-assisted judging. A green test suite therefore
means different things depending on which layer was exercised.

The central rule is:

> **Each validation level has explicit claim boundaries.**

A deterministic mock test is useful evidence about pipeline behaviour. It is not
evidence that the evaluator is accurate on unseen model outputs. A successful
live run is evidence about observed behaviour under defined conditions. It is
not automatically evidence of production-grade robustness.

See also:

- [`gaps.md`](gaps.md) — unresolved validation and evidence gaps
- [`known-limitations.md`](known-limitations.md) — concise current-state boundaries
- [`future-ideas.md`](future-ideas.md) — deliberately deferred research directions
- [`conceptual-model.md`](conceptual-model.md) — working conceptual model and high-level requirements
- [`../LEARNINGS.md`](../LEARNINGS.md) — chronological reasoning and lessons learned

---

## 1. Validation model

The project uses five distinct validation levels:

```text
1. Unit / deterministic evaluator tests
   → Does the technical logic work as implemented?

2. Mock pipeline tests
   → Does the integrated pipeline behave consistently and deterministically?

3. Evaluator validation
   → Does the evaluator correctly distinguish known-good, known-bad,
     borderline, and ambiguous cases?

4. Controlled live-model validation
   → How does the system behave on real, non-deterministic model outputs?

5. Regression evaluation
   → Has behaviour degraded relative to a trusted, comparable baseline?
```

These levels are related but not interchangeable.

| Level | Primary question | Can support | Cannot prove |
|---|---|---|---|
| Unit / deterministic | Does isolated logic behave as specified? | code-level correctness for tested inputs | evaluator accuracy |
| Mock pipeline | Does the integrated pipeline behave consistently? | integration and scoring-flow consistency | real model robustness |
| Evaluator validation | Does the evaluator judge known cases correctly? | scoped evidence of evaluator effectiveness | universal correctness |
| Controlled live validation | What happens on real model outputs? | observed behaviour under defined conditions | permanent robustness |
| Regression evaluation | Did behaviour degrade versus baseline? | controlled change detection | correctness if baseline is weak |

The project must not collapse these into:

> "All tests passed, therefore the system is robust."

That conclusion is not supported by the current testing model.

---


# Conceptual evaluation model used by this strategy

The validation levels above sit on top of a richer conceptual model than:

```text
prompt → response → score
```

For regulated-domain evaluation, the working chain is:

```text
evaluation objective / risk
        ↓
test condition / scenario
        ↓
stimulus
        ↓
system under evaluation
        ↓
candidate response
        +
test basis
        ↓
assessment eligibility & scope determination
        ↓
evaluator
        ↓
scoped findings + disposition
```

## Response strategy is part of correctness

A response should not be evaluated only for factual content.

The expected behaviour may be:

```text
ANSWER
CLARIFY
CORRECT_FALSE_PREMISE
REFUSE
REDIRECT
REQUEST_EVIDENCE
APPLY_DEFINED_FALLBACK
ESCALATE
```

Testing should therefore distinguish:

```text
response-strategy correctness
```

from:

```text
execution/content quality
```

This matters because a factually plausible answer may still be wrong if the
system should have clarified, refused, corrected a false premise, or escalated.

## Test Basis model

The working Test Basis model is:

```text
TEST BASIS
│
├── Facts / ground truth
├── Rules / policies / regulations
├── Expected response strategy
├── Behavioural constraints
├── Required evidence
├── Gradability prerequisites
└── Provenance / applicability
```

The Test Basis defines not only what is true, but what behaviour is required,
what evidence is sufficient, and when a verdict is justified.

## Gradability is scoped

Gradability should not be assumed to apply to the entire response uniformly.

Example:

```text
response strategy       → gradable
policy adherence        → gradable
factual claim A         → gradable
factual claim B         → ungradable
final numeric outcome   → ungradable
```

Therefore, validation design should ask:

> **What exactly can be judged reliably for this evaluation objective?**

rather than only:

> "Is the whole response gradable?"

## Evaluation result is layered

The working result model separates:

```text
Evaluation status
Assessment scope
Scoped findings
Evidence / rationale
Disposition / escalation
```

A technical evaluation error must remain separate from substantive findings.

`REVIEW` is conceptually a disposition or escalation decision, not necessarily a
substantive verdict.

See `conceptual-model.md` for the current working model and HLR draft.

---

# 2. Level 1 — Unit / deterministic evaluator tests

## Purpose

Verify isolated technical logic against controlled inputs.

Typical targets:

- keyword and forbidden-phrase detection
- uncertainty signals
- regex matching
- score composition
- threshold comparison
- parsing judge output
- error/fallback paths
- result model construction
- mock-response routing

Examples:

```text
known uncertainty phrase
    → expected uncertainty signal

forbidden identifier
    → expected penalty

known dimension scores + weights
    → expected composite score

valid judge JSON
    → expected structured result
```

## Claim boundary

A passing unit test supports:

> The implementation behaves as specified for these tested inputs.

It does not support:

> The evaluator is accurate on real, unseen LLM responses.

Unit tests usually encode expectations defined by the same project that
implemented the evaluator. They verify consistency with the specification, not
independent validity of that specification.

## Current status

**Implemented as part of the current prototype.**

Known issue: some evaluator failures may still fall back to neutral-looking
numeric values instead of a distinct execution-error state.

See `gaps.md` G-06.

---

# 3. Level 2 — Mock pipeline tests

## Purpose

Verify the full technical pipeline without relying on paid or non-deterministic
live model calls.

```text
test case
    ↓
predefined mock response
    ↓
evaluator / judge mock
    ↓
score and signals
    ↓
threshold decision
    ↓
pytest result
    ↓
Allure / CI reporting
```

The primary question is:

> **Does the whole pipeline behave consistently and reproducibly?**

## Why mock mode is intentional

Mock mode is not merely a workaround for missing API keys.

It provides:

- deterministic CI
- zero-cost execution
- fast feedback
- reproducible failures
- stable evaluator-path testing
- validation of integration and reporting flow

The current project documents 30 domain-oriented scenarios across hallucination,
prompt injection, response quality, regression, and edge cases.

## Claim boundary

A green mock suite supports:

> The pipeline is internally consistent for the predefined scenarios.

It does not support:

```text
validated evaluator accuracy
validated real-model behaviour
production robustness
formal audit assurance
```

The critical rule is:

> **Mock pipeline validation must never be presented as live-model validation.**

Mock responses are known in advance. Passing them does not establish that the
evaluator will reliably handle unseen real-world outputs.

## Current status

**Implemented and used as the default deterministic CI path.**

This layer should remain even after live validation is added.

---

# 4. Level 3 — Evaluator validation

## Purpose

Validate whether the evaluators actually distinguish response classes in the way
the project claims.

This is the first level that directly asks:

> **Does the evaluator work as an evaluator, not merely as code?**

## Validation set

A deliberately small, reviewed validation set should include:

```text
KNOWN_GOOD
KNOWN_BAD
BORDERLINE
AMBIGUOUS
INSUFFICIENT_EVIDENCE
```

Labels must not be generated solely by the evaluator being tested.

Possible label sources:

- human review
- domain-expert review where required
- deterministic ground truth
- trusted reference material
- explicit business rules
- multi-reviewer agreement with adjudication where needed

Quality of labels matters more than raw dataset size.

## What to measure

Depending on evaluator type:

- false-positive rate
- false-negative rate
- human/evaluator agreement
- disagreement patterns
- repeatability across judge runs
- sensitivity to judge prompt changes
- borderline-case behaviour
- insufficient-evidence behaviour

Possible outputs:

```text
confusion matrix
agreement rate
false-positive rate
false-negative rate
per-risk-category breakdown
review of systematic disagreements
```

## Test basis requirement

Evaluator validation must include the evidence required to support the verdict.

Depending on the case, this may include:

- trusted reference evidence
- source provenance
- applicable policy/document version
- effective date
- business rules
- calculation inputs
- reference algorithm
- domain context
- judge-only context
- intentionally missing information
- explicit expected behaviour
- critical forbidden behaviour
- gradability prerequisites

A prompt and candidate answer alone are not always a sufficient test basis.

## Claim boundary

Successful evaluator validation supports a scoped statement such as:

> Within this labelled dataset and defined evaluation scope, the evaluator
> achieved the measured level of performance.

It does not prove universal accuracy across all domains, models, prompts, and
future cases.

## Current status

**Not yet completed.**

Current gaps:

- no human-labelled calibration dataset
- no established false-positive/false-negative rates
- no measured human agreement
- no formal borderline-case validation
- no formal insufficient-evidence handling

See `gaps.md` G-01 to G-04.

---

# 5. Level 4 — Controlled live-model validation

## Purpose

Exercise the toolkit against real, non-deterministic model outputs under
controlled and documented conditions.

The key question is:

> **What happens when real models produce responses the test author did not
> predefine?**

## Principles

Live validation should be:

- deliberately scoped
- cost-aware
- documented
- versioned
- repeated enough to expose relevant variability
- compared with trusted expectations where applicable

It does not need to start as a large benchmark.

A small, well-designed experiment is preferable to hundreds of weakly reviewed
calls.

## Suggested first experiment

Use a compact set containing:

```text
known-good
known-bad
borderline
ambiguous
insufficient-evidence
```

For each case:

```text
1. generate or collect a real model response
2. preserve response and execution metadata
3. evaluate it with current evaluators
4. compare verdict with trusted/human expectation
5. repeat selected cases to observe variability
6. document disagreements and evaluator failure modes
```

Possible comparison:

```text
human expectation
    vs
heuristic evaluator
    vs
LLM judge
    vs
combined toolkit result
```

## Metadata

A controlled live run should preserve enough context to interpret the result:

```text
provider
model / model identifier
temperature
system prompt version
test-case version
judge model/version
judge prompt version
evaluator version
timestamp
run count
response
evaluation result
execution status
```

Where external evidence is used:

```text
evidence source
evidence version
effective date
```

## What this level should discover

- judge instability
- unexpected answer shapes
- parser failures
- false positives
- false negatives
- threshold sensitivity
- evidence gaps
- cases requiring human review
- cases that should be ungradable
- failure modes hidden by mocks

The purpose is not to maximize the pass rate.

The purpose is to learn where the evaluation approach breaks.

## Claim boundary

Controlled live validation supports:

> Under these documented conditions, this model/evaluator configuration produced
> these observed results.

It does not prove permanent or universal robustness.

## Current status

**Live-provider execution exists, but a controlled evaluator-validation
experiment is still pending.**

See `gaps.md` G-07.

---

# 6. Level 5 — Regression evaluation

## Purpose

Detect whether behaviour has degraded relative to an approved, comparable
baseline.

Possible change sources:

- model version
- provider
- system prompt
- evaluator logic
- judge model
- judge prompt
- thresholds
- temperature/sampling
- test-case definition

Conceptually:

```text
approved baseline
    ↓
comparable run
    ↓
difference / drift
    ↓
investigation if outside tolerance
```

## Current model

The project currently uses baseline scores and acceptable deltas.

Example:

```python
lower_bound = baseline_score - acceptable_delta
assert current_score >= lower_bound
```

This is useful for expressing a quality floor, but a numeric baseline alone is
not enough.

## Baseline provenance

A trustworthy baseline should eventually record:

```text
model/provider
model version
system prompt version
test-case version
judge model/version
judge prompt version
evaluator version
temperature
sampling settings
execution date
number of runs
mock/live mode
aggregation method
approval basis
```

Mock and live baselines must be clearly distinguished.

## Three regression meanings

### Deterministic pipeline regression

```text
Did code changes break known pipeline behaviour?
```

Execution: mock mode.

Suitable for CI on every push.

### Evaluator regression

```text
Did evaluator changes worsen performance against a labelled validation set?
```

Requires Level 3.

### Live behavioural regression

```text
Did model/prompt/provider behaviour materially change?
```

Requires controlled live runs and strong provenance.

These must not be reported as if they were the same test type.

## Claim boundary

Regression testing supports:

> Behaviour changed or did not change materially relative to this defined
> baseline under comparable conditions.

It does not support:

> The system is correct because it matches the baseline.

A weak baseline can be reproduced perfectly.

## Current status

**Regression mechanics exist; baseline provenance and validation maturity remain
limited.**

See `gaps.md` G-05.

---

# 7. Cross-cutting principles

## Risk-based depth

Not every scenario needs the same assurance depth.

Higher-risk cases may require:

- stronger test basis
- stricter thresholds
- hard failure gates
- repeated runs
- domain-expert review
- human approval
- stronger provenance
- lower tolerance for false negatives

Example:

```text
formatting quality
```

does not require the same assurance as:

```text
fabricated bank transaction confirmation
```

---

## Critical gates versus weighted scores

Weighted scoring is useful for nuanced quality assessment.

But good performance in low-risk dimensions must not compensate for a critical
failure.

Future validation should test whether some conditions should act as hard gates:

```text
CRITICAL CONDITIONS
    ↓
must pass
    ↓
QUALITY SCORING
```

Potential examples:

- fabricated transaction confirmation
- fabricated coverage decision
- prompt/system instruction disclosure
- unauthorized action
- unsupported high-risk factual claim

This remains an open design question, not a current implementation commitment.

---

## Execution status versus verdict

A technical evaluator failure is not a model-quality result.

Conceptually:

```text
evaluation_status:
COMPLETED
ERROR

verdict:
PASS
FAIL
REVIEW
UNGRADABLE
NOT_AVAILABLE
```

Example:

```text
judge parser failed
→ evaluation_status = ERROR
→ verdict = NOT_AVAILABLE
```

Not:

```text
judge parser failed
→ score = 50
```

See `gaps.md` G-06.

---

## Gradability before judgement

A mature evaluator may eventually need to ask:

```text
Do we have sufficient evidence?
Is it trustworthy?
Is it current?
Is it applicable?
Is the rubric precise enough?
Does this require domain expertise?
Is the claim objectively gradable?
```

Possible outcomes:

```text
PASS
FAIL
REVIEW
UNGRADABLE
```

This is an ambitious future direction, not a v1.0 commitment.

---

## Human involvement

Human participation should be risk-based.

Possible future model:

```text
clear low-risk case + strong evidence
    → automated verdict

borderline / conflicting evidence
    → REVIEW

insufficient evidence
    → UNGRADABLE

high-impact specialist judgement
    → domain expert review
```

The goal is not maximum automation.

The goal is a clear boundary between automated authority and human
responsibility.

---

# 8. Current test categories

## Hallucination

Focus:

- fabricated prices/rates
- fabricated identifiers
- unsupported legal/coverage claims
- recency uncertainty

Current strength:

```text
pipeline/evaluator mechanics demonstrated
independent evaluator accuracy not yet validated
```

## Prompt injection

Focus:

- system prompt extraction
- jailbreak attempts
- fake system instructions
- unauthorized actions
- structured injection payloads
- multilingual attacks

Current strength:

```text
deterministic attack-path logic demonstrated
real-world coverage remains scoped
```

## Response quality

Dimensions:

- completeness
- precision
- format
- actionability

Current strength:

```text
scoring mechanics demonstrated
weights and thresholds not empirically calibrated
```

## Regression

Focus:

- quality-floor degradation
- consistency
- temperature sensitivity
- stability after changes

Current strength:

```text
regression mechanism demonstrated
baseline provenance remains limited
```

## Edge cases / robustness

Focus:

- empty input
- long input
- multilingual input
- special characters
- competitor mentions

Current strength:

```text
selected edge scenarios covered
not a comprehensive robustness audit
```

---

# 9. CI strategy

## Default CI path

```text
push / pull request
    ↓
mock-based pytest suite
    ↓
Allure results
    ↓
fast, reproducible feedback
```

Purpose:

- detect code regressions
- detect broken evaluator integration
- detect scoring-flow changes
- preserve deterministic developer feedback

Mock CI remains intentionally zero-cost where possible.

## What a green CI badge means

A green CI badge means:

> The deterministic automated suite passed under its configured test conditions.

It does not mean:

> The evaluated LLM is production-robust.

The CI badge is a software-quality signal for the toolkit implementation.

It is not an AI robustness certification.

## Live runs

Live runs should remain deliberately triggered until:

- evaluator validity is better understood
- cost expectations are defined
- provenance exists
- repeatability strategy is defined
- result interpretation is clear

Possible later models:

- manual controlled run
- change-triggered validation
- scheduled regression experiment

Monitoring intensity should follow risk and purpose.

---

# 10. Reporting strategy

Allure should report observable facts clearly.

Useful information includes:

- test ID
- category
- domain
- risk/severity
- evaluator
- score/signals
- threshold
- execution mode: mock/live
- provider/model where applicable
- verdict
- evaluation status

Future reporting may add:

- judge model/version
- evaluator version
- test-case version
- evidence version
- human-review requirement
- provenance metadata

Principle:

> **A report communicates evidence; it does not create evidence.**

A polished dashboard must not hide weak test basis, unvalidated thresholds, or
evaluation errors.

---

# 11. Entry and exit criteria

## Level 1 — Unit / deterministic

Entry:

- expected logic is defined
- deterministic input exists

Exit:

- expected branches and error paths pass

Claim:

```text
implementation behaves as specified for tested inputs
```

## Level 2 — Mock pipeline

Entry:

- components integrated
- deterministic fixtures available

Exit:

- pipeline executes end to end
- expected scenarios pass reproducibly
- reporting path works

Claim:

```text
pipeline is internally consistent for predefined scenarios
```

## Level 3 — Evaluator validation

Entry:

- evaluation scope defined
- labelled reference cases available
- labels independently justified
- test basis documented

Exit:

- evaluator performance measured
- disagreements analysed
- known failure modes documented
- thresholds reviewed

Claim:

```text
evaluator performance measured within defined validation scope
```

## Level 4 — Controlled live validation

Entry:

- model/provider configuration recorded
- experiment defined
- metadata captured
- evaluator limitations explicit

Exit:

- real outputs preserved
- trusted comparison completed
- variability/failures analysed

Claim:

```text
observed real-model behaviour under documented conditions
```

## Level 5 — Regression

Entry:

- approved baseline exists
- baseline provenance recorded
- comparable conditions defined

Exit:

- differences measured
- tolerance evaluated
- significant regressions investigated

Claim:

```text
change relative to defined baseline under comparable conditions
```

---

# 12. What is explicitly not claimed today

The current test suite does not establish:

- production-grade LLM robustness
- formal AI audit assurance
- validated universal evaluator accuracy
- universal threshold validity
- authoritative domain correctness
- comprehensive safety coverage
- continuous robustness monitoring
- multi-provider evaluator superiority

These remain validation gaps or future directions.

---

# 13. Immediate testing priority

The next priority is not broader test-category coverage.

It is:

> **validate the evaluation approach itself.**

Recommended sequence:

```text
1. define a small labelled validation set
2. include good / bad / borderline / ambiguous cases
3. include insufficient-evidence cases
4. compare evaluator verdicts with trusted labels
5. measure disagreement and failure modes
6. review thresholds and critical gates
7. perform a small controlled live-model experiment
8. only then broaden benchmarking
```

The governing principle remains:

> **Validation before expansion.**

---

## Summary

```text
LEVEL 1 — Unit / deterministic evaluator tests
→ Does the technical logic work?

LEVEL 2 — Mock pipeline tests
→ Does the integrated pipeline behave consistently?

LEVEL 3 — Evaluator validation
→ Does the evaluator correctly distinguish known cases?

LEVEL 4 — Controlled live-model validation
→ How does the system behave on real model outputs?

LEVEL 5 — Regression evaluation
→ Has behaviour degraded relative to a trusted baseline?
```

Final rule:

> **Never make a stronger claim than the validation level can support.**

A green mock suite is useful, but it is not a validated evaluator.

A validated evaluator is useful, but it is not production robustness.

A successful live run is useful, but it is not a permanent guarantee.
