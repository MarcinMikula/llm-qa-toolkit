# Integration architecture

> **Status: working architecture direction for the Pre-v1.0 runtime bridge.**
>
> This document defines roles, normalised contracts, adapter categories, and
> validation boundaries. It does not commit the project to implementing every
> transport or provider.

Integration forms two of the framework's three configurable pillars:

```text
Examinee Integration
Evaluator Integration
```

The third pillar, the Validation Engine, consumes and constrains their
normalised outputs.

See [`framework-architecture.md`](framework-architecture.md).

---

## 1. Problem

The framework needs access to two external roles:

```text
system under evaluation
        "examinee"

external semantic evaluator
        "examiner"
```

The final systems have not yet been selected.

They may be available through:

- HTTP API
- vendor SDK
- local Python process
- CLI
- browser-only chat interface
- controlled manual interaction
- previously captured response files

The architecture must remain usable before those choices are final.

---

## 2. Core principle

> **The evaluation pipeline must depend on normalised contracts, not on how the
> examinee or evaluator is accessed.**

And:

> **API is one transport option, not the definition of an LLM integration.**

Conceptually:

```text
TEST STIMULUS
        ↓
EXAMINEE ADAPTER
        ↓
CANDIDATE RESPONSE
        ↓
ASSESSMENT PIPELINE
        ↓
EVALUATOR ADAPTER
        ↓
PROPOSED EVALUATOR RESULT
        ↓
DETERMINISTIC RESULT VALIDATION
```

---

## 3. Separate ports for separate roles

The examinee and evaluator have different responsibilities.

They should not share one generic `LLMClient` contract merely because both may
use language models.

### 3.1 Examinee port

Conceptual responsibility:

```text
Stimulus
    → system under evaluation
        → CandidateResponse
```

The examinee adapter may need to:

- create or resume a conversation
- submit the test stimulus
- provide model-visible context
- wait for completion
- collect response content
- collect citations or visible sources
- collect tool calls where available
- capture attachments or screenshots
- preserve timestamps and latency
- classify technical failures

### 3.2 Evaluator port

Conceptual responsibility:

```text
CandidateResponse
+
AssessmentContract
    → external evaluator
        → ProposedEvaluatorResult
```

The evaluator adapter may need to:

- build the constrained evaluator request
- provide only allowed Test Basis
- submit allowed targets and verdicts
- enforce or request structured output
- preserve raw output
- normalise proposed findings
- preserve rule and evidence references
- classify technical failures

The evaluator adapter does not decide whether the proposed findings are valid.

That remains the responsibility of deterministic result validation.

---


## 3.5 Shared transport infrastructure, separate role contracts

The two pillars may reuse technical utilities:

```text
HTTP client
authentication helper
file loader
JSON parser
subprocess runner
browser session
retry and timeout utilities
```

They must not reuse one unbounded semantic contract.

```text
shared transport
is allowed

shared role authority
is not
```

A file loader, for example, may support both:

```text
prompt + candidate response file
```

and:

```text
saved proposed evaluator result file
```

Each output still enters a different role-specific envelope and validation path.

---

## 4. Normalised envelopes

Exact runtime types are not yet committed.

The following sketches identify information the core may need.

### 4.1 Candidate response

```yaml
candidate_response:
  content:
    text: "..."
    structured_data: null

  evidence:
    citations: []
    tool_calls: []
    attachments: []
    screenshots: []

  metadata:
    system_id: "..."
    model_id: null
    conversation_id: null
    adapter_type: "replay"
    started_at: null
    completed_at: null
    latency_ms: null

  technical_status:
    state: COMPLETED
    error_type: null
    message: null

  raw:
    preserved: true
    location: "..."
```

### 4.2 Proposed evaluator result

```yaml
proposed_evaluator_result:
  proposed_findings:
    - target: response_strategy
      verdict: PASS
      rule_id: INS-CLAIM-01
      evidence_used:
        - candidate_response
        - missing_incident_context
      rationale: "..."

  not_assessed:
    - target: actual_insurance_liability
      reason: missing_required_evidence

  technical_status:
    state: COMPLETED
    error_type: null
    message: null

  metadata:
    evaluator_id: "..."
    model_id: null
    adapter_type: "stub"
    latency_ms: null

  raw:
    preserved: true
    output: "..."
```

These are design sketches, not final schemas.

---

## 5. Adapter categories

### 5.1 API / SDK adapter

Suitable for:

- hosted model providers
- OpenAI-compatible endpoints
- Anthropic
- Ollama HTTP
- internal gateways
- vendor SDKs

Advantages:

- structured access
- automation
- metadata availability
- lower UI fragility

Risks:

- cost
- provider coupling
- data-handling restrictions
- model/version drift
- rate limits
- API deprecation

### 5.2 Python callable adapter

Suitable for:

- local inference libraries
- Transformers pipelines
- in-process prototypes
- internal Python services

Possible conceptual use:

```python
result = callable_model(request)
```

The adapter normalises the callable's output.

### 5.3 CLI / subprocess adapter

Suitable for:

- local model tools
- agent runtimes
- company utilities
- prototypes without a server interface

Possible interaction:

```text
request via stdin or file
        ↓
subprocess
        ↓
stdout / JSON / output file
```

The adapter owns process timeout, exit-code handling, and output parsing.

### 5.4 Browser / chat UI adapter

Suitable when the system is available only through a user interface.

A concrete adapter may use Playwright:

```text
login
start conversation
submit stimulus
wait for completion
extract response
collect visible citations
capture screenshot / trace
```

This adapter is system-specific.

A generic browser agent is not assumed to understand every chat UI.

Browser selectors and flows remain outside the core evaluation package.

### 5.5 Replay adapter

Reads a controlled captured response from a file or fixture.

Suitable for:

- deterministic CI
- repeated rule experiments
- regression testing
- malformed-output testing
- result-validator testing
- cost-free development

Replay should preserve enough metadata to explain the origin of the capture.

### 5.6 Manual-capture adapter

Normalises a response copied or exported by a human.

Suitable when:

- no API is available
- UI automation is prohibited or unstable
- access requires interactive authentication
- the validation sample is intentionally small

Manual capture is not inferior merely because it is less automated.

It must still be traceable.

---


## 5.7 File-based workflows

### Examinee file

May contain:

```text
stimulus
candidate response
system / model metadata
provenance
evidence references
```

### Evaluator file

May contain:

```text
case identifier
proposed findings
not-assessed targets
rule references
evidence references
raw output
technical metadata
```

File input does not bypass framework validation.

A loaded evaluator result must pass the same case, target, rule, evidence,
verdict, and claim checks as a live result.

Synthetic, manually captured, replayed, and captured-live sources must remain
distinguishable.

---

## 6. Technical status is not substantive verdict

Each adapter can fail independently from the system behaviour being evaluated.

Examples:

```text
AUTHENTICATION_ERROR
TIMEOUT
RATE_LIMITED
MALFORMED_RESPONSE
BROWSER_EXTRACTION_ERROR
PROCESS_EXIT_ERROR
FILE_PARSE_ERROR
```

Those statuses belong to integration or evaluation-process reporting.

They must not be converted into:

```text
candidate model FAIL
```

The result model should preserve:

```text
technical status
assessment status
substantive findings
```

as distinct layers.

---

## 7. Replay-first development strategy

The first runtime slice should not require live models.

```text
INS-MIXED-001 fixture
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

The stub evaluator should deliberately support controlled behaviours:

- valid result
- out-of-scope finding
- nonexistent rule reference
- missing-evidence invention
- prohibited verdict
- malformed structured output
- overall score despite partial scope

This proves whether the framework can constrain an evaluator.

It does not prove whether a live evaluator is semantically competent.

---

## 8. Adapter contract tests

Every adapter should pass a shared behavioural contract appropriate to its port.

### 8.1 Examinee adapter contract

Verify that the adapter:

- accepts a valid stimulus request
- returns a normalised candidate response
- never reports `COMPLETED` with unusable empty content unless explicitly allowed
- preserves relevant evidence
- classifies technical errors
- preserves raw response or a traceable reference
- does not make substantive evaluation decisions

### 8.2 Evaluator adapter contract

Verify that the adapter:

- accepts the candidate response and assessment contract
- forwards only allowed evaluator context
- returns a normalised proposed result
- preserves raw output
- classifies malformed or technical failures
- does not silently widen assessment scope
- does not itself accept proposed findings as final

---

## 9. Live-model validation boundary

A live integration should be added only for a defined measurement question.

Examples:

```text
Can model X follow the bounded output contract?
How often does model X assess excluded targets?
Can model X separate mixed intents consistently?
How stable are findings across five repeated runs?
```

A live experiment should record:

- model/provider identifier
- access mode
- date and configuration
- prompt and contract version
- rule versions
- run count
- raw outputs
- latency
- cost where applicable
- technical failures
- human-labelled expectation
- accepted and rejected findings

Live-model tests should not run by default in pull-request CI.

---

## 10. Security and access boundaries

The adapter layer does not grant authority to access a system.

Before integrating a real organisation's model or UI, the project must consider:

- permission to automate or call the system
- data classification
- credential handling
- terms of service
- rate limits
- retention and logging
- screenshot sensitivity
- personal or confidential information
- external-provider data transfer

A technically possible integration may still be organisationally prohibited.

---

## 11. Implementation status and next integration work

### Implemented

```text
CandidateResponse
ProposedEvaluatorResult
ExamineePort
EvaluatorPort
ReplayExamineeAdapter
StubEvaluatorAdapter
```

These support the current replay-first assessment slice.

### Current priority outside the integration layer

The next sprint belongs primarily to the Validation Engine:

```text
feature/runtime-rule-catalogue
```

Integration breadth should not expand while the assessment contract still
contains opaque rule IDs.

### Next integration work

After the runtime rules and contract path are stable:

```text
adapt existing provider integration behind EvaluatorPort
add one examinee adapter required by a controlled experiment
```

### Later, only when required

```text
Python callable adapter
CLI adapter
browser adapter
manual-capture helper
additional API providers
```

The architecture remains broad.

Implementation remains evidence-led and narrow.


## 12. Acceptance questions

Before implementation is considered successful:

```text
Can the same assessment pipeline consume API, replay, or browser-derived
CandidateResponse without changing core logic?

Can a replay fixture exercise the complete deterministic pipeline?

Can adapter failure remain separate from candidate failure?

Can evaluator output be preserved and rejected without losing traceability?

Can one live adapter be added without changing assessment eligibility or rule
logic?
```

---

## 13. Protected principle

> **Build the smallest transport-neutral slice that can be validated without
> live-model access, then add only the integrations required by the next
> evidence-gathering experiment.**
