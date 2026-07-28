# Scope drift guardrails

> **Status: active project guardrails.**
>
> These boundaries protect the project from turning every valid conceptual
> discovery into immediate implementation scope.

`llm-qa-toolkit` is deliberately allowed to understand a broad problem.

It is not allowed to implement the whole problem at once.

The project follows three connected principles:

> **Never make a stronger claim than the validation level can support.**

> **Understand broadly. Implement narrowly.**

> **Validation before expansion.**

---

## 1. Why these guardrails exist

The project is maturing from a runnable LLM-evaluation demo into a research
prototype and technical skeleton of a future evidence-grounded evaluation
framework.

That maturation naturally reveals adjacent problems:

```text
Test Basis
    → provenance
        → version management
            → governance

gradability
    → expert review
        → workflow
            → roles and permissions

scoped findings
    → audit trail
        → compliance reporting
            → certification
```

Each step is logically connected.

That does not mean each step belongs in the same product or in the next
implementation slice.

Without explicit guardrails, the repository could gradually become an attempt
to build all of the following at once:

- LLM testing framework
- AI robustness audit platform
- evidence-management system
- compliance and governance product
- domain-knowledge platform
- human-review workflow
- universal benchmarking suite
- production decision engine
- certification system

That would make the project broader while making its evidence weaker.

These guardrails preserve a smaller core proposition:

> **Define and execute a controlled, evidence-grounded protocol for evaluating
> an external LLM, using constrained evaluators and scoped, traceable findings.**

---

# 2. Product identity boundary

## SG-01 — This is an evaluation framework skeleton, not a complete AI assurance platform

### Inside the boundary

The project may define and validate:

- evaluation objectives
- risk-oriented scenarios
- stimuli and model-visible context
- Candidate Responses
- Test Basis
- expected response strategies
- behavioural constraints
- gradability prerequisites
- evaluator inputs and rubrics
- scoped findings
- rationale and traceability
- review or escalation disposition

### Outside the boundary

The project does not currently claim to provide:

- complete AI-system assurance
- formal regulatory compliance
- organisational AI governance
- independent audit certification
- production approval for high-impact deployment
- legal or medical conformity assessment

### Why

A controlled evaluation protocol can produce useful evidence.

It cannot by itself prove that an entire organisation, product, model, dataset,
process, and deployment lifecycle is compliant or safe.

---

## SG-02 — The framework controls the protocol, not evaluator cognition

### Inside the boundary

The framework may constrain an external evaluator through:

```text
role and prompt
context
evidence package
rubric
assessment targets
output schema
required rationale
gradability rules
consistency validation
```

### Outside the boundary

The framework cannot guarantee that the evaluator:

- truly understands the domain
- reasons correctly internally
- has no bias
- interprets every source correctly
- is more competent than the examinee
- does not rely on unsupported internal knowledge

### Why

Structured prompts and schemas can limit observable behaviour.

They cannot manufacture missing expertise or ground truth.

The framework therefore controls:

> **the conditions under which a finding may be accepted**

not:

> **the private reasoning process of the model producing it.**

---

## SG-03 — The project uses domain knowledge; it does not become the domain authority

### Inside the boundary

The framework may consume supplied:

- laws and regulations
- policies
- product rules
- tariffs
- procedures
- deterministic calculations
- domain-expert reference decisions

It may preserve their source, version, and applicability metadata.

### Outside the boundary

The framework does not itself become:

- a legal interpretation authority
- a medical authority
- an underwriting authority
- a banking-policy owner
- an energy-regulation authority
- a source of official administrative decisions

### Why

The project evaluates behaviour against a Test Basis.

It should not silently author the Test Basis for domains where correctness
requires accountable specialist ownership.

---

# 3. Evidence and Test Basis boundary

## SG-04 — Validate supplied Test Basis before building full evidence infrastructure

### Inside the boundary

The project may require explicit Test Basis components:

```text
Facts / ground truth
Rules / policies / regulations
Expected response strategy
Behavioural constraints
Required evidence
Gradability prerequisites
Provenance / applicability
```

It may validate that required fields exist and are internally coherent.

### Outside the boundary

Pre-v1.0 does not require:

- enterprise document ingestion
- full RAG infrastructure
- automatic legal-source discovery
- document lifecycle management
- policy approval workflows
- cryptographic evidence custody
- organisation-wide evidence catalogues

### Why

The immediate research question is whether supplied evidence can support a
scoped finding.

Building a general evidence platform before validating that evaluation model
would reverse the project order.

---

## SG-05 — Provenance must be represented before it is fully automated

### Inside the boundary

The model should understand that evidence may need:

```text
source
version
effective date
jurisdiction
product
customer segment
scope
applicability
```

A first slice may accept these values as manually supplied metadata.

### Outside the boundary

The first credible version does not need to automatically:

- monitor every source for updates
- resolve legal conflicts
- determine jurisdiction
- infer policy applicability
- certify document authenticity

### Why

A concept can be essential to correctness without requiring a complete subsystem
in the first implementation.

Manual explicit input is acceptable when it preserves the epistemic boundary
being validated.

---

# 4. Human responsibility boundary

## SG-06 — Support escalation without building a complete case-management product

### Inside the boundary

The evaluation result may express:

```text
REVIEW_REQUIRED
DOMAIN_EXPERT_REVIEW
ESCALATION_REQUIRED
NO_VERDICT_POSSIBLE
```

It may preserve the reason and unresolved assessment targets.

### Outside the boundary

The project does not currently need:

- review queues
- role-based assignment
- SLA tracking
- email or chat notifications
- approval chains
- reviewer dashboards
- electronic signatures
- case-management analytics

### Why

The conceptual need for accountable human review must exist before automation.

A disposition field can validate the decision boundary without creating a new
workflow product.

---

## SG-07 — The framework supports human responsibility; it does not transfer it to the judge

### Inside the boundary

The framework may detect that:

- evidence is insufficient
- specialist interpretation is required
- model disagreement is material
- impact requires human accountability

### Outside the boundary

The system must not claim that an LLM judge:

- replaces a regulated professional
- owns the final high-impact decision
- legally authorises an outcome
- removes the need for accountable human review

### Why

Automation can organise evidence and identify uncertainty.

It cannot eliminate responsibility merely by producing a confident structured
output.

---

# 5. Evaluation and scoring boundary

## SG-08 — Scoped findings before universal scores

### Inside the boundary

The project may produce findings such as:

```text
response strategy      → PASS
policy adherence       → FAIL
decision integrity     → FAIL
factual claim          → NOT_ASSESSED
numeric outcome        → UNGRADABLE
```

### Outside the boundary

The project should not default to:

```text
overall quality = 82/100
```

when dimensions differ in:

- importance
- evidence quality
- gradability
- severity
- consequence

### Why

A single score can hide the most important failure and imply comparability that
has not been validated.

Thresholds and aggregation should follow empirical validation, not aesthetic
convenience.

---

## SG-09 — Benchmarking is downstream of evaluator validation

### Inside the boundary

The project may compare systems only for dimensions where:

- the evaluator has been validated
- the Test Basis is adequate
- assessment targets are comparable
- uncertainty is reported

### Outside the boundary

The current project does not need to become:

- a universal model leaderboard
- a provider marketplace
- a benchmark for every domain
- a definitive ranking of commercial LLMs

### Why

Scaling an unvalidated measurement does not improve its credibility.

It only produces more precise-looking unsupported results.

---

## SG-10 — Evaluation automation is not autonomous regulatory decision-making

### Inside the boundary

The framework may automate:

- test execution
- evidence packaging
- evaluator invocation
- schema validation
- gradability checks
- finding generation
- result traceability
- review routing decisions

### Outside the boundary

The framework does not automatically:

- approve insurance coverage
- set premiums
- grant or deny credit
- issue legal determinations
- provide medical diagnosis
- make administrative decisions
- execute regulated customer outcomes

### Why

The framework evaluates AI behaviour.

It is not the production system making the regulated decision.

---

# 6. Technology and productisation boundary

## SG-11 — Provider breadth follows validation need

### Inside the boundary

Additional providers may be added when they are necessary to test a defined:

- evaluator hypothesis
- model-comparison question
- privacy or deployment constraint
- reproducibility concern

### Outside the boundary

The project should not add providers merely to display integration breadth.

### Why

Every integration creates maintenance work and apparent product maturity.

Provider count is not evidence of evaluator reliability.

---

## SG-12 — Reporting supports traceability, not product theatre

### Inside the boundary

Reporting may show:

- test objective
- assessment scope
- evidence references
- findings
- rationale
- technical status
- unresolved targets
- disposition

### Outside the boundary

Pre-v1.0 does not require:

- a commercial dashboard
- multi-tenant administration
- billing
- user management
- polished workflow UI
- executive compliance analytics

### Why

A simple report can validate the information model.

A product surface should not be built before the underlying verdicts are
credible.

---

# 7. Conceptual breadth vs implementation scope

## SG-13 — Documentation does not automatically create implementation scope

A concept may belong in:

```text
conceptual model
high-level requirement
known limitation
future idea
research question
```

without becoming:

```text
next module
Pre-v1.0 acceptance criterion
v1.0 blocker
```

### Why

The project must understand adjacent risks to avoid false claims.

Understanding a risk does not prove that implementing its complete solution is
necessary for the current validation objective.

---

## SG-14 — Pre-v1.0 proves the smallest credible evaluation slice

The current direction should remain narrower than the complete conceptual model.

A plausible minimum slice may demonstrate that the framework can:

- accept an explicit evaluation objective and scenario
- accept a supplied Test Basis
- distinguish model-visible context from evaluator-only evidence
- define or validate expected response strategy
- determine whether selected assessment targets are gradable
- constrain an evaluator to those targets
- separate technical execution status from substantive findings
- return scoped findings with rationale and evidence references
- express review or escalation when authority is insufficient
- validate this behaviour on controlled known cases

It does not need to solve every future domain, evidence, workflow, or governance
problem.

### Why

A small validated slice is stronger than a broad unvalidated architecture.

---


## SG-15 — Do not use recursive judge chains as a substitute for assessment basis

### Inside the boundary

The project may later compare:

- evaluator providers
- evaluator models
- independent judge outputs
- disagreement patterns

### Outside the boundary

The project should not treat:

```text
more judges
more votes
more agreement
```

as a substitute for:

```text
valid Test Basis
applicable rules
sufficient evidence
bounded scope
external validation
```

### Why

Several evaluators can share the same unsupported assumption.

Consensus is not automatically correctness.

The primary control mechanism should be deterministic assessment boundaries
around a bounded evaluator.

---

## SG-16 — Domain packs cover selected scenario classes, not complete industries

### Inside the boundary

A domain pack may define and validate a narrow subset such as:

```text
mixed-domain questions
insufficient evidence
unsupported certainty
live-data requests
selected coverage-information scenarios
```

### Outside the boundary

A pack does not claim to encode:

- all insurance law
- all product wording
- all underwriting logic
- all banking regulation
- all telco processes
- all energy-market rules

### Why

The rule space is open-ended, versioned, jurisdiction-dependent, and owned by
accountable domain specialists.

Selected validated coverage is stronger than fictional completeness.

---

## SG-17 — Missing rule coverage limits the verdict

When no applicable sufficiently authoritative rule exists, the framework should
represent the gap explicitly.

Possible conceptual outcomes:

```text
NO_APPLICABLE_RULE
NOT_ASSESSED
REVIEW_REQUIRED
```

The evaluator must not be invited to invent an evaluation standard from general
model knowledge.

### Why

A missing rule is a limitation of the evaluation basis.

It is not evidence that the system under evaluation failed.

---

## SG-18 — Rule growth must be controlled and evidence-led

New rules should not enter validated use merely because they are plausible.

Rule development should preserve, as applicable:

```text
source / owner
version
status
scope
applicability
test cases
review evidence
known gaps
```

A first implementation slice should validate a few rules deeply rather than add
a broad unreviewed catalogue.

### Why

Rule count is not evidence of rule quality.

An expanding unvalidated catalogue would recreate the same problem as an
unvalidated evaluator: confident outputs built on weak foundations.

---



## SG-19 — Transport neutrality does not require adapter completeness

### Inside the boundary

The architecture may define stable contracts for:

```text
API
callable
CLI
browser
replay
manual capture
```

### Outside the boundary

The project does not need to implement every transport before the first
assessment-grounded slice.

### Rule

Add an adapter only when a concrete validation target requires it.

The first slice should prefer replay and stubs.

---

## SG-20 — Browser automation remains outside the evaluation core

A browser-only examinee may be accessed through a Playwright adapter.

The following remain adapter-specific:

```text
login
selectors
waiting
conversation creation
response extraction
screenshots
trace capture
```

They must not leak into:

```text
rule applicability
assessment eligibility
verdict semantics
claim boundaries
```

### Why

A brittle chat UI must not redefine the evaluation methodology.

---

## SG-21 — Live-model access is a validation resource, not a development dependency

Default development and CI should not require paid or unstable live-model calls.

Live integrations should be used for scoped experiments with:

- explicit purpose
- fixed budget
- preserved raw evidence
- known model/version where available
- repeat count
- documented limitations

### Why

The project should remain runnable and reviewable without external spending.

---


# 8. Scope classification model

Every newly discovered idea should be classified before implementation.

## NOW — implement in the current slice

Use when the capability:

- is necessary for the current validation objective
- directly supports the core product proposition
- has measurable acceptance criteria
- can be tested with available evidence
- does not depend on several unvalidated subsystems

Current runtime-bridge examples:

```text
minimum CandidateResponse contract
minimum ProposedEvaluatorResult contract
separate ExamineePort and EvaluatorPort
ReplayExamineeAdapter
StubEvaluatorAdapter
assessment eligibility
result validation
INS-MIXED-001 end-to-end replay
```

## RECORD — represent conceptually or as metadata

Use when the concept:

- materially affects correctness
- must be visible in the model
- can currently be supplied manually
- does not require a complete automated subsystem

Examples:

```text
evidence version
jurisdiction
review disposition
applicability note
```

## PARK — retain as a future research or product direction

Use when the idea:

- is relevant but not required for the current claim
- creates substantial new workflows
- needs additional research or domain ownership
- would distract from evaluator validation

Examples:

```text
broad API-provider catalogue
Python-callable adapter
CLI adapter
generic browser-chat adapter
automatic legal-source ingestion
human-review dashboard
multi-provider leaderboard
full evidence lifecycle
```

## SEPARATE — treat as another product or programme

Use when the idea changes the project category into:

- governance platform
- compliance-management suite
- certification authority
- production decision engine
- enterprise document-management system

---

# 9. Expansion gate

A new implementation capability should not enter the active roadmap until the
following questions have explicit answers.

```text
1. Which evaluation risk or HLR does it address?

2. Which current or planned claim would be invalid without it?

3. What is the smallest testable behaviour?

4. What evidence will validate that behaviour?

5. Can the concept be represented manually before being automated?

6. Does it create a new product category, workflow, or accountable role?

7. Which existing scope item will be delayed or removed to make room?

8. What would make us stop or reject this direction?
```

A capability that has no answers to these questions belongs in `future-ideas.md`,
not in code.

---

# 10. Drift warning signs

The project may be drifting when:

- the architecture grows faster than evaluator-validation evidence
- new providers are added without a measurement question
- additional judges are added without an external correctness basis
- rule count grows faster than rule review and validation evidence
- domain packs are described as complete industry knowledge
- missing rule coverage is hidden by evaluator improvisation
- dashboards appear before trustworthy findings
- workflows are built before review rules are validated
- domain content is generated internally without accountable ownership
- overall scores are added before dimension validity is established
- every HLR is treated as a Pre-v1.0 feature
- documentation of a risk is interpreted as commitment to automate it
- the project claims audit, compliance, or assurance without corresponding
  standards, evidence, and independent validation
- the roadmap contains more platform features than validation experiments

---

# 11. Decision rule

When uncertain, apply:

```text
Does this improve the credibility of the next evaluation claim?
        │
        ├── YES → define the smallest measurable slice
        │
        └── NO
             ↓
Can it be represented explicitly without automation?
        │
        ├── YES → RECORD
        │
        └── NO
             ↓
Is it adjacent and potentially valuable?
        │
        ├── YES → PARK
        │
        └── NO → SEPARATE / REJECT
```

---

# 12. Current protected direction

The protected direction of `llm-qa-toolkit` is:

> **A focused, evidence-grounded evaluation framework skeleton for
> regulated-domain LLM scenarios, designed to control the evaluation protocol,
> use a controlled and evolving rules layer, bound evaluator authority,
> determine assessment scope, and return traceable findings without overstating
> certainty.**

The project may continue to mature conceptually.

Implementation expansion must remain earned by validation.
