# Development workflow — SDLC, STLC, branches, and releases

> **Status: active project delivery model from the next implementation sprint.**
>
> The goal is to keep `main` runnable while organising Validation Engine
> development as small, reviewable, evidence-backed vertical slices.

---

## 1. Core workflow

```text
main
→ always runnable and tested

short-lived feature branch
→ one vertical slice or one architectural decision

Pull Request
→ scope, risks, Test Basis, implementation, tests, limitations

merge to main
→ only after review and green validation

tag / release
→ completed roadmap milestone
```

The project will not maintain a long-lived alternative implementation branch.

---

## 2. Why not a permanent development branch

A long-lived `develop`, `validator-v2`, or similar branch would risk:

- divergence from `main`
- hidden integration problems
- documentation describing one branch while code lives in another
- large and difficult merges
- unclear project truth for reviewers
- reduced value of CI on `main`

The preferred model is:

```text
small branch
small diff
explicit acceptance criteria
review
merge
delete branch
```

---

## 3. Branch naming

Recommended patterns:

```text
feature/runtime-rule-catalogue
feature/assessment-contract-builder
feature/bounded-evaluator-prompt
feature/live-evaluator-adapter

fix/evaluator-case-boundary
fix/rule-version-validation

test/evaluator-boundary-cases
docs/validation-engine-guide
```

A branch name should identify the narrow change.

It should not describe an entire future architecture.

Avoid:

```text
feature/new-framework
feature/validator-v2
feature/all-improvements
```

---

## 4. Sprint structure

Each implementation sprint or vertical slice should contain:

```text
Sprint Goal
Requirements / acceptance criteria
Test Basis
Implementation
Unit tests
Integration tests
Controlled evaluation cases
Known limitations
Review
Merge to main
```

### 4.1 Sprint Goal

One sentence describing the behaviour to prove.

Example:

> Load a controlled runtime rule catalogue and ensure that only applicable,
> non-deprecated rules enter the AssessmentContract.

### 4.2 Requirements and acceptance criteria

Criteria must be observable.

Good examples:

```text
duplicate rule IDs are rejected
unknown requested rules stop contract construction
DEPRECATED rules cannot enter a new contract
rule version and source are preserved
INS-MIXED-001 still completes end to end
```

Weak examples:

```text
rules work well
architecture is flexible
validation is robust
```

### 4.3 Test Basis

Every sprint should identify what supports the expected behaviour.

Possible Test Basis:

- architecture decision
- HLR
- scope guardrail
- rule definition
- controlled scenario
- data contract
- Python language or library contract
- existing regression behaviour

The sprint must not invent acceptance expectations only after implementation.

### 4.4 Implementation

Implementation should remain the smallest slice that satisfies the sprint goal.

No unrelated refactoring unless required for correctness.

### 4.5 Unit tests

Cover local invariants and error handling.

### 4.6 Integration tests

Prove interaction between the changed components.

### 4.7 Controlled evaluation cases

Where evaluation semantics are involved, use explicit controlled cases such as:

```text
KNOWN_GOOD
KNOWN_BAD
BORDERLINE
INSUFFICIENT_EVIDENCE
NO_APPLICABLE_RULE
EVALUATOR_OVERREACH
MALFORMED_OUTPUT
```

### 4.8 Known limitations

Document what the sprint does not prove.

### 4.9 Review and merge

Review should confirm both implementation quality and evidence quality.

---

## 5. SDLC and STLC in this project

The toolkit tests evaluation systems, so software correctness alone is not
enough.

Each sprint has two parallel questions.

## SDLC question

> Was the functionality designed and implemented correctly?

Examples:

- parser loads files
- duplicate IDs raise an error
- adapters follow interfaces
- exceptions are classified
- CI remains green

## STLC question

> What evidence shows that the framework makes the intended evaluation decision?

Examples:

- the applicable rule is selected
- an inapplicable rule is rejected
- missing evidence limits the verdict
- evaluator overreach is preserved and rejected
- a technical error does not become examinee `FAIL`
- partial coverage does not become a universal claim

A sprint is incomplete when only one layer is tested.

---

## 6. Definition of Ready

A branch should not begin implementation until the following are known:

```text
1. Sprint Goal
2. affected HLR / decision / guardrail
3. concrete acceptance criteria
4. controlled input or fixture
5. expected result
6. known out-of-scope behaviour
7. validation commands
```

Minor exploratory spikes may precede this, but spike code is not production
completion.

---

## 7. Definition of Done

A slice is done when:

- acceptance criteria are met
- relevant unit tests pass
- relevant integration tests pass
- full default mock suite passes
- compile/static checks used by the project pass
- technical and substantive failures remain correctly separated
- documentation reflects the implemented state
- known limitations are recorded
- no stronger claim is made than the evidence supports
- PR review is complete
- branch is merged to `main`
- branch is deleted

Live-model evidence is required only when the sprint goal depends on live-model
behaviour.

---

## 8. Pull Request content

Each PR should contain a concise structured description.

```text
## Sprint Goal

## Why this slice now

## Scope

## Out of scope

## Test Basis

## Acceptance criteria

## Implementation summary

## Tests executed

## Controlled cases

## Risks and limitations

## Documentation impact

## Claim boundary
```

### Claim boundary example

> This PR demonstrates deterministic runtime rule loading and applicability
> validation. It does not validate domain correctness of the rules or live
> evaluator performance.

---

## 9. Review checklist

### Architecture

- Does the change respect the three-pillar architecture?
- Does transport logic remain outside the Validation Engine?
- Are ExamineePort and EvaluatorPort responsibilities still separate?
- Does configuration preserve invariants?

### SDLC

- Is the code understandable and focused?
- Are failure paths explicit?
- Is traceability preserved?
- Are public contracts documented?
- Is unrelated refactoring avoided?

### STLC

- Is the Test Basis explicit?
- Do tests cover positive and negative decisions?
- Are insufficient-evidence cases represented?
- Are rejected evaluator outputs preserved?
- Are claim boundaries explicit?
- Does a green test support the stated claim?

### Scope

- Does the slice address the current roadmap milestone?
- Was adapter or domain breadth added without a measurement need?
- Did a documented future idea silently become implementation scope?

---

## 10. Commit strategy

Prefer logically complete commits.

Examples:

```text
feat: add controlled runtime rule catalogue
test: expand rule applicability cases
fix: reject deprecated rules during contract construction
refactor: place Anthropic behind evaluator port
docs: document rule authoring contract
```

Avoid mixing:

```text
new rule catalogue
+
provider refactor
+
README redesign
+
unrelated evaluator cleanup
```

unless they are inseparable for a single acceptance criterion.

---

## 11. Tags and milestone releases

Tags record completed evidence milestones.

They are not marketing labels and do not imply production maturity.

### Proposed milestone tags

```text
v0.3.0-runtime-bridge
```

Created only when Phase 2 is complete:

- runtime rule catalogue
- AssessmentContract construction
- deterministic eligibility
- bounded evaluator request/result shape
- result validation
- replay-based end-to-end proof
- documentation aligned with runtime

```text
v0.4.0-bounded-evaluator
```

Created when one real evaluator is integrated behind `EvaluatorPort` and can
follow the constrained protocol under controlled tests.

```text
v0.5.0-controlled-live-validation
```

Created when a scoped live examinee/evaluator experiment is repeatable and
compared with independently justified expectations.

These versions remain pre-v1 research milestones.

---

## 12. Current sprint sequence

### Completed slice A — executable assessment contract

Implemented:

- normalised candidate and evaluator result models
- separate ports
- replay examinee
- stub evaluator
- eligibility checker
- AssessmentContract
- result validator
- `INS-MIXED-001`
- technical versus substantive status separation

### Completed slice B — evaluator boundary violations

Implemented validation for:

- unknown rules
- unavailable evidence
- prohibited claims
- disallowed verdicts
- mismatched `case_id`
- malformed evaluator output

### Completed slice C — runtime rule catalogue

Implemented branch:

```text
feature/runtime-rule-catalogue
```

Sprint Goal:

> Replace opaque rule IDs with controlled, versioned runtime rule definitions
> inside the Validation Engine.

Implemented:

- versioned runtime rule definitions
- five controlled `DRAFT` rules
- deterministic catalogue loading
- duplicate, unknown, malformed, missing-file, and status errors
- rule applicability and evidence participation in eligibility
- resolved rules inside the AssessmentContract
- process-error separation before evaluator invocation

The slice did not add live LLM integration, broad domain catalogues,
jurisdiction handling, a generic configuration framework, or a large rules
engine.

### Completed slice D — AssessmentContract builder

Implemented:

- public `AssessmentContractBuilder`
- cross-field test-definition validation
- rule resolution before eligibility evaluation
- pure evidence-based `AssessmentEligibilityChecker`
- defensive read-only contract mappings
- configuration errors before evaluator invocation

Claim boundary:

> The slice validates the current runtime structure and cross-field invariants.
> It does not prove that the complete conceptual Test Basis is sufficient or
> domain-correct.

### Current slice E — bounded evaluator request and parser

```text
feature/bounded-evaluator-prompt
```

### Later integration slice

```text
feature/live-evaluator-adapter
```

Each remains subject to its own acceptance criteria and scope gate.

---

## 13. Protected principles

> **Main is the public project truth.**

> **Branches are short-lived experiments that become product capability only
> after review and merge.**

> **Every slice must prove both software behaviour and evaluation behaviour.**

> **Tags mark completed evidence milestones, not architectural ambition.**
