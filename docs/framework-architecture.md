# Framework architecture — three configurable pillars

> **Status: current product architecture direction.**
>
> This document describes the public shape of the future framework and maps it
> to the runtime capabilities already implemented. It does not claim that every
> adapter, validation rule, or configuration surface already exists.

---

## 1. Product evolution

The repository started as a portfolio-oriented LLM testing prototype:

```text
prompt
    → model response
        → heuristics / LLM-as-a-judge
            → score
                → pytest
```

That prototype remains useful, but the project is evolving toward a reusable,
configurable evaluation framework with three explicit pillars:

```text
1. Examinee Integration
2. Evaluator Integration
3. Validation Engine
```

The first two pillars connect external systems.

The third pillar defines and enforces the examination protocol.

---

## 2. High-level architecture

```text
┌──────────────────────────────────────────────┐
│          1. EXAMINEE INTEGRATION             │
│                                              │
│ API │ callable │ CLI │ browser │ file       │
└──────────────────────┬───────────────────────┘
                       ↓
               CandidateResponse
                       ↓
┌──────────────────────────────────────────────┐
│             3. VALIDATION ENGINE             │
│                                              │
│ test-definition validation                   │
│ Test Basis validation                        │
│ controlled rules and heuristics              │
│ evidence requirements                        │
│ assessment eligibility                       │
│ target and scope selection                    │
│ AssessmentContract construction              │
└──────────────────────┬───────────────────────┘
                       ↓
               AssessmentContract
                       ↓
┌──────────────────────────────────────────────┐
│          2. EVALUATOR INTEGRATION            │
│                                              │
│ API │ callable │ CLI │ file │ replay        │
└──────────────────────┬───────────────────────┘
                       ↓
            ProposedEvaluatorResult
                       ↓
┌──────────────────────────────────────────────┐
│        3. VALIDATION ENGINE — RESULT          │
│                                              │
│ target validation                            │
│ rule and evidence validation                 │
│ verdict constraints                          │
│ prohibited-claim checks                      │
│ technical-status separation                  │
│ scoped findings and claim boundaries         │
└──────────────────────┬───────────────────────┘
                       ↓
              ScopedEvaluationResult
```

The Validation Engine appears twice in the flow because it validates both:

```text
before evaluation
→ whether and what may be judged

after evaluation
→ whether the proposed judgement may be accepted
```

---

# 3. Pillar 1 — Examinee Integration

## Purpose

Connect the framework to the system under evaluation.

Examples:

- insurance chatbot
- legal assistant
- banking chatbot
- telco assistant
- local LLM
- agent or tool-using system
- previously captured response

## Public contract

```text
TestStimulus
        ↓
ExamineePort
        ↓
CandidateResponse
```

The adapter may preserve:

- prompt or stimulus
- response text
- structured response data
- citations
- tool calls
- attachments
- screenshots
- conversation identifiers
- model or system identifiers
- timestamps and latency
- technical status
- raw response evidence
- provenance

## Supported access directions

The architecture should allow:

```text
API / SDK
Python callable
CLI / subprocess
browser / Playwright
file input
manual capture
replay
```

Not every adapter must exist in the first release.

## File-based examinee input

A file may act as a complete examinee source.

Conceptually:

```yaml
stimulus:
  text: "..."

candidate_response:
  text: "..."

provenance:
  source_type: synthetic | captured_live | manual_capture
  system_id: null
  model_id: null
  captured_at: null
```

This allows the framework to evaluate a prompt-response pair without requiring
direct access to the original model.

The provenance must remain explicit.

A synthetic fixture must never be presented as a captured live response.

---

# 4. Pillar 2 — Evaluator Integration

## Purpose

Connect the framework to an external semantic evaluator.

Examples:

- Claude
- another hosted LLM
- local evaluator model
- project-specific evaluator service
- saved evaluator output
- replay or controlled stub

## Public contract

```text
CandidateResponse
+
AssessmentContract
        ↓
EvaluatorPort
        ↓
ProposedEvaluatorResult
```

The evaluator integration may preserve:

- proposed findings
- target identifiers
- verdicts
- rule references
- evidence references
- rationale
- not-assessed targets
- raw output
- model and provider metadata
- technical status
- latency and cost where available

## Shared infrastructure versus separate roles

The examinee and evaluator may use the same transport technology.

For example, both may use:

```text
HTTP
file input
CLI
browser automation
```

Shared transport utilities are acceptable.

The role contracts must remain separate:

```text
ExamineePort
→ obtains the candidate response

EvaluatorPort
→ proposes findings under an AssessmentContract
```

A generic transport helper must not collapse those responsibilities into one
unbounded `LLMClient`.

## File-based evaluator input

A saved evaluator result may be supplied for:

- deterministic replay
- parser testing
- result-validator testing
- controlled comparison
- offline review

It must still pass the same result validation as a live evaluator output.

---

# 5. Pillar 3 — Validation Engine

## Purpose

The Validation Engine is the hardest and most distinctive part of the framework.

It is broader than a rules catalogue.

It validates:

```text
the examination definition
the basis and scope of the assessment
the proposed evaluator result
the final claim boundary
```

## Internal responsibilities

```text
Validation Engine
├── test-definition validation
├── scenario and stimulus checks
├── Test Basis validation
├── controlled rule catalogue
├── deterministic heuristics
├── evidence requirements
├── rule applicability
├── assessment eligibility
├── target and scope selection
├── allowed-verdict selection
├── prohibited-claim constraints
├── AssessmentContract construction
├── evaluator-result validation
├── technical-status separation
├── accepted and rejected findings
└── claim-boundary enforcement
```

## Pre-evaluation validation

The engine should answer:

```text
Is the evaluation objective explicit?
Does the stimulus exercise the intended risk?
Is the scenario coherent?
Which rules are applicable?
Which rule versions and statuses are allowed?
What evidence is required?
What evidence is available?
What evidence is missing?
Which targets are gradable?
Which targets must remain NOT_ASSESSED?
Which verdicts are permitted?
Which claims are prohibited?
```

## Post-evaluation validation

The engine should reject or limit a proposed result when:

- the `case_id` does not match
- the target is excluded
- the rule is unknown or inapplicable
- required evidence was not supplied
- the evaluator invented evidence
- the verdict is not permitted
- the evaluator makes a prohibited claim
- a partial assessment produces an unsupported overall score
- technical failure is represented as examinee failure
- the rationale supports a broader conclusion than the contract permits

## Rules as a component

The controlled rules catalogue belongs inside the Validation Engine.

Rules are:

> **A controlled, versioned, and continuously developed catalogue of explicit
> constraints, applicability conditions, evidence requirements, permitted
> response strategies, and justified conclusions for selected classes of
> evaluation scenarios.**

Rules are not the whole Validation Engine.

They are one of the engine's inputs and control mechanisms.

---

# 6. Configuration model

All three pillars are intended to be configurable.

## Examinee configuration

Possible configuration:

```text
adapter type
system identifier
input source
authentication reference
conversation settings
capture options
timeout
provenance fields
```

## Evaluator configuration

Possible configuration:

```text
adapter type
provider / model
prompt version
output format
timeout
cost limit
retry policy
raw-output retention
```

## Validation Engine configuration

Possible configuration:

```text
domain pack
rule versions
allowed rule statuses
requested targets
evidence sources
response-strategy policy
allowed verdicts
claim boundaries
review policy
```

## Configurable does not mean uncontrolled

```text
configurable
≠
arbitrary
```

Configuration may select valid behaviour.

It must not bypass framework invariants.

Invalid examples:

```text
factual target allowed
+
mandatory evidence missing
+
PASS / FAIL still permitted
```

```text
result case_id differs from contract case_id
+
findings still accepted
```

```text
rule status DEPRECATED
+
rule silently used as current authority
```

The Validation Engine must reject inconsistent configuration before substantive
evaluation begins.

---

# 7. Public extension points

The future repository should make three extension questions easy to answer.

## How do I connect a new examinee?

Expected documentation:

- required port contract
- adapter lifecycle
- candidate-response envelope
- technical-status mapping
- provenance requirements
- example adapter
- adapter contract tests

## How do I connect a new evaluator?

Expected documentation:

- required port contract
- assessment-contract input
- structured result expectations
- technical-status mapping
- raw-output preservation
- example adapter
- evaluator adapter contract tests

## How do I extend validation?

Expected documentation:

- rule definition format
- rule status and version
- evidence requirements
- target applicability
- verdict constraints
- test-definition checks
- result-validator invariants
- controlled test cases
- validation level and claim boundary

---

# 8. Current implementation mapping

The project does not yet implement the complete architecture.

## Implemented runtime bridge

The following concepts now have executable counterparts:

```text
CandidateResponse
ProposedEvaluatorResult
ExamineePort
EvaluatorPort
ReplayExamineeAdapter
StubEvaluatorAdapter
AssessmentEligibilityChecker
AssessmentContract
EvaluationResultValidator
ScopedEvaluationResult
```

The first controlled scenario is:

```text
INS-MIXED-001
```

The runtime currently demonstrates:

- synthetic replay with explicit provenance
- behavioural targets allowed independently from factual targets
- missing evidence excluding factual assessment
- accepted and rejected evaluator findings
- rejection of out-of-scope findings
- rejection of unknown rule references
- rejection of invented evidence
- rejection of prohibited claims
- rejection of disallowed verdicts
- rejection of mismatched `case_id`
- malformed evaluator output as technical error
- adapter error separated from substantive model failure

## Not yet implemented

Important missing runtime capabilities include:

```text
runtime rule definitions rather than rule IDs only
test-definition validation
formal AssessmentContract builder
rule lifecycle enforcement
bounded evaluator prompt
structured live-result parser
live evaluator adapter behind EvaluatorPort
live or manually captured examinee experiment
configuration loading and validation
public extension guides
```

The next implementation step is the runtime rule catalogue as a component of the
Validation Engine.

---

# 9. Product boundary

The framework should not become:

- a complete insurance, legal, banking, telco, or energy knowledge base
- a universal LLM adapter platform
- an unrestricted orchestration framework
- a certification authority
- an enterprise governance suite
- an autonomous regulated decision engine

Its product value is narrower:

> **Provide configurable integration surfaces and a controlled Validation Engine
> that make LLM evaluation scope, authority, evidence, and conclusions explicit,
> traceable, and testable.**

---

# 10. Protected principles

> **The system under evaluation and external evaluator are configurable external
> roles. The Validation Engine controls the protocol between them.**

> **Configuration may select behaviour, but it may not silently violate
> assessment invariants.**

> **Rules are a component of validation, not a substitute for the complete
> validation process.**

> **Transport flexibility must not weaken role separation, provenance, or result
> validation.**
