# Office Hub - Antigravity Multi-Agent System Architecture
**Client / Entity:** Det Norske Brenneri AS (Org.nr 996 928 977)  
**Industry:** 46.340 Engroshandel med drikkevarer  
**Framework Standard:** Antigravity Agent Orchestration Engine (v2.4)  
**Author / Lead:** Frank Ellingsen (Øk/Adm AI Integration Specialist)

---

## 1. System Overview & Executive Summary

Office Hub is an autonomous, multi-agent AI framework engineered to execute the operational, administrative, compliance, and financial management responsibilities for Det Norske Brenneri AS. 

Instead of relying on a single monolithic LLM, Office Hub operates a **hierarchical supervisor-specialist multi-agent DAG (Directed Acyclic Graph)**. High-level reasoning, intent classification, and task orchestration are managed by the **Supervisor Agent**, while specialized execution is delegated to four domain-specific autonomous agents equipped with deterministic tools (DuckDB, ChromaDB, Altinn XML/JSON schema generators, and Financial 3-Statement engines).

```
                             ┌─────────────────────────────────────────┐
                             │       OFFICE HUB SUPERVISOR             │
                             │       (Orchestrator Agent)              │
                             └────────────────────┬────────────────────┘
                                                  │
         ┌───────────────────────┬────────────────┴───────┬───────────────────────┐
         ▼                       ▼                        ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  COMPLIANCE &    │    │   ANALYTICS &    │    │   TAX & EXCISE   │    │   CASH & FP&A    │
│   RAG AGENT      │    │ RESKONTRO AGENT  │    │  ALTINN AGENT    │    │   RADAR AGENT    │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                        │                       │
         ▼                       ▼                        ▼                       ▼
   [ChromaDB Vector Store]   [DuckDB Engine / Pandas] [Altinn XML Schema / API]  [3-Statement & S-Curve]
```

---

## 2. Specialist Agent Taxonomy & Responsibilities

### 2.1 Supervisor Agent (`supervisor_agent`)
* **Role:** Master Orchestrator, Router, and Context Evaluator.
* **Responsibilities:**
  * Parse incoming user queries, document uploads (PDF/CSV/Excel), and API events.
  * Classify query intent and construct sub-task execution graphs.
  * Delegate tasks to specialist agents in parallel or sequence.
  * Synthesize outputs into executive summaries and action plans.

### 2.2 Compliance & RAG Agent (`compliance_rag_agent`)
* **Role:** Legal, MVA, and Accounting Regulatory Specialist.
* **Domain Knowledge:** Merverdiavgiftsloven (§ 8-1, § 8-2, § 8-3), Bokføringsforskriften (§ 8-10-6), Aksjeloven, Skatteloven.
* **Primary Tools:** ChromaDB Vector Store (`merverdiavgiftsloven.pdf`, `regnskapsloven.pdf`).
* **Output:** Cited legal grounding, MVA code verification, deductible vs. non-deductible representation classification.

### 2.3 Analytics & Reskontro Agent (`analytics_reskontro_agent`)
* **Role:** Structured Data Processing, Ledger Reconciliation, and Inventory Audit.
* **Domain Knowledge:** Customer/Supplier ledgers (AP/AR), Vinmonopolet price lists, Bonded vs. Taxable spirits inventory (Harahorn Gin, Arvesølvet, Eiktyrne).
* **Primary Tools:** DuckDB SQL Analytics Engine, Pandas, Excel/CSV Importers.
* **Output:** Aging reports (0-30, 31-60, 60+ days), inventory reconciliation, gross margin analysis by SKU.

### 2.4 Tax & Excise Altinn Agent (`tax_excise_agent`)
* **Role:** Tax Reporting, Payroll Control, and Government Filings.
* **Domain Knowledge:** Skatteetaten Altinn filings, Alcohol excise tax (kr 942.50/L pure alcohol), Beverage packaging eco-tax, A-melding payroll & tax deduction account (Konto 1925).
* **Primary Tools:** Altinn XML Generator, Payroll Tax Matcher (100% Tax Account Verification).
* **Output:** Validated Altinn XML files for MVA Termin 1-6, Alcohol Excise Statements, Tax Account Coverage Certificates.

### 2.5 Cash & FP&A Radar Agent (`cash_fpa_radar_agent`)
* **Role:** 3-Statement Financial Modeling, Working Capital Optimization, and Early Warning System.
* **Domain Knowledge:** P&L, Balance Sheet, Cash Flow Waterfall, Cash Conversion Cycle (CCC = DSO + DIO - DPO), Project EAC Variance.
* **Primary Tools:** 3-Statement Financial Simulator, Liquidity Scenario Engine, Early Warning Radar.
* **Output:** 12-month Cash Flow S-Curve, Working capital optimization plans, Financial health alerts.

---

## 3. Communication Protocols & Data Contracts

All agents communicate via standardized JSON message frames passed over the Antigravity Event Bus:

```json
{
  "task_id": "TASK-20261105-001",
  "sender": "supervisor_agent",
  "target": "tax_excise_agent",
  "intent": "AUDIT_TAX_DEDUCTION_ACCOUNT",
  "payload": {
    "payroll_file": "lonn_aga_avstemming.csv",
    "bank_account_1925_balance": 93000.00
  },
  "constraints": {
    "require_100_percent_coverage": true,
    "output_format": "JSON_AND_SUMMARY"
  }
}
```

---

## 4. Antigravity Deployment & Execution Workflow

1. **Ingestion Trigger:** User drops a PDF document, CSV ledger, or asks a natural language question via the Web UI.
2. **Intent Parsing:** `supervisor_agent` inspects file schemas and query semantics.
3. **DAG Execution:**
   - If CSV → `analytics_reskontro_agent` runs DuckDB queries.
   - If Legal/MVA → `compliance_rag_agent` queries ChromaDB.
   - If Tax Filing → `tax_excise_agent` compiles Altinn payloads.
   - If Forecast → `cash_fpa_radar_agent` simulates 3-statement impact.
4. **Validation & Guardrails:** All numbers audited for balance ($Assets = Liabilities + Equity$, $Skattetrekk = 100\%$).
5. **Publishing:** Results published directly to Studio Panel artifacts and user UI.
