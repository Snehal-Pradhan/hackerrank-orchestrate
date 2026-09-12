# Plugin Catalog — What Can Plug In, and When

> Reference for the plugin-first architecture in `PLAN.md`.
> Every row is a **plugin type** you may implement, install, or stub. Recipes bind these.
> Category maps 1:1 to the feature groups, so nothing from the original FEATURE_LIST is lost.

Legend — When to need it:
- **always** = core safety, every challenge needs a minimal version
- **topic** = only if the challenge topic demands it
- **optional** = polish/impact multiplyer

---

## 1. INPUT SOURCE — reading data

| Plugin type | Provides | When | Notes |
|---|---|---|---|
| `csv.input` | schema-inferred rows | always | streaming for 100K rows |
| `json.input` / `jsonl.input` | nested records | topic | flatten to `Item` |
| `media.input` | image/voice paths + bytes | topic (multi-modal) | never base64 into LLM prompt raw |
| `dir.input` | batch of files | topic | pairs with media |
| `api.input` | remote pull | optional | only if challenge feeds an API |

Also: encoding detection, mojibake repair, oversized-file quarantine.

---

## 2. CLEANING / NORMALIZATION — making rows honest

| Plugin type | Provides | When |
|---|---|---|
| `text.normalize` | whitespace/unicode/control-char cleanup | always |
| `type.coerce` | str→number/date/boolean | always |
| `dedupe.exact` / `dedupe.fuzzy` | duplicate-aware flags | topic |
| `malformed.quarantine` | bad-row quarantine + quality report | always |
| `pii.harden` | mask/PII flags before logging | always (safety optics) |

---

## 3. CONTEXT ASSEMBLY — what a row sees

| Plugin type | Provides | When |
|---|---|---|
| `context.history` | per-user/per-group history | topic (behavior, triage) |
| `context.metadata` | business/group/org metadata | topic |
| `context.graph` | who-interacts-with-whom edges | optional |
| `context.token-budget` | truncation/summary strategy | always when LLM used |
| `context.isolation` | same-user evidence only (no leakage) | **always** (judge checks) |

---

## 4. RETRIEVAL — finding evidence

| Plugin type | Provides | When |
|---|---|---|
| `retrieval.vector` | embedding similarity (Chroma/FAISS/HP) | topic (rag, verification) |
| `retrieval.keyword` | BM25 / TF-IDF / exact-boost | topic |
| `retrieval.hybrid` | RRF merge of vector+keyword | topic (default choice) |
| `retrieval.fuzzy` | Levenshtein/soundex | optional |
| `retrieval.rank` | top-k, threshold reject, diversity | always with retrieval |
| `retrieval.isolation` | restrict to same user/group | **always** |
| `retrieval.mock` | deterministic fake index | dev/tests/offline |

Capability note: requesting `retrieval.hybrid` lets the registry auto-pick vector+keyword providers.

---

## 5. FEATURE EXTRACTION — interpretable signals

| Plugin type | Provides | When |
|---|---|---|
| `features.text` | length, urgency, caps, emojis, sentiment | always |
| `features.structural` | type, media presence, group role, thread depth | topic |
| `features.behavior` | sender freq/recency, response times, prefs | topic (behavior-profile) |
| `features.risk` | scam families, prompt injection, credential signals, URL rep | always |
| `features.anomaly` | unusual sender/content/amount | topic (fraud/finance) |

Every signal is `{key: {value, provenance, type}}` — provenance makes ablations and interview answers concrete ("this rule used 3 signals: urgency=high, len>200, sender_recent=no").

---

## 6. PERCEPTION — LLM understanding (constrained)

| Plugin type | Provides | When |
|---|---|---|
| `perception.lang` | intents, entities, sentiments, labels (JSON-mode) | always (main LLM role) |
| `perception.vision` | image descriptions/scores | topic (multi-modal) |
| `perception.voice` | transcript/stt semantics | topic (voice) |
| `perception.committee` | best-of-N votes / self-consistency | optional |
| `perception.mock` | canned outputs | dev/tests/day-1 offline |

Constrain the LLM: structured output schema + refusal conditions + fallback chain to a heuristic when no API key is configured.

---

## 7. POLICY / DECISION — where code decides (THE core)

| Plugin type | Provides | When | Slot in cascade |
|---|---|---|---|
| `policy.safety` | escalate-on-risk, nothing overrides | always | L1 |
| `policy.confidence-gate` | guess? escalate? never guess | always | L2 |
| `policy.domain-rules` | the business routing logic | topic (write per challenge) | L3 |
| `policy.evidence-gate` | no/weak/conflicting evidence handling | topic (retrieval present) | L4 |
| `policy.fallback` | safest default + explanation | always | L5 |
| `policy.cascade` | the adjudicator router (order + short-circuit + parallel-vote mode) | always | — |

Rules keep a `rule_fired` string for every decision → judge sees a decision trace, not a model hallucination.

---

## 8. CONFIDENCE — calibrated scoring

| Plugin type | Provides | When |
|---|---|---|
| `confidence.heuristic` | from signal strength (rules) | always (baseline) |
| `confidence.calibrated` | ridge/probabilistic calibration on sample gold | high-value |
| `confidence.band` | bands: auto-act / log / escalate / immediate-escalate | always |
| `confidence.ensemble` | combine independent estimates | optional |
| `confidence.validation` | not-all-0.99 checks, calibration curve, per-category | always (evidence of rigor) |

---

## 9. VALIDATION — enforcing the output contract

| Plugin type | Provides | When |
|---|---|---|
| `validation.schema` | column names/types/order, allowed values | always |
| `validation.coverage` | every input row → one output row | always |
| `validation.evidence-hygiene` | valid doc ids, no cross-user leakage | always |
| `validation.atomic-write` | temp file → validate → rename | always |
| `validation.compliance` | domain-specific invariants (money/legal) | topic |

---

## 10. OUTPUT — submission artifacts

| Plugin type | Provides | When |
|---|---|---|
| `output.csv-atomic` | exact expected columns/order | always |
| `output.jsonl` | extra artifacts/log | optional |
| `output.console` | pretty progress | dev |
| `output.report` | summary numbers for interview | optional |

---

## 11. RELIABILITY — resilience wrappers

| Plugin type | Provides | When |
|---|---|---|
| `reliability.retry` | exponential backoff, idempotent replay | always (external calls) |
| `reliability.circuit-breaker` | open/half-open/close per service | always (external calls) |
| `reliability.degrade` | skip non-critical plugins under load | optional |
| `reliability.checkpoint` | resume mid-run | always (big datasets) |

---

## 12. OBSERVABILITY — proof of production thinking

| Plugin type | Provides | When |
|---|---|---|
| `obs.json-log` | structured per-item logs + rotation | always |
| `obs.trace-sink` | decision traces (feeding REPL show) | always |
| `obs.metrics` | Prometheus gauges/counters (used by fast-deploy) | high-value |
| `obs.replay` | deterministic replay from a trace | troubleshooting |

---

## 13. TESTING / EVALUATION — verifiable claims

| Plugin type | Provides | When |
|---|---|---|
| `benchmark.golden` | accuracy vs sample gold, per-field + joint | always |
| `benchmark.ablations` | disable each plugin → Δ accuracy | high-value (interview) |
| `adversarial.*` | injection, malformed, boundary, poisoning | always (safety proof) |
| `property.*` | Hypothesis-generated invariants | optional |
| `mutation.*` | break rules → verify detection | optional (rigor proof) |

---

## 14. LIFECYCLE / ORCHESTRATION — glue

| Plugin type | Provides | When |
|---|---|---|
| `orchestrate.recipe-loader` | load/validate recipes | always |
| `orchestrate.wizard` | generate recipe from 6 questions | always |
| `orchestrate.scheduler` | batch/stream/parallel executors | always |
| `orchestrate.cli` | `run / recipe / wizard / evaluate / trace` subcommands | always |

---

## Plugin Selection Cheat-Sheet

```
Is there text?              → features.text + perception.lang + policy.safety
Is there history for a row? → context.history + retrieval.hybrid + evidence-gate
Images/voice?               → media.input + perception.vision/voice
Money/legal/safety?         → features.risk + policy.safety + validation.compliance + no-guess fallback
Big dataset (100K)?         → checkpoint + stream executor + csv.input streaming
Must explain every answer?  → obs.trace-sink + evidence logging + rule_fired strings
```

If a capability is missing that a recipe requests, the registry error message tells you exactly which `plugins/*` file to create — stubs are generated by `orchestrate.wizard`.