# Project roadmap

> **Updated: July 2026**
>
> The roadmap is organised around evidence and architectural risk reduction,
> not feature count.

---

## 1. Current position

The project has a functioning technical baseline and a newer conceptual target.

```text
CURRENT CODE BASELINE
├── heuristic evaluators
├── LLM-assisted evaluator
├── scores and thresholds
├── mocked model responses
├── pytest
├── regression baselines
├── CI
└── Allure reporting
```

```text
DOCUMENTED TARGET ARCHITECTURE
├── explicit Test Basis
├── assessment eligibility
├── scoped gradability
├── controlled rules
├── domain evaluation packs
├── bounded external evaluator
├── deterministic result validation
├── traceable findings
└── claim boundaries
```

The project is currently between those two states.

> **Current phase: build the smallest runtime bridge from the existing
> judge/score prototype to the assessment-grounded architecture.**

---

## 2. Roadmap principles

The roadmap follows:

> **Understand broadly. Implement narrowly.**

> **Validation before expansion.**

> **Never make a stronger claim than the validation level can support.**

> **Adapter breadth follows validation need, not architectural imagination.**

---

## 3. Phase map

| Phase | Name | Status | Primary evidence |
|---|---|---|---|
| 0 | Runnable evaluation prototype | ✅ Implemented | Mock-based tests, CI, Allure |
| 1 | Conceptual reframing and scope control | ✅ Documented | Conceptual model, HLRs, decisions, guardrails |
| 2 | Assessment-grounded runtime bridge | 🔶 Current | Deterministic end-to-end replay slice |
| 3 | Controlled live integration | ⬜ Planned | Small repeated live-model experiment |
| 4 | Evaluator and rule validation | ⬜ Planned | Human-justified labelled cases and failure analysis |
| 5 | Legacy scoring/evaluator migration | ⬜ Planned | Evidence-based keep/change/remove decisions |
| 6 | v1.0 Credible Evaluation Foundation | ⬜ Future gate | Measurable acceptance criteria and scoped claims |
| 7 | Post-v1 research expansion | ⬜ Parked | Only after v1 evidence |

---

# Phase 0 — Runnable evaluation prototype

## Status

✅ **Implemented baseline**

## Existing capability

- hallucination-oriented scenarios
- prompt-injection scenarios
- response-quality scenarios
- regression baselines
- edge cases
- heuristic evaluators
- LLM-assisted evaluation
- scores and thresholds
- mock execution
- pytest
- GitHub Actions
- Allure reporting

## Evidence supported

The baseline demonstrates:

- the pipeline runs
- evaluators can be invoked or mocked
- output can be parsed
- scores can feed pytest decisions
- CI and reporting work

## Evidence not supported

It does not establish:

- independent evaluator accuracy
- domain correctness
- calibrated universal thresholds
- justified LLM-as-a-judge authority
- production-grade robustness assurance

---

# Phase 1 — Conceptual reframing and scope control

## Status

✅ **Documented; runtime implementation pending**

## Completed design work

- project identity reframed beyond `LLM-as-a-judge`
- Test Basis model
- response-strategy model
- assessment eligibility
- scoped gradability
- technical status versus substantive finding
- bounded evaluator
- deterministic pre/post controls
- controlled and evolving rules catalogue
- shared and domain evaluation packs
- mixed-domain insurance case
- scope-drift guardrails
- claim boundaries
- transport-neutral integration direction

## Exit condition

This phase is complete enough to derive the first narrow runtime slice.

It remains open to revision as implementation exposes contradictions.

---

# Phase 2 — Assessment-grounded runtime bridge

## Status

🔶 **Current phase**

## Objective

Prove that the framework can:

```text
allow a justified behavioural assessment
while blocking an unsupported factual assessment
and rejecting evaluator overreach
```

without paid live-model access.

## Vertical slice

```text
INS-MIXED-001
        ↓
ReplayExamineeAdapter
        ↓
CandidateResponse
        ↓
AssessmentEligibilityChecker
        ↓
AssessmentContract
        ↓
StubEvaluatorAdapter
        ↓
ProposedEvaluatorResult
        ↓
EvaluationResultValidator
        ↓
ScopedEvaluationResult
```

## Step 2.1 — Pre-coding acceptance criteria

Define:

- minimum input and output information
- allowed assessment targets
- excluded targets
- required and available evidence
- permitted verdicts
- prohibited findings
- technical error taxonomy
- traceability requirements

## Step 2.2 — Normalised integration contracts

Introduce the smallest useful concepts:

```text
CandidateResponse
ProposedEvaluatorResult
TechnicalStatus
ExamineePort
EvaluatorPort
```

Avoid broad provider abstractions.

## Step 2.3 — Replay and stub adapters

Implement:

```text
ReplayExamineeAdapter
StubEvaluatorAdapter
```

Add shared adapter contract tests.

## Step 2.4 — Deterministic assessment contract

Implement the smallest logic for:

- selected applicable rules
- required evidence
- missing evidence
- allowed targets
- excluded targets
- allowed verdicts
- prohibited claims

## Step 2.5 — Deterministic result validation

Reject proposed findings that:

- target excluded content
- use nonexistent or inapplicable rules
- cite unavailable evidence
- use prohibited verdicts
- convert `NOT_ASSESSED` into `FAIL`
- create an unsupported overall score
- exceed the assessment claim boundary

## Step 2.6 — First end-to-end proof

Run `INS-MIXED-001`.

Expected scope:

```text
GRADABLE
├── intent separation
├── insurance response strategy
├── domain-boundary compliance
├── live-data handling
└── unsupported certainty

NOT ASSESSED
├── actual insurance liability
├── actual Warsaw weather
└── medical / nutritional correctness
```

## Phase 2 exit criteria

- [ ] Same replay input produces deterministic eligibility and validation results
- [ ] Behavioural targets can be allowed independently from factual targets
- [ ] Missing evidence does not create examinee `FAIL`
- [ ] Evaluator is not called for excluded factual assessment, or its excluded findings are rejected
- [ ] Evaluator overreach is preserved and reported, not silently discarded
- [ ] Technical adapter failure remains distinct from substantive result
- [ ] No live API or paid model is required
- [ ] README example can demonstrate `judge can score` versus `judge is allowed to score`

---

# Phase 3 — Controlled live integration

## Status

⬜ **Planned after Phase 2**

## Objective

Connect the stable transport-neutral pipeline to real external systems without
making live access a default dependency.

## Integration order

1. adapt the existing evaluator provider integration behind `EvaluatorPort`
2. select one concrete examinee required by a validation question
3. implement only the adapter that system needs

Possible examinee access:

```text
API
callable
CLI
browser
manual capture
```

The first live experiment does not need all transports.

## Experiment questions

Examples:

- can the evaluator follow allowed/excluded target constraints?
- how often does it invent missing evidence?
- how often does it issue prohibited factual verdicts?
- how consistently does it separate the mixed intents?
- what changes across repeated runs?
- what is the cost and latency?

## Phase 3 exit criteria

- [ ] At least one real examinee response is captured through a documented adapter
- [ ] At least one live evaluator is invoked behind the evaluator port
- [ ] Raw inputs and outputs are preserved
- [ ] Model/provider/access method is recorded
- [ ] Multiple repeated runs are compared
- [ ] Framework and adapter failures are classified separately
- [ ] Live tests remain opt-in and budget-aware
- [ ] Results support only scoped claims

---

# Phase 4 — Evaluator and controlled-rule validation

## Status

⬜ **Planned**

## Objective

Test whether the evaluator and initial rules behave as intended on independently
justified cases.

## Initial dataset classes

```text
KNOWN_GOOD
KNOWN_BAD
BORDERLINE
AMBIGUOUS
INSUFFICIENT_EVIDENCE
EVALUATOR_OVERREACH
NO_APPLICABLE_RULE
MALFORMED_EVALUATOR_OUTPUT
```

## Human basis

Cases should be reviewed against:

- explicit expected strategy
- supplied Test Basis
- applicable rules
- expected gradability
- acceptable finding range
- known disagreement points

Domain-expert review is required only where the claim depends on domain
correctness.

## Phase 4 exit criteria

- [ ] First rules have explicit version and status
- [ ] Validation cases cover both correct and incorrect evaluator behaviour
- [ ] Failure taxonomy is documented
- [ ] Repeatability or instability is measured
- [ ] Human disagreement is recorded rather than hidden
- [ ] Rule coverage gaps lead to limited verdicts
- [ ] Claims remain scoped to validated scenario classes

---

# Phase 5 — Legacy scoring and evaluator migration

## Status

⬜ **Planned after evidence**

## Objective

Decide what should happen to the original scoring architecture.

Possible outcomes per evaluator:

```text
KEEP
→ useful under explicit gradability and claim constraints

REFINE
→ useful but needs new input/output contract

REPLACE
→ mechanism does not support the new methodology

PARK
→ interesting experiment, not needed for v1

REMOVE
→ misleading or unsupported
```

## Questions

- Which dimensions are genuinely gradable?
- Does a numeric score add information over scoped findings?
- Are thresholds supported by labelled evidence?
- Can heuristic evaluators remain as fast guardrails?
- Where should `PASS/FAIL` become `NOT_ASSESSED` or `REVIEW_REQUIRED`?
- Is an overall composite score ever justified in the v1 scope?

## Exit criteria

- [ ] Every retained score has a defined interpretation
- [ ] Every retained threshold has supporting evidence or an explicit provisional label
- [ ] Legacy evaluator claims are updated
- [ ] No ungradable target receives a numeric score
- [ ] Mock tests reflect the new result semantics

---

# Phase 6 — v1.0 Credible Evaluation Foundation

## Status

⬜ **Future evidence gate**

`v1.0` is not a target number of adapters, models, domains, or test cases.

It is the minimum credible evidence level for a narrow framework capability.

## Candidate v1.0 scope

- one controlled domain/scenario pack
- transport-neutral examinee/evaluator contracts
- replay-based deterministic regression
- one controlled live examinee/evaluator path
- bounded evaluator
- deterministic eligibility and result validation
- explicit rule versions and coverage
- scoped findings
- `FAIL`, `NOT_ASSESSED`, review, and technical status separation
- documented evaluator failure modes
- explicit claim boundaries

## Release gate

The exact numerical acceptance thresholds remain intentionally unresolved.

They should be derived from Phase 3 and Phase 4 evidence.

---

# Phase 7 — Post-v1 research directions

## Status

⬜ **Parked**

Possible directions:

- additional domain packs
- additional providers and transports
- multi-judge comparison
- judge-disagreement analysis
- RAG faithfulness
- agent and tool-use evaluation
- MCP evaluation
- PII leakage
- toxicity and fairness
- adversarial case generation
- automated evidence ingestion
- rule-authoring and review workflow
- broader labelled datasets
- production monitoring

Each direction must pass the scope-expansion gate.

---

## 4. Explicitly not on the current roadmap

The current roadmap does not include:

- complete insurance, banking, telco, or energy rulebooks
- universal LLM robustness scoring
- generic browser automation for every chatbot
- automatic legal or regulatory interpretation
- full human-review case-management platform
- mandatory multi-judge consensus
- broad production monitoring
- enterprise governance suite

---

## 5. Current next decision

Before writing production code, define the acceptance criteria for Phase 2:

> **What is the minimum normalised contract and deterministic behaviour required
> to execute `INS-MIXED-001` through replay, eligibility, bounded evaluation, and
> result validation?**

That is the next project decision boundary.
