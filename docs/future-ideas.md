# Future ideas — thematic index

Brainstormed improvements deliberately kept outside the current scope.
These ideas are recorded to preserve architectural direction rather than
serve as an implementation backlog.

The toolkit already evaluates LLM quality, hallucinations and prompt
injection resistance. The ideas below focus on making the framework more
useful as a reusable benchmarking platform rather than simply adding
more test cases.

Full reasoning behind implementation decisions belongs in
`LEARNINGS.md`; this document is intentionally a high-level roadmap.

---

## Multi-provider benchmarking

Today the toolkit executes evaluations against a single provider
(Anthropic). A natural evolution is running the same evaluation suite
against multiple providers:

- Anthropic Claude
- OpenAI GPT
- Google Gemini
- local Ollama models

allowing direct score comparison on identical prompts.

The long-term goal is not "which model is best" but "which model is
best for a particular evaluation category."

**Revisit:** first major feature after the evaluation pipeline becomes
stable.

---

## Judge calibration

Currently the toolkit trusts the LLM-as-judge score and augments it with
deterministic heuristics.

A future improvement would compare multiple judge prompts, multiple
judge models, or ensemble voting to measure judge consistency rather
than assuming a single judge is always correct.

This would make evaluator scores themselves measurable.

**Revisit:** after multiple providers are supported.

---

## Historical benchmark tracking

Regression tests currently compare a response against a single baseline.

Future versions should store benchmark history across runs, making it
possible to answer questions such as:

- Is this model improving?
- Is quality slowly degrading?
- Which prompt version performs best?
- Which evaluator changed the final score?

The emphasis shifts from single-pass evaluation toward continuous model
quality tracking.

---

## Evaluation datasets

Today prompts are maintained directly inside the repository.

Eventually the toolkit should support reusable benchmark datasets,
allowing hundreds or thousands of evaluation cases to be grouped by:

- domain
- language
- safety category
- business scenario
- evaluation objective

This would move the project closer to a genuine benchmarking framework.

---

## Rich reporting

Current reports focus on pytest and Allure.

Future reports could include:

- score distributions
- evaluator breakdowns
- regression trends
- provider comparison dashboards
- historical quality evolution

The objective is making benchmark results understandable at a glance
rather than reading individual test reports.

---

## Custom evaluator plugins

Today evaluators are implemented directly inside the project.

A plugin architecture would allow users to create their own evaluators,
for example:

- legal compliance
- medical safety
- financial accuracy
- company-specific policies

without modifying the core framework.

---

## Automatic threshold calibration

Thresholds (`min_score`) are currently selected manually.

A future calibration tool could analyze historical benchmark results and
recommend thresholds that better separate acceptable from unacceptable
responses.

This would reduce manual tuning as benchmark datasets grow.

---

## Prompt version benchmarking

The same evaluation suite could execute against multiple prompt
templates.

Instead of only comparing models, the framework would also compare
prompt engineering strategies using identical evaluation criteria.

This turns the toolkit into a prompt optimization platform as well.

---

## CI quality gates

Currently mock mode is intended for deterministic CI execution while
live API runs are performed manually.

Future CI workflows could:

- run deterministic evaluator validation on every commit
- execute scheduled live benchmark runs
- detect model regressions automatically
- publish benchmark reports after each scheduled execution

---

## Evaluation metadata

Future benchmark runs should capture richer metadata alongside scores:

- model version
- temperature
- execution time
- token usage
- evaluation cost
- prompt version
- evaluator version

This enables reproducible historical analysis long after individual
models evolve.

---

## Where to read more

- `LEARNINGS.md` documents architectural reasoning behind implemented
  decisions.
- `docs/gaps.md` tracks known shortcomings of the current framework.
- `docs/architecture-decisions.md` records major design choices that
  shaped the project.