# Gaps — thematic index

Short-form index of the architectural and methodological gaps identified
so far. Each entry is intentionally brief — the full reasoning belongs
in `LEARNINGS.md` as the project evolves.

The purpose of this document is not to list bugs, but to record the
questions that still need answering before the framework can be
considered a mature LLM evaluation platform.

| # | Gap | Status | One-line summary |
|---|------|--------|------------------|
| 1 | LLM-as-a-Judge reliability | 🟡 Named, not resolved | The framework assumes the evaluator itself is trustworthy, but different LLM judges may produce different scores for identical answers. |
| 2 | Missing human benchmark | 🔴 Open | Model scores are compared only against each other; there is no expert QA baseline showing how close the best model is to a human reviewer. |
| 3 | Prompt sensitivity | 🔴 Open | Evaluation results may depend on prompt wording rather than model capability. Prompt robustness has not yet been measured. |
| 4 | Evaluation criteria weighting | 🟡 Partially resolved | All criteria currently contribute equally. No evidence-based weighting model has been defined yet. |
| 5 | Missing statistical confidence | 🔴 Open | The framework reports averages but not variance, confidence intervals or score stability across multiple executions. |
| 6 | Cost vs quality analysis | 🟡 Planned | Quality is measured independently of inference cost. Future versions should compare quality-per-dollar rather than quality alone. |
| 7 | Dataset diversity | 🔴 Open | Current benchmark coverage is intentionally small. Broader QA scenarios (UI, API, automation, security, performance) should be added over time. |
| 8 | Regression tracking | 🟡 Planned | Results represent single executions. Long-term trends between model versions are not yet tracked. |
| 9 | Judge disagreement | 🟡 Named | The framework does not yet compare how different evaluator models score the same response. |
| 10 | Synthetic vs real QA tasks | 🟡 Named | Current datasets combine controlled prompts. Future benchmarks should include more real-world QA artifacts such as production bugs and requirements. |

---

## Status legend

- 🔴 Open — identified but not yet addressed
- 🟡 Planned / partially resolved — architecture exists, implementation deferred
- 🟢 Resolved — implemented and validated

---

## Where to read more

As the project evolves, each gap will receive its detailed discussion in
`LEARNINGS.md`, including design decisions, rejected alternatives and
implementation notes.