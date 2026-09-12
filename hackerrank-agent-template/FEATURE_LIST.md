# Agent Template — Feature List

## 1. Input Layer

### 1.1 CSV/JSON Loader
- Auto-detect file format (CSV, JSON, JSONL)
- Schema inference from headers
- Encoding detection (UTF-8, Latin-1, etc.)
- Large file streaming (chunked reading)

### 1.2 Input Normalization
- Text cleaning (whitespace, control characters, Unicode normalization)
- Encoding fixes (mojibake detection and repair)
- Deduplication (exact and fuzzy)
- Type coercion (strings to numbers, dates, etc.)

### 1.3 Malformed Input Detection
- Missing required fields
- Invalid values (out of range, wrong type)
- Quarantine system (log bad rows, continue processing)
- Input quality report

### 1.4 Parallel File Loading
- Concurrent CSV/JSON reading
- Progress tracking for large files
- Memory-efficient streaming

---

## 2. Context Builder

### 2.1 Per-Item Context Assembly
- Load metadata for current item (user, group, business, etc.)
- Attach historical messages/events
- Build relationship graph (who interacts with whom)
- Token budget management (fit context within model limits)

### 2.2 Domain-Aware Context Selection
- Different context sources per item category
- Priority-based context ranking
- Context deduplication
- Relevance scoring

### 2.3 Evidence Pairing
- Match items to relevant historical data
- Same-user evidence isolation (no cross-user leakage)
- Temporal relevance (recent > old)
- Similarity threshold filtering

### 2.4 Context Window Management
- Token counting (tiktoken / local counter)
- Truncation strategies (head, tail, middle, importance-based)
- Summary fallback (compress when too long)
- Multi-turn context assembly

---

## 3. Retrieval Engine

### 3.1 Vector Similarity Search
- ChromaDB / FAISS / local embeddings
- Embedding model selection (sentence-transformers, etc.)
- Batch embedding for efficiency
- Persistence (save/load index)

### 3.2 Keyword-Based Retrieval
- BM25 scoring
- TF-IDF fallback
- Exact match boosting
- Fuzzy matching (Levenshtein, soundex)

### 3.3 Hybrid Retrieval
- Combine vector + keyword scores
- Configurable weights
- Score normalization
- Merge strategies (reciprocal rank fusion, etc.)

### 3.4 Evidence Ranking
- Top-k selection
- Relevance threshold (reject low-quality matches)
- Diversity scoring (avoid redundant evidence)
- Evidence explanation (why this evidence matters)

---

## 4. Feature Extraction

### 4.1 Text Features
- Length metrics (char count, word count, sentence count)
- Urgency detection (keywords, ALL CAPS, exclamation marks)
- Sentiment scoring (positive, negative, neutral)
- Entity extraction (names, dates, amounts, codes)
- Language detection
- Readability score

### 4.2 Behavioral Features
- Sender history (frequency, recency, engagement patterns)
- Response time patterns
- Notification preferences
- Group activity level
- Business interaction history

### 4.3 Structural Features
- Message type (text, image, voice, video)
- Media presence and quality
- Group membership and role
- Thread depth
- Forwarding chain

### 4.4 Risk Features
- Scam pattern detection (24+ families)
- Prompt injection detection (33+ patterns)
- Credential harvesting signals
- URL reputation
- Anomaly detection (unusual sender, unusual content)

---

## 5. Policy Cascade (THE CORE)

### 5.1 Level 1: Safety Gate
- Scam detection (keyword + pattern matching)
- Prompt injection prevention (instruction detection)
- PII exposure check
- Credential harvesting detection
- Fraud pattern matching
- Action: ESCALATE immediately, nothing downstream overrides

### 5.2 Level 2: Confidence Gate
- Minimum confidence threshold
- Below threshold → escalate (never guess)
- Configurable per domain
- Dynamic threshold based on item complexity

### 5.3 Level 3: Domain Rules
- Business logic routing
- Category classification
- Priority assignment
- SLA-based escalation

### 5.4 Level 4: Evidence Gate
- No evidence → escalate
- Weak evidence → low confidence
- Conflicting evidence → escalate
- Evidence quality scoring

### 5.5 Level 5: Fallback
- Default to safest action
- Log for manual review
- Never make up answers
- Always explain why

### 5.6 Decision Trace
- Every decision logged with:
  - Which level fired
  - What rule triggered
  - What evidence was used
  - What confidence was assigned
  - Timestamp and processing time

---

## 6. Confidence Calibration

### 6.1 Calibration Model
- Ridge regression fitted on sample gold rows
- Per-category calibration
- Temporal decay (older predictions less confident)
- Confidence capping (max 0.95)

### 6.2 Confidence Bands
- High confidence (> 0.8): Auto-action
- Medium confidence (0.5–0.8): Action with logging
- Low confidence (0.3–0.5): Escalate with reason
- Very low confidence (< 0.3): Immediate escalation

### 6.3 Confidence Validation
- Distribution analysis (not all 0.99)
- Calibration curve (predicted vs actual)
- Per-category breakdown

---

## 7. Validation Framework

### 7.1 Pre-Call Validation
- Validate input schema before processing
- Check required fields present
- Verify data types
- Reject malformed input early

### 7.2 Post-Call Validation
- Validate output against Pydantic model
- Check allowed values (enum membership)
- Verify row coverage (every input has output)
- Schema enforcement (column names, types, order)

### 7.3 Output Contract
- Exact column names and order
- Allowed value sets per column
- Evidence hygiene (valid IDs, no cross-user leakage)
- Confidence range validation (0–1)

### 7.4 Atomic Writes
- Write to temp file first
- Validate complete output
- Atomic rename (all-or-nothing)
- Rollback on failure

---

## 8. Prompt Engineering Module

### 8.1 System Prompts
- Role assignment
- Task description
- Output format specification
- Constraints and refusal conditions
- Few-shot examples

### 8.2 Prompt Management
- Isolated prompt files (not hardcoded)
- Version control for prompts
- A/B testing support
- Domain-specific prompt variants

### 8.3 Prompt Construction
- Dynamic context injection
- Evidence formatting
- Schema reminder
- Token budget management

---

## 9. LLM Integration Layer

### 9.1 Multi-Model Support
- Local models (Ollama, HuggingFace)
- API models (OpenAI, Anthropic, etc.)
- Model routing (different models for different tasks)
- Fallback chain (model A → model B → rule-based)

### 9.2 Inference Management
- Retry logic with exponential backoff
- Timeout handling
- Rate limiting
- Concurrent request management

### 9.3 Response Parsing
- JSON mode enforcement
- Structured output extraction
- Malformed response handling
- Schema validation on response

### 9.4 Token Tracking
- Input/output token counting
- Cost estimation
- Budget management
- Usage reporting

---

## 10. Observability Hooks

### 10.1 Structured Logging
- JSON log format
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Contextual fields (item_id, processing_time, decision)
- Log rotation

### 10.2 Decision Traces
- Full decision path for every item
- Rule execution order
- Evidence used
- Confidence scores
- Timing per stage

### 10.3 Performance Metrics
- Latency per item (total and per-stage)
- Throughput (items/second)
- Error rates by category
- Model usage statistics

### 10.4 Error Tracking
- Error classification (transient, permanent, data)
- Stack traces
- Recovery attempts
- Error rate trends

---

## 11. Testing Infrastructure

### 11.1 Unit Tests
- Test each module independently
- Mock external dependencies
- Edge case coverage
- Regression prevention

### 11.2 Property-Based Testing
- Hypothesis for generative testing
- Invariant checking
- Fuzz testing

### 11.3 Adversarial Testing
- Prompt injection attempts
- Malformed input handling
- Boundary condition testing
- Data poisoning detection

### 11.4 Mutation Testing
- Break rules intentionally
- Verify detection
- Test guard effectiveness

### 11.5 Regression Testing
- Track accuracy over iterations
- Detect performance degradation
- Compare approaches

### 11.6 Golden Dataset Testing
- Compare against sample gold
- Per-field accuracy
- Joint accuracy (all fields correct)
- Safety score

---

## 12. Configuration Management

### 12.1 YAML Configuration
- All thresholds, flags, model choices in one place
- Comments explaining each setting
- Example configuration provided

### 12.2 Environment Overrides
- Environment-based config (dev/staging/prod)
- CLI argument overrides
- Runtime configuration changes

### 12.3 Secret Management
- Environment variables (never hardcoded)
- .env file support
- Secret detection in CI
- No secrets in git history

### 12.4 Feature Flags
- Toggle components on/off
- A/B testing support
- Gradual rollout capability

---

## 13. Documentation

### 13.1 Architecture Docs
- Mermaid diagram of pipeline
- Module responsibilities
- Data flow explanation
- Design decisions log

### 13.2 API Reference
- Function signatures
- Parameter descriptions
- Return types
- Usage examples

### 13.3 Runbook
- How to debug common issues
- Log interpretation guide
- Performance tuning tips
- Known limitations

### 13.4 Interview Prep
- Architecture talking points
- Tradeoff explanations
- Failure mode descriptions
- Improvement roadmap
