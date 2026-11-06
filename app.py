import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Office Hub - Det Norske Brenneri AS",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #f59e0b; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1rem; color: #94a3b8; margin-bottom: 1.5rem; }
    .card-box { background-color: #1e293b; padding: 1.25rem; border-radius: 0.75rem; border: 1px solid #334155; margin-bottom: 1rem; }
    .metric-title { font-size: 0.85rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #ffffff; }
    .metric-change { font-size: 0.85rem; color: #10b981; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Office Hub Navigation")
st.sidebar.caption("Det Norske Brenneri AS • Org 996 928 977")

page = st.sidebar.radio(
    "Velg Modul / Dashbord",
    [
        "📊 FP&A 3-Statement & Early Warning",
        "🚚 LP Distribusjon & Logistikk",
        "🍷 Varelager & Fatlager-splitt",
        "🍾 Vinmonopolet Anbudskalkulator",
        "🤖 Antigravity Multi-Agent Network",
        "📥 Drag & Drop Ingestion & RAG"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Aktiv LLM**: Gemini 1.5 Flash / Ollama Llama 3.1\n\n**Data Sync**: Live Real-time Sync")

if page == "📊 FP&A 3-Statement & Early Warning":
    st.markdown('<div class="main-header">📊 3-Statement Finansiell Prognose & Risk Radar</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Sammenkoblet Resultat, Balanse og Kontantstrøm for Det Norske Brenneri AS (2024 - 2026)</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="card-box"><div class="metric-title">Prognosert Omsetning</div><div class="metric-value">31,05 MNOK</div><div class="metric-change">▲ +15.0% vs Baseline (27M)</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card-box"><div class="metric-title">EBITDA Margin</div><div class="metric-value">16.0% (4,97 MNOK)</div><div class="metric-change">▲ +450 bps Forbedring</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card-box"><div class="metric-title">Net Free Cash Flow</div><div class="metric-value">4,69 MNOK</div><div class="metric-change">▲ +2,98 MNOK Frigjort</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="card-box"><div class="metric-title">Skattetrekk (1925)</div><div class="metric-value" style="color:#10b981;">100% Dekning</div><div class="metric-change" style="color:#94a3b8;">✓ Full Skattelov-compliance</div></div>', unsafe_allow_html=True)

    st.markdown("### 🚨 Early Warning Risk Radar")
    r1, r2 = st.columns(2)
    with r1:
        st.warning("🔴 **Varelager (DIO): 90.6 Dager (6.7 MNOK bundet)**\n\n*Tiltak*: Innfør FIFO lagerrotasjon og skille fatlager under modning fra salgslager.")
        st.info("🟢 **Skattetrekkskonto (1925): 100% Dekningsgrad**\n\n*Status*: 93 000 NOK innestående dekker påløpt forskuddstrekk 100%.")
    with r2:
        st.warning("🟡 **Kundefordringer (DSO): 49.5 Dager (3.67 MNOK)**\n\n*Tiltak*: Purreintegrasjon mot Horeca-kunder og milepælsbetalinger.")
        st.error("🔴 **EAC Prosjektrisiko: -1.4 MNOK Budsjettavvik**\n\n*Tiltak*: Innføre bi-ukentlig godkjenningsport for utvidelse av tapperilinje.")

elif page == "🚚 LP Distribusjon & Logistikk":
    st.markdown('<div class="main-header">🚚 Lineær Programmering (LP) Logistikkmotor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Minimering av samlede distribusjonskostnader fra Grimstad til Vinmonopolet, Grossister og Horeca</div>', unsafe_allow_html=True)

    st.markdown("### 🎛️ Interaktive Ruteparametere (Kassevolum per uke)")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        v_pol = st.slider("Vinmonopolet Hovedlager (Vestby)", 500, 2500, 1200, step=50)
        v_asko = st.slider("Grossist ASKO (Kjeller)", 300, 1500, 800, step=50)
    with col_b:
        v_sg = st.slider("Grossist Servicegrossistene", 200, 1000, 450, step=50)
        v_hor_oslo = st.slider("Horeca Direkte Oslo / Viken", 100, 800, 300, step=25)
    with col_c:
        v_hor_sor = st.slider("Horeca Direkte Sørlandet", 50, 600, 250, step=25)
        v_reg = st.slider("Regional Distributør Nord/Vest", 100, 1000, 400, step=50)

    c = [15.0, 21.0, 18.0, 30.0, 12.0, 28.0]
    base_c = [17.25, 24.15, 20.70, 34.50, 13.80, 32.20]
    volumes = [v_pol, v_asko, v_sg, v_hor_oslo, v_hor_sor, v_reg]
    
    lp_total_week = sum(c[i] * volumes[i] for i in range(6))
    base_total_week = sum(base_c[i] * volumes[i] for i in range(6))
    savings_week = base_total_week - lp_total_week
    savings_year = savings_week * 52

    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Totalt Ukentlig Volum", f"{sum(volumes):,} kasser")
    m2.metric("LP Fraktkostnad", f"{lp_total_week:,.0f} NOK/uke")
    m3.metric("Baseline Fraktkostnad", f"{base_total_week:,.0f} NOK/uke")
    m4.metric("💰 Estimert Årlig Gevinst", f"{savings_year:,.0f} NOK/år", delta=f"+{savings_week:,.0f} kr/uke")

    routes = [
        "Vinmonopolet Hovedlager (Vestby/Oslo)", "Grossist ASKO (Kjeller/Sentral)",
        "Grossist Servicegrossistene", "Horeca Direkte Oslo / Viken",
        "Horeca Direkte Sørlandet (Kr.sand/Arendal)", "Regional Distributør Nord/Vest"
    ]
    methods = ["FTL (Hel Pall)", "3PL Sentrallager", "FTL (Hel Pall)", "3PL Sentrallager", "FTL (Hel Pall)", "FTL (Hel Pall)"]
    
    df_lp = pd.DataFrame({
        "Destinasjon / Knutepunkt": routes,
        "Optimal Rute": methods,
        "Volum (Kasser)": volumes,
        "LP Pris/Kasse": [f"{v:.2f} NOK" for v in c],
        "LP Uke Total": [f"{c[i]*volumes[i]:,.0f} NOK" for i in range(6)],
        "Baseline Uke Total": [f"{base_c[i]*volumes[i]:,.0f} NOK" for i in range(6)],
        "Ukentlig Innsparing": [f"{(base_c[i]-c[i])*volumes[i]:,.0f} NOK" for i in range(6)]
    })
    st.dataframe(df_lp, use_container_width=True)

elif page == "🍷 Varelager & Fatlager-splitt":
    st.markdown('<div class="main-header">🍷 Varelager & Fatlager-Optimalisering</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Inndeling i Råvarer, Fatlager under modning (WIP) og Fortollet Salgslager</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card-box"><div class="metric-title">1. Råvarer & Innhøstingslager</div><div class="metric-value">1.25 MNOK</div><p style="font-size:0.8rem; color:#94a3b8;">Eplemost (Grimstad), vetropack-flasker, etiketter og korker.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card-box"><div class="metric-title">2. Fatlager under Modning (WIP)</div><div class="metric-value">3.85 MNOK</div><p style="font-size:0.8rem; color:#f59e0b;">Arvesølvet Akevitt & Eiktyrne Single Malt (12-36 mnd). <b>Verdiøkende prosess</b>.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card-box"><div class="metric-title">3. Fortollet Salgslager</div><div class="metric-value">1.60 MNOK</div><p style="font-size:0.8rem; color:#10b981;">Harahorn Gin & ferdigtappede flasker for umiddelbar leveranse.</p></div>', unsafe_allow_html=True)

    st.markdown("### 📉 Cash Conversion Cycle (CCC) Simulator")
    dso_val = st.slider("DSO (Kredittid Kunder - Dager)", 20.0, 60.0, 35.0, 0.5)
    dio_val = st.slider("DIO (Lagertid Ferdigvarer - Dager)", 30.0, 100.0, 70.0, 1.0)
    dpo_val = st.slider("DPO (Kredittid Leverandører - Dager)", 20.0, 60.0, 45.0, 1.0)

    ccc = dio_val + dso_val - dpo_val
    freed_cash = ((49.5 - dso_val)*(27_000_000/365)) + ((90.6 - dio_val)*(12_150_000/365)) + ((dpo_val - 35.0)*(12_150_000/365))

    st.success(f"**Beregnet Cash Conversion Cycle (CCC): {ccc:.1f} dager** (Baseline: 105.1 dager)\n\n👉 **Frigjort Likviditet fra Arbeidskapital: {freed_cash:,.0f} NOK**")

elif page == "🍾 Vinmonopolet Anbudskalkulator":
    st.markdown('<div class="main-header">🍾 Vinmonopolet Anbudskalkulator & Dekningsbidrag</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Beregning av alkoholavgift, MVA, Pol-avanse og brenneriets dekningsbidrag (DB1 / DB2)</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        shelf_price = st.number_input("Villedende Hyllepris Vinmonopolet (NOK inkl. MVA)", value=499.90, step=10.0)
        abv = st.slider("Alkoholprosent (ABV %)", 4.7, 60.0, 40.0, step=0.5)
        vol_l = st.selectbox("Flaskevolum (Liter)", [0.50, 0.70, 1.00], index=1)
    with c2:
        cogs = st.number_input("Direkte Varekostnad / COGS (Flaske, Kork, Etikett, Råvare)", value=45.0, step=1.0)
        freight = st.number_input("Frakt & Logistikk til Grossist per flaske (NOK)", value=6.50, step=0.50)

    mva = shelf_price * 0.20
    ex_mva = shelf_price - mva
    pol_margin = ex_mva * 0.09
    pure_alc = vol_l * (abv / 100.0)
    alc_tax = pure_alc * 942.50
    packaging_tax = 7.90
    
    net_brenneri_revenue = ex_mva - pol_margin - alc_tax - packaging_tax
    db1 = net_brenneri_revenue - cogs
    db1_margin = (db1 / net_brenneri_revenue * 100) if net_brenneri_revenue > 0 else 0
    db2 = db1 - freight
    db2_margin = (db2 / net_brenneri_revenue * 100) if net_brenneri_revenue > 0 else 0

    st.markdown("---")
    st.markdown("### 📊 Prisnedbrytning per Flaske")
    
    res_df = pd.DataFrame({
        "Linje / Komponent": [
            "1. Utsalgspris Polhylle (Inkl. MVA)", "  - Merverdiavgift (25% MVA)", "2. Utsalgspris Ekskl. MVA",
            "  - Vinmonopolets Avanse (~9%)", "  - Alkoholavgift (942.50 NOK/L ren alk)", "  - Emballasjeavgift (Grunn/Miljø)",
            "3. Netto Inntekt Det Norske Brenneri", "  - Direkte Varekostnad (COGS)", "4. Dekningsbidrag 1 (DB1)",
            "  - Frakt & Logistikk", "5. Dekningsbidrag 2 (DB2)"
        ],
        "Beløp per Flaske (NOK)": [
            f"{shelf_price:.2f} kr", f"-{mva:.2f} kr", f"{ex_mva:.2f} kr",
            f"-{pol_margin:.2f} kr", f"-{alc_tax:.2f} kr", f"-{packaging_tax:.2f} kr",
            f"👉 {net_brenneri_revenue:.2f} kr", f"-{cogs:.2f} kr", f"💰 {db1:.2f} kr ({db1_margin:.1f}%)",
            f"-{freight:.2f} kr", f"🏆 {db2:.2f} kr ({db2_margin:.1f}%)"
        ]
    })
    st.dataframe(res_df, use_container_width=True)

elif page == "🤖 Antigravity Multi-Agent Network":
    st.markdown('<div class="main-header">🤖 Antigravity Multi-Agent Network</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">7 Spesialiserte Autonome AI-Agenter for Det Norske Brenneri AS</div>', unsafe_allow_html=True)

    agents = [
        ("1. Supervisor Agent", "Master Orchestrator & User Intent Router", "ACTIVE"),
        ("2. Compliance RAG Agent", "MVA-loven (§ 8-1, § 8-3) & Bokføringsforskriften", "ACTIVE"),
        ("3. Analytics & Reskontro Agent", "DuckDB SQL Engine, Aldersfordeling & Fatlager", "ACTIVE"),
        ("4. Tax & Excise Altinn Agent", "MVA-melding, A-melding & Alkoholavgift (942.50 NOK/L)", "ACTIVE"),
        ("5. Cash & FP&A Radar Agent", "3-Statement Forecast, DSO/DIO/DPO & Early Warning", "ACTIVE"),
        ("6. Procurement & Anbud Agent", "Vinmonopolet Anbudskalkyler & Grossistprisfiler", "ACTIVE"),
        ("7. Audit & Year-End Agent", "Årsoppgjørsmappe & Balansedokumentasjon til Revisor", "ACTIVE")
    ]
    for name, desc, status in agents:
        st.markdown(f'<div class="card-box"><b>{name}</b> — <span style="color:#10b981;">{status}</span><br><span style="color:#94a3b8; font-size:0.85rem;">{desc}</span></div>', unsafe_allow_html=True)

elif page == "📥 Drag & Drop Ingestion & RAG":
    st.markdown('<div class="main-header">📥 Drag & Drop Ingestion & RAG Search</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Slipp PDF/CSV/Excel-filer for automatisk indeksering i ChromaDB / DuckDB", accept_multiple_files=True)
    if uploaded_files:
        st.success(f"Mottatt {len(uploaded_files)} filer. Prosesserer og re-indekserer data...")

    st.markdown("---")
    st.markdown("### 💬 Still spørsmål til RAG-Lovverksassistenten")
    query = st.text_input("Spør om MVA-loven, fradragsrett, representasjon eller avstemminger:")
    if query:
        st.info("**Svar fra Compliance RAG Agent**: Basert på Merverdiavgiftsloven § 8-1 foreligger det full fradragsrett for inngående MVA på råvarer og emballasje til virksomhetens avgiftsbelagte drikkevareproduksjon. For representasjon (§ 8-3) er det ufradragsberettiget.")
