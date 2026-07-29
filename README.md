# OpenSearch vs Zilliz Cloud Cost Benchmark

This repository contains the supporting data and cost model for an
OpenSearch vs Zilliz Cloud vector-search cost comparison.

It includes:

1. A measured 1M-vector benchmark summary.
2. Shared cost assumptions for AWS and Zilliz Cloud.
3. A reproducible monthly cost model for 1M, 10M, 100M, and 1B vectors.
4. Generated cost tables used by the article.

## Cost Model

```bash
python3 scripts/cost_model.py
```

## Directory Layout

```text
docs/       Assumptions and source notes
results/    Benchmark result summaries
scripts/    Benchmark and cost-model scripts
```
