# Bounded evaluator protocol — request and result schema v0.1

> **Status: executable provider-neutral runtime protocol.**
>
> This document describes the request rendered for an external evaluator and the
> strict JSON result accepted by the replay/parser path. It does not claim that a
> live evaluator follows the protocol reliably.

---

## 1. Purpose

The protocol creates a hard boundary between:

```text
validated AssessmentContract
        ↓
bounded evaluator request
        ↓
external semantic evaluator
        ↓
raw structured output
        ↓
strict parser
        ↓
ProposedEvaluatorResult
        ↓
deterministic result validator
```

The evaluator proposes findings.

It does not decide its own:

- assessment scope
- applicable rule catalogue
- available evidence
- allowed verdicts
- prohibited claims
- final acceptance of findings

---

## 2. Runtime components

```text
BoundedEvaluatorRequestBuilder
BoundedEvaluatorRequest
EvaluatorPort
ReplayEvaluatorAdapter
StructuredEvaluatorResultParser
ProposedEvaluatorResult
EvaluationResultValidator
```

Protocol constants:

```text
evaluator protocol version: 0.1
result schema version:      0.1
```

---

## 3. Bounded request input

The request builder accepts:

```text
ExamineeRequest
CandidateResponse
AssessmentContract
```

It verifies that:

- all `case_id` values match
- the candidate response ID matches the contract
- the stimulus is non-empty

A mismatch is an evaluation-process error.

It does not create an examinee `FAIL`.

---

## 4. Data included in the request

The rendered payload contains only the information required by the current
assessment protocol.

### Case

```text
case_id
stimulus
candidate response ID
candidate response text
```

### Allowed scope

For each allowed target:

```text
target
allowed verdicts
effective required-evidence identifiers
```

### Explicitly excluded scope

For each excluded target:

```text
target
exclusion reason
missing-evidence identifiers
```

### Controlled rules

For each resolved rule:

```text
rule ID
version
status
title
evaluator instruction
allowed-target intersection
required evidence
source
forbidden behaviours
permitted conclusions
```

### Other constraints

```text
available-evidence identifiers
prohibited claims
required result schema
```

---

## 5. Data intentionally not included

The current request does not serialize arbitrary candidate metadata or response
provenance.

For example, it does not expose:

```text
adapter_type
local fixture paths
creation_method
live_model_response
unrelated provider metadata
```

This is a data-minimisation boundary.

The current evidence model still carries identifiers rather than complete
versioned evidence objects. Therefore, this slice proves bounded serialization,
not complete Test Basis delivery.

---

## 6. Provider-neutral rendered form

`BoundedEvaluatorRequest` contains:

```text
protocol_version
result_schema_version
case_id
candidate_response_id
instruction
payload_json
rendered_prompt
```

A future API, CLI, local-model, or browser adapter may map the rendered request
to its transport.

Transport-specific authentication, retries, model parameters, and message
formatting remain outside the Validation Engine.

---

## 7. Required raw result

The evaluator must return one JSON object only.

No markdown fences, preamble, explanation outside JSON, or additional top-level
fields are accepted.

```json
{
  "schema_version": "0.1",
  "case_id": "INS-MIXED-001",
  "findings": [
    {
      "finding_id": "F-001",
      "target": "intent_separation",
      "verdict": "PASS",
      "rule_id": "GLOBAL-MULTI-INTENT-01",
      "evidence_used": [
        "candidate_response",
        "stimulus_intents"
      ],
      "rationale": "...",
      "claims": []
    }
  ],
  "overall_score": null
}
```

Every finding requires exactly:

```text
finding_id
target
verdict
rule_id
evidence_used
rationale
claims
```

---

## 8. Parser responsibilities

`StructuredEvaluatorResultParser` validates syntax and shape.

It rejects:

- invalid JSON
- markdown-fenced JSON
- non-object roots
- missing fields
- unexpected fields
- duplicate JSON object keys
- unsupported schema versions
- invalid target or verdict enum values
- empty required strings
- non-array evidence or claims
- duplicate evidence or claim identifiers
- duplicate finding IDs
- non-finite or incorrectly typed overall scores

Malformed output becomes:

```text
TechnicalState.ERROR
accepted findings: none
substantive examinee failure: false
```

The raw output is preserved whenever it was available.

---

## 9. Parser versus result validator

The parser validates structure.

The result validator validates authority and scope.

The parser intentionally does not reject a structurally valid result merely
because it contains:

- a different `case_id`
- an unknown rule ID
- an unavailable evidence reference
- a prohibited claim
- an out-of-scope target
- a disallowed verdict
- an overall score under partial scope

Those outputs are normalised and passed to `EvaluationResultValidator`, which
preserves and rejects the overreach deterministically.

This separation allows the framework to distinguish:

```text
malformed output
from
well-formed evaluator overreach
```

---

## 10. Replay-first evaluator adapter

`ReplayEvaluatorAdapter` reads a saved raw output file and runs it through the
same public parser intended for a future live adapter.

It supports deterministic testing of:

- valid structured output
- malformed JSON
- unsupported schema versions
- schema violations
- missing replay files
- downstream result-boundary violations

A replay success proves protocol and framework behaviour.

It does not prove live evaluator competence.

---

## 11. Partial-scope overall-score policy

When any requested target is excluded, the bounded request states:

```text
overall_score: must_be_null
```

The parser still accepts a structurally valid numeric score so that the result
validator can preserve and reject that explicit evaluator overreach.

This is deliberate:

```text
request constrains
parser normalises
validator accepts or rejects
```

---

## 12. Current claim boundary

This slice demonstrates:

- deterministic request rendering
- explicit allowed and excluded scope
- explicit missing evidence
- full controlled rule serialization
- result-schema versioning
- strict structured parsing
- raw-output preservation
- separation of parse errors from substantive findings
- replay-based end-to-end execution

It does not demonstrate:

- live evaluator compliance
- evaluator semantic accuracy
- complete evidence delivery
- domain correctness of the rules
- provider reliability
- model repeatability
- production readiness
