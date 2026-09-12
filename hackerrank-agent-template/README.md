# Hackerrank Agent Template

The core agent architecture for HackerRank Orchestrate. Built to adapt to any challenge topic in under 4 hours.

## Philosophy

```
LLMs understand. Code decides. Testing proves it.
```

- LLMs for: understanding text, extracting features, classifying intent
- Code for: routing decisions, safety checks, confidence thresholds, validation
- Testing for: adversarial robustness, regression detection, accuracy verification

## Architecture

```
Input → Context Build → Retrieval → Feature Extract → Policy Cascade → Validate → Output
                                                        ↑
                                              DETERMINISTIC RULES
                                              (not LLM decisions)
```

## Directory Structure

```
hackerrank-agent-template/
├── AGENTS.md                    # AI tool rules + transcript logging
├── README.md                    # Architecture docs (judge reads this)
├── config.yaml                  # Model configs, thresholds, flags
├── main.py                      # CLI entry point
├── code/
│   ├── __init__.py
│   ├── input_loader.py          # Load CSVs, normalize, validate schemas
│   ├── context_builder.py       # Build per-item context (retrieval, metadata)
│   ├── features.py              # Feature extraction (120+ interpretable signals)
│   ├── retrieval.py             # Evidence retrieval (similarity, same-user, etc.)
│   ├── policy.py                # Deterministic decision cascade (THE CORE)
│   ├── confidence.py            # Calibrated confidence scoring
│   ├── validation.py            # Schema validation, allowed values, atomic write
│   ├── prompts.py               # System prompts (isolated, editable)
│   └── models.py                # Pydantic schemas for I/O
├── evaluation/
│   ├── benchmark.py             # Run against sample, measure accuracy
│   ├── ablations.py             # Test individual components
│   └── adversarial.py           # Edge case testing
├── tests/
│   ├── test_policy.py           # Test deterministic rules
│   ├── test_retrieval.py        # Test evidence selection
│   ├── test_validation.py       # Test output contract
│   └── test_adversarial.py      # Injection, edge cases
├── dataset/                     # Challenge data (arrives with problem)
├── output.csv                   # Final predictions
└── log.txt                      # Chat transcript (auto-generated)
```

## Quick Start

```bash
# 1. Clone template
git clone <this-repo> hackerrank-agent
cd hackerrank-agent

# 2. Copy challenge data
cp /path/to/challenge/dataset/ ./dataset/

# 3. Configure
cp config.example.yaml config.yaml
# Edit config.yaml with your settings

# 4. Run
python main.py

# 5. Evaluate
python evaluation/benchmark.py --gold --dataset dataset/

# 6. Check output
head -20 output.csv
```

## Customization Checklist

When the challenge drops, fill in these files:

- [ ] `code/policy.py` — Domain-specific decision rules
- [ ] `code/context_builder.py` — What context to assemble per item
- [ ] `code/features.py` — What features to extract
- [ ] `code/retrieval.py` — How to find evidence
- [ ] `code/prompts.py` — System prompts for LLM calls
- [ ] `config.yaml` — Thresholds, model choices, flags

Everything else (input loading, validation, confidence, testing) works out of the box.

## Evaluation Criteria Mapping

| Criterion | Module | What It Shows |
|---|---|---|
| Agent Architecture (30%) | `policy.py`, `main.py` | Multi-stage pipeline, tool-calling loops |
| Prompt & Tool Craft (30%) | `prompts.py` | Structured output, refusal conditions |
| Agent Robustness (25%) | `validation.py`, `policy.py` | Guardrails, retries, fallback behavior |
| Engineering Rigor (15%) | All modules | Modularity, type hints, secrets via env |
