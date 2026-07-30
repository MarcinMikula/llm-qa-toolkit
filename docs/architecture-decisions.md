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
- [`conceptual-model.md`](conceptual-model.md) — working conceptual model and HLR draft
- [`framework-architecture.md`](framework-architecture.md) — three-pillar product architecture and extension points
- [`development-workflow.md`](development-workflow.md) — SDLC/STLC branch, PR, and milestone process
- [`integration-architecture.md`](integration-architecture.md) — external-system ports, adapters, replay, and validation boundaries
- [`roadmap.md`](roadmap.md) — staged implementation and validation path

---

## Decision summary

| ID | Decision | Status |
|---|---|---|
| AD-01 | Separate test-case data, evaluator logic, and test orchestration | Active |
| AD-02 | Use scoring and thresholds instead of exact-output assertions where the target is gradable | Active, bounded by AD-10 |
| AD-03 | Combine deterministic heuristics with LLM-assisted evaluation | Active |
| AD-04 | Keep mock mode as an intentional permanent validation layer | Active |
| AD-05 | Treat regression baselines as comparison references, not ground truth | Active |
| AD-06 | Keep project scope as a focused evaluation toolkit / framework skeleton, not a full AI robustness audit platform | Active |
| AD-07 | Validate evaluator behaviour before expanding to multi-provider benchmarking | Active |
| AD-08 | Treat the future framework as an evaluation-protocol controller between external examinee and examiner systems | Working direction |
| AD-09 | Use explicit scope-drift guardrails: conceptual breadth does not automatically become implementation scope | Active |
| AD-10 | Determine assessment basis, eligibility, and scope before invoking or accepting evaluator judgement | Active |
| AD-11 | Prefer deterministic protocol boundaries around one bounded evaluator over recursive LLM judge chains | Active direction |
| AD-12 | Treat rules as a controlled, versioned, evolving catalogue organised into shared and domain evaluation packs | Active direction |
| AD-13 | Make the evaluation core depend on normalised examinee/evaluator contracts rather than a specific transport or provider | Active direction |
| AD-14 | Treat replay, stubs, and controlled capture as first-class validation modes; reserve live models for scoped evidence gathering | Active direction |
| AD-15 | Structure the framework as Examinee Integration, Evaluator Integration, and a Validation Engine | Active |
| AD-16 | Make all three pillars configurable while enforcing non-bypassable assessment invariants | Active |
| AD-17 | Keep main runnable; develop through short-lived feature branches, PR evidence, and milestone tags | Active delivery model |

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

The current prototype uses composite scores and category-specific thresholds.

Scoring is an evaluation mechanism, not the default conceptual starting point.

It should only be applied after the project can justify:

```text
assessment target
Test Basis
expected behaviour
gradability
evaluator scope
```

A target that is not gradable must not receive a convenient numeric score merely
because the evaluator can generate one.

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

Keep the project scoped as a focused **LLM evaluation toolkit, research
prototype, and technical skeleton of a future evidence-grounded evaluation
framework**.

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

# AD-08 — Framework controls the evaluation protocol, not evaluator cognition

## Status

**Working architectural direction.**

The responsibility boundary is clear enough to guide further requirements, but
the matching implementation architecture has not yet been designed.

## Decision

Treat the intended framework as an orchestration and control layer between:

```text
external system under evaluation
        ↓
evaluation framework
        ↓
external LLM evaluator
        ↓
scoped evaluation result
```

The system under evaluation and the evaluator may both be externally supplied.

The framework shall not be modelled as an all-knowing judge.

Its intended responsibility is to control the evaluation protocol and the
conditions under which an evaluator may issue a finding.

## Intended framework responsibilities

The framework should eventually be able to coordinate or validate:

- evaluation objective, risk, and scenario
- stimulus and model-visible context
- evaluator-only Test Basis and evidence
- expected response strategy
- behavioural constraints
- rubric and assessment targets
- gradability prerequisites and allowed scope
- structured findings and rationale
- technical evaluation status
- review and escalation conditions
- traceability between evidence, finding, and claim

## Constraint boundary

The framework may constrain an evaluator through:

```text
prompt / role
input context
evidence package
rubric
output schema
required rationale
consistency checks
```

It cannot guarantee that an external evaluator:

- understands the domain
- interprets evidence correctly
- is unbiased
- is more competent than the evaluated system
- does not invent missing ground truth

Therefore:

> **The framework controls the examination protocol, verdict conditions, and
> claim boundaries. It does not control the examiner's internal reasoning or
> create missing expertise.**

## Consequence

Future architecture should not be designed as merely:

```text
send response to judge
        ↓
parse score
```

It should be derived from responsibilities such as:

```text
validate test definition
validate Test Basis
determine assessment eligibility
constrain evaluator scope
validate result consistency
preserve evidence and rationale
route review / escalation
```

The exact services, classes, schemas, and enums remain deliberately unresolved.

---



# AD-09 — Conceptual breadth does not automatically become implementation scope

## Status

**Active.**

## Context

The conceptual model now includes evidence provenance, scoped gradability,
human/domain-expert escalation, evaluator authority, decision integrity, and
traceable findings.

Each concept is relevant to credible regulated-domain evaluation.

Implementing every consequence would expand the project into adjacent product
categories such as governance, compliance, evidence management, case
management, benchmarking, or regulated decision automation.

## Decision

Apply explicit scope-drift guardrails.

```text
Understand broadly.
Implement narrowly.
Validate before expanding.
```

A documented concept may remain:

```text
high-level requirement
manual input
known limitation
research question
future idea
```

without becoming a current implementation requirement.

## Scope classification

Every new capability shall be classified as:

```text
NOW
RECORD
PARK
SEPARATE
```

- `NOW` — necessary for the active validation objective
- `RECORD` — conceptually required but currently representable through explicit
  metadata or manual input
- `PARK` — valuable adjacent direction that is not required for the current
  evidence-backed claim
- `SEPARATE` — a different product category or programme

## Expansion gate

A capability should enter implementation only when:

- it maps to a defined risk or HLR
- the current/planned claim would be materially weaker without it
- its smallest testable behaviour is defined
- validation evidence is available or obtainable
- manual representation is insufficient
- adding it does not silently create a different product
- roadmap trade-offs are explicit

## Consequences

The project may document complete conceptual dependencies while implementing
only a narrow vertical slice.

Examples:

```text
provenance
→ metadata before automated source lifecycle

review
→ disposition before workflow platform

traceability
→ structured result before enterprise audit system

provider comparison
→ validated dimension before universal benchmark
```

The canonical boundary document is `scope-guardrails.md`.

---



# AD-10 — Assessment basis, eligibility, and scope precede evaluator judgement

## Status

**Active.**

## Context

The first implementation model centred on:

```text
candidate response
        ↓
heuristic / LLM-as-a-judge
        ↓
score
        ↓
threshold verdict
```

This is a useful technical pipeline, but it begins too late in the evaluation
process.

An evaluator can produce a fluent rationale and parseable score even when:

- the evaluation objective is unclear
- the stimulus does not exercise the intended risk
- the expected behaviour is undefined
- the Test Basis is missing or inapplicable
- only part of the response is gradable
- the evaluator lacks sufficient evidence or competence
- the requested verdict is broader than the available basis

## Decision

Determine the basis, eligibility, and allowed scope of the assessment before
invoking or accepting substantive evaluator judgement.

Conceptually:

```text
evaluation objective
        +
scenario / stimulus
        +
candidate response
        +
Test Basis
        ↓
assessment eligibility
and scope determination
        ↓
evaluation mechanism
        ↓
scoped findings
```

`LLM-as-a-judge`, deterministic heuristics, scoring, and thresholds remain
available mechanisms.

They do not define whether the assessment is justified.

## Required conceptual checks

Before accepting substantive findings, the future framework should be able to
represent or determine:

- evaluation objective
- risk or requirement under test
- expected response strategy
- relevant behavioural constraints
- required evidence
- evidence provenance and applicability
- gradability prerequisites
- allowed assessment targets
- evaluator authority boundaries

## Consequences

### Scores are conditional outputs

A numeric score is acceptable only when the scored dimension:

- is defined
- has an adequate Test Basis
- is gradable
- has a validated interpretation
- stays within evaluator authority

### Ungradable does not mean model failure

Missing evidence may prevent factual-outcome assessment while still allowing
behavioural assessment.

Example:

```text
factual premium correctness → NOT_ASSESSED
unsupported certainty       → FAIL
response strategy            → FAIL
```

### Evaluator output requires validation

A parseable answer from the judge is not automatically an acceptable evaluation
result.

The framework may reject or limit it when:

- assessment prerequisites are missing
- the finding exceeds the allowed scope
- evidence does not support the rationale
- technical status is confused with substantive verdict
- the evaluator invents missing ground truth

## Relationship to earlier decisions

AD-02 and AD-03 remain valid as implementation mechanisms.

AD-10 bounds them:

```text
AD-02 / AD-03
→ how evaluation may be performed

AD-10
→ whether that evaluation is justified,
  what it may target,
  and what it may conclude
```

## Claim boundary

This decision records the conceptual order.

It does not claim that the current code already implements a complete
assessment-eligibility engine.

---



# AD-11 — Prefer deterministic protocol boundaries around one bounded evaluator

## Status

**Active direction for the next validation slice.**

## Context

A judge-centric architecture can grow recursively:

```text
system under evaluation
        ↓
LLM evaluator
        ↓
LLM checking evaluator quality
        ↓
LLM resolving evaluator disagreement
```

Additional judges may be useful for later comparative experiments.

They do not automatically solve:

- missing ground truth
- missing or inapplicable rules
- insufficient evidence
- evaluator competence mismatch
- unjustified assessment scope
- shared systematic bias

Agreement between evaluators is not equivalent to correctness.

## Decision

Use deterministic framework logic to define the assessment contract before
invoking one external bounded evaluator.

Then validate the evaluator output deterministically.

```text
ASSESSMENT ELIGIBILITY
        ↓
ASSESSMENT CONTRACT
        ↓
ONE BOUNDED LLM EVALUATOR
        ↓
RESULT VALIDATION
        ↓
SCOPED FINDINGS
```

The evaluator is treated as:

> **A semantic executor of a constrained examination protocol.**

## Deterministic responsibilities

Before evaluator invocation:

- select applicable rules
- identify required and available evidence
- determine allowed and excluded targets
- constrain allowed verdicts
- define prohibited claims

After evaluator response:

- reject out-of-scope findings
- reject unsupported evidence references
- reject invented rule IDs
- reject prohibited verdicts
- prevent `NOT_ASSESSED` from becoming model failure
- prevent partial assessment from becoming an unsupported overall score

## LLM responsibilities

Use the evaluator for semantic tasks such as:

- multi-intent separation
- response-strategy classification
- nuanced rule application
- unsupported-certainty detection
- explanation within the permitted scope

## Consequence

The project does not need another LLM merely to decide whether the first
evaluator was allowed to assess a target.

Multi-judge comparison remains a later validation experiment, not the primary
control mechanism.

## Claim boundary

This decision defines architectural responsibility.

It does not claim that deterministic validation can prove the evaluator's private
reasoning was correct.

---

# AD-12 — Rules are a controlled, versioned, evolving catalogue

## Status

**Active conceptual direction. Runtime schema not yet committed.**

## Context

The rules layer may become the most distinctive part of the project.

Unlike a short completeness checklist, the potential rule space depends on:

```text
domain
system role
scenario class
user intent
available evidence
jurisdiction
current data
allowed tools
risk level
response strategy
```

A complete encoded rulebook for insurance, banking, telco, or energy is not a
credible solo-project commitment.

## Decision

Treat rules as:

> **A controlled, versioned, and continuously developed catalogue of explicit
> constraints, applicability conditions, evidence requirements, permitted
> response strategies, and justified conclusions for selected classes of
> evaluation scenarios.**

Rules should be organised conceptually into:

```text
shared evaluation rules
+
domain-specific evaluation packs
```

Possible shared categories:

- multi-intent handling
- out-of-domain behaviour
- live-data handling
- evidence sufficiency
- verdict constraints
- claim boundaries

Possible domain-pack content:

- domain rules
- evidence requirements
- response strategies
- assessment scope
- controlled cases

## Rule authority

Rule metadata may need to express:

```text
id
version
status
owner / source
scope
applicability
trigger
required evidence
allowed strategy
forbidden behaviour
gradable targets
permitted conclusions
```

Conceptual lifecycle states may include:

```text
DRAFT
REVIEWED
VALIDATED
DEPRECATED
PROJECT_SPECIFIC
```

## Missing coverage

No applicable rule shall not be treated as permission for evaluator
improvisation.

It should limit the result toward:

```text
NO_APPLICABLE_RULE
NOT_ASSESSED
REVIEW_REQUIRED
```

## Domain boundary

A model may retain knowledge outside its specialised domain.

Therefore:

```text
latent capability
≠
authorised capability
```

Operational and evaluation boundaries must be imposed by the protocol rather
than inferred from the model label.

## Consequence

The project may build a small validated rule subset without claiming complete
domain coverage.

The first pack should prove rule applicability, scoped authority, and safe
handling of missing coverage.

It should not attempt to encode an industry.

## Claim boundary

This decision does not commit the project to a final directory layout, YAML
schema, rules engine, or external policy-ingestion platform.

Those remain downstream implementation decisions.

---



# AD-13 — Integration core depends on contracts, not transports

## Status

**Active direction for the runtime bridge.**

## Context

The project has not yet selected final examinee chatbots or evaluator models.

Available systems may expose:

- HTTP APIs
- vendor SDKs
- Python callables
- CLI tools
- browser-only chat interfaces
- manually captured responses
- previously recorded fixtures

Defining integration as an API call would couple the evaluation architecture to
one access method and make non-API validation unnecessarily difficult.

## Decision

Model two separate ports:

```text
ExamineePort
EvaluatorPort
```

and normalised envelopes:

```text
CandidateResponse
ProposedEvaluatorResult
```

The core pipeline shall depend on those contracts.

Transport-specific adapters may include:

```text
API
Python callable
CLI / subprocess
browser / Playwright
replay file
manual capture
```

## Examinee responsibility

The examinee side:

- accepts a test stimulus
- invokes or accesses the system under evaluation
- captures content and available evidence
- preserves metadata
- reports technical status

## Evaluator responsibility

The evaluator side:

- receives the candidate response
- receives the bounded assessment contract
- invokes the semantic evaluator
- normalises proposed findings
- preserves raw output and technical status

## Consequence

Core evaluation logic remains independent from:

- authentication method
- vendor SDK
- browser selectors
- process invocation
- file format
- provider-specific response shape

Browser automation, when needed, stays inside a system-specific adapter.

## Claim boundary

Transport neutrality does not mean every adapter will be implemented.

Adapters are added only when required by a concrete validation experiment.

---

# AD-14 — Replay and stubs are first-class validation modes

## Status

**Active direction for the first runtime slice.**

## Context

Using two live paid or externally hosted LLMs for every development and CI run
would be expensive, non-deterministic, and unnecessary for validating most
framework logic.

The project must distinguish:

```text
framework correctness
evaluator effectiveness
examinee behaviour
integration reliability
```

## Decision

Use replay fixtures, controlled captures, fakes, and stubs as first-class
validation modes.

The first assessment-grounded runtime slice should use:

```text
ReplayExamineeAdapter
+
StubEvaluatorAdapter
```

before adding a new live integration.

Replay may exercise:

- response normalisation
- evidence preservation
- assessment eligibility
- rule selection
- evaluator constraints
- result rejection
- reporting
- regression behaviour

## What replay does not prove

Replay does not establish:

- current live-model quality
- current provider behaviour
- non-deterministic stability
- real latency or cost
- browser or API integration reliability

Those require separate controlled live experiments.

## Manual capture

Manual response capture is acceptable when it is the safest or most practical
way to obtain a small controlled sample.

Automation level is not itself validation quality.

## CI consequence

Default CI should remain deterministic and zero-cost.

Live-model tests should be:

- explicitly triggered
- separately labelled
- budget-aware
- excluded from default pull-request validation
- accompanied by preserved raw evidence

## Claim boundary

A green replay suite demonstrates internal framework consistency against the
captured evidence.

It does not demonstrate independent evaluator accuracy or broad model
robustness.

---



# AD-15 — Use a three-pillar framework architecture

## Status

**Active.**

## Context

The project was initially described as an evaluator toolkit.

Further design and the first runtime slices show a broader product structure.

Two external roles must be connected:

```text
system under evaluation
external evaluator
```

A separate internal component must validate the examination protocol.

## Decision

Structure the target framework around:

```text
1. Examinee Integration
2. Evaluator Integration
3. Validation Engine
```

### Examinee Integration

Responsible for obtaining and normalising the candidate response.

### Evaluator Integration

Responsible for invoking or loading the external evaluator and normalising its
proposed result.

### Validation Engine

Responsible for:

- test-definition validation
- Test Basis validation
- rules and heuristics
- evidence requirements
- eligibility and scope
- AssessmentContract construction
- evaluator-result validation
- scoped findings
- claim boundaries

## Consequence

The controlled rule catalogue is a Validation Engine component.

It is not the complete third pillar.

The repository documentation and future public APIs should explain extension
points by these three responsibilities.

## Current runtime mapping

The first two runtime slices already implement partial foundations for all three
pillars:

```text
ExamineePort / ReplayExamineeAdapter
EvaluatorPort / StubEvaluatorAdapter
AssessmentEligibilityChecker / EvaluationResultValidator
```

The architecture remains incomplete.

---

# AD-16 — Configuration is allowed only inside validated invariants

## Status

**Active.**

## Context

The future framework should allow users to configure:

- integration adapters
- input sources
- evaluator providers
- domain packs
- rule versions
- evidence
- targets
- verdict policies

Unrestricted configuration could produce internally inconsistent assessment
contracts.

## Decision

Treat configuration as a selection mechanism, not an authority override.

```text
configurable
≠
uncontrolled
```

The Validation Engine must reject configuration that violates invariants.

Examples:

- factual target allowed while mandatory evidence is missing
- deprecated rule treated as current authority
- result from another `case_id` accepted
- partial scope converted into an overall score
- technical failure converted into examinee failure

## Consequence

Configuration loading requires deterministic validation.

A configuration error is an evaluation-process outcome.

It is not a substantive finding about the examinee.

---

# AD-17 — Main remains runnable; implementation uses short-lived evidence-backed branches

## Status

**Active delivery model.**

## Context

The Validation Engine will require several experiments and vertical slices.

A long-lived parallel branch would separate public documentation, CI, and the
project's visible truth from active implementation.

## Decision

Use:

```text
main
→ always runnable and tested

short-lived feature branch
→ one slice or decision

Pull Request
→ scope, Test Basis, acceptance criteria, tests, limitations

merge
→ after review and green validation

tag
→ completed roadmap milestone
```

Recommended branches:

```text
feature/runtime-rule-catalogue
feature/assessment-contract-builder
feature/bounded-evaluator-prompt
feature/live-evaluator-adapter
```

## SDLC and STLC requirement

Every slice must demonstrate:

```text
software correctness
+
evaluation-decision correctness or correct limitation
```

## Milestone tags

Planned evidence milestones:

```text
v0.3.0-runtime-bridge
v0.4.0-bounded-evaluator
v0.5.0-controlled-live-validation
```

Tags do not imply production readiness.

## Consequence

No long-lived `develop` or `validator-v2` branch is planned.

Branch code becomes project capability only after review and merge into `main`.

---


# Decision boundary — conceptual model is design input, not committed code architecture

The project now has a working conceptual model covering:

```text
regulated-domain evaluation objective
test intent and stimulus
candidate response strategy
Test Basis
assessment eligibility / scoped gradability
evaluator authority
layered evaluation result
```

The model is documented in `conceptual-model.md`.

This is **not yet a decision to implement matching classes, enums, database
tables, or services**.

In particular, concepts such as:

```text
Expected response strategy
Behavioural constraints
FULLY_GRADABLE / PARTIALLY_GRADABLE
scoped findings
disposition / escalation
```

are conceptual vocabulary used to reason about requirements and validation.

They should become committed implementation architecture only after:

- the model survives further regulated-domain examples
- contradictions and missing concepts are identified
- high-level requirements are refined
- measurable Pre-v1.0 validation objectives are agreed
- the smallest useful implementation slice is defined

This preserves an important order:

```text
conceptual model
    → high-level requirements
        → measurable acceptance criteria
            → implementation architecture
```

not:

```text
existing code
    → invent requirements that justify it
```


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

# Decision boundary: evidence-grounded judge authority is not yet implementation architecture

Concepts such as:

```text
scoped PASS / FAIL findings
NOT_ASSESSED / UNGRADABLE targets
gradability checks
evidence authority
domain-expert escalation
human-review requirements
```

are now part of the working conceptual model in `conceptual-model.md`.

They guide the high-level requirements and the AD-08 responsibility boundary,
but they are **not yet committed implementation architecture for v1.0**.

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
