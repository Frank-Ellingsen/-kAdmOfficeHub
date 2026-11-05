import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Legg til prosjektets rot i sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.analytics.duckdb_engine import DuckDBEngine
from src.core.agent_engine import SupervisorAgent
from app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="ØkAdmOfficeHub – Det Norske Brenneri AS",
    page_icon="🥃",
    layout="wide"
)

render_sidebar()
engine = DuckDBEngine()
provider = st.session_state.get("llm_provider", "gemini")

st.title("🥃 ØkAdmOfficeHub – AI Cockpit & Finansiell Drift")
st.markdown(
    "**Virksomhet:** Det Norske Brenneri AS (Org.nr 996 928 977)  \n"
    "**Orkestrering:** Antigravity Multi-Agent Hierarkisk DAG (Supervisor + 4 Domene-spesialister)"
)

st.markdown("---")

# Hent nøkkeltall deterministisk fra DuckDB
reskontro_df = engine.reskontro_aldersfordeling()
tot_utestaaende = reskontro_df["Totalt_Utestaaende"].sum() if not reskontro_df.empty else 0.0
over_60d = reskontro_df["Forfalt_over_60d"].sum() if not reskontro_df.empty else 0.0

skattetrekk = engine.skattetrekk_verifier()
mva = engine.beregn_netto_mva()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Kundereskontro Totalt", f"{tot_utestaaende:,.0f} NOK")
col2.metric("Forfalt >60 dager", f"{over_60d:,.0f} NOK", delta="-8,500 NOK risiko", delta_color="inverse")
col3.metric("Skattetrekksdekning", f"{skattetrekk['dekning_prosent']}%", delta=f"{skattetrekk['differanse']:,.0f} NOK mangel", delta_color="inverse")
col4.metric("Netto MVA Termin 1", f"{mva['netto_mva_til_betaling']:,.0f} NOK", delta="Forfall 10. apr")

st.markdown("---")

# Supervisor Agent Chat / Query
st.subheader("🤖 Supervisor Agent – Autonom Oppgaveløser")
st.caption("Still et spørsmål om MVA, reskontro, alkoholavgifter, likviditet eller regelverk:")

user_input = st.text_input("Hva ønsker du utført i dag?", placeholder="F.eks: 'Hvor mye skylder vi i skattetrekk?' eller 'Hva er reglene for MVA-fradrag på representasjon?'")

if st.button("Kjør oppgave", type="primary"):
    if user_input:
        with st.spinner("Supervisor analyserer og ruter oppgaven..."):
            supervisor = SupervisorAgent(provider=provider)
            response = supervisor.route_and_execute(user_input, provider=provider)
            st.markdown(response)
    else:
        st.warning("Vennligst skriv inn en oppgave eller et spørsmål.")

st.markdown("---")

# Oversikt over operative moduler
st.subheader("📚 Operative Moduler")
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("#### 1️⃣ MVA & Lovverk RAG")
    st.write("Semantisk søk i Lovdata (Merverdiavgiftsloven, Skatteloven, Regnskapsloven, Bokføringsforskriften).")
    st.info("Bruk menyen til venstre for å åpne modulen.")

with m2:
    st.markdown("#### 2️⃣ Reskontro & Særavgifter")
    st.write("DuckDB-drevet aldersfordeling på kundefordringer, avgiftsfritt vs fortollet spritlager, og skattetrekk 100%.")
    st.info("Bruk menyen til venstre for å åpne modulen.")

with m3:
    st.markdown("#### 3️⃣ FP&A & Risk Radar")
    st.write("12-måneders S-kurve for kontantstrøm, 3-Statement integrasjon og Early Warning-risikometrikker.")
    st.info("Bruk menyen til venstre for å åpne modulen.")

