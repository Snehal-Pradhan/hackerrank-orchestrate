# Hackerrank Stress Test

Generate impressive, verifiable performance numbers. Not claimed — measured.

## Philosophy

```
Numbers talk. Bullshit walks. Show, don't tell.
```

## What You Get

- Throughput benchmarks (items/sec at various batch sizes)
- Latency distribution (p50, p95, p99)
- Concurrency tests (parallel processing limits)
- Scale tests (1K → 10K → 100K items)
- Reliability tests (error recovery, fallback validation)
- Accuracy under load (does speed kill accuracy?)
- HTML reports with charts (impress the judge)

## Quick Start

```bash
# Run all tests
python run_all.py

# Run specific category
python run_all.py --category throughput
python run_all.py --category concurrency
python run_all.py --category scale
python run_all.py --category reliability
python run_all.py --category accuracy

# Generate report
python generate_report.py

# Open report
open reports/latest/index.html
```

## Sample Output

```
╔══════════════════════════════════════════════════════════╗
║           HACKERRANK ORCHESTRATE — PERFORMANCE REPORT    ║
╠══════════════════════════════════════════════════════════╣
║ Items processed:        10,000                          ║
║ Total time:             2m 34s                          ║
║ Throughput:             64.9 items/sec                  ║
║ Latency p50:            12ms                            ║
║ Latency p95:            28ms                            ║
║ Latency p99:            45ms                            ║
║ Memory peak:            1.2GB                           ║
║ CPU utilization:        78%                             ║
║ Error rate:             0.00%                           ║
║ Accuracy (sample gold): 85%                             ║
╚══════════════════════════════════════════════════════════╝
```

## Directory Structure

```
hackerrank-stress-test/
├── run_all.py                   # Main test runner
├── generate_report.py           # HTML report generator
├── config.yaml                  # Test configuration
├── tests/
│   ├── __init__.py
│   ├── throughput.py            # Throughput benchmarks
│   ├── concurrency.py           # Parallel processing tests
│   ├── scale.py                 # Dataset size scaling
│   ├── reliability.py           # Error recovery tests
│   └── accuracy.py              # Accuracy under load
├── metrics/
│   ├── __init__.py
│   ├── collector.py             # Metrics collection
│   ├── aggregator.py            # Statistical aggregation
│   └── exporter.py              # Export to various formats
├── reports/
│   ├── templates/               # HTML report templates
│   └── latest/                  # Latest generated report
├── fixtures/
│   ├── small_dataset.csv        # 100 items
│   ├── medium_dataset.csv       # 1,000 items
│   ├── large_dataset.csv        # 10,000 items
│   └── stress_dataset.csv       # 100,000 items
└── baseline/
    └── baseline.json            # Previous results for comparison
```
