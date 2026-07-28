# Conceptual model — regulated-domain LLM evaluation

> **Status: working conceptual model (v0.2), not committed code architecture.**

This document captures the current conceptual model behind `llm-qa-toolkit`
before the next implementation stage.

Its purpose is to answer:

> **What must be true for an evaluation verdict to mean something?**

The model is intentionally more abstract than code, data models, or acceptance
criteria. It should be refined through further design discussion and validation
before it is translated into implementation.

The current project principle remains:

> **Never make a stronger claim than the validation level can support.**

---

## 0. Project identity and target framework role

The term `framework` describes the intended direction more accurately than the
current maturity level.

### Current state

At present, `llm-qa-toolkit` is best described as:

> **A research-oriented evaluation harness and technical framework skeleton,
> supported by a working conceptual model, lightweight methodology, and
> high-level requirements for regulated-domain LLM evaluation.**

The repository already contains a runnable technical prototype:

```text
test scenarios
provider / mock integration
heuristic evaluators
LLM-assisted evaluators
scoring and thresholds
pytest orchestration
CI and Allure reporting
```

It does not yet provide a validated, production-ready evaluation framework.

### Target system relationship

The intended framework sits between two externally supplied roles:

```text
EXTERNAL SYSTEM UNDER EVALUATION
          "examinee"
                │
                ▼
┌───────────────────────────────────────────────────────┐
│              EVALUATION FRAMEWORK                    │
│                                                       │
│  test-definition validation                          │
│  Test Basis and evidence control                     │
│  context separation                                  │
│  evaluation strategy and rubric                      │
│  evaluator constraints and output schema             │
│  assessment eligibility and scope                    │
│  findings, rationale, review, and escalation          │
└────────────────────────┬──────────────────────────────┘
                         │
                         ▼
              EXTERNAL LLM EVALUATOR
                    "examiner"
                         │
                         ▼
              SCOPED EVALUATION RESULT
```

The framework is not the source of all domain truth and is not intended to
replace domain experts.

Its role is to control and make explicit:

- the evaluation objective
- the risk or requirement under test
- the scenario and stimulus
- the Test Basis
- model-visible context
- evaluator-only evidence
- expected response strategy
- gradability prerequisites
- allowed assessment scope
- required result structure
- review and escalation conditions
- traceability from evidence to finding and claim

### Protocol control, not cognition control

The framework may constrain an external evaluator through:

```text
prompt and role definition
evidence package
rubric
assessment targets
output schema
required rationale
validation and consistency checks
```

It cannot guarantee that the evaluator:

- truly understands the domain
- interprets every source correctly
- is unbiased
- is more competent than the system under evaluation
- will not invent missing ground truth

Therefore:

> **The framework controls the evaluation protocol, the conditions under which a
> verdict may be issued, and the boundaries of the allowed claim. It does not
> control the evaluator's internal reasoning or manufacture missing expertise.**

### Test-definition responsibility

The framework should eventually validate more than prompt syntax.

It should help determine whether:

```text
the evaluation objective is defined
the stimulus exercises the intended risk
the scenario is coherent
the expected response strategy is justified
the Test Basis is sufficient and applicable
the assessment target is gradable
the evaluator has authority to judge it
the resulting finding can support the intended claim
```

This identity is a target direction, not a claim that all of these capabilities
already exist in code.

### Central conceptual shift — assessment eligibility before judgement

The project began with a judge-centric implementation model:

```text
candidate response
        ↓
heuristic / LLM evaluator
        ↓
score / threshold / verdict
```

That model remains useful as a description of the current technical prototype.

It is no longer sufficient as the conceptual model.

The framework should first establish:

```text
what is being tested
what behaviour is expected
what Test Basis supports that expectation
what evidence is available
which assessment targets are gradable
what authority the evaluator has
```

Only then should an evaluator produce findings.

The conceptual order is therefore:

```text
TEST DEFINITION
        +
CANDIDATE RESPONSE
        +
TEST BASIS
        ↓
ASSESSMENT ELIGIBILITY
& SCOPE DETERMINATION
        ↓
EVALUATION MECHANISM
        ↓
SCOPED FINDINGS
```

This leads to a core distinction:

```text
LLM-AS-A-JUDGE
→ one possible evaluation mechanism

ASSESSMENT-GROUNDED METHODOLOGY
→ determines whether the mechanism has a justified target,
  sufficient evidence, bounded scope, and authority to judge
```

Therefore:

> **The project does not begin by asking how to score a response. It begins by
> asking whether there is a justified assessment to perform, what part is
> gradable, and what the resulting evidence is allowed to support.**

---

## 1. Meta-assumption: the system under evaluation operates in a regulated domain

The primary target is not a generic conversational assistant whose main quality
goal is to sound helpful.

The conceptual target is an AI system operating in a regulated or
high-consequence domain where responses may be constrained by:

- law or regulation
- business rules
- policy wording
- tariffs or calculation rules
- customer-specific facts
- safety constraints
- procedural requirements
- disclosure restrictions
- escalation rules

Examples include banking, insurance, energy, and potentially healthcare, legal
services, or public administration.

The system may still use conversational language, but fluent conversation is not
the primary correctness criterion.

A response can be:

```text
fluent
polite
plausible
helpful-sounding
```

and still be unacceptable because it:

```text
violates policy
ignores a material fact
uses insufficient evidence
accepts a false premise
yields to user pressure
discloses restricted information
issues a verdict outside its authority
```

Therefore:

> **Correctness in regulated-domain AI is not only linguistic correctness.**

---

## 2. Evaluation intent comes before the question

A question or prompt is only a **test stimulus**.

It does not define by itself what is being tested.

The conceptual chain is:

```text
EVALUATION OBJECTIVE
        ↓
RISK / REQUIREMENT
        ↓
TEST CONDITION / SCENARIO
        ↓
TEST STIMULUS
        ↓
SYSTEM UNDER EVALUATION
        ↓
CANDIDATE RESPONSE
```

Example:

```text
Stimulus:
"What is the weather in Bucharest today?"
```

When asked to a legal-domain assistant without live weather access, the test may
not evaluate meteorological knowledge at all.

It may evaluate:

```text
domain-boundary awareness
honesty about capabilities
data-access awareness
hallucination resistance
appropriate redirection
```

Therefore:

> **The meaning of a stimulus comes from the evaluation objective and scenario,
> not from the wording of the question alone.**

---

## 3. Candidate response: first evaluate strategy, then execution

A good response is not always a direct factual answer.

The appropriate response type depends on:

- question validity
- available evidence
- domain scope
- safety constraints
- policy constraints
- ambiguity
- user behaviour
- required process state

The system may need to:

```text
ANSWER_DIRECTLY
CLARIFY
CORRECT_FALSE_PREMISE
REFUSE
REDIRECT
REQUEST_EVIDENCE
APPLY_DEFINED_FALLBACK
ESCALATE
```

This creates two distinct evaluation layers.

### 3.1 Response strategy selection

First ask:

> **Did the system choose the right type of behaviour for this situation?**

Examples:

```text
false premise
→ correct premise before answering

insufficient context
→ clarify

outside supported domain/data access
→ acknowledge boundary and redirect

unsafe or unauthorized request
→ refuse or limit

strategic ambiguity around required data
→ resolve ambiguity or apply defined fallback
```

### 3.2 Response execution quality

Only then ask whether the selected behaviour was executed well:

```text
factually correct?
logically coherent?
policy-compliant?
appropriately complete?
clear?
safe?
evidence-grounded?
```

A system may fail even when individual sentences are factually plausible because
it selected the wrong response strategy.

---

## 4. Controlled and evolving rules layer

The rules layer is not intended to become a complete encoded rulebook for an
entire regulated industry.

It is defined as:

> **A controlled, versioned, and continuously developed catalogue of explicit
> constraints, applicability conditions, evidence requirements, permitted
> response strategies, and justified conclusions for selected classes of
> evaluation scenarios.**

### 4.1 Working response-behaviour rules discovered so far

These are working conceptual rules, not yet formal acceptance criteria.

#### False premise

```text
false or misleading premise
        ↓
do not silently accept it
        ↓
correct / clarify / reframe
```

#### Insufficient information

```text
valid question
+ insufficient required context
        ↓
clarify / request evidence
```

#### Unsupported current fact

```text
current factual question
+ no current authoritative data
        ↓
state limitation
        ↓
do not fabricate
```

#### Domain boundary

```text
question outside supported competence
        ↓
acknowledge boundary
        ↓
redirect appropriately
```

#### Safety or disclosure boundary

```text
truthful information exists
+ disclosure is unsafe / unauthorized
        ↓
withhold / refuse / limit / redirect
```

Therefore:

> **Truthfulness does not imply unrestricted disclosure.**

#### User pressure or preferred outcome

```text
user wants favourable result
+ required rule/evidence still applies
        ↓
do not bend requirement
        ↓
maintain process integrity
```

Therefore:

> **Helpful does not mean compliant with the user's preferred outcome.**

#### Future uncertainty

```text
future cannot be known with certainty
        ↓
do not invent certainty
        ↓
apply current rule / declared assumption / defined fallback
```

### 4.2 What one rule should express

A rule may need to represent:

```text
identity and version
status and owner
scope and applicability
trigger condition
expected response strategy
forbidden behaviour
required evidence
gradable assessment targets
non-gradable targets
allowed verdicts
prohibited claims
source and rationale
```

The exact runtime schema is deliberately unresolved.

### 4.3 Rule lifecycle

Conceptual rule states may include:

```text
DRAFT
REVIEWED
VALIDATED
DEPRECATED
PROJECT_SPECIFIC
```

A rule being present in a file does not automatically make it authoritative.

Its status, version, ownership, and applicability affect whether it can support a
substantive finding.

### 4.4 Rule coverage is necessarily partial

A domain pack should declare:

```text
supported scenario classes
unsupported scenario classes
known gaps
applicable rule versions
coverage status
```

When no suitable rule exists:

```text
NO_APPLICABLE_RULE
        ↓
NOT_ASSESSED / REVIEW_REQUIRED
```

not:

```text
evaluator invents a standard from general knowledge
```

Therefore:

> **Missing rule coverage must limit the verdict, not encourage evaluator
> improvisation.**

### 4.5 Domain specialisation does not imply competence isolation

A specialised model may retain broad knowledge from its base model.

The protocol must not infer operational authority from the model label.

```text
latent capability
≠
authorised capability
```

Even when a domain model can answer an out-of-domain question, the protocol
determines:

- where that knowledge may be used
- whether current evidence or tools are required
- when the model should refuse or redirect
- whether only domain-boundary behaviour is gradable
- which substantive claims remain outside evaluator authority

### 4.6 Shared and domain-specific packs

Conceptual organisation:

```text
domains/
├── shared/
│   ├── multi-intent rules
│   ├── out-of-domain rules
│   ├── live-data rules
│   ├── evidence rules
│   └── verdict constraints
│
├── insurance/
├── banking/
├── telco/
└── energy/
```

`shared` rules govern evaluation behaviour that is not owned by one regulated
domain.

Domain packs add supplied domain-specific constraints and evidence requirements.

The framework consumes those rules.

It does not silently become their accountable domain owner.

---

## 5. Test Basis — more than an answer key

The original "answer key" analogy is too narrow.

In regulated-domain evaluation there may be no single canonical textual answer.

The Test Basis defines:

> **On what basis do we know what the system should do, what can be judged, and
> when a verdict is justified?**

Current model:

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

### 5.1 Facts / ground truth

What is actually known to be true for the evaluated claim?

Examples:

- customer facts
- transaction facts
- product data
- policy content
- deterministic reference outcome
- verified current state

### 5.2 Rules / policies / regulations

Which rules govern the behaviour or decision?

Examples:

- business rules
- underwriting rules
- legal requirements
- internal policy
- tariff logic
- procedural requirements

### 5.3 Expected response strategy

What type of response is appropriate?

Examples:

```text
ANSWER_DIRECTLY
CLARIFY
CORRECT_FALSE_PREMISE
REFUSE
REDIRECT
REQUEST_EVIDENCE
APPLY_DEFINED_FALLBACK
ESCALATE
```

### 5.4 Behavioural constraints

What must the system not do even if the user requests or pressures it?

Examples:

- must not omit a material risk factor without basis
- must not fabricate a required fact
- must not bypass a mandatory process step
- must not convert ambiguity into a convenient assumption
- must not reveal restricted information
- must not issue an unsupported high-impact verdict

### 5.5 Required evidence

What information must exist for a particular conclusion?

Example for premium correctness:

```text
customer data
vehicle data
declared drivers
discounts / surcharges
applicable tariff
calculation rules
```

### 5.6 Gradability prerequisites

What must be available before a specific aspect can be judged reliably?

This may differ by assessment target:

```text
response strategy
policy adherence
factual claim
numeric outcome
legal interpretation
```

### 5.7 Provenance / applicability

Evidence must not be trusted merely because it exists.

Relevant properties may include:

```text
source
version
effective date
jurisdiction
product
customer segment
scope
```

True but outdated or inapplicable evidence may be as dangerous as missing
evidence.

---

## 6. Outcome correctness and behavioural correctness are separate

The model distinguishes:

```text
OUTCOME CORRECTNESS
```

from:

```text
BEHAVIOURAL / PROCESS CORRECTNESS
```

A correct final result does not automatically prove a correct decision process.

Example:

```text
final premium happens to be correct
+
required young-driver information was improperly ignored
        ↓
outcome may appear correct
process is still wrong
```

The reverse is also possible.

A system may correctly refuse to provide a final answer because evidence is
insufficient.

```text
no final factual answer
+
correct clarification / refusal / escalation
        ↓
behaviour can be correct
```

Therefore:

> **Correct outcome does not necessarily imply correct decision process.**

---

## 7. Strategic user behaviour and decision integrity

Users do not need technical prompt injection to pressure a regulated process.

Realistic user behaviour may include:

- minimising inconvenient facts
- answering indirectly
- selective disclosure
- plausible deniability
- emotional pressure
- reframing required information as irrelevant
- asking for an exception
- threatening to leave for a competitor
- attempting to obtain a favourable interpretation

Working concepts:

```text
decision integrity
policy adherence
constraint compliance
manipulation resistance
evidence sufficiency
strategic ambiguity handling
```

Example:

```text
"My 18-year-old daughter got her licence a month ago,
but who would let an inexperienced driver use a 400k car?"
```

This is not an explicit declaration that she will not use the vehicle.

A system must not silently convert persuasive framing into missing evidence.

If the user later says:

```text
"How should I know what happens in the future?
I'm not Nostradamus."
```

the regulated-domain system should not reward ambiguity by inventing the
customer-favourable assumption.

It should follow the applicable rule:

```text
clarify
request required declaration
apply policy-defined fallback
or escalate
```

depending on the Test Basis.

This is a parked research direction and a source of future realistic scenarios,
not automatically new Pre-v1.0 feature scope.

---

## 8. Assessment eligibility, gradability, and scope

A binary:

```text
gradable / ungradable
```

is too simple.

Before substantive judgement, the evaluation process should determine:

> **Which aspects can actually be judged reliably with the available Test Basis?**

Conceptually:

```text
EVALUATION OBJECTIVE
        +
CANDIDATE RESPONSE
        +
TEST BASIS
        ↓
ASSESSMENT ELIGIBILITY
& SCOPE DETERMINATION
        ↓
WHAT CAN BE RELIABLY ASSESSED?
```

Possible conceptual states:

```text
FULLY_GRADABLE
PARTIALLY_GRADABLE
BEHAVIOUR_ONLY
REVIEW_REQUIRED
UNGRADABLE
```

These are conceptual categories, not committed implementation enums.

### Gradability can be per assessment target

Example:

```text
response strategy       → gradable
policy adherence        → gradable
factual claim A         → gradable
factual claim B         → ungradable
final numeric outcome   → ungradable
```

Therefore:

> **Gradability is relative to the evaluation objective and assessment target,
> not an intrinsic property of the entire response.**

### Test Basis vs gradability

```text
TEST BASIS asks:
"What would be required to judge this?"

GRADABILITY CHECK asks:
"Do we actually have it for this case and this assessment target?"
```

---

## 9. Evaluator — semantic executor of a constrained examination protocol

The evaluator remains a reasoning layer, not a source of truth.

The preferred architecture does not begin by multiplying LLM judges.

```text
NOT PREFERRED AS FOUNDATION

examinee
    → judge
        → judge of the judge
            → disagreement resolver
```

Agreement between several probabilistic evaluators does not create missing
ground truth or prove that the shared assessment basis is valid.

The preferred direction is:

```text
DETERMINISTIC ASSESSMENT CONTRACT
        ↓
ONE BOUNDED EXTERNAL EVALUATOR
        ↓
DETERMINISTIC RESULT VALIDATION
```

The evaluator is therefore:

> **A semantic executor of a constrained examination protocol.**

The framework should supply:

```text
exact evaluation objective
applicable rules
available evidence
missing evidence
allowed assessment targets
excluded assessment targets
allowed verdicts
prohibited verdicts and claims
required result structure
```

The evaluator applies those constraints to the candidate response.

Conceptually:

```text
CANDIDATE RESPONSE
        +
ASSESSMENT CONTRACT
        +
ALLOWED TEST BASIS
        ↓
BOUNDED EVALUATOR
        ↓
PROPOSED SCOPED FINDINGS
```

### 9.1 Deterministic controls before evaluator invocation

Framework logic should determine:

- whether an assessment is justified
- which rules are applicable
- which evidence is required and available
- which targets are gradable
- which targets are excluded
- which verdicts are allowed
- which claims are prohibited

### 9.2 Deterministic controls after evaluator output

Framework logic should reject or limit an evaluator result when:

- it assesses an excluded target
- it uses a prohibited verdict
- it references a nonexistent or inapplicable rule
- it cites evidence that was not supplied
- it invents missing ground truth
- it converts `NOT_ASSESSED` into model failure
- it produces an overall score despite partial scope
- its rationale supports a broader claim than the contract permits

A rejected evaluator result is an evaluation-process outcome.

It is not automatically a failure of the system under evaluation.

### 9.3 Where semantic evaluation remains useful

The LLM may still be useful for:

- multi-intent separation
- response-strategy recognition
- nuanced natural-language rule application
- detection of unsupported certainty
- domain-boundary behaviour assessment
- explanation within the permitted scope

The evaluator should not decide its own authority.

Its authority is bounded by:

- evidence
- provenance
- applicability
- controlled rules
- rubric
- supplied domain competence
- assessment scope

Therefore:

> **An evaluator may be capable of producing a judgement without being justified
> or authorised to produce that judgement.**

---

## 10. Evaluation result — layered, not one score

A single score or single enum is not expressive enough.

Current conceptual result:

```text
EVALUATION RESULT
│
├── Evaluation status
│   └── COMPLETED / ERROR
│
├── Assessment scope
│   └── FULL / PARTIAL / BEHAVIOUR_ONLY / UNGRADABLE
│
├── Findings
│   ├── response strategy
│   ├── policy adherence
│   ├── factual correctness
│   ├── decision integrity
│   └── other scoped targets
│
├── Evidence / rationale
│   └── why the finding is justified
│
└── Disposition
    └── no further action / review / domain expert / escalation
```

Exact enum names are not yet committed.

### 10.1 Evaluation status

Technical execution state:

```text
COMPLETED
ERROR
```

A parser failure or judge timeout is not a substantive model verdict.

### 10.2 Assessment scope

What could be judged reliably?

Examples:

```text
FULLY_GRADABLE
PARTIALLY_GRADABLE
BEHAVIOUR_ONLY
UNGRADABLE
```

### 10.3 Findings

Findings should be scoped to the actual assessment target.

Example:

```text
response strategy      → PASS
policy adherence       → FAIL
decision integrity     → FAIL
premium correctness    → NOT_ASSESSED
```

### 10.4 Evidence / rationale

The result should preserve enough basis to explain why the finding is justified.

### 10.5 Disposition

What should happen next?

Examples:

```text
NO_FURTHER_ACTION
REVIEW_REQUIRED
DOMAIN_EXPERT_REVIEW
ESCALATION_REQUIRED
NO_VERDICT_POSSIBLE
```

`REVIEW` is therefore better understood as a disposition than as a substantive
verdict.

---


## 10.5 Integration boundary — roles and contracts, not transports

The framework communicates with two external roles:

```text
system under evaluation
external evaluator
```

Neither role is defined by an HTTP API.

Possible access methods include:

```text
API / SDK
Python callable
CLI / subprocess
browser / chat UI
replay file
manual capture
```

The conceptual core should depend on two separate ports.

### Examinee port

```text
TEST STIMULUS
        ↓
EXAMINEE PORT / ADAPTER
        ↓
CANDIDATE RESPONSE ENVELOPE
```

The response envelope may preserve:

- text or structured content
- citations
- tool calls
- attachments
- screenshots
- conversation identifiers
- timestamps and latency
- technical status
- raw response evidence

### Evaluator port

```text
CANDIDATE RESPONSE
        +
ASSESSMENT CONTRACT
        ↓
EVALUATOR PORT / ADAPTER
        ↓
PROPOSED EVALUATOR RESULT
```

The proposed result may preserve:

- proposed findings
- not-assessed targets
- rule references
- evidence references
- rationale
- raw evaluator output
- technical status

The deterministic result validator remains downstream from the evaluator
adapter.

### Transport-specific logic remains outside core

Examples:

```text
API authentication
browser selectors
chat login
CLI process management
SDK invocation
file parsing
```

belong to adapters.

They must not redefine assessment eligibility, rule authority, verdict meaning,
or result validation.

### Replay is part of the conceptual architecture

Replay is not only a test convenience.

It is a first-class input mode that supports reproducible validation of the
framework independently from live-model access.

```text
captured external response
        ↓
normalised CandidateResponse
        ↓
same assessment pipeline
```

Replay evidence supports framework-behaviour claims.

It does not independently support claims about current live-model behaviour.

---

## 11. Current conceptual flow

```text
REGULATED-DOMAIN EVALUATION OBJECTIVE
                ↓
        RISK / REQUIREMENT
                ↓
       TEST CONDITION / SCENARIO
                ↓
            STIMULUS
                ↓
      SYSTEM UNDER EVALUATION
            "examinee"
                ↓
        EXAMINEE ADAPTER
                ↓
        CANDIDATE RESPONSE
                ↓
              +
          TEST BASIS
   ┌────────────────────────────┐
   │ Facts / ground truth       │
   │ Controlled rules          │
   │ Expected strategy          │
   │ Behavioural constraints    │
   │ Required evidence          │
   │ Gradability prerequisites  │
   │ Provenance / applicability │
   └────────────────────────────┘
                ↓
   ASSESSMENT ELIGIBILITY
      & SCOPE DETERMINATION
                ↓
       ASSESSMENT CONTRACT
   ┌────────────────────────────┐
   │ Applicable rules           │
   │ Available evidence         │
   │ Missing evidence           │
   │ Allowed targets            │
   │ Excluded targets           │
   │ Allowed verdicts           │
   │ Prohibited claims          │
   └────────────────────────────┘
                ↓
        EVALUATOR ADAPTER
                ↓
    BOUNDED EXTERNAL EVALUATOR
  "semantic executor of the protocol"
                ↓
    PROPOSED EVALUATOR RESULT
                ↓
 DETERMINISTIC RESULT VALIDATION
                ↓
        EVALUATION RESULT
   ┌────────────────────────────┐
   │ Technical status           │
   │ Assessment scope           │
   │ Accepted findings          │
   │ Rejected findings          │
   │ Evidence / rationale       │
   │ Rule coverage              │
   │ Review / escalation        │
   └────────────────────────────┘
```

The framework controls:

```text
what may be assessed
which rules apply
which evidence may support the assessment
which verdicts are permitted
which evaluator findings may be accepted
```

It does not control private model cognition and does not create missing domain
authority.


# 12. High-level requirements — working draft v0.2

These are conceptual high-level requirements.

They are **not yet measurable acceptance criteria** and do not imply that the
current implementation satisfies them.

## HLR-01 — Defined regulated-domain evaluation scope

Each evaluation shall define:

- system under evaluation
- regulated/high-consequence domain
- evaluation objective
- risk or quality concern
- scope boundaries

The project does not evaluate whether an LLM is generically "good".

---

## HLR-02 — Traceable test intent

Each test stimulus shall be traceable to:

```text
requirement / expected behaviour
        ↓
risk or quality concern
        ↓
test condition / scenario
        ↓
stimulus
```

The stimulus alone shall not define test intent.

---

## HLR-03 — Context separation

The evaluation model shall distinguish:

```text
MODEL-VISIBLE CONTEXT
```

from:

```text
EVALUATOR-ONLY EVIDENCE
```

Missing information may be an intentional part of the test.

---

## HLR-04 — Expected response strategy

The Test Basis shall be able to define the appropriate response strategy for the
scenario, such as:

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

---

## HLR-05 — Explicit Test Basis

Each substantive evaluation shall use a Test Basis adequate to the claim being
assessed.

The conceptual Test Basis includes:

```text
Facts / ground truth
Rules / policies / regulations
Expected response strategy
Behavioural constraints
Required evidence
Gradability prerequisites
Provenance / applicability
```

---

## HLR-06 — Behaviour and outcome shall be distinguishable

The evaluation model shall distinguish:

- outcome correctness
- behavioural/process correctness

A correct outcome shall not automatically imply a correct process.

A missing final answer shall not automatically imply failure.

---

## HLR-07 — Decision integrity and constraint preservation

The system under evaluation shall be assessable for maintaining material rules
and constraints despite:

- user pressure
- strategic ambiguity
- minimisation
- selective disclosure
- misleading framing
- attempts to obtain favourable treatment

---

## HLR-08 — Evidence shall not be replaced by user framing

User confidence, pressure, plausibility, emotional framing, or preferred outcome
shall not substitute for evidence required by the regulated process.

---

## HLR-09 — Assessment eligibility before substantive judgement

Before issuing a substantive finding, the evaluation process shall determine
which assessment targets are supported by the available Test Basis.

---

## HLR-10 — Scoped gradability

The evaluation model shall support the concept that different parts of one
response may have different gradability states.

Possible conceptual scopes include:

```text
FULL
PARTIAL
BEHAVIOUR_ONLY
UNGRADABLE
```

---

## HLR-11 — Evaluator authority shall be bounded

The evaluator shall not be treated as a source of truth beyond the:

- Test Basis
- evidence quality
- provenance
- applicability
- rubric
- evaluation scope
- relevant domain competence

---

## HLR-12 — Evaluator validity shall be independently established

Evaluator effectiveness shall be validated independently from implementation
tests and deterministic mock pipeline checks.

Validation should eventually include:

```text
KNOWN_GOOD
KNOWN_BAD
BORDERLINE
AMBIGUOUS
INSUFFICIENT_EVIDENCE
```

---

## HLR-13 — Evaluation status shall be separate from substantive findings

Technical evaluation failure shall not be represented as model quality.

Conceptually:

```text
evaluation_status
≠
substantive finding
```

---

## HLR-14 — Findings shall be scoped

A finding shall identify what was actually judged.

Example:

```text
response strategy      → PASS
policy adherence       → FAIL
factual claim          → NOT_ASSESSED
final outcome          → UNGRADABLE
```

---

## HLR-15 — Human and domain-expert escalation

The evaluation approach shall support escalation when:

- evidence is insufficient
- judgement is ambiguous
- specialist interpretation is required
- decision impact requires human responsibility

Automated PASS/FAIL shall not be forced when authority is insufficient.

---

## HLR-16 — Evidence provenance and applicability

Evidence used for substantive evaluation shall be traceable, as required by the
case, to properties such as:

```text
source
version
effective date
jurisdiction/domain
scope/applicability
```

---

## HLR-17 — Truthfulness shall not imply unrestricted disclosure

The system may be required to:

```text
withhold
refuse
limit disclosure
redirect
escalate
```

even when requested information is factually true.

Truthfulness and disclosure authority are separate concerns.

---

## HLR-18 — Helpfulness shall remain within constraints

The system shall not optimise user satisfaction by violating:

- policy
- law
- safety
- decision integrity
- evidence requirements
- mandatory process rules

> **Helpful does not mean compliant with the user's preferred outcome.**

---

## HLR-19 — Claims shall remain within validation boundaries

Project and evaluation claims shall be bounded by:

- validation level
- evaluation scope
- Test Basis
- evidence quality
- known limitations

> **Never make a stronger claim than the validation level can support.**

---

## HLR-20 — Evaluator role shall be semantically capable but protocol-bounded

The external evaluator shall be treated as a semantic executor of a constrained
evaluation protocol.

It shall not determine its own:

- evaluation objective
- applicable rule set
- evidence sufficiency
- assessment scope
- allowed verdicts
- claim authority

---

## HLR-21 — Deterministic controls shall constrain evaluator input and validate output

The framework shall support deterministic controls before and after evaluator
invocation.

Pre-evaluation controls shall determine:

- applicable rules
- required and available evidence
- allowed and excluded assessment targets
- allowed verdicts
- prohibited claims

Post-evaluation controls shall reject or limit findings that exceed the supplied
assessment contract.

---

## HLR-22 — Rules shall be controlled, versioned, and developed explicitly

Rules used to support substantive findings shall expose, as required by the
scenario:

```text
identity
version
status
scope
applicability
required evidence
allowed strategies
forbidden behaviour
gradable targets
permitted conclusions
source / owner
```

The rule catalogue shall be treated as an evolving project artefact, not a
complete or timeless domain rulebook.

---

## HLR-23 — Missing rule coverage shall limit the verdict

When no applicable and sufficiently authoritative rule supports an assessment
target, the framework shall not invite evaluator improvisation.

The result shall instead represent an outcome such as:

```text
NO_APPLICABLE_RULE
NOT_ASSESSED
REVIEW_REQUIRED
```

Exact runtime vocabulary remains unresolved.

---

## HLR-24 — Domain boundaries shall be imposed by protocol, not inferred from model labels

A domain-specialised model may retain capabilities outside its assigned domain.

The framework shall therefore define and test:

- authorised domain scope
- permitted out-of-domain behaviour
- tool and live-data boundaries
- redirection or refusal requirements
- assessment targets that remain outside evaluator authority

Model capability shall not be treated as operational authority.

---

## HLR-25 — Integration shall be transport-neutral

The evaluation core shall depend on normalised examinee and evaluator contracts,
not on a specific API, SDK, browser, CLI, or provider.

Transport-specific logic shall remain inside adapters.

---

## HLR-26 — Examinee and evaluator roles shall use separate ports

The framework shall model separate integration responsibilities for:

```text
test stimulus → candidate response
```

and:

```text
candidate response + assessment contract → proposed evaluator result
```

The roles shall not be collapsed merely because both systems may use LLM
technology.

---

## HLR-27 — Replay and controlled capture shall be supported as validation inputs

The framework shall support controlled replay or manually captured external
responses so that deterministic framework behaviour can be validated without
repeated live-model calls.

Replay evidence shall be clearly distinguished from current live-model evidence.

---

## HLR-28 — Technical integration status shall remain separate from substantive findings

Adapter failures, timeouts, authentication errors, malformed responses, and
browser-extraction failures shall not be represented as substantive failures of
the system under evaluation.

---


## 13. Scope discipline — broad understanding, narrow implementation

The conceptual model is intentionally broader than the next implementation
slice.

Its purpose is to expose the real conditions required for a credible verdict,
including conditions that may remain:

```text
manual inputs
documented limitations
future research
human responsibilities
external domain ownership
```

A concept appearing in this model does not automatically become:

- a Pre-v1.0 capability
- a release blocker
- a new module
- a commitment to full automation

The project applies:

> **Understand broadly. Implement narrowly.**

and:

> **Validation before expansion.**

Examples:

```text
Evidence provenance
→ conceptually required
→ may initially be explicit metadata
→ does not yet require an evidence-management platform

Human escalation
→ conceptually required
→ may initially be a structured disposition
→ does not yet require a review workflow product

Evaluator authority
→ must be bounded
→ may be constrained and validated externally
→ cannot be solved by pretending to control model cognition
```

The protected project boundary is a focused evaluation framework skeleton, not a
complete AI governance, compliance, certification, evidence-management, or
regulated decision platform.

Detailed product and implementation guardrails are defined in
`scope-guardrails.md`.

---

## 14. What is deliberately unresolved

This model does not yet define:

- final implementation classes
- database schemas
- exact verdict enums
- exact gradability enums
- acceptance thresholds
- dataset size
- minimum evaluator agreement
- acceptable false-positive/false-negative rates
- mandatory domain-expert roles
- final v1.0 Definition of Done

Those should be derived from validation design, not invented prematurely.

---

## 15. Next conceptual step

The next conceptual validation target is deliberately narrow:

```text
one mixed-domain insurance scenario
+
a small controlled rule subset
+
normalised replay input
+
explicit available and missing evidence
+
behaviour gradable
+
factual outcome not gradable
+
deterministic rejection of evaluator overreach
```

Before coding the runtime slice:

1. validate the mixed-domain case and expected strategy
2. review the first shared and insurance-specific rules
3. define minimum candidate-response and evaluator-result envelopes
4. define separate examinee and evaluator ports
5. define the minimum conceptual assessment contract
6. define deterministic rejection conditions for evaluator output
7. derive measurable acceptance criteria
8. only then commit runtime classes, enums, or YAML schemas

The conceptual model is expected to evolve.

That is a feature of the research process, not documentation drift.
