# Hackerrank Fast Deploy

Production-grade deployment in under 45 minutes. One command. Full observability. No manual steps.

## Philosophy

```
Zero to production in 45 minutes. Not a hackathon prototype — a real system.
```

## What You Get

- Full containerized stack (Docker Compose)
- Real-time metrics dashboard (Prometheus + Grafana)
- Structured logging pipeline
- Circuit breaker and rate limiting
- Health checks and auto-recovery
- Smoke test validation
- Rollback capability

## Quick Start

```bash
# Full deployment (one command)
./scripts/deploy.sh

# Check status
./scripts/health.sh

# View dashboard
open http://localhost:3000

# Stop everything
./scripts/stop.sh

# Rollback to last good state
./scripts/rollback.sh
```

## Deployment Timeline

| Stage | Time | What Happens |
|---|---|---|
| Environment Setup | 5 min | Docker, Python, dependencies |
| Data Ingestion | 5 min | Load data, validate schema, create indices |
| Model Setup | 5 min | Download model, health check, configure fallback |
| Observability Stack | 10 min | Prometheus, Grafana, dashboards, alerts |
| Production Hardening | 10 min | Circuit breaker, rate limits, resource limits |
| Deployment Validation | 10 min | Smoke tests, accuracy check, latency benchmark |
| **Total** | **45 min** | **Production-ready system** |

## Directory Structure

```
hackerrank-fast-deploy/
├── docker-compose.yml           # Full stack definition
├── Dockerfile                   # Agent container
├── requirements.txt             # Python dependencies
├── scripts/
│   ├── setup.sh                 # Environment setup
│   ├── start.sh                 # Start all services
│   ├── stop.sh                  # Graceful shutdown
│   ├── health.sh                # Check all services healthy
│   ├── deploy.sh                # Full deployment in one command
│   ├── rollback.sh              # Revert to last good state
│   ├── monitor.sh               # Real-time metrics display
│   └── backup.sh                # Backup data and configs
├── config/
│   ├── prometheus.yml           # Prometheus configuration
│   ├── grafana/
│   │   ├── dashboards/          # Pre-built Grafana dashboards
│   │   └── provisioning/        # Auto-provision datasources
│   └── alertmanager.yml         # Alert rules
├── nginx/
│   └── nginx.conf               # Rate limiting, reverse proxy
├── monitoring/
│   ├── metrics.py               # Custom metrics definitions
│   ├── alerts.py                # Alert rule definitions
│   └── dashboards/
│       ├── agent-overview.json  # Main dashboard
│       ├── performance.json     # Latency/throughput
│       └── accuracy.json        # Accuracy metrics
└── validation/
    ├── smoke_test.py            # Quick validation
    ├── accuracy_check.py        # Compare against sample gold
    └── latency_benchmark.py     # Measure p50/p95/p99
```
