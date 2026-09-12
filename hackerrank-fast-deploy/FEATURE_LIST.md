# Fast Deploy — Feature List

## 1. Environment Setup (5 min)

### 1.1 Docker Environment
- Docker Compose for entire stack
- Multi-stage builds (smaller images)
- Layer caching (faster rebuilds)
- Health checks for all services

### 1.2 Python Environment
- pyproject.toml / uv for dependency management
- Frozen lockfile (reproducible installs)
- Virtual environment isolation
- Pre-commit hooks (lint, typecheck)

### 1.3 Dependency Installation
- Automated pip/uv install
- Version pinning
- Binary wheel caching
- Offline fallback (cached wheels)

### 1.4 Config Validation
- Check all required env vars present
- Validate config.yaml syntax
- Verify secrets available
- Test database/model connectivity

### 1.5 Health Check Endpoints
- `/health` — basic liveness
- `/ready` — readiness (all dependencies available)
- `/metrics` — Prometheus endpoint
- Per-service health status

---

## 2. Data Ingestion (5 min)

### 2.1 Automated Data Loading
- Load CSVs/JSONs from dataset/
- Schema validation on load
- Type inference and coercion
- Progress tracking

### 2.2 Data Quality Checks
- Missing field detection
- Format validation (dates, emails, IDs)
- Range checks (numeric values)
- Duplicate detection

### 2.3 Index Creation
- Vector embeddings (ChromaDB / FAISS)
- Keyword index (BM25 / inverted index)
- Metadata index (user, group, business)
- Persistence (save/load without recomputation)

### 2.4 Backup
- Raw data backup before processing
- Checksum verification
- Restore capability

---

## 3. Model Setup (5 min)

### 3.1 Local Model Download
- Ollama model pull (automated)
- HuggingFace model download (cached)
- Model size verification
- GPU detection and configuration

### 3.2 Model Health Check
- Inference test (send sample input)
- Response format validation
- Latency baseline measurement
- Memory usage check

### 3.3 Fallback Configuration
- Primary model → secondary model → rule-based
- Automatic failover on error
- Configurable retry logic
- Graceful degradation

### 3.4 Inference Endpoint
- FastAPI / Flask endpoint
- Concurrent request handling
- Timeout configuration
- Request queuing

---

## 4. Observability Stack (10 min)

### 4.1 Metrics Collection (Prometheus)
- Custom agent metrics:
  - `agent_items_processed_total` — total items processed
  - `agent_processing_duration_seconds` — per-item latency
  - `agent_decision_type_total` — decisions by type (reply/escalate/mute)
  - `agent_confidence_score` — confidence distribution
  - `agent_errors_total` — errors by category
  - `agent_retrieval_hits_total` — evidence retrieval hits
  - `agent_model_inference_seconds` — LLM inference time
- System metrics:
  - CPU usage
  - Memory usage
  - Disk I/O
  - Network I/O

### 4.2 Logging Pipeline
- Structured JSON logging
- Log levels (DEBUG → CRITICAL)
- Contextual fields (item_id, processing_time, decision)
- Log rotation (size-based, time-based)
- Centralized collection (Loki / stdout)

### 4.3 Decision Traces
- Full decision path per item
- Rule execution order
- Evidence used
- Confidence scores
- Timing per stage
- Exportable for debugging

### 4.4 Dashboards (Grafana)
- **Agent Overview:**
  - Real-time throughput (items/sec)
  - Decision distribution (pie chart)
  - Confidence histogram
  - Error rate timeline
- **Performance:**
  - Latency distribution (p50, p95, p99)
  - Latency over time
  - Model inference time
  - Retrieval time
- **Accuracy:**
  - Accuracy vs sample gold
  - Per-field accuracy breakdown
  - Confidence calibration curve
  - Error categories

### 4.5 Alerts
- Error rate > threshold → alert
- Latency p95 > threshold → alert
- Memory usage > 80% → alert
- Disk usage > 90% → alert
- Model inference failure → alert
- Configurable thresholds

---

## 5. Production Hardening (10 min)

### 5.1 Rate Limiting
- Per-client rate limits
- Global rate limits
- Token bucket algorithm
- Configurable via nginx

### 5.2 Circuit Breaker
- Detect failures (consecutive errors)
- Open circuit (stop processing)
- Half-open (test recovery)
- Close circuit (resume normal)
- Configurable thresholds

### 5.3 Graceful Degradation
- Partial results > crash
- Fallback to simpler model on failure
- Skip non-critical features under load
- Always return something useful

### 5.4 Resource Limits
- CPU limits per container
- Memory limits per container
- Disk space monitoring
- Process count limits

### 5.5 Process Management
- Supervisord for process supervision
- Auto-restart on failure
- Graceful shutdown (SIGTERM handling)
- Log stdout/stderr

### 5.6 Log Rotation
- Size-based rotation (100MB)
- Time-based rotation (daily)
- Compressed archives
- Retention policy (7 days)

### 5.7 Disk Space Monitoring
- Check available disk space
- Alert on low disk
- Auto-cleanup of old logs
- Data archiving

---

## 6. Deployment Validation (10 min)

### 6.1 Smoke Test
- Run 10 items end-to-end
- Verify output format
- Check no errors in logs
- Confirm all services healthy

### 6.2 Accuracy Check
- Compare against sample gold
- Per-field accuracy
- Joint accuracy (all fields correct)
- Safety score (no dangerous outputs)

### 6.3 Latency Benchmark
- Measure p50, p95, p99 latency
- Compare against baseline
- Identify bottlenecks
- Report results

### 6.4 Error Injection Test
- Simulate model failure → verify fallback
- Simulate network timeout → verify retry
- Simulate malformed input → verify validation
- Simulate memory pressure → verify degradation

### 6.5 Rollback Script
- Revert to last good state
- Restore from backup
- Verify rollback worked
- Log rollback event

---

## 7. Scripts Reference

### deploy.sh
```bash
# Full deployment in one command
# 1. Setup environment
# 2. Load data
# 3. Start model
# 4. Start observability
# 5. Harden production
# 6. Validate deployment
# Total time: ~45 minutes
```

### health.sh
```bash
# Check all services
# - Docker containers running?
# - Model serving?
# - Prometheus scraping?
# - Grafana accessible?
# - Agent responding to requests?
```

### monitor.sh
```bash
# Real-time metrics display
# - Throughput (items/sec)
# - Latency (p50, p95, p99)
# - Error rate
# - Confidence distribution
# - Model usage
```

### rollback.sh
```bash
# Revert to last good state
# 1. Stop current services
# 2. Restore from backup
# 3. Restart with previous config
# 4. Verify health
```

### backup.sh
```bash
# Backup everything
# - Dataset
# - Config
# - Model artifacts
# - Logs
# - Output
```
