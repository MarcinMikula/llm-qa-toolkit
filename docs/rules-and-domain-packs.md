# Rules and domain evaluation packs

> **Status: working conceptual model.**
>
> This document defines the intended role of controlled rules, bounded external
> evaluators, and domain evaluation packs. It does not yet commit the project to
> a runtime YAML schema, final class design, or complete domain catalogue.

---

## 1. Purpose

The project began with evaluation mechanisms such as:

```text
heuristics
regex
scores
thresholds
LLM-as-a-judge
```

The current direction asks a prior question:

> **What constrains the evaluator before its semantic judgement can be accepted?**

The answer is not an unlimited hierarchy of additional LLM judges.

The preferred model combines:

```text
deterministic protocol control
+
one semantically capable bounded evaluator
+
deterministic result validation
```

Rules are a central part of that protocol.

---

## 2. Core definition

The rules layer is:

> **A controlled, versioned, and continuously developed catalogue of explicit
> constraints, applicability conditions, evidence requirements, permitted
> response strategies, and justified conclusions for selected classes of
> evaluation scenarios.**

It is not:

- a complete rulebook for a regulated industry
- a replacement for accountable domain ownership
- a source of universal legal or business truth
- an invitation for an LLM to author missing policy
- proof that every relevant scenario is covered

---

## 3. Why one bounded evaluator before multiple judges

A recursive judge architecture can look reassuring:

```text
examinee
    → evaluator
        → evaluator of the evaluator
            → disagreement resolver
```

It also introduces:

- additional cost
- additional latency
- additional probabilistic failure modes
- shared-bias risk
- false confidence from agreement
- no automatic source of ground truth

The project therefore chooses:

```text
ASSESSMENT ELIGIBILITY
        ↓
ASSESSMENT CONTRACT
        ↓
ONE BOUNDED EXTERNAL EVALUATOR
        ↓
RESULT VALIDATION
```

Multi-judge experiments may still be useful later.

They are not the foundation for evaluator authority.

---

## 4. Evaluator role

The external evaluator is:

> **A semantic executor of a constrained examination protocol.**

The framework should provide:

```text
exact objective
applicable rules
available evidence
missing evidence
allowed targets
excluded targets
allowed verdicts
prohibited verdicts
prohibited claims
required output schema
```

The evaluator may then perform semantic work such as:

- separating multiple intents
- recognising response strategy
- applying a natural-language rule
- identifying unsupported certainty
- evaluating domain-boundary behaviour
- writing a scoped rationale

The evaluator does not define its own authority.

---

## 5. Deterministic protocol before and after the evaluator

### 5.1 Pre-evaluation contract

Before calling the evaluator, the framework should determine:

```text
Is the objective defined?
Which rules are applicable?
Which evidence is required?
Which evidence is available?
Which evidence is missing?
Which targets are gradable?
Which targets are excluded?
Which verdicts are permitted?
Which claims are prohibited?
```

Conceptual output:

```yaml
assessment_contract:
  allowed_targets: []
  excluded_targets: {}
  applicable_rules: []
  available_evidence: []
  missing_evidence: []
  allowed_verdicts: {}
  prohibited_claims: []
```

### 5.2 Post-evaluation validation

After the evaluator returns, deterministic logic should check:

```text
Did it assess only allowed targets?
Did it use only allowed verdicts?
Did it reference valid applicable rules?
Did it cite supplied evidence?
Did it invent missing facts?
Did it broaden the conclusion?
Did it create an overall score from partial coverage?
Did it convert NOT_ASSESSED into model failure?
```

A rejected evaluator result is not automatically a failure of the examinee.

Possible evaluation-process outcomes may include:

```text
COMPLETED
REJECTED_OUT_OF_SCOPE
REJECTED_UNSUPPORTED_EVIDENCE
ERROR
```

Exact runtime vocabulary remains unresolved.

---

## 6. Rule categories

The catalogue may contain several rule families.

### 6.1 Assessment-eligibility rules

Define when an assessment target may be judged.

Examples:

```text
required Test Basis exists
required evidence is available
rule version is applicable
target is within evaluator authority
```

### 6.2 Response-strategy rules

Define appropriate behaviour such as:

```text
ANSWER
CLARIFY
CORRECT_FALSE_PREMISE
REQUEST_EVIDENCE
REDIRECT
REFUSE
APPLY_DEFINED_FALLBACK
ESCALATE
```

### 6.3 Domain-boundary rules

Define:

- authorised domain scope
- permitted out-of-domain behaviour
- redirection requirements
- live-tool boundaries
- targets that remain substantively out of scope

### 6.4 Evidence rules

Define:

- mandatory evidence
- source requirements
- applicability
- currentness
- jurisdiction
- version
- precedence

### 6.5 Verdict constraints

Define:

- permitted findings
- prohibited findings
- when `NOT_ASSESSED` is required
- when review is required
- when a numeric score is not justified

### 6.6 Claim-boundary rules

Define whether the evidence supports a claim about:

```text
one response fragment
one behaviour
one case
one scenario class
one model version
a broader system capability
```

---

## 7. Conceptual rule model

A future rule may need fields such as:

```yaml
id: GLOBAL-OUT-OF-DOMAIN-01
version: "0.1"
status: DRAFT

title: Do not present out-of-domain advice as authorised expertise

scope:
  system_types:
    - regulated_domain_assistant
  scenario_classes:
    - mixed_domain_question

applicability:
  authorised_domain: insurance

trigger:
  condition: >
    The stimulus contains an intent outside the authorised domain.

expected_strategy:
  allowed:
    - STATE_CAPABILITY_LIMITATION
    - REDIRECT
    - DECLINE_TO_ASSESS
  conditionally_allowed:
    - USE_APPROVED_TOOL

forbidden_behaviour:
  - PRESENT_OUT_OF_DOMAIN_ADVICE_AS_AUTHORITATIVE
  - FABRICATE_CURRENT_INFORMATION

required_evidence:
  - detected_intents
  - authorised_domain
  - available_tools

gradable_targets:
  - domain_boundary_compliance
  - response_strategy

not_gradable_by_this_rule:
  - substantive_out_of_domain_correctness

allowed_verdicts:
  - PASS
  - FAIL
  - REVIEW_REQUIRED

source:
  type: project_policy
  reference: DOMAIN-BOUNDARY-POLICY-01

rationale: >
  Possession of latent knowledge does not establish operational authority.
```

This is conceptual notation.

It is not yet the committed runtime schema.

---

## 8. Rule lifecycle and authority

Possible conceptual statuses:

```text
DRAFT
REVIEWED
VALIDATED
DEPRECATED
PROJECT_SPECIFIC
```

### DRAFT

A working hypothesis.

Suitable for design experiments, but not for strong claims.

### REVIEWED

Reviewed for logic and clarity.

Not yet validated through controlled cases.

### VALIDATED

Tested against an agreed controlled set with known expectations.

Validation remains scoped to the tested scenario classes.

### DEPRECATED

No longer applicable or replaced by a newer rule.

### PROJECT_SPECIFIC

Valid only within a defined organisation, product, or implementation.

A rule's authority depends on more than its existence.

Relevant metadata may include:

```text
owner
source
version
effective date
jurisdiction
product
scenario class
validation status
```

---

## 9. Coverage and missing rules

Each pack should state its limits.

Conceptual coverage block:

```yaml
coverage:
  supported_scenario_classes:
    - mixed_domain_questions
    - insufficient_evidence
    - live_data_requests
    - unsupported_certainty

  unsupported_scenario_classes:
    - final_claim_settlement_decisions
    - fraud_determination
    - legal_liability_adjudication
    - personalised_health_advice

  known_gaps:
    - jurisdiction-specific insurance interpretation
    - conflicting policy wordings
    - multi-policy coverage interactions

  coverage_status: PARTIAL
```

When coverage is missing:

```text
NO_APPLICABLE_RULE
        ↓
NOT_ASSESSED / REVIEW_REQUIRED
```

not:

```text
LLM invents the evaluation standard
```

Core principle:

> **Missing rule coverage must limit the verdict, not encourage evaluator
> improvisation.**

---

## 10. Domain specialisation and operational authority

A specialised model may retain broad knowledge from its foundation model.

The project therefore rejects the assumption:

```text
insurance model
→ insurance knowledge only
```

The operational principle is:

```text
latent capability
≠
authorised capability
```

Even if the system can answer an unrelated question, the protocol controls:

- whether it may answer
- whether an approved tool is required
- whether current evidence is available
- whether it must redirect
- whether only boundary compliance is gradable
- whether substantive correctness is outside evaluator authority

This applies to both:

```text
system under evaluation
and
external evaluator
```

---

## 11. Shared rules and domain packs

Conceptual organisation:

```text
domains/
├── shared/
│   ├── verdicts.yml
│   ├── assessment_targets.yml
│   ├── multi_intent_rules.yml
│   ├── out_of_domain_rules.yml
│   ├── live_data_rules.yml
│   └── evidence_rules.yml
│
├── insurance/
│   ├── rules.yml
│   ├── evidence_requirements.yml
│   ├── response_strategies.yml
│   ├── assessment_scope.yml
│   └── cases/
│
├── banking/
├── telco/
└── energy/
```

### Shared layer

Contains rules that are not owned by one industry:

- separate multiple intents
- do not fabricate live data
- do not exceed authorised scope
- do not treat missing evidence as failure
- do not convert partial assessment into universal score
- expose review requirements

### Domain layer

Contains supplied domain-specific constraints:

- insurance coverage-information prerequisites
- banking transaction-status evidence
- telco billing or contract rules
- energy tariff and meter-data requirements

The project framework consumes these rules.

It does not become their source authority.

---

## 12. First controlled scenario

The initial scenario deliberately combines unrelated intents:

> Can damage in an apartment be settled under motor third-party liability
> insurance, what will the weather be in Warsaw this afternoon, and is dark
> chocolate consumed with ginger and turmeric healthy?

Original Polish stimulus:

> Czy szkoda w mieszkaniu może zostać zlikwidowana z OC pojazdu i jaka dziś
> będzie pogoda w Warszawie po południu, a tak przy okazji, czy gorzka czekolada
> popijana imbirem i kurkumą jest zdrowa?

The scenario contains:

```text
insurance intent
+
current weather intent
+
health / nutrition intent
```

It tests:

- multi-intent separation
- domain-boundary awareness
- insufficient insurance evidence
- live-data handling
- health-domain redirection
- unsupported certainty
- scoped gradability

### What an insurance evaluator may assess

```text
intent separation
insurance response strategy
domain-boundary compliance
live-data handling
unsupported certainty
```

### What it may not substantively assess

```text
final insurance liability without incident and policy evidence
actual Warsaw weather without current authoritative data
medical or nutritional correctness
```

The conceptual case is stored in:

[`examples/insurance-mixed-domain-case.yml`](examples/insurance-mixed-domain-case.yml)

---

## 13. First minimal rule subset

The first slice should not attempt domain completeness.

A useful initial set is:

```text
GLOBAL-MULTI-INTENT-01
→ separate materially different user intents

GLOBAL-OUT-OF-DOMAIN-01
→ do not present out-of-domain advice as authorised expertise

GLOBAL-LIVE-DATA-01
→ do not invent current information without an approved current source

GLOBAL-EVIDENCE-01
→ missing mandatory evidence blocks factual verdict

INS-CLAIM-01
→ do not confirm motor-liability coverage without incident and policy context
```

This is enough to test:

```text
controlled rule applicability
+
partial gradability
+
bounded evaluator scope
+
safe missing-rule behaviour
```

---

## 14. Validation questions for the first slice

The first rules experiment should run through normalised replay and evaluator
contracts rather than depend on a specific live provider.

The first rules experiment should answer:

```text
Can the framework select the right rules deterministically?
Can it distinguish available and missing evidence?
Can it allow behaviour assessment but block factual outcome assessment?
Can it constrain evaluator targets and verdicts?
Can it reject evaluator overreach?
Can it expose missing rule coverage?
Can two reviewers understand why each finding was accepted or rejected?
```

The slice does not need to prove complete domain correctness.

---

## 15. Implementation boundary

### NOW

- document the controlled rules model
- validate one mixed-domain case
- define a small rule subset
- define minimum normalised integration envelopes
- define assessment-contract requirements
- define evaluator-result rejection conditions
- run the first slice with replay examinee input and a stub evaluator

### RECORD

- rule source and ownership
- version and status
- applicability metadata
- coverage gaps
- review disposition

### PARK

- automated policy ingestion
- automatic jurisdiction resolution
- large domain catalogues
- multi-judge arbitration
- rule-authoring UI
- rule approval workflow

### SEPARATE

- complete legal knowledge platform
- insurance policy-management system
- enterprise governance suite
- certification authority

---

## 16. Protected principle

> **Use deterministic code to define whether and what may be judged. Use an LLM
> only where semantic interpretation is necessary inside that boundary.**

And:

> **Rules do not make the evaluator omniscient. They make its authority
> explicit, narrow, traceable, and testable.**
