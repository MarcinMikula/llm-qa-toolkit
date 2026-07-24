# Future ideas — deliberately deferred directions

This file collects ideas that may be valuable later but are **not current
commitments**.

The purpose is to preserve useful directions without silently turning every
interesting question into roadmap scope.

Some ideas below may eventually become implementation work. Others may be
resolved through experiments, documentation, narrower scope, or a decision not
to build them.

The current project priority remains:

> **validate the evaluation approach before expanding feature breadth**

See [`gaps.md`](gaps.md) for current validation gaps and
[`known-limitations.md`](known-limitations.md) for the concise present-state
boundaries.

---

## Prioritisation principle

A recurring risk in an LLM evaluation project is to expand horizontally too
early:

```text
more providers
more models
more metrics
more domains
more dashboards
more datasets
more evaluators
```

before answering the more basic question:

> **Does the current evaluator reliably distinguish the cases it claims to
> evaluate?**

The preferred sequence is therefore:

```text
1. validate evaluator behaviour
2. understand evidence and gradability requirements
3. calibrate decision boundaries
4. perform controlled live validation
5. only then broaden providers, models, tasks, and automation
```

Provider breadth is not evidence of evaluator correctness.

---

## Evaluator validation and calibration

### Why this comes before multi-provider benchmarking

The current prototype can execute evaluators and produce deterministic results
against predefined mock responses.

That demonstrates pipeline behaviour, not independent evaluator accuracy.

Before asking:

> Which judge is better — Claude, GPT, Gemini, or an ensemble?

the project should first ask:

> Does this evaluator produce reliable verdicts at all?

A useful validation approach could use a deliberately small labelled set
containing:

```text
known-good responses
known-bad responses
borderline responses
ambiguous responses
insufficient-evidence cases
```

Possible measurements:

- agreement with human-labelled expectations
- false-positive rate
- false-negative rate
- disagreement patterns
- stability across repeated judge runs
- sensitivity to judge prompt changes
- behaviour on borderline cases
- behaviour when evidence is insufficient

The goal is not necessarily to build a large academic benchmark.

A small, well-designed calibration set with traceable labels may provide more
useful evidence than broad but weak coverage.

### Important sequencing decision

Earlier thinking treated judge calibration mainly as a future multi-model or
multi-provider comparison problem.

That is now considered the wrong order.

```text
FIRST:
Can the evaluator be trusted for its intended scope?

LATER:
Which provider/model performs best as the evaluator?
```

Multi-judge consistency is useful only after there is some external basis for
deciding whether agreement between judges corresponds to correctness.

Three judges agreeing with each other can still be three judges sharing the
same unsupported assumption.

---

## Evidence-grounded judging and judge authority

> **Ambitious future direction — explicitly not a v1.0 commitment.**

The current LLM-as-judge pattern assumes that the evaluator can usually produce a
score when given a candidate response and evaluation prompt.

A more mature evaluation architecture may need to ask a prior question:

> **Does the judge have sufficient authority and evidence to issue a verdict?**

Possible pre-evaluation checks:

```text
Do I have sufficient evidence?
Is the evidence trustworthy?
Is it current?
Is it applicable to this exact case?
Is the rubric precise enough?
Is this within the evaluator's competence?
Does this decision require domain expertise?
Can the claim be objectively graded?
```

Conceptually:

```text
candidate response
        ↓
test basis + evidence
        ↓
GRADABILITY / AUTHORITY CHECK
        ↓
  ┌───────────────┬─────────────────────┐
  │ gradable      │ not safely gradable │
  ↓               ↓
evaluation        REVIEW / UNGRADABLE
  ↓
PASS / FAIL
```

Possible future verdict vocabulary:

```text
PASS
FAIL
REVIEW
UNGRADABLE
```

Execution state should remain separate from substantive verdicts, for example:

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

This avoids treating a technical evaluator failure as if it were a meaningful
quality score.

### Possible test-basis model

A future test case may need to distinguish between:

```text
model-visible context
```

and:

```text
judge-only evidence
```

Possible fields or concepts:

- test objective
- risk being evaluated
- trusted reference evidence
- evidence provenance
- source owner
- source version
- effective date / validity period
- domain-specific rules
- deterministic calculations or reference algorithms
- assumptions
- intentionally missing context
- expected behaviour
- critical forbidden behaviour
- gradability prerequisites
- escalation requirements

This would allow tests to represent an important distinction:

> The model may correctly be expected to say "I do not know" because the
> information is intentionally unavailable to it, while the evaluator may still
> need trusted judge-only evidence to verify that behaviour.

### Evidence provenance

Evidence should not be treated as trustworthy merely because it appears in an
evaluation prompt.

A future evidence model may need metadata such as:

```text
source
version
effective date
jurisdiction/domain
owner
retrieval date
confidence/authority level
known limitations
```

The evaluator's reasoning cannot be more trustworthy than the basis supplied to
it.

### Domain-expert escalation

Some evaluations cannot be safely automated from generic LLM knowledge.

Examples may include:

- legal interpretation
- insurance coverage decisions
- regulated financial decisions
- medical or safety-critical claims
- business-rule calculations dependent on proprietary logic

A future framework could explicitly indicate:

```text
domain_expert_review_required = true
```

rather than forcing an automated verdict.

The role of the judge would then include recognising the boundary of its own
authority, not pretending that every well-formed question is automatically
gradable.

### Human review

Human participation should be risk-based.

A possible future model:

```text
low-risk + strong evidence + clear rubric
    → automated verdict may be sufficient

borderline / ambiguous / incomplete evidence
    → REVIEW

high-impact domain decision
    → mandatory specialist review

insufficient test basis
    → UNGRADABLE
```

The principle is similar to bounded autonomy in other AI-assisted QA tooling:

> the system should define where AI autonomy ends and human responsibility
> begins.

Again, this is a research direction, not a committed v1.0 architecture.

---


## Strategic user behaviour, decision integrity, and manipulation resistance

> **Parked research direction — not automatic Pre-v1.0 feature scope.**

Regulated-domain systems face more than technical prompt injection.

Users may attempt to influence a regulated process through ordinary human
behaviour:

- minimising inconvenient facts
- answering indirectly
- selective disclosure
- plausible deniability
- emotional pressure
- reframing required information as irrelevant
- requesting exceptions
- threatening to leave for a competitor
- repeatedly pushing for a favourable interpretation

This is different from a classic jailbreak.

The user may never issue an explicit malicious instruction. Instead, the system
is gradually encouraged to relax a rule, infer a convenient fact, or convert
ambiguity into a customer-favourable assumption.

Working concepts:

```text
decision integrity
policy adherence
constraint compliance
manipulation resistance
evidence sufficiency
strategic ambiguity handling
```

Example pattern:

```text
material risk factor is raised
        ↓
user minimises its relevance
        ↓
system asks for clarification
        ↓
user refuses certainty:
"How should I know what happens in the future?"
        ↓
user pressures system:
"Just enter the favourable option."
```

A robust regulated-domain system should not reward this sequence by silently
changing the evidentiary or policy requirement.

Depending on the applicable Test Basis, expected behaviour may be:

```text
clarify
request required declaration
preserve the constraint
apply a defined fallback
or escalate
```

This direction may later produce realistic multi-turn pressure tests across
insurance, banking, energy, legal, healthcare, or public-administration
scenarios.

The research question is broader than:

> "Can the model resist prompt injection?"

It is:

> **Can the system preserve decision integrity under realistic human pressure,
> ambiguity, and attempts to obtain a favourable outcome?**


## Threshold and scoring calibration

Current thresholds and score weights are manually selected design assumptions.

Future validation could explore whether thresholds should be calibrated using:

- labelled validation examples
- risk classes
- acceptable false-positive / false-negative trade-offs
- domain-specific requirements
- evaluator-specific behaviour
- confidence intervals rather than single cut-offs

A critical question is whether all risks belong in one weighted score.

For example:

```text
critical factual fabrication
+ excellent formatting
+ high completeness
```

should probably not become a passing result merely because non-critical quality
dimensions compensate for the critical failure.

A future evaluation model may therefore distinguish:

```text
CRITICAL GATES
    ↓
only if passed
    ↓
QUALITY SCORING
```

Possible gates:

- fabricated transaction confirmation
- fabricated coverage decision
- system prompt disclosure
- unsupported high-risk claim
- unauthorized action

This remains an open design question until validated against real examples.

---

## Baseline provenance and reproducibility

Regression baselines should eventually carry more context than a single numeric
score.

Possible metadata:

```text
model/provider
model version
system prompt version
test-case version
judge model/version
judge prompt version
evaluator version
temperature
sampling configuration
execution date
number of runs
mock/live mode
aggregation method
approval basis
```

This would make statements such as:

```text
baseline_score = 85
```

traceable to the conditions under which the value was produced.

A later implementation could store baselines as versioned structured artifacts
rather than constants embedded directly in tests.

---

## Controlled live validation

Before large-scale benchmarking, run a small controlled experiment against real
model outputs.

A useful experiment could compare:

```text
human-labelled expectation
vs
heuristic evaluator
vs
LLM judge
vs
combined evaluator result
```

across:

```text
known-good
known-bad
borderline
ambiguous
insufficient-evidence
```

The purpose would be to discover evaluator failure modes, not to produce an
impressive benchmark number.

Useful outputs:

- agreement/disagreement table
- false positives
- false negatives
- judge instability
- parser/evaluator errors
- examples requiring human review
- cases that should have been ungradable
- threshold sensitivity

Only after this should broader live benchmark automation become a priority.

---

## Multi-provider and multi-judge comparison

Multi-provider support remains useful, but it should come **after evaluator
validation**, not before it.

Potential providers/models:

- Anthropic / Claude
- OpenAI / GPT
- Google / Gemini
- local models through Ollama
- other provider-compatible backends

Potential experiments:

```text
same candidate response
same rubric
same evidence
different judge model
```

Measure:

- verdict agreement
- score variance
- cost
- latency
- structured-output reliability
- sensitivity to prompt wording
- domain-specific disagreement

Possible future patterns:

- single primary judge
- primary + fallback judge
- judge ensemble
- disagreement-triggered human review

Important caution:

> Judge agreement is not equivalent to ground truth.

Multi-judge comparison supplements external validation; it does not replace it.

---

## Scheduled live benchmark runs

Scheduled live runs may eventually provide drift and regression signals after
the evaluation approach itself has been validated.

Possible triggers:

- model version change
- evaluator prompt change
- system prompt change
- scheduled weekly/monthly run
- provider migration
- major dependency update

Possible outputs:

- score drift
- verdict changes
- variance changes
- cost/token changes
- judge disagreement
- newly failing critical cases

This should not be described as "continuous robustness assurance" unless the
monitoring scope, evidence, thresholds, and response process actually justify
that claim.

For lower-risk use cases, periodic or change-triggered reassessment may be more
appropriate than real-time monitoring.

---

## Evaluation datasets

A future dataset layer could move cases out of Python constants into versioned
structured data.

Possible formats:

```text
JSON
YAML
JSONL
```

Potential benefits:

- easier review
- provenance/version control
- human labelling
- dataset slicing
- reproducible experiments
- domain-specific packs
- separation between test data and evaluator implementation

Possible labels:

```text
GOOD
BAD
BORDERLINE
AMBIGUOUS
INSUFFICIENT_EVIDENCE
```

Dataset size should follow the evaluation question.

A small, carefully labelled set is preferable to a large synthetic dataset whose
ground truth is itself questionable.

---

## Richer evaluation metadata

Future result records could include:

```text
model
model_version
provider
temperature
prompt_version
judge_model
judge_version
judge_prompt_version
evaluator_version
input_tokens
output_tokens
latency
cost
timestamp
test_case_version
evidence_version
evaluation_status
verdict
```

This supports:

- reproducibility
- regression analysis
- baseline provenance
- cost analysis
- auditability
- debugging evaluator changes

Metadata should be collected because it supports a concrete question, not merely
because it is possible to collect it.

---

## Reporting and dashboards

Allure currently provides useful test reporting.

A richer dashboard could eventually visualise:

- pass/fail/review/ungradable distribution
- evaluator error rate
- score distribution
- risk-category coverage
- regression trends
- judge disagreement
- human-review rate
- cost and latency
- model/provider comparison

Important principle:

> A dashboard communicates evidence; it does not create evidence.

A polished visualisation must not hide weak test basis, unvalidated thresholds,
or unsupported claims.

---

## Broader safety and fairness evaluation

Potential later categories:

- toxicity
- demographic bias
- PII leakage
- unsafe advice
- refusal quality
- jailbreak robustness beyond current injection cases

These should not be added merely to increase the number of test categories.

Each new category needs:

- explicit scope
- risk rationale
- test basis
- evaluation method
- known limitations
- evidence that the evaluator itself is fit for that category

---

## RAG faithfulness evaluation

Potential future work:

- answer-to-context faithfulness
- unsupported claim detection
- citation correctness
- retrieval relevance
- missing-context handling
- conflicting-source handling
- outdated-source detection

RAG evaluation makes the evidence problem even more explicit:

```text
retrieved evidence
    ↓
candidate answer
    ↓
judge applies explicit rubric
```

The evaluator should distinguish:

- answer unsupported by retrieved context
- retrieved context itself being wrong/outdated
- insufficient context
- conflicting evidence

---

## Agent and tool-use evaluation

Potential later scope:

- correct tool selection
- argument correctness
- unauthorized actions
- tool-result grounding
- recovery from tool failure
- bounded retries
- approval gates
- side-effect safety

Agent evaluation introduces new questions because correctness may depend on the
sequence of actions, not only the final text response.

This belongs to a later project stage after the simpler response-evaluation
foundation is validated.

---

## Adversarial test generation

LLMs could eventually assist with generating:

- prompt-injection variants
- multilingual attacks
- paraphrased edge cases
- adversarial domain scenarios
- mutation-based test inputs

Generated tests should not automatically become trusted test cases.

They would still require:

- deduplication
- risk classification
- review
- expected-behaviour definition
- evidence/test-basis definition

LLMs can help generate hypotheses; they do not automatically generate ground
truth.

---

## Research direction: evaluation of the evaluator

The most interesting long-term question may not be:

> How many LLM tests can this toolkit run?

but:

> How do we know when the evaluation itself deserves to be trusted?

This includes:

- evaluator validity
- evidence sufficiency
- judge authority
- calibration
- uncertainty
- human escalation
- reproducibility
- failure semantics
- claim boundaries

A mature version of the toolkit could demonstrate not only how to produce a
score, but also when an automated verdict is justified — and when it is not.

That direction is intentionally broader than the current v1.0 commitment.

---

## Explicit non-commitment

Nothing in this file is automatically part of the v1.0 Definition of Done.

Ideas should move from `future-ideas.md` into active scope only when there is a
clear reason, testable objective, and acceptable implementation cost.

The project should resist feature accumulation for its own sake.

The current rule remains:

> **Validation before expansion.**
