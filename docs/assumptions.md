# Assumptions

This repository is prepared for a public benchmark article comparing
OpenSearch and Zilliz Cloud for vector-search cost.

## Workload

- Dataset used in measured benchmark: VDBBench Cohere / Wikipedia 1M
- Vector dimension: 768
- Metric: COSINE
- Main measured scale: 1,000,000 vectors
- Estimated scales: 10M, 100M, 1B

## OpenSearch Cost Model

- Cloud cost model: Amazon OpenSearch Service, AWS US West (Oregon)
- Instance family: r7g.search
- Vector memory model: SQ8-friendly estimate, 1 byte per dimension
- HNSW graph: M=16, 4 bytes per edge, 1.05 upper-layer factor
- RAM sizing: `required_RAM = 2 * (vector_GB + hnsw_graph_GB)`
- Index disk: `2 * (vector_GB + hnsw_graph_GB + metadata_GB)`
- Metadata: 100 bytes per row
- EBS: gp3 storage at $0.122/GB-month

The cost model uses the SQ8-friendly storage assumption, while the measured
OpenSearch run used the default float vector storage.

## Zilliz Cloud Cost Model

- Dedicated / Capacity CU price: $0.175/CU/hour
- Tiered-storage CU price: $0.263/CU/hour
- Storage lower bound: $0.025/GB/month
- Capacity sizing used in the article: 1CU at 1M, 2CU at 10M, 16CU at 100M, and 128CU at 1B
- Tiered-storage sizing used in the article: 1CU at 1M, 1CU at 10M, 4CU at 100M, and 24CU at 1B
- 1B sparse analytics / On-Demand reference: Zilliz Cloud On-Demand official case reports a reduction from multi-thousand-dollar always-on estimates to under $500/month for sparse analytics.

## Sources

- Zilliz pricing guide: https://zilliz.com/pricing/pricing-guide
- Zilliz storage cost docs: https://docs.zilliz.com/docs/storage-cost
- VDBBench cost-aware blog: https://zilliz.com/blog/vdbbench-adds-cost-aware-benchmarking-for-vector-databases
- Zilliz Cloud On-Demand blog: https://zilliz.com/blog/zilliz-cloud-on-demand
- AWS OpenSearch Service price list JSON: https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonES/current/us-west-2/index.json
