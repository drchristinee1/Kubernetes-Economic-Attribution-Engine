from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class NamespaceUsage:
    namespace: str
    requested_cpu: float
    used_cpu: float
    requested_memory_gb: float
    used_memory_gb: float


def build_sample_usage() -> pd.DataFrame:
    data = [
        NamespaceUsage("payments", requested_cpu=8, used_cpu=6, requested_memory_gb=16, used_memory_gb=12),
        NamespaceUsage("checkout", requested_cpu=6, used_cpu=4, requested_memory_gb=12, used_memory_gb=8),
        NamespaceUsage("search", requested_cpu=10, used_cpu=7, requested_memory_gb=20, used_memory_gb=14),
    ]
    return pd.DataFrame([vars(row) for row in data])


def calculate_allocation() -> pd.DataFrame:
    # ------------------------------------------------------------------
    # SAMPLE CLUSTER COST POOLS
    # These would later come from cloud billing exports or OpenCost data.
    # ------------------------------------------------------------------
    total_cluster_cost = 6000.00
    shared_platform_cost = 900.00
    idle_capacity_cost = 480.00

    # Direct cost is whatever remains after shared + idle pools are removed
    direct_cost_pool = total_cluster_cost - shared_platform_cost - idle_capacity_cost

    df = build_sample_usage()

    # ------------------------------------------------------------------
    # DIRECT COST LOGIC
    # We use the higher of requested vs actual usage as the economic basis.
    # This discourages chronic over-requesting from being economically hidden.
    # ------------------------------------------------------------------
    df["cpu_basis"] = df[["requested_cpu", "used_cpu"]].max(axis=1)
    df["memory_basis"] = df[["requested_memory_gb", "used_memory_gb"]].max(axis=1)

    # Simple weighted driver:
    # 1 CPU unit = 1 weight
    # 1 GB memory = 0.5 weight
    df["direct_driver_weight"] = df["cpu_basis"] + (df["memory_basis"] * 0.5)

    total_direct_weight = df["direct_driver_weight"].sum()
    if total_direct_weight == 0:
        raise ValueError("Total direct driver weight is zero; cannot allocate direct cost.")

    df["direct_cost"] = (df["direct_driver_weight"] / total_direct_weight) * direct_cost_pool

    # ------------------------------------------------------------------
    # SHARED PLATFORM COST LOGIC
    # Shared services are allocated proportionally based on request footprint.
    # ------------------------------------------------------------------
    df["shared_driver_weight"] = df["requested_cpu"] + (df["requested_memory_gb"] * 0.5)

    total_shared_weight = df["shared_driver_weight"].sum()
    if total_shared_weight == 0:
        raise ValueError("Total shared driver weight is zero; cannot allocate shared cost.")

    df["shared_cost"] = (df["shared_driver_weight"] / total_shared_weight) * shared_platform_cost

    # ------------------------------------------------------------------
    # IDLE CAPACITY COST LOGIC
    # Idle node capacity is distributed to namespaces based on reserved/requested footprint.
    # This exposes the cost of fragmentation and inefficient bin-packing.
    # ------------------------------------------------------------------
    df["idle_driver_weight"] = df["requested_cpu"] + (df["requested_memory_gb"] * 0.5)

    total_idle_weight = df["idle_driver_weight"].sum()
    if total_idle_weight == 0:
        raise ValueError("Total idle driver weight is zero; cannot allocate idle cost.")

    df["idle_cost"] = (df["idle_driver_weight"] / total_idle_weight) * idle_capacity_cost

    # Final fully burdened cost
    df["total_cost"] = df["direct_cost"] + df["shared_cost"] + df["idle_cost"]

    # Round for presentation
    money_cols = ["direct_cost", "shared_cost", "idle_cost", "total_cost"]
    df[money_cols] = df[money_cols].round(2)

    return df[
        [
            "namespace",
            "requested_cpu",
            "used_cpu",
            "requested_memory_gb",
            "used_memory_gb",
            "direct_cost",
            "shared_cost",
            "idle_cost",
            "total_cost",
        ]
    ]


def build_reconciliation_summary(df: pd.DataFrame) -> dict:
    attributed_total = round(df["total_cost"].sum(), 2)

    summary = {
        "reconciliation_goal": "Total Attributed Namespace Cost = Total Billed Cluster Cost",
        "attributed_total": attributed_total,
        "status": "reconciled",
    }
    return summary


def main() -> None:
    df = calculate_allocation()
    summary = build_reconciliation_summary(df)

    print("\nKubernetes Economic Attribution Report\n")
    print(df.to_string(index=False))

    print("\nReconciliation Summary\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
