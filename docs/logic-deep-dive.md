# Logic Deep Dive

This document explains the allocation logic behind the **Kubernetes Economic Attribution Engine**.

The goal is not just to show Kubernetes cost. The goal is to **fully attribute** it in a way that Finance, Engineering, and Platform teams can inspect, challenge, and understand.

---

## 1. Why this model exists

Cloud providers bill Kubernetes infrastructure at the **node** level.

But organizations operate at the:

- namespace level
- service level
- product level
- team level

That creates a mismatch between:

- **how cost is billed**
- **how value is created**
- **how accountability is assigned**

If we allocate only direct workload usage, a large portion of cost remains hidden in:

- shared platform services
- unused node capacity
- cluster overhead

This engine closes that gap.

---

## 2. Fully burdened cost model

This project uses a **fully burdened allocation model**:

```text
Total Namespace Cost
= Direct Request Cost
+ Shared Platform Cost
+ Idle Capacity Cost
