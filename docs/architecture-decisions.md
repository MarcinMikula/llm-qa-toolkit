# Architecture decisions — thematic index

Short-form index of the key architectural decisions made during the
development of the evaluation framework.

This document captures *why* the framework is built the way it is.
Implementation details belong in the code, chronological reasoning lives
in `LEARNINGS.md`; this file records the architectural conclusions.

---

## Evaluation pipeline

- **Every evaluation follows the same deterministic pipeline.**
  Prompt generation → model execution → response parsing → scoring →
  report generation. Each stage has a single responsibility and can be
  replaced independently.

- **Evaluators are isolated modules rather than one monolithic scorer.**
  Completeness, Accuracy, Security, Maintainability and other dimensions
  are evaluated independently before producing the final score. This
  makes adding or removing evaluation criteria straightforward.

- **Scoring is deterministic wherever possible.**
  Numerical aggregation is handled entirely in Python after evaluation.
  LLMs produce judgments, but never calculate final weighted scores.

---

## Prompt architecture

- **Evaluation prompts are stored separately from evaluation logic.**
  Prompt engineering evolves much faster than application logic.
  Separating prompts from code makes experimentation significantly
  easier.

- **Prompt templates remain human-readable.**
  The framework deliberately avoids complex prompt builders or DSLs.
  Simple templates are easier to review, version and compare.

---

## Dataset design

- **Test cases are version-controlled assets.**
  Benchmark inputs are treated as project data rather than temporary
  examples. This ensures reproducibility between benchmark runs.

- **Small datasets before large datasets.**
  Early development focuses on correctness and repeatability instead of
  benchmark size. Dataset expansion comes only after the evaluation
  methodology stabilizes.

---

## Model abstraction

- **Models are interchangeable.**
  The framework is designed around provider-independent execution rather
  than provider-specific APIs. Adding another LLM should require minimal
  architectural changes.

- **Evaluation logic never depends on a specific vendor.**
  Providers are considered infrastructure, not business logic.

---

## Reporting

- **Reports are generated from structured evaluation data.**
  Markdown reports are outputs, not sources of truth. Raw scores remain
  available for future visualizations or statistical analysis.

- **Machine-readable artifacts are preferred over screenshots.**
  Structured outputs make future dashboards and automated comparisons
  possible.

---

## Documentation philosophy

- **LEARNINGS.md remains chronological.**
  It documents how ideas evolved over time.

- **docs/*.md remain thematic indexes.**
  Each document summarizes one aspect of the project without duplicating
  the implementation history.

- **Architecture decisions are recorded explicitly.**
  Design choices are considered part of the project deliverable, not
  knowledge hidden inside commits.

---

## Future-proofing

- **The framework is designed for experimentation rather than a single benchmark.**
  New evaluation criteria, providers and datasets should extend the
  framework without requiring architectural rewrites.

- **Methodology before optimisation.**
  Reliable measurements are prioritised over execution speed while the
  benchmark methodology is still evolving.

---

## Where to read more

Detailed reasoning behind each decision will be documented in
`LEARNINGS.md` as the project evolves.