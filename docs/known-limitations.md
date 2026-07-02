# Known limitations — thematic index

Things that are intentionally incomplete, outside the current project
scope or known to require further research. These are documented
deliberately rather than treated as hidden shortcomings.

Full discussion and future decisions belong in `LEARNINGS.md`; this file
serves as a quick reference.

---

## Scope boundaries (intentional, not bugs)

- **The framework evaluates responses rather than executing real software.**
  It measures the quality of generated QA artefacts, not whether those
  artefacts actually succeed against a live application.

- **The framework is prompt-driven.**
  Evaluation quality depends on carefully designed prompts rather than a
  formal verification engine. This is an accepted design choice for the
  current version.

- **Single-response evaluation.**
  Each benchmark currently evaluates one generated answer at a time.
  Multi-turn conversations and iterative refinement are outside the
  current scope.

- **Provider-independent architecture does not imply provider-independent results.**
  Different models naturally produce different outputs, and the framework
  intentionally exposes those differences rather than attempting to
  normalize them.

---

## Known methodological limitations

- **LLM-as-a-Judge remains an approximation of human review.**
  Evaluation scores should be interpreted as structured model opinions,
  not objective truth.

- **No human baseline exists yet.**
  Benchmark results currently compare models against each other rather
  than against experienced QA engineers.

- **Prompt wording influences results.**
  Small prompt changes may affect model performance. Prompt robustness
  has not yet been systematically evaluated.

- **Evaluation criteria currently use equal weighting.**
  No empirical weighting model has yet been established for different QA
  quality dimensions.

---

## Known technical limitations

- **Statistical confidence is not yet calculated.**
  Reports present average scores but do not yet include variance,
  confidence intervals or repeatability metrics.

- **Historical benchmark tracking is not yet implemented.**
  Individual benchmark runs are independent. Long-term trends between
  model versions are planned for a future iteration.

- **Cost analysis is intentionally deferred.**
  The framework focuses first on evaluation quality before introducing
  cost-per-quality comparisons across providers.

---

## Dataset limitations

- **Current benchmark datasets are intentionally small.**
  Early development prioritizes evaluation methodology over benchmark
  size.

- **Coverage of QA domains is still limited.**
  Additional datasets covering API testing, performance, security,
  accessibility and enterprise workflows are planned.

- **Most benchmark tasks are synthetic.**
  Future versions should incorporate larger collections of real-world QA
  artefacts such as production bug reports, requirements and test cases.

---

## Environment / tooling notes

- **LLM quality depends on the selected provider and model version.**
  Benchmark results obtained today should not be expected to remain
  identical after future model updates.

- **Inference latency varies between providers.**
  Runtime measurements should therefore be interpreted relative to the
  execution environment rather than as absolute performance metrics.

---

## Where to read more

Search `LEARNINGS.md` for the corresponding topic as the project
evolves. Architectural decisions and future improvements referenced here
are tracked separately in `docs/architecture-decisions.md`,
`docs/future-ideas.md` and `docs/gaps.md`.