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

## 4. Response-behaviour rules discovered so far

These are working conceptual rules, not yet formal acceptance criteria.

### False premise

```text
false or misleading premise
        ↓
do not silently accept it
        ↓
correct / clarify / reframe
```

### Insufficient information

```text
valid question
+ insufficient required context
        ↓
clarify / request evidence
```

### Unsupported current fact

```text
current factual question
+ no current authoritative data
        ↓
state limitation
        ↓
do not fabricate
```

### Domain boundary

```text
question outside supported competence
        ↓
acknowledge boundary
        ↓
redirect appropriately
```

### Safety or disclosure boundary

```text
truthful information exists
+ disclosure is unsafe / unauthorized
        ↓
withhold / refuse / limit / redirect
```

Therefore:

> **Truthfulness does not imply unrestricted disclosure.**

### User pressure or preferred outcome

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

### Future uncertainty

```text
future cannot be known with certainty
        ↓
do not invent certainty
        ↓
apply current rule / declared assumption / defined fallback
```

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

## 9. Evaluator — reasoning layer, not source of truth

The evaluator applies a rubric to a candidate response using the available Test
Basis.

Conceptually:

```text
CANDIDATE RESPONSE
        +
TEST BASIS
        +
EVALUATION RUBRIC
        ↓
EVALUATOR
        ↓
REASONED FINDINGS
```

The evaluator should not create missing ground truth and then use that invented
ground truth to issue an authoritative verdict.

Its authority is bounded by:

- evidence
- provenance
- applicability
- rubric
- domain competence
- evaluation scope

Therefore:

> **An evaluator may be capable of producing a judgement without being justified
> in producing that judgement.**

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
        CANDIDATE RESPONSE
                ↓
              +
          TEST BASIS
   ┌────────────────────────────┐
   │ Facts / ground truth       │
   │ Rules / policies           │
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
       WHAT CAN BE JUDGED?
                ↓
            EVALUATOR
            "examiner"
                ↓
       SCOPED FINDINGS
                ↓
   ┌─────────────────────────┐
   │ Evaluation status       │
   │ Assessment scope        │
   │ Findings / verdicts     │
   │ Evidence / rationale    │
   │ Disposition / escalation│
   └─────────────────────────┘
```

---

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

## 13. What is deliberately unresolved

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

## 14. Next conceptual step

Before coding the next architecture slice:

1. challenge this model with more real regulated-domain examples
2. identify contradictions or missing concepts
3. refine the high-level requirements
4. define the smallest measurable Pre-v1.0 validation objectives
5. only then derive acceptance criteria and implementation architecture

The conceptual model is expected to evolve.

That is a feature of the research process, not documentation drift.
