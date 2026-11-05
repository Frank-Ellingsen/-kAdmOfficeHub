
from pathlib import Path

content = """# ØkAdmOfficeHub – Det Norske Brenneri AS

En AI-drevet, multi-agent plattform og operasjonell sentral for økonomi, regnskap, særlovgivning og likviditetsstyring skreddersydd for Det Norske Brenneri AS.

Systemet kombinerer RAG (Retrieval-Augmented Generation) mot relevante lover og forskrifter, DuckDB SQL Analytic Engine for reskontro- og lageranalyse, en 3-Statement Finansiell Prognosemodell (P&L, Balanse, Cash Flow), og et Antigravity Multi-Agent Økosystem.

---

## 🏛️ Systemarkitektur & Spesialistagenter (Antigravity Framework)

Systemet er bygget opp som et autonomt multi-agent økosystem som fordeler oppgavene på fem spesialiserte agenter:

1. **supervisor_agent (Orchestrator)**
   - Håndterer brukerhenvendelser, filopplasting (PDF, CSV, Excel) og ruter oppgaver dynamisk i en Directed Acyclic Graph (DAG) til riktig spesialistagent.
2. **compliance_rag_agent (Regelverksspesialist)**
   - Semantisk oppslag i ChromaDB mot Merverdiavgiftsloven (§ 8-1, § 8-2, § 8-3), Bokføringsforskriften (§ 8-10-6) og forretningsjus.
3. **analytics_reskontro_agent (Dataingeniør)**
   - Utfører aldersfordelingsanalyser på kundereskontro, oppdaterer prisfiler og avstemmer avgiftsfritt fatlager (ulåst) mot fortollet salgslager.
4. **tax_excise_agent (Offentlig Rapportering)**
   - Beregner MVA-oppgaver, alkoholavgift (kr 942,50/L ren alkohol) og emballasjeavgift, samt gjennomfører 100% automatisk skattetrekkskontroll (konto 1925 mot skyldig forskuddstrekk).
5. **cash_fpa_radar_agent (Likviditet & Prognose)**
   - Driver 3-statement prognosemodellen (2024–2026), simulerer arbeidskapitalendringer (DSO, DIO, DPO) og drifter Early Warning Risk Radar.
6. **procurement_anbud_agent (Anbud & Prising - NY)**
   - Bistår med Vinmonopolet anbudsbesvarelser, grossistprisfiler (Asko, Servicegrossistene), kalkyleberegning baklengs fra hyllepris og marginbeskyttelse.
7. **audit_year_end_agent (Årsavslutning & Revisor - NY)**
   - Utarbeider standardiserte avstemmingsbilag, dokumentasjonsmapper for ekstern revisor, anleggsavskrivninger og periodiseringskontroll.

---

## 📁 Prosjektstruktur

```
ØkAdmOfficeHub/
├── index.html                          # GitHub Pages Web UI & Dashboard
├── README.md                           # Prosjektdokumentasjon
├── .env                                # Miljøvariabler
├── data/
│   ├── raw_documents/                  # Lovdata PDF-er
│   ├── reskontro.csv                   # Kundereskontro
│   ├── lager_avstemming.csv            # Fatlager vs salgslager
│   ├── mva_oppgave_termin1.csv         # MVA-oppgave
│   ├── lonn_aga_avstemming.csv         # Lønnsdata & Forskuddstrekk
│   └── saravgift_spesifikasjon.csv     # Særavgifter
├── vector_store/
│   └── chroma_db/                      # Vektordatabase
└── src/
    ├── config.py                       # Konfigurasjon
    ├── main.py                         # CLI Hovedmeny
    ├── app.py                          # Streamlit Web App
    ├── rag/
    │   ├── ingest.py                   # PDF-innlesing & Vektorindeksering
    │   └── retriever.py                # RAG-søkemotor
    └── analytics/
        ├── duckdb_engine.py            # DuckDB SQL-analyse
        └── scenario_simulator.py       # Likviditetssimulator
```

---

## ⚙️ Installasjon & Hurtigstart

### 1. Klon repositoriet & installer avhengigheter
```bash
git clone <repository_url>
cd OkAdmOfficeHub
pip install pandas duckdb openpyxl langchain-chroma langchain-ollama langchain-google-genai streamlit
```

### 2. Bygg Vektordatabasen
```bash
python -m src.rag.ingest
```

### 3. Kjør CLI-Hovedmenyen
```bash
python -m src.main
```

### 4. Kjør Streamlit Web App
```bash
streamlit run src/app.py
```

---

## 🌐 Publisere via GitHub Pages (index.html)

1. Push endringene til GitHub.
2. Gå til **Settings** -> **Pages** i GitHub-repositoriet.
3. Velg **Source**: `Deploy from a branch` (Branch: `main`, Folder: `/root`).
4. Klikk **Save**. Dashboardet er nå tilgjengelig på din GitHub Pages nettadresse.

---

## 📊 Nøkkeltallsanalyse & Early Warning Radar

- **Total Omsetning**: 27,00 MNOK -> 31,05 MNOK (+15,0%)
- **EBITDA-margin**: 11,5% -> 16,0% (+450 bps)
- **DSO (Kreditdager)**: 49,5 dager -> 35,0 dager
- **DIO (Lagertid)**: 90,6 dager -> 70,0 dager
- **Net Free Cash Flow**: 1,71 MNOK -> 4,69 MNOK (+175%)
- **Skattetrekkdekning**: 100% verifisert mot konto 1925
