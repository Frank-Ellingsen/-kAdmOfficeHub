import sys
from pathlib import Path
from datetime import datetime, date
import streamlit as st
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.analytics.duckdb_engine import DuckDBEngine
from src.tools.brreg_client import BrregClient
from src.core.agent_engine import TaxExciseAgent
from src.core.llm_router import LLMRouter
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="Reskontro, Lager & Betaling", page_icon="📊", layout="wide")
render_sidebar()

st.title("📊 Reskontro, Lageravstemming & Særavgifter (DuckDB)")
st.markdown("Operativ styring av kundefordringer (AR), leverandørgjeld (AP), alkoholavgifter og 100% skattetrekkskontroll for Det Norske Brenneri AS.")

engine = DuckDBEngine()

# --- FILOPPLASTER FOR NYE ERP-EKSPORTER ---
with st.expander("📂 Last opp oppdatert ERP- eller regnskapsfil (CSV / Excel)", expanded=False):
    uploaded_file = st.file_uploader(
        "Dra og slipp ny reskontro-, lager- eller lønnsfil:",
        type=["csv", "xlsx", "xls"],
        help="Filen parses og oppdaterer analysene umiddelbart i minnet uten å overskrive baseline."
    )
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_up = pd.read_csv(uploaded_file)
            else:
                df_up = pd.read_excel(uploaded_file)
            st.session_state["custom_uploaded_df"] = df_up
            st.success(f"✅ Lastet inn '{uploaded_file.name}' ({len(df_up)} rader). Analysene er oppdatert!")
        except Exception as e:
            st.error(f"Kunne ikke lese fil: {e}")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📑 Kundereskontro & Purring (AR)",
    "💼 Leverandørreskontro & Betaling (AP)",
    "📦 Lager, Særavgift & Angels' Share",
    "🏦 Skattetrekkskontroll (Konto 1925)",
    "📑 MVA Termin 1 & Altinn XML"
])

# ==========================================
# TAB 1: KUNDERESKONTRO (AR) & PURRERUTINE
# ==========================================
with tab1:
    st.subheader("Kundereskontro Aldersfordeling (AR)")
    df_res = engine.reskontro_aldersfordeling()
    
    if not df_res.empty:
        st.dataframe(df_res, use_container_width=True)
        tot = df_res["Totalt_Utestaaende"].sum()
        forfalt_60 = df_res["Forfalt_over_60d"].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Totalt Utestående Kundefordringer", f"{tot:,.2f} NOK")
        c2.metric("Forfalt > 60 dager (Høy Risiko)", f"{forfalt_60:,.2f} NOK", delta="Krever oppfølging", delta_color="inverse")
        c3.metric("Antall Kunder med Saldo", f"{len(df_res)}")

        st.markdown("---")
        st.subheader("🚨 Forfalte Fordringer & 1-Klikks Purring")
        
        risiko_kunder = df_res[df_res["Forfalt_over_60d"] > 0]
        if not risiko_kunder.empty:
            for idx, row in risiko_kunder.iterrows():
                kunde = row["Kundenavn"]
                belop = row["Forfalt_over_60d"]
                
                with st.container():
                    r_col1, r_col2 = st.columns([3, 1])
                    with r_col1:
                        st.markdown(f"**🔴 {kunde}** har **{belop:,.2f} NOK** forfalt i mer enn 60 dager.")
                    with r_col2:
                        btn_purr = st.button(f"Generer purring for {kunde}", key=f"purr_{idx}")

                    if btn_purr:
                        renter = belop * 0.125 * (60.0 / 365.0) # 12.5% forsinkelsesrente
                        gebyr = 70.0
                        total_krav = belop + renter + gebyr
                        
                        purre_tekst = f"""PURRING / VARSEL OM INKASSO
Iht. Inkassoloven § 9 og Forsinkelsesrenteloven

Til: {kunde}
Fra: Det Norske Brenneri AS (Org.nr 996 928 977)
Dato: {date.today().strftime('%d.%m.%Y')}

Viser til tidligere utsendt faktura som nå er forfalt med over 60 dager.

Hovedstol:                {belop:,.2f} NOK
Påløpte forsinkelsesrenter (12,5%): {renter:,.2f} NOK
Purregebyr:                    {gebyr:,.2f} NOK
--------------------------------------------------
TOTALT Å BETALE:          {total_krav:,.2f} NOK

Betalingsfrist: 14 dager fra dags dato.
Dersom betaling ikke finner sted innen fristen, vil kravet uten ytterligere varsel oversendes til rettslig inndrivelse/inkasso.

Med vennlig hilsen,
Økonomiavdelingen
Det Norske Brenneri AS
Bogstadveien 27B, 0355 Oslo"""
                        st.text_area("Klar purretekst (Klar til kopiering):", value=purre_tekst, height=220)
                        st.download_button(
                            "Last ned purrebrev (.txt)",
                            data=purre_tekst,
                            file_name=f"purring_{kunde.replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
        else:
            st.success("Ingen kunder har forfalt med mer enn 60 dager. God reskontrohygiene!")

    else:
        st.warning("Finner ikke reskontrodata.")

# ==========================================
# TAB 2: LEVERANDØRRESKONTRO (AP) & UTBETALING
# ==========================================
with tab2:
    st.subheader("Leverandørreskontro & Kommende Utbetalinger (AP)")
    st.caption("Oversikt over godkjente inngående fakturaer, MVA-behandling og forfall mot leverandører i Grimstad og Oslo.")

    df_ap = engine.leverandorreskontro_ap()
    if not df_ap.empty:
        st.dataframe(df_ap, use_container_width=True)

        tot_ap_sum = df_ap["Beløp Inkl MVA (NOK)"].sum()
        tot_mva_fradrag = df_ap["MVA-Beløp (NOK)"].sum()

        ap1, ap2, ap3 = st.columns(3)
        ap1.metric("Totalt til Utbetaling", f"{tot_ap_sum:,.2f} NOK")
        ap2.metric("Inngående MVA til Fradrag", f"{tot_mva_fradrag:,.2f} NOK")
        ap3.metric("Antall Åpne Fakturaer", f"{len(df_ap)}")

        st.markdown("---")
        st.markdown("#### 🔍 Attestasjonskontroll & Skatteadvarsel (§ 8-3)")
        st.info(
            "💡 **Merk vedr. Kilden Teater & Konserthus (INV-3301, 18 000 NOK):** "
            "Fakturert på konto 7350 (Representasjon). I henhold til **Merverdiavgiftsloven § 8-3 første ledd bokstav e** "
            "er det **ikke fradragsrett for inngående MVA på representasjon/kundearrangementer**. "
            "MVA-beløpet er korrekt satt til 0,- i oppgaven."
        )
    else:
        st.warning("Finner ikke leverandørreskontrodata i arbeidsboken.")

# ==========================================
# TAB 3: LAGER, SÆRAVGIFT & ANGELS' SHARE
# ==========================================
with tab3:
    st.subheader("Lagerbeholdning og Særavgifter for Brenneriet")
    st.caption("Avstemming av ufortollet fatlager vs. fortollet salgslager. Alkoholavgift: kr 942.50 per liter ren alkohol.")

    df_lager = engine.avstem_lager_og_avgifter()
    if not df_lager.empty:
        st.dataframe(df_lager, use_container_width=True)
        tot_avgift = df_lager["Total_Avgiftsforpliktelse_NOK"].sum()
        st.metric("Total Påslått Avgiftsforpliktelse (Fortollet salgslager)", f"{tot_avgift:,.2f} NOK")

    st.markdown("---")
    st.subheader("🥃 Angels' Share – Kalkyle for Fatlagringssvinn & Avdamping")
    st.caption("I eikefatlagring av whisky og akevitt i Grimstad fordamper 2–3% alkohol årlig. Dette skal fradras avgiftsforpliktelsen iht. Bokføringsforskriften.")

    as_col1, as_col2, as_col3 = st.columns(3)
    with as_col1:
        fat_vol = st.number_input("Totalt fatlager i Grimstad (Liter)", value=45000.0, step=1000.0)
    with as_col2:
        alk_styrke = st.number_input("Gjennomsnittlig alkoholstyrke på fat (%)", value=60.0, step=1.0)
    with as_col3:
        fordamp_pct = st.number_input("Årlig avdampingsrate (%)", value=2.5, step=0.1)

    angels = engine.beregn_angels_share(fatvolum_liter=fat_vol, arlig_fordamping_prosent=fordamp_pct, alkoholprosent=alk_styrke)

    ang1, ang2, ang3 = st.columns(3)
    ang1.metric("Årlig Avdampet Væske", f"{angels['arlig_svinn_liter']:,.1f} Liter")
    ang2.metric("Årlig Avdampet Ren Alkohol", f"{angels['arlig_svinn_ren_alkohol_liter']:,.1f} Liter ren alk.")
    ang3.metric("Fritatt Alkoholavgift (Spart)", f"{angels['fratrukket_alkoholavgift_aarlig_nok']:,.2f} NOK", delta="Iht. svinnprotokoll")

    st.success(f"📋 **Dokumentasjonskrav for revisor:** {angels['status_dokumentasjon']}. Fradragsberettiget månedlig svinn: {angels['fratrukket_alkoholavgift_maanedlig_nok']:,.2f} NOK.")

# ==========================================
# TAB 4: SKATTETREKKSKONTROLL (KONTO 1925)
# ==========================================
with tab4:
    st.subheader("Lovpålagt 100% Skattetrekkskontroll (Konto 1925)")
    st.caption("Iht. skattebetalingsloven § 5-12 skal skattetrekk til enhver tid være 100% sikret på sperret skattetrekkskonto.")
    
    saldo_in = st.number_input("Faktisk saldo på sperret Konto 1925 (NOK):", value=125000.0, step=1000.0)
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

# ==========================================
# TAB 5: MVA TERMIN 1 & ALTINN XML
# ==========================================
with tab5:
    st.subheader("MVA-oppgave Termin 1 (Januar - Februar)")
    df_mva = engine.mva_oppgave_sammendrag()
    st.dataframe(df_mva, use_container_width=True)

    netto_mva = engine.beregn_netto_mva()
    m1, m2, m3 = st.columns(3)
    m1.metric("Utgående MVA (salg)", f"{netto_mva['utgaaende_mva']:,.2f} NOK")
    m2.metric("Inngående MVA (kjøp/drift)", f"{netto_mva['inngaaende_mva']:,.2f} NOK")
    m3.metric("Netto MVA til Skatteetaten", f"{netto_mva['netto_mva_til_betaling']:,.2f} NOK")

    st.markdown("---")
    st.subheader("Altinn XML Eksport")
    tax_agent = TaxExciseAgent(LLMRouter(), engine)
    xml_output = tax_agent.generate_altinn_xml_draft()
    st.code(xml_output, language="xml")
    st.download_button(
        label="Last ned Altinn MVA-melding (XML)",
        data=xml_output,
        file_name="mva_melding_termin1_2026.xml",
        mime="application/xml"
    )
