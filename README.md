# HackerRank Orchestrate — 24-Hour Hackathon System

Three repos. One goal: win.

## The Repos

| Repo | Purpose | When to Use |
|---|---|---|
| `hackerrank-agent-template/` | Core agent architecture — plug in domain rules | Hour 0–4 |
| `hackerrank-fast-deploy/` | Production deployment in 45 minutes | Hour 4–5 |
| `hackerrank-stress-test/` | Generate impressive performance numbers | Hour 2–6 |

## 24-Hour Workflow

### Hour 0: Challenge Arrives (6 PM IST)

```
1. Read problem_statement.md carefully (15 min)
2. Identify: input format, output format, evaluation criteria
3. Clone hackerrank-agent-template
4. Copy challenge data into dataset/
5. Start AGENTS.md transcript logging
```

### Hour 0–1: Architecture Design

```
1. Map the challenge to template modules:
   - What's the input? → input_loader.py
   - What context is available? → context_builder.py
   - What retrieval is needed? → retrieval.py
   - What decisions to make? → policy.py (THE CORE)
   - What's the output schema? → models.py + validation.py
2. Write the policy cascade rules (pseudocode first)
3. Define confidence thresholds
4. Set up test cases from sample data
```

### Hour 1–4: Build the Agent

```
1. Implement policy.py — deterministic decision cascade
2. Implement retrieval.py — evidence selection
3. Implement context_builder.py — per-item context
4. Implement features.py — feature extraction
5. Implement confidence.py — calibrated scoring
6. Wire up main.py — end-to-end pipeline
7. Run against sample data → iterate
8. Target: 70%+ accuracy on sample gold
```

### Hour 2–3: Stress Testing (Parallel)

```
1. Clone hackerrank-stress-test
2. Run throughput tests on your agent
3. Capture baseline numbers
4. Identify bottlenecks
5. Optimize hot paths
6. Re-run tests → show improvement
```

### Hour 4–5: Production Deployment

```
1. Clone hackerrank-fast-deploy
2. Run deploy.sh — full stack in 45 min
3. Verify observability dashboards
4. Run smoke tests
5. Confirm production-grade setup
```

### Hour 5–8: Polish and Iterate

```
1. Improve accuracy on edge cases
2. Add adversarial tests
3. Refine prompts
4. Run full stress test suite → capture final numbers
5. Generate performance report (HTML with charts)
6. Write architecture docs (README.md for judge)
```

### Hour 8–12: Prepare for Submission

```
1. Final accuracy check against sample gold
2. Generate output.csv on full dataset
3. Run validation suite (schema, coverage, allowed values)
4. Package code.zip (no secrets, no caches)
5. Export chat transcript (log.txt)
6. Review submission checklist:
   - [ ] output.csv: one row per input row
   - [ ] output.csv: correct columns in correct order
   - [ ] code.zip: runnable solution + setup instructions
   - [ ] log.txt: AI chat transcript
```

### Hour 12: Submit

```
1. Upload to HackerRank Community Platform
2. Verify submission received
3. Take a break
```

### Hour 13+: AI Judge Interview (30 min)

```
1. Pitch: Walk through architecture (2 min)
2. Problem framing: Why these design choices? (5 min)
3. Technical deep-dive: Code, retrieval, policy cascade (10 min)
4. Safety and failure modes: What breaks? How do you handle it? (5 min)
5. Production viability: Monitoring, scaling, reliability (3 min)
6. What's novel: Your unique contribution (3 min)
7. Honest limitations: What you'd improve with more time (2 min)
```

**Interview Strategy:**
- Be specific: "I used a 5-level deterministic cascade, Level 1 is safety, Level 2 is confidence gate..."
- Be honest: "This edge case isn't handled yet, with more time I'd add X"
- Show ownership: "I chose RAG over fine-tuning because..."
- Reference evidence: "On sample rows, this rule achieved 85% accuracy"
- Don't say "validated" without saying HOW

## The Winning Formula

```
Deterministic decisions (code) + LLM understanding (model) + Production thinking (DevOps)
```

- LLMs for: understanding text, extracting features, classifying intent
- Code for: routing decisions, safety checks, confidence thresholds, validation
- DevOps for: observability, testing, deployment, reliability

## What Judges Look For

| Signal | Weight | How to Nail It |
|---|---|---|
| Agent Architecture | 30% | Tool-calling loops, model-driven routing, multi-stage pipeline |
| Prompt & Tool Craft | 30% | Clear system prompts, structured output, refusal conditions |
| Agent Robustness | 25% | Guardrails, retries, validation, fallback behavior |
| Engineering Rigor | 15% | Modularity, type hints, secrets via env, function size |

## Interview Scoring

| Dimension | Weight | What to Show |
|---|---|---|
| Technical Depth & Ownership | 40% | Explain architecture, retrieval, classification, prompts, guardrails |
| Problem Understanding & Judgment | 25% | Tradeoffs, failure modes, why your approach fits |
| Communication Clarity | 20% | Direct answers, concrete examples, structured explanation |
| Honesty & Self-Awareness | 15% | Limitations, what you'd improve, where AI helped |

## Key Insight from Winners

> "I didn't pick the smartest model. I built the smartest system."
> — Faraaz Khan, 3rd Place (June 2026)

> "The model only describes what it sees. Plain code makes the actual decision."
> — Swayam Mishra, 3rd Place (June 2026)

> "79/79 tests passing, 30/30 sample gold, safety 1.000. The decision is the code."
> — August 2026 top submission

**The pattern:** LLMs understand. Code decides. Testing proves it.
