# Known limitations — thematic index

Known limitations of the current `llm-qa-toolkit` prototype.

This file is intentionally short. It is a map of current boundaries, not a copy
of the full reasoning. See [`gaps.md`](gaps.md) for the detailed validation gaps
and `../LEARNINGS.md` for the reasoning behind them.

---

## Current validation boundaries

- **Mock mode demonstrates pipeline consistency, not evaluator accuracy.**
  Deterministic mock responses are useful for verifying execution flow,
  evaluator integration, scoring logic, CI behaviour, and reporting. A green
  mock suite does not prove that the evaluators will correctly judge previously
  unseen real model outputs.

- **Evaluator effectiveness has not yet been independently calibrated.**
  The current evaluators have not been validated against a human-labelled
  ground-truth or calibration dataset. False-positive rate, false-negative rate,
  agreement with human reviewers, and behaviour on borderline cases are not yet
  established.

- **The current LLM judge may score cases without sufficient domain evidence.**
  The present evaluation flow does not formally require trusted reference
  evidence, provenance, applicable document or policy versions, judge-only
  context, or explicit gradability prerequisites before a score is issued.
  Domain-specific factual correctness may therefore require stronger test basis
  than the current prototype provides.

- **Current thresholds and score weights are manually selected design
  assumptions.** They reflect intended relative risk between test categories,
  but they have not yet been empirically calibrated against validated outcomes
  and should not be treated as universal robustness thresholds.

- **The current implementation follows a single primary provider/judge path.**
  The architecture is not yet validated across multiple evaluator models or
  providers. Results may therefore depend on provider-specific behaviour,
  prompting, parsing, and model characteristics.

- **Regression baselines have limited provenance metadata.**
  Baseline scores exist as comparison points, but the current implementation
  does not yet capture all context needed for strong reproducibility claims,
  such as model version, prompt version, judge version, run date, number of
  runs, live/mock mode, and approval basis.

- **Evaluation execution errors are not yet fully separated from substantive
  verdicts.** Some evaluator or parser failures can fall back to neutral-looking
  numeric values. A technical evaluation failure should not be interpreted as
  equivalent to a medium-quality candidate response.

- **Controlled live validation is still pending.**
  Live-provider execution is supported, but the toolkit has not yet completed a
  deliberately designed validation experiment demonstrating evaluator
  effectiveness against real, non-deterministic model responses.

---

## Scope boundary

The current test suite and reports should be interpreted as evidence of a
working evaluation prototype and risk-oriented testing approach.

**No production-grade robustness, formal audit assurance, validated evaluator
accuracy, or authoritative domain-correctness claims should be inferred from the
current test suite alone.**
