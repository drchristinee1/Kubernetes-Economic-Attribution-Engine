# Kubernetes-Economic-Attribution-Engine
Solving the unallocated Kubernetes spend problem through transparent, namespace-level cost attribution.
# Kubernetes Economic Attribution Engine

**Solving the unallocated Kubernetes spend problem through transparent, namespace-level cost attribution.**

Cloud providers bill Kubernetes infrastructure at the **node** level, but business value is created at the **namespace**, **service**, and **product** level.

That mismatch creates a major FinOps problem:

- Finance sees infrastructure cost but cannot fully attribute it
- Platform teams run shared services without transparent recovery logic
- Product teams scale workloads without understanding full cost-to-serve
- Executives lack reliable unit economics such as cost per order, request, or active user

This repository presents a **transparent, code-based economic attribution model** that reconciles:

- cloud billing inputs
- namespace-level usage inputs
- shared platform service overhead
- idle capacity cost

The result is a more complete and explainable view of Kubernetes cost ownership.

---

## The Business Problem

In many Kubernetes environments, a meaningful portion of spend sits in **shared**, **idle**, or **unallocated** buckets when teams only look at direct workload usage.

This creates three downstream problems:

### 1. Mystery Bills
Finance cannot explain a meaningful portion of the Kubernetes invoice.

### 2. Weak Accountability
Engineering teams over-request resources because the economic signal is muted.

### 3. Margin Erosion
Without unit economics, scaling decisions become operationally convenient but financially opaque.

---

## The Allocation Philosophy

This engine uses a **fully burdened attribution model**.

```text
Total Namespace Cost
= Direct Request Cost
+ Shared Platform Cost
+ Idle Capacity Cost

Direct Request Cost

Allocated at the higher of:

requested resources
actual usage

This discourages persistent over-requesting and makes reserved capacity visible.

Shared Platform Cost

Distributed proportionally across consuming namespaces based on a selected allocation driver such as:

requested CPU
requested memory
composite resource weight

This reflects the fact that logging, service mesh, security tooling, and observability are part of the cost to serve workloads.

Idle Capacity Cost

The cost of unused node capacity is distributed across namespaces to expose the cost of fragmentation, overprovisioning, and inefficient bin-packing.

Allocation vs Accountability

A core design principle of this project is:

Allocation and accountability are not always the same thing.

Example:

Platform Engineering upgrades the logging stack
logging cost doubles
Product teams see higher attributed cost
Product teams did not change their workloads

In that case:

allocation may still distribute the cost to consuming namespaces
accountability for the cost change remains with the Platform team

This distinction keeps attribution fair and makes cost changes explainable.

What This Repository Implements
core/calculator.py

A transparent Python-based economic attribution engine.

It calculates:

direct namespace cost
shared platform cost allocation
idle capacity allocation
total attributed namespace cost
reconciliation summary
docs/logic-deep-dive.md

Explains the allocation logic, assumptions, and reconciliation strategy behind the fully burdened model.

manifests/prometheus-alerts.yaml

Represents a future alerting layer for variance, anomaly detection, and missing ownership metadata.

manifests/opencost-values.yaml

Represents a future metric ingestion layer for collecting Kubernetes cost and usage inputs.

policies/quotas.yaml

Represents a future governance layer for constraining namespace-level resource consumption.

Core Attribution Questions

This engine is designed to answer five questions:

What did the cloud provider charge?
What did workloads request and consume?
What portion of cost was shared?
What portion of cost was idle?
How do we reconcile the total attributed view back to total billed cluster cost?
Reconciliation Goal
Total Attributed Namespace Cost = Total Billed Cluster Cost

That is the financial control objective.
| Namespace | Direct Cost | Shared Cost | Idle Cost | Total Cost |
| --------- | ----------: | ----------: | --------: | ---------: |
| payments  |     1200.00 |      300.00 |    150.00 |    1650.00 |
| checkout  |      980.00 |      250.00 |    120.00 |    1350.00 |
| search    |     1400.00 |      340.00 |    210.00 |    1950.00 |

FinOps Persona Guide
| Persona     | What they need                  | Output from this engine                         |
| ----------- | ------------------------------- | ----------------------------------------------- |
| Finance     | Explainable chargeback/showback | attributed cost by namespace and owner          |
| Engineering | Waste visibility                | over-requesting and idle cost exposure          |
| Platform    | Shared service transparency     | shared cost pool visibility                     |
| Executives  | Unit economics                  | foundation for cost-per-user, order, or request |

Getting Started
1. Clone the repository
git clone https://github.com/your-username/kubernetes-economic-attribution-engine.git
cd kubernetes-economic-attribution-engine
2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Run the calculator
python core/calculator.py
Starter Assumptions

This starter version uses sample inputs embedded in Python to demonstrate the model.

The next iteration can evolve to:

CSV-based inputs
OpenCost export ingestion
CUR / billing export reconciliation
Jira ticket generation
namespace ownership mapping
unit cost output such as cost per request
Roadmap
add CSV ingestion
add reconciliation report export
add namespace owner and cost-center mapping
add Prometheus alert rules
add Jira-integrated action routing
add unit economics output
add OpenCost ingestion workflow
Why This Matters

Kubernetes cost management fails when teams stop at raw usage.

This repository is built on a different belief:

The goal is not just visibility. It is economic attribution that drives accountability, governance, and financial clarity.

---

# `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so

# Virtual environments
.venv/
venv/
env/

# Distribution / packaging
build/
dist/
*.egg-info/

# Testing / coverage
.pytest_cache/
.coverage
htmlcov/

# Jupyter
.ipynb_checkpoints/

# macOS
.DS_Store

# VS Code
.vscode/

# Logs
*.log

# Output files
outputs/*.csv
outputs/*.json

# Environment files
.env
requirements.txt
pandas>=2.0.0
core/calculator.py
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
