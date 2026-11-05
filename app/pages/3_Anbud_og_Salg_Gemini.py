import sys
from pathlib import Path
import streamlit as st
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.analytics.duckdb_engine import DuckDBEngine
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="FP&A, Likviditet & Risk Radar", page_icon="📈", layout="wide")
render_sidebar()

st.title("📈 FP&A, Likviditetsstyring & Early Warning Radar")
st.markdown("3-Statement prognoser, 12-måneders S-kurve for kontantstrøm og risikostyring for Det Norske Brenneri AS.")

engine = DuckDBEngine()

tab1, tab2, tab3 = st.tabs([
    "🎯 Early Warning Radar",
    "🌊 12-Måneders S-Kurve Kontantstrøm",
    "💼 3-Statement & Arbeidskapital"
])

with tab1:
    st.subheader("Finansiell Prognose & Avviksanalyse (Varians)")
    df_radar = engine.early_warning_radar()
    if not df_radar.empty:
        st.dataframe(df_radar, use_container_width=True)
    else:
        st.warning("Finner ikke financial_prognosis.csv.")

    st.markdown("---")
    st.markdown("### ⚠️ Kritiske Risikopunkter (EAC & Arbeidskapital)")
    st.markdown("""
    - **Project EAC Variance Risk:** Redusert fra 1.4 MNOK til 0.28 MNOK med AI-assistert ressursstyring (+1.12 MNOK gevinst).
    - **Cash Conversion Cycle (CCC):** Optimalisering av lagerdager (DIO) og kredittid (DSO) frigjør opptil 2.98 MNOK i fri kontantstrøm.
    """)

with tab2:
    st.subheader("12-Måneders S-Kurve: Akkumulert Kontantstrøm (MNOK)")
    df_scurve = engine.cashflow_scurve_analyse()
    if not df_scurve.empty:
        # Plot S-kurve
        chart_data = df_scurve.set_index("Maaned")[["Baseline_Akkumulert_CF_MNOK", "AI_Prognose_Akkumulert_CF_MNOK"]]
        st.line_chart(chart_data)
        
        st.markdown("#### Månedlige akkumulerte tall (MNOK)")
        st.dataframe(df_scurve, use_container_width=True)
    else:
        st.warning("Finner ikke scurve_cashflow_12m.csv.")

with tab3:
    st.subheader("Balanse og Eiendeler Komposisjon")
    path_eiendeler = BASE_DIR / "data" / "erp_exports" / "eiendeler_komposisjon_2025.csv"
    if path_eiendeler.exists():
        df_eiendeler = pd.read_csv(path_eiendeler)
        st.dataframe(df_eiendeler, use_container_width=True)
        
        c_chart = df_eiendeler.set_index("Underkategori")["Verdi_NOK_M"]
        st.bar_chart(c_chart)
    else:
        st.info("Finner ikke eiendeler_komposisjon_2025.csv.")

    st.markdown("---")
    st.subheader("3-Statement Prognose 2026")
    path_3stmt = BASE_DIR / "data" / "erp_exports" / "tre_statement_prognose_2026.csv"
    if path_3stmt.exists():
        df_3s = pd.read_csv(path_3stmt)
        st.dataframe(df_3s, use_container_width=True)
    else:
        st.info("Finner ikke tre_statement_prognose_2026.csv.")

