# Office Hub - Antigravity Multi-Agent System Architecture (v2 - 7-Agent System)

## Overview
This document specifies the expanded 7-agent topology for **Office Hub** at **Det Norske Brenneri AS** (Org.nr 996 928 977). The multi-agent architecture automates accounting, legal compliance, tax reporting, liquidity management, tendering, and year-end audit preparation.

---

## 🤖 Agent Roster & Responsibilities

### 1. `supervisor_agent` (Master Orchestrator)
- **Role:** Central routing, intent recognition, session state management, and user interaction dispatch.
- **Inputs:** User text, uploaded PDF/CSV/Excel documents, API webhooks.
- **Outputs:** Targeted sub-agent routing, synthesized multi-agent responses.

### 2. `compliance_rag_agent` (Legal & Regulatory Specialist)
- **Role:** Merverdiavgiftsloven (§ 8-1, § 8-2, § 8-3 representasjon), Bokføringsforskriften (§ 8-10-6 samlede innkjøp).
- **Engine:** ChromaDB Vector Store + Gemini Flash / Llama 3.1.
- **Outputs:** Cited legal summaries, MVA code verification.

### 3. `analytics_reskontro_agent` (DuckDB Data & Inventory Specialist)
- **Role:** Accounts Receivable (AR) aging (0–30, 31–60, 60+ days), accounts payable matching, and bond warehouse vs. taxed inventory reconciliation (Harahorn, Arvesølvet, Eiktyrne).
- **Engine:** DuckDB In-Memory Analytical Engine.
- **Outputs:** Structured SQL query results, inventory variance reports.

### 4. `tax_excise_agent` (Altinn & Tax Authorities Specialist)
- **Role:** MVA returns, A-melding payroll verification, 100% Skattetrekk coverage check (Konto 1925), alcohol excise tax (NOK 942.50/L pure alc), and packaging environmental taxes.
- **Outputs:** Altinn XML/JSON payloads, Skattetrekk compliance reports.

### 5. `cash_fpa_radar_agent` (Liquidity & FP&A Risk Radar)
- **Role:** 3-Statement financial projections (P&L, BS, CF), working capital optimization (DSO, DIO, DPO simulation), and Early Warning Risk Radar.
- **Outputs:** S-curve cashflow trajectory, Early Warning alerts, capital release metrics.

### 6. `procurement_anbud_agent` (Tender & Pricing Specialist - NEW)
- **Role:** Assisting the sales team with Vinmonopolet tender submissions, wholesaler price file maintenance (Asko, Servicegrossistene), volume discount calculations, and margin protection.
- **Outputs:** Standardized tender pricing responses, updated wholesaler price files (CSV/Excel).

### 7. `audit_year_end_agent` (Year-End & External Auditor Specialist - NEW)
- **Role:** Period-end closing checklist, balance sheet specification, documentation folders for external auditors, fixed asset depreciation schedules, and accrual verifications.
- **Outputs:** Audit-ready working papers, balance sheet specification folders.

---

## 🔄 Multi-Agent Workflow DAG

```
                        ┌─────────────────────────────────┐
                        │       supervisor_agent          │
                        └────────────────┬────────────────┘
                                         │
 ┌───────────────┬───────────────┼───────────────┼───────────────┬───────────────┬───────────────┐
 ▼               ▼               ▼               ▼               ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Compliance  │ │ Analytics   │ │ Tax & Excise│ │ Cash & FP&A │ │ Procurement │ │ Audit & Year│ │ User UI     │
│ RAG Agent   │ │ Reskontro   │ │ Altinn      │ │ Radar Agent │ │ Anbud Agent │ │ End Agent   │ │ (Streamlit/ │
│             │ │ Agent       │ │ Agent       │ │             │ │ (NEW)       │ │ (NEW)       │ │ HTML)       │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```
