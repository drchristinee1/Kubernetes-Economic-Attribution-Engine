# Jira Workflow Mapping

**From Cost Signal → Ownership → Engineering Action**

This document describes how the **Kubernetes Economic Attribution Engine** integrates with Jira to convert cost signals into structured, actionable workflows.

The goal is to eliminate the gap between:

- cost visibility
- and engineering action

---

## 1. The problem

In many organizations:

- FinOps detects cost anomalies
- dashboards show spikes and inefficiencies
- reports are shared with engineering teams

But nothing happens.

This creates a “notification gap”:

> insight exists, but no structured action is taken.

This integration closes that gap.

---

## 2. The solution

This engine maps Kubernetes cost signals into **Jira issues with ownership and context**.

Instead of:

- sending reports
- emailing stakeholders
- relying on manual follow-ups

We create:

> **structured, trackable, owner-assigned cost actions**

---

## 3. Signal → Action Mapping

| FinOps Signal | Description | Jira Action |
|---|---|---|
| Cost Spike | Sudden increase in namespace cost (>25%) | Create investigation ticket |
| Idle Capacity | High unused cluster capacity | Create optimization task |
| Overprovisioning | Requests significantly exceed usage | Recommend rightsizing |
| Missing Ownership | Namespace lacks `finops.owner` | Create governance ticket |
| Platform Cost Change | Shared service cost increase | Notify platform team |

---

## 4. Jira Issue Structure

Each cost signal is translated into a Jira issue with standardized fields.

### Example Issue

**Summary**

[FinOps] Cost Spike Detected – Namespace: payments

**Description**
A cost spike (>25%) has been detected in the "payments" namespace.

Details:

Usage increased significantly compared to baseline
Potential drivers: traffic increase, scaling behavior, or misconfiguration

Recommended actions:

Review recent deployments
Validate autoscaling configuration
Compare requests vs actual usage
