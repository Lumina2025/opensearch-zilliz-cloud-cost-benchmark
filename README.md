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

The Capacity estimates use Standard pricing for 1M, 10M, and 100M vectors,
and Enterprise pricing for the 128-CU cluster at 1B. At 1B, the estimated
monthly cost is **$25,509.12 compute + $21.70 modeled storage = $25,530.82**
(approximately **$25,531**). See [assumptions and pricing sources](docs/assumptions.md).

To regenerate the published cost table:

```bash
python3 scripts/cost_model.py > results/cost_table.md
```

## Directory Layout

```text
docs/       Assumptions and source notes
results/    Benchmark result summaries
scripts/    Benchmark and cost-model scripts
```
