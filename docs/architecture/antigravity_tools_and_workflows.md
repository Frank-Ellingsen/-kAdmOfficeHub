# Office Hub - Antigravity Tools & Automated Workflows
**Client / Entity:** Det Norske Brenneri AS  
**Framework Standard:** Antigravity Tool Specs & Workflow Triggers (v2.4)

---

## 1. Tool Registry

| Tool Name | Agent Owner | Backing Engine | Purpose |
| :--- | :--- | :--- | :--- |
| `chromadb_legal_search` | `compliance_rag_agent` | ChromaDB + Ollama/Gemini | Semantic search across Norwegian tax laws & precedents. |
| `duckdb_sql_query` | `analytics_reskontro_agent` | DuckDB / In-Memory SQL | Executes SQL queries directly on CSV/Excel files. |
| `reskontro_aging_analyser` | `analytics_reskontro_agent` | DuckDB Engine | Groups AR/AP ledgers into 0-30, 31-60, 60+ days aging buckets. |
| `skattetrekk_verifier` | `tax_excise_agent` | Python / DuckDB | Checks 100% tax account coverage (Konto 1925 vs. Payroll). |
| `altinn_xml_builder` | `tax_excise_agent` | Python XML Generator | Builds validated Altinn MVA & Excise Tax XML submission files. |
| `liquidity_simulator` | `cash_fpa_radar_agent` | Python Scenario Engine | Simulates cash freed by adjusting DSO, DIO, and DPO parameters. |
| `three_statement_engine` | `cash_fpa_radar_agent` | Integrated Financial Model | Generates linked P&L, Balance Sheet, and Cash Flow forecasts. |
| `early_warning_radar` | `cash_fpa_radar_agent` | Python Risk Engine | Evaluates 5 key financial risk metrics and flags warnings. |

---

## 2. Automated Operational Workflows

### Workflow 1: Bi-Monthly MVA & Altinn Filing Routine
```
[Trigger: Bi-monthly deadline]
   │
   ├──> 1. `analytics_reskontro_agent` extracts MVA transaction logs from Visma / CSV.
   ├──> 2. `compliance_rag_agent` validates MVA codes & checks representation items under § 8-3.
   ├──> 3. `tax_excise_agent` compiles MVA Termin Statement & builds Altinn XML payload.
   └──> 4. `supervisor_agent` presents final validation report to user for electronic signature.
```

### Workflow 2: Monthly Payroll & Skattetrekk Control
```
[Trigger: 20th of each month (Payroll Run)]
   │
   ├──> 1. `tax_excise_agent` parses A-melding draft and calculates total Forskuddstrekk.
   ├──> 2. `skattetrekk_verifier` queries Konto 1925 bank balance via Open Banking / API.
   ├──> 3. IF Bank Balance >= Skyldig Forskuddstrekk:
   │         └──> Mark status: "✅ 100% FULL DEKNING (GODKJENT)".
   └──> 4. ELSE:
             └──> Trigger urgent alert: "❌ DEKNINGSMANGEL - OVERFØR [X] NOK STRAKS".
```

### Workflow 3: Weekly Cash Flow & Working Capital Radar
```
[Trigger: Every Monday Morning]
   │
   ├──> 1. `analytics_reskontro_agent` updates DSO and DIO metrics from recent invoices & stock logs.
   ├──> 2. `cash_fpa_radar_agent` executes 12-month S-Curve cash flow projection.
   ├──> 3. `early_warning_radar` checks for EAC risk overruns or DSO spikes.
   └──> 4. `supervisor_agent` updates the interactive Web Cockpit in Studio.
```
