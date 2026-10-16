#!/usr/bin/env python3
"""Cost model for OpenSearch vs Zilliz Cloud vector-search workloads."""

from __future__ import annotations

import math
from dataclasses import dataclass


HOURS_PER_MONTH = 730

DIM = 768
M = 16
HNSW_UPPER_LAYER_FACTOR = 1.05
METADATA_BYTES_PER_ROW = 100

AWS_OPENSEARCH_GP3_GB_MONTH = 0.122
ZILLIZ_STANDARD_MAX_CU = 32
ZILLIZ_CAPACITY_CU_HOUR = {"Standard": 0.175, "Enterprise": 0.273}
ZILLIZ_TIERED_CU_HOUR = 0.263
ZILLIZ_STORAGE_GB_MONTH = 0.025


@dataclass(frozen=True)
class OSInstance:
    name: str
    ram_gb: int
    hourly: float


OPENSEARCH_R7G = [
    OSInstance("r7g.large.search", 16, 0.178),
    OSInstance("r7g.xlarge.search", 32, 0.356),
    OSInstance("r7g.2xlarge.search", 64, 0.711),
    OSInstance("r7g.4xlarge.search", 128, 1.422),
    OSInstance("r7g.8xlarge.search", 256, 2.845),
    OSInstance("r7g.12xlarge.search", 384, 4.267),
    OSInstance("r7g.16xlarge.search", 512, 5.689),
]


def vector_gb_sq8(rows: int) -> float:
    return rows * DIM * 1 / 1_000_000_000


def hnsw_graph_gb(rows: int) -> float:
    return rows * M * 4 * HNSW_UPPER_LAYER_FACTOR / 1_000_000_000


def metadata_gb(rows: int) -> float:
    return rows * METADATA_BYTES_PER_ROW / 1_000_000_000


def opensearch_required_ram_gb(rows: int) -> float:
    return 2 * (vector_gb_sq8(rows) + hnsw_graph_gb(rows))


def opensearch_index_disk_gb(rows: int) -> float:
    return 2 * (vector_gb_sq8(rows) + hnsw_graph_gb(rows) + metadata_gb(rows))


def pick_opensearch(rows: int) -> tuple[OSInstance, int]:
    required = opensearch_required_ram_gb(rows)
    for inst in OPENSEARCH_R7G:
        if inst.ram_gb >= required:
            return inst, 1
    largest = OPENSEARCH_R7G[-1]
    return largest, math.ceil(required / largest.ram_gb)


def opensearch_monthly(rows: int) -> dict[str, float | str | int]:
    inst, nodes = pick_opensearch(rows)
    compute = inst.hourly * nodes * HOURS_PER_MONTH
    ebs_gb = opensearch_index_disk_gb(rows)
    ebs = ebs_gb * AWS_OPENSEARCH_GP3_GB_MONTH
    return {
        "instance": inst.name,
        "nodes": nodes,
        "required_ram_gb": opensearch_required_ram_gb(rows),
        "index_disk_gb": ebs_gb,
        "compute_month": compute,
        "ebs_month": ebs,
        "total_month": compute + ebs,
    }


def zilliz_capacity_cu(rows: int) -> int:
    sizing = {
        1_000_000: 1,
        10_000_000: 2,
        100_000_000: 16,
        1_000_000_000: 128,
    }
    if rows not in sizing:
        raise ValueError(f"No Zilliz Capacity sizing configured for {rows:,} rows")
    return sizing[rows]


def zilliz_tiered_cu(rows: int) -> int:
    sizing = {
        1_000_000: 1,
        10_000_000: 1,
        100_000_000: 4,
        1_000_000_000: 24,
    }
    if rows not in sizing:
        raise ValueError(f"No Zilliz Tiered sizing configured for {rows:,} rows")
    return sizing[rows]


def zilliz_storage_month(rows: int) -> float:
    # Lower-bound raw SQ8-style vector footprint plus small metadata; real billed
    # storage includes index/system overhead and should be verified from billing.
    return (vector_gb_sq8(rows) + metadata_gb(rows)) * ZILLIZ_STORAGE_GB_MONTH


def zilliz_capacity_monthly(rows: int) -> dict[str, float | int | str]:
    cu = zilliz_capacity_cu(rows)
    # The article uses Standard where supported; its single 128-CU cluster
    # exceeds the Standard plan's 32-CU limit and uses Enterprise pricing.
    plan = "Standard" if cu <= ZILLIZ_STANDARD_MAX_CU else "Enterprise"
    hourly = ZILLIZ_CAPACITY_CU_HOUR[plan]
    compute = cu * hourly * HOURS_PER_MONTH
    storage = zilliz_storage_month(rows)
    return {
        "cu": cu,
        "plan": plan,
        "cu_hourly": hourly,
        "compute_month": compute,
        "storage_month": storage,
        "total_month": compute + storage,
    }


def zilliz_tiered_monthly(rows: int) -> dict[str, float | int]:
    cu = zilliz_tiered_cu(rows)
    compute = cu * ZILLIZ_TIERED_CU_HOUR * HOURS_PER_MONTH
    storage = zilliz_storage_month(rows)
    return {"cu": cu, "compute_month": compute, "storage_month": storage, "total_month": compute + storage}


def money(v: float) -> str:
    return f"${v:,.0f}" if v >= 100 else f"${v:,.2f}"


def main() -> None:
    print("| Scale | OpenSearch AWS monthly | Zilliz Capacity monthly | Zilliz Tiered monthly | Notes |")
    print("|-|-:|-:|-:|-|")
    for rows in [1_000_000, 10_000_000, 100_000_000, 1_000_000_000]:
        os = opensearch_monthly(rows)
        cap = zilliz_capacity_monthly(rows)
        tier = zilliz_tiered_monthly(rows)
        scale = f"{rows//1_000_000}M" if rows < 1_000_000_000 else "1B"
        notes = (
            f"OpenSearch {os['nodes']} x {os['instance']}; "
            f"Capacity {cap['cu']}CU ({cap['plan']}); Tiered {tier['cu']}CU (Standard)"
        )
        print(
            f"| {scale} | {money(os['total_month'])} | {money(cap['total_month'])} | "
            f"{money(tier['total_month'])} | {notes} |"
        )


if __name__ == "__main__":
    main()
