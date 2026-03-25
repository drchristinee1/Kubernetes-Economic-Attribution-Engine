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

