# Agent Template — Master Plan (Plugin-First Architecture)

> Goal: ONE template that becomes ANY challenge agent in under 4 hours.
> Method: the pipeline is **composed**, not coded. Every capability is a **plugin**.
> A lightweight core skeleton wires plugins together based on a declarative **recipe**.

---

## 1. Design Principles

1. **Everything is a plugin.** No domain logic in `main.py`. Input, cleaning, retrieval, features, policy, confidence, validation, output, retries, logging — all plugins.
2. **The pipeline is data, not code.** A YAML recipe binds capabilities → concrete plugins → ordering → thresholds. Swapping a plugin is a config change, not a code change.
3. **Deterministic by default.** Code makes decisions. LLMs only perceive/understand. Where an LLM is unavoidable, its output is constrained (JSON schema) and gated (confidence).
4. **Contracts, not coupling.** Every plugin reads/writes typed, versioned schema objects (`Item`, `Evidence`, `ContextPackage`, …). Neighbors never import implementation — only contracts.
5. **Fail safe.** Every external touch point wraps in a fallback chain. The final fallback is the **safest action** (escalate / refuse / default).
6. **Verifiable in isolation.** Each plugin ships unit + adversarial tests. The harness can prove: "X plugin accounts for Y% of gold accuracy" (ablations).
7. **Observable in depth.** Every plugin appends a `TraceEvent`. The judge hears "decision = code", and the trace is the receipt.

---

## 2. Core Abstractions

### 2.1 `Plugin`

The single contract every plugin implements.

| Member | Purpose |
|---|---|
| `name` / `version` / `category` | Identity (registry keys) |
| `config_schema` | What YAML/ENV config it accepts; registry validates before run |
| `requires` (capabilities) | What it needs from other plugins (e.g. `features.text`, `perception.lang`) |
| `provides` (capabilities) | What it offers (e.g. `policy.safety`, `retrieval.hybrid`) |
| `hooks: setup / process(ctx) / shutdown` | Lifecycle: resource init → per-item work → cleanup |
| `health()` | Optional liveness used by observability/`fast-deploy` |

Rules:
- `process()` reads from `ctx`, writes only the fields its `provides` promises.
- A plugin must be side-effect-free on shared state (thread-safe) unless declared `actor=True` (single-threaded, e.g. a writer).
- Config validation fails loudly at setup, never mid-batch.

### 2.2 `Stage`

A named slot in the pipeline skeleton. Stages are FIXED; plugins are the muscle.

```
INPUT → CLEAN → CONTEXT → RETRIEVE → EXTRACT → PERCEIVE → DECIDE → CONFIDENCE → VALIDATE → OUTPUT
```

A stage can host:

| Mode | Meaning | Typical use |
|---|---|---|
| `one` | exactly one plugin | `policy.cascade` |
| `list` | any number, in order | feature extractors |
| `select` | run several, pick best (votes/quality) | confidence ensembling |
| `chain` | run first that succeeds (fallback) | model A → B → rule-based |
| `router` | decide which branch runs next | safety-gate short-circuit |

### 2.3 `ExecutionContext` (`ctx`)

Per-item bag of contracts, passed through all stages.

| Field | Written by | Contents |
|---|---|---|
| `item` | INPUT | raw record, original row id |
| `normalized` | CLEAN | cleaned/coerced record |
| `context` | CONTEXT | assembled package (history, metadata, token budget) |
| `evidence` | RETRIEVE | ranked evidence list + isolation info |
| `features` | EXTRACT | `{signal_key: {value, provenance}}` |
| `perception` | PERCEIVE | constrained LLM extractions |
| `decision` | DECIDE | label + reason + which rule fired |
| `confidence` | CONFIDENCE | score + band + calibration info |
| `validation` | VALIDATE | schema/coverage/enum results |
| `trace` | ALL | ordered `TraceEvent[]` |

`ctx` is never shared across items (only read-only indexes/resources are, and they are thread-safe).

### 2.4 Capability model

- Plugins **publish** capabilities and **consume** capabilities.
- The registry resolves `consumes → provides` using plugin availability + current config.
- Example: `features.risk` needs `perception.lang` OR `features.risk.heuristic`. If no LLM key is configured, the registry auto-picks the heuristic provider — same capability, different plugin.

This is the core malleability trick: **request intent, get an implementation**.

### 2.5 `Registry`

1. Discovers plugins (folder scan + entry points).
2. Validates each plugin's config against its `config_schema`.
3. Resolves the capability dependency graph; detects cycles / missing caps with clear errors.
4. Detects conflicts (two plugins claim the same single-slot capability).
5. Builds the pipeline from a recipe, verifying every `requires` is satisfied.

### 2.6 `TraceEvent`

Everything is traceable: `{stage, plugin, version, input_sig, output, confidence, time_ms, fallback_used}`. Trace is the source for: judge explanation, debugging, regression diffs, and "which plugin fired" ablations.

---

## 3. Execution Engine

### 3.1 Default flow + branches

- Default: linear stages. But the engine supports **routers**:

```
INPUT → CLEAN → CONTEXT → PERCEIVE(optional) → EXTRACT
                                                        ↓
                                             DECIDE (cascade)
                                           /    |      \
                           safety block   low conf    OK
                              ↓              ↓          ↓
                          ESCALATE      ESCALATE     AUTO-ACT
                              ↓              ↓          ↓
                        VALIDATE ←──────────┴──────────┘
                              ↓
                          OUTPUT (atomic write)
```

- A router plugin can **short-circuit** (safety gate fires → jump straight to VALIDATE+OUTPUT with escalate) — later stages never override it.

### 3.2 Executors (interchangeable)

| Executor | Use when | Notes |
|---|---|---|
| `sync-batch` | determinism / debugging | sequential, seeded RNGs |
| `thread-pool` | I/O-bound (LLM, retrieval) | default for perf |
| `process-pool` | CPU-bound extraction | picklable contracts |
| `stream` | very large datasets | memory-bounded generator→workers→sink |

Determinism harness: rerun under `sync-batch` to confirm same input → same output.

### 3.3 Checkpoints & quarantine

- **Checkpoint** after each stage on every batch → resume mid-run after crash (protects 100K-item runs).
- **Quarantine** bad rows to `quarantine/` (never crash the batch), produce a quality report.
- Atomic output: write temp file → validate → rename.

---

## 4. Policy Cascade as a Plugin Lattice

The original 5 levels become **plugin slots** you can reorder, insert, or replace.

| Slot | When it fires | Plugins that can fill it |
|---|---|---|
| **L1 Safety Gate** | first — nothing overrides | `risk.heuristic`, `risk.llm-guard`, injection/PII/credential rules |
| **L2 Confidence Gate** | decides "guess or escalate?" | `confidence.band`, dynamic thresholds |
| **L2.5 Escalation Bands** *(optional insert)* | per-domain escalation routing | SLA/scam/urgency plugins |
| **L3 Domain Rules** | the actual business logic | one plugin per domain ("banking", "support", "whatsapp"...) |
| **L4 Evidence Gate** | retrievable history present? | `evidence.threshold`, `evidence.vote` |
| **L5 Fallback** | nothing else decided | `fallback.safest-action` (escalate + explain, never invent) |

Adjudication: a `policy.cascade` router runs slots in configured order and collects the first definitive decision. Parallel-vote merge is an alternative mode (ensemble among plugins).

---

## 5. Recipe Layer — "the need of the hour"

A **recipe** is a YAML that locks: capability→plugin bindings, per-stage ordering, thresholds, model routing, fallback chains, target metric. Switching "needs" = switching recipes.

### 5.1 Recipe shape (planning sketch)

```yaml
name: multi-modal-verification
stages:
  input:      [csv.input, media.input]
  clean:      [text.normalize, media.validate]
  context:    [context.history]
  retrieve:   [retrieval.hybrid]
  extract:    [features.text, features.structural, features.risk]
  perceive:   [perception.vision, perception.lang]
  decide:     [policy.cascade]
  confidence: [confidence.calibrated]
  validate:   [validation.output-contract]
  output:     [output.csv-atomic]
policy:
  levels: {1: safety, 2: confidence-bands, 3: domain.routing, 4: evidence-gate, 5: fallback}
  action_on_low_confidence: escalate
models:
  perception:  {primary: api, fallback: [local, heuristic]}
  retrieval:   {embedder: local}
reliability:
  retries: 3; circuit_breaker: open_after_5; degrade: skip_non_critical
```

### 5.2 Pre-built recipes (shipped)

| Recipe | For challenges like | Hooks in |
|---|---|---|
| `text-classification.yaml` | triage / routing / intent | risk + simple rule cascade |
| `multi-modal-verification.yaml` | text + images (damage claims) | perception.vision, media validation |
| `retrieval-rag.yaml` | Q&A / evidence-heavy / history-dependent | retrieval.hybrid, evidence gate |
| `behavior-profile.yaml` | notification prefs, personalization | context.history, behavior features |
| `strict-compliance.yaml` | legal / financial | heavy validation, hard safety, no-guess |
| `safety-first.yaml` | safety-critical | max escalation, minimal auto-action |

### 5.3 Config Wizard (CLI)

The template ships a wizard that asks ~6 questions and **generates** a recipe + a starter plugin stub per need:

1. What input types? (text / image / voice / structured) → input+perception plugins
2. What output? (single label / multi-field / score + evidence) → validation plugins
3. Is per-user history or other rows available? → retrieval + isolation
4. Safety-critical? → L1 safety plugin set (scam/injection/PII)
5. Must explain? → trace + evidence emphasis
6. Local model only or API available? → model-resolution plugins

The wizard is a `lifecycle.*` plugin itself — batteries-included malleability.

---

## 6. Malleability Mechanisms (the full toolbox)

- **Plugins only** — zero domain logic in core code.
- **Config-driven composition** — recipe swap is the "how to change needs" answer.
- **Capability resolution** — ask for `retrieval.hybrid`, let registry pick the best provider.
- **Open-list stages** — add extractors / rules / risk detectors freely.
- **Fallback chains** — every external dependency: primary → secondary → rule-based → safest default.
- **Selector stages** — best-of-N LLM votes, quality-ranked evidence.
- **Feature flags** — disable any plugin without deleting it.
- **ENV overrides** — thresholds, keys, model names from environment (no hardcoding).
- **Prompts as plugins** — versioned, swappable, isolated prompt templates.
- **Mock adapters** — every external service (LLM, vector DB) ships a mock plugin for tests + day-1 offline runs.
- **Deterministic harness** — replayable, seeded, same input → same output; isolates LLM nondeterminism to its own stage.
- **A/B swaps** — two plugins offering the same capability, toggle by config.
- **Ablations** — disable any plugin and re-benchmark gold; quantifies each plugin's contribution.

---

## 7. Contracts (typed I/O) — swap-implementation-safe

| Contract | Written by | Key fields |
|---|---|---|
| `Item` | INPUT | `row_id`, raw fields (flexibly typed) |
| `Normalized` | CLEAN | cleaned fields, `quarantined`, issues[] |
| `ContextPackage` | CONTEXT | history[], metadata, token_budget, truncation log |
| `Evidence` | RETRIEVE | `doc_id`, score, `is_same_user`, source, snippet |
| `FeatureSet` | EXTRACT | `{key: {value, provenance, type}}` |
| `Perception` | PERCEIVE | constrained structured extractions (labels, entities, intents) |
| `Decision` | DECIDE | `label`, `reason`, `rule_fired`, `is_fallback` |
| `Confidence` | CONFIDENCE | `score`, `band`, `calibration`, `basis` |
| `ValidationResult` | VALIDATE | schema ok, enums, coverage, evidence hygiene |
| `OutputRow` | OUTPUT | exact expected columns/order, atomic |

All Pydantic-backed; any plugin can be swapped as long as it emits the same contract.

---

## 8. Reliability & Failure Model

- **Never crash the batch:** plugin errors → quarantine row → continue; external errors → retry → fallback → degrade.
- **Circuit breaker per external service** (LLM API, vector index, DB): open after N failures, half-open probe, close on recovery.
- **Graceful degradation:** under load, skip non-critical plugins (feature flags turn them off at runtime); core path always completes.
- **Deterministic replay:** given a trace/timestamp, re-run the exact path for debugging what the judge saw.

---

## 9. Proposed Directory Layout

```
hackerrank-agent-template/
├── AGENTS.md                  # AI tool rules + transcript logging
├── README.md                  # Architecture overview (judge-facing)
├── PLAN.md                    # This document
├── PLUGIN_CATALOG.md          # Plugin type encyclopedia
├── pyproject.toml             # deps, entry points (plugin discovery)
├── recipes/                   # declarative compositions
│   ├── text-classification.yaml
│   ├── multi-modal-verification.yaml
│   ├── retrieval-rag.yaml
│   ├── behavior-profile.yaml
│   ├── strict-compliance.yaml
│   └── safety-first.yaml
├── core/                      # skeleton (no domain logic)
│   ├── plugin.py              # Plugin ABC + manifest helpers
│   ├── registry.py            # discovery + capability resolution
│   ├── pipeline.py            # stage graph + routers + executors
│   ├── context.py             # ExecutionContext
│   ├── contracts.py           # Item/Evidence/ContextPackage/Decision/...
│   ├── recipe.py              # load/validate recipes, generate via wizard
│   └── wizard.py              # 6-question recipe generator
├── plugins/                   # EVERY capability lives here
│   ├── input/                 #   csv, json, jsonl, media...
│   ├── cleaning/              #   normalize, dedupe, coerce, quarantine...
│   ├── context/               #   history, graph, token-budget, truncate...
│   ├── retrieval/             #   vector, keyword, hybrid, fuzzy, isolation...
│   ├── features/              #   text, structural, behavioral, risk...
│   ├── perception/            #   lang, vision, voice (LLM constrained out)
│   ├── policy/                #   cascade, safety-gate, domain-rules, evidence-gate, fallback...
│   ├── confidence/            #   heuristic, calibrated, band, ensemble...
│   ├── validation/            #   output-contract, coverage, atomic-write...
│   ├── output/                #   csv, jsonl, console...
│   ├── reliability/           #   retry, circuit-breaker, degrade, checkpoint...
│   ├── observability/         #   json-log, metrics, trace-sink...
│   └── testing/               #   benchmark, ablations, adversarial, mutation...
├── dataset/                   # challenge data (arrives with problem)
├── output.csv                 # final predictions
└── evaluation/
    ├── benchmark.py
    ├── ablations.py
    └── adversarial.py
```

---

## 10. Build Order (day of challenge)

| Phase | When | What |
|---|---|---|
| **S0 Core** | Hour 0–1 | skeleton: contracts → registry → pipeline → executors → recipe loader; 1 toy plugin + minimal recipe end-to-end; checkpoint/quarantine/atomic write |
| **S1 Safety defaults** | Hour 1 | L1 safety gate plugins (heuristic + mock LLM guard), L5 fallback, confidence bands |
| **S2 Validation** | Hour 1–2 | output-contract validation, coverage, atomic write, table already tested |
| **S3 Recipe fit** | Hour 2 | run wizard against the real problem statement → generate challenge recipe + plugin stubs |
| **S4 Challenge plugins** | Hour 2–4 | fill PERCEIVE / DECIDE / EXTRACT for the topic; iterate on sample gold to 70%+ |
| **S5 Prove** | Hour 4+ | full test suite, ablation numbers, stress test (other repo), deploy (other repo) |

### Definition of done for EVERY plugin
manifest + config schema + unit tests + adversarial tests + doc line + wired into at least one recipe.

---

## 11. Walkthrough Examples

### 11.1 Text triage challenge (May 2026 style)
- Recipe: `text-classification.yaml`
- Active plugins: `csv.input`, `text.normalize`, `features.text` (urgency/sentiment/length), `features.risk` (scam/injection), `perception.intent` (LLM), `policy.safety` (L1), `domain.triage-rules` (L3), `confidence.band`, `output.csv-atomic`.
- What decides: `domain.triage-rules` — plain rules on extracted signals. LLM only labels intent; code routes.
- Malleability: if gold shows LLM labels hurt, swap `perception.intent` for `features.intent-heuristic` (same capability).

### 11.2 Multi-modal verification challenge (June 2026 style)
- Recipe: `multi-modal-verification.yaml`
- Extras vs triage: `media.input`, `media.validate`, `perception.vision`, `retrieval.hybrid` (previous claims), `evidence-gate`.
- Cross-modal plugin: images described by vision plugin; policy decides support/contradict/NEI using evidence threshold + same-user isolation.

### 11.3 Build-vs-buy matrix (when to use what)

| Need | Buy (plugin) | Build (own plugin) |
|---|---|---|
| "understand text" | `perception.lang` (LLM) | heuristic keyword variant |
| "decide label" | — | **always your own** `policy.domain-rules` |
| "find history" | `retrieval.hybrid` | challenge-specific distance fn |
| "safety" | `features.risk` defaults | domain risk rules |
| "money/legal proof" | validation defaults | compliance rules |

---

## 12. Mapping to the Original 13 Features (preserved)

The old FEATURE_LIST modules become plugin **categories** (see PLUGIN_CATALOG.md). No planning is lost — it is reorganized under "core skeleton" vs "plugin catalog", where any numbered feature (e.g. "5.1 Scam detection", "6.1 Ridge calibration") maps to a concrete plugin spec.