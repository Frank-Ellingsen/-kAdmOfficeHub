import sys
from pathlib import Path
import streamlit as st
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.analytics.duckdb_engine import DuckDBEngine
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="Reskontro, Lager & Skatt", page_icon="📊", layout="wide")
render_sidebar()

st.title("📊 Reskontro, Lageravstemming & Skattetrekk (DuckDB)")
st.markdown("Deterministisk analyse av kundefordringer, særavgifter for brenneriet, og lovpålagt skattetrekkskontroll.")

engine = DuckDBEngine()

tab1, tab2, tab3, tab4 = st.tabs([
    "📑 Kundereskontro (AR)",
    "📦 Lager & Særavgifter",
    "🏦 Skattetrekkskontroll (Konto 1925)",
    "📑 MVA Termin 1 & Altinn XML"
])

with tab1:
    st.subheader("Kundereskontro Aldersfordeling")
    df_res = engine.reskontro_aldersfordeling()
    if not df_res.empty:
        st.dataframe(df_res, use_container_width=True)
        tot = df_res["Totalt_Utestaaende"].sum()
        forfalt_60 = df_res["Forfalt_over_60d"].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Totalt Utestående Fordringer", f"{tot:,.2f} NOK")
        c2.metric("Forfalt > 60 dager (Høy Risiko)", f"{forfalt_60:,.2f} NOK", delta="Krever purring/inkasso", delta_color="inverse")
    else:
        st.warning("Finner ikke reskontrodata.")

with tab2:
    st.subheader("Lagerbeholdning og Særavgift (Alkohol kr 942.50/L ren alkohol)")
    df_lager = engine.avstem_lager_og_avgifter()
    if not df_lager.empty:
        st.dataframe(df_lager, use_container_width=True)
        tot_avgift = df_lager["Total_Avgiftsforpliktelse_NOK"].sum()
        st.metric("Total Påslått Avgiftsforpliktelse (Fortollet lager)", f"{tot_avgift:,.2f} NOK")
    else:
        st.warning("Finner ikke lagerdata.")

with tab3:
    st.subheader("Lovpålagt 100% Skattetrekkskontroll (Konto 1925)")
    st.caption("Iht. skattebetalingsloven § 5-12 skal skattetrekk til enhver tid være 100% sikret på sperret skattetrekkskonto.")
    
    saldo_in = st.number_input("Faktisk saldo på Konto 1925 (NOK):", value=125000.0, step=1000.0)
    sjekk = engine.skattetrekk_verifier(bank_1925_balance=saldo_in)
    
    if sjekk.get("godkjent_100_prosent"):
        st.success(sjekk.get("status_melding"))
    else:
        st.error(sjekk.get("status_melding"))

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Bankkonto 1925 Saldo", f"{sjekk['bank_konto_1925_saldo']:,.2f} NOK")
    k2.metric("Skyldig Skattetrekk", f"{sjekk['total_skattetrekk_skyldig']:,.2f} NOK")
    k3.metric("Dekningsgrad", f"{sjekk['dekning_prosent']}%")
    k4.metric("Differanse", f"{sjekk['differanse']:,.2f} NOK", delta_color="normal" if sjekk['differanse'] >= 0 else "inverse")

    st.markdown("#### Lønns- og AGA-underlag")
    st.dataframe(sjekk["detaljert_tabell"], use_container_width=True)

with tab4:
    st.subheader("MVA-oppgave Termin 1 (Januar - Februar 2026)")
    df_mva = engine.mva_oppgave_sammendrag()
    st.dataframe(df_mva, use_container_width=True)

    netto_mva = engine.beregn_netto_mva()
    m1, m2, m3 = st.columns(3)
    m1.metric("Utgående MVA (salg)", f"{netto_mva['utgaaende_mva']:,.2f} NOK")
    m2.metric("Inngående MVA (kjøp/drift)", f"{netto_mva['inngaaende_mva']:,.2f} NOK")
    m3.metric("Netto MVA til Skatteetaten", f"{netto_mva['netto_mva_til_betaling']:,.2f} NOK")

    st.markdown("---")
    st.subheader("Altinn XML Eksport")
    from src.core.agent_engine import TaxExciseAgent
    from src.core.llm_router import LLMRouter
    tax_agent = TaxExciseAgent(LLMRouter(), engine)
    xml_output = tax_agent.generate_altinn_xml_draft()
    st.code(xml_output, language="xml")
    st.download_button(
        label="Last ned Altinn MVA-melding (XML)",
        data=xml_output,
        file_name="mva_melding_termin1_2026.xml",
        mime="application/xml"
    )

