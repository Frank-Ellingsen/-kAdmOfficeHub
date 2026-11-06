import sys
from pathlib import Path
from datetime import datetime, date
import streamlit as st
import pandas as pd

# Legg til prosjektets rot i sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.analytics.duckdb_engine import DuckDBEngine
from src.core.agent_engine import SupervisorAgent
from src.tools.brreg_client import BrregClient
from app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="ØkAdmOfficeHub – Det Norske Brenneri AS",
    page_icon="🥃",
    layout="wide"
)

render_sidebar()
engine = DuckDBEngine()
provider = st.session_state.get("llm_provider", "gemini")

# --- TOPPBANNER ---
st.title("🥃 ØkAdmOfficeHub – AI Cockpit & Finansiell Drift")
st.markdown(
    "**Virksomhet:** Det Norske Brenneri AS (Org.nr 996 928 977)  |  "
    "**Destilleri:** Industriveien 6, Grimstad  |  "
    "**Hovedkontor:** Bogstadveien 27B, Oslo  \n"
    "**Orkestrering:** Antigravity 7-Agent Hierarkisk DAG (Supervisor + 6 Domene-spesialister)"
)

st.markdown("---")

# --- 1. OPERATIV FRIST- OG SKATTEKALENDER ---
st.subheader("⏱️ Operativ Frist- og Oppgaveradar (Skatteetaten & Vinmonopolet)")
st.caption("Lovpålagte tidsfrister for brenneriet med automatisk dagsnedtelling.")

today = date.today()

# Beregn neste frister dynamisk
def get_next_deadline(target_day: int, months: list = None) -> date:
    y = today.year
    m = today.month
    if months:
        valid_months = [mo for mo in months if (mo > m) or (mo == m and target_day >= today.day)]
        if not valid_months:
            m = months[0]
            y += 1
        else:
            m = valid_months[0]
    else:
        if today.day > target_day:
            if m == 12:
                m = 1
                y += 1
            else:
                m += 1
    return date(y, m, target_day)

d_amelding = get_next_deadline(5)                             # 5. hver mnd
d_saravgift = get_next_deadline(18)                           # 18. hver mnd (alkohol/emballasje)
d_mva = get_next_deadline(10, [2, 4, 6, 8, 10, 12])           # 10. annenhver mnd (Termin 1-6)
d_skattetrekk = get_next_deadline(15, [1, 3, 5, 7, 9, 11])   # 15. annenhver mnd (Konto 1925 / AGA)
d_vinmonopolet = get_next_deadline(1, [1, 5, 9])             # Vinmonopolet prisjusteringsvindu

def format_deadline_card(title: str, d_date: date, desc: str, icon: str):
    days = (d_date - today).days
    color = "normal" if days > 7 else "inverse"
    status_text = f"Om {days} dager ({d_date.strftime('%d.%m.%Y')})"
    return title, status_text, desc, days

f1, f2, f3, f4, f5 = st.columns(5)

with f1:
    days = (d_saravgift - today).days
    farge = "#dc3545" if days <= 5 else "#fd7e14" if days <= 12 else "#0d6efd"
    st.markdown(f"**🥃 Særavgift Alkohol & Miljø**")
    st.caption(f"Frist: **{d_saravgift.strftime('%d.%m.%Y')}**")
    st.markdown(f"<span style='color:{farge}; font-size:1.1rem; font-weight:700;'>⏳ {days} dager igjen</span>", unsafe_allow_html=True)
    st.caption("kr 942.50/L ren alkohol + emballasje")

with f2:
    days = (d_amelding - today).days
    farge = "#dc3545" if days <= 3 else "#fd7e14" if days <= 7 else "#0d6efd"
    st.markdown(f"**📑 A-melding & Lønn**")
    st.caption(f"Frist: **{d_amelding.strftime('%d.%m.%Y')}**")
    st.markdown(f"<span style='color:{farge}; font-size:1.1rem; font-weight:700;'>⏳ {days} dager igjen</span>", unsafe_allow_html=True)
    st.caption("Forskuddstrekk & AGA 14,1%")

with f3:
    days = (d_skattetrekk - today).days
    st.markdown(f"**🏦 Oppgjør Skattetrekk**")
    st.caption(f"Frist: **{d_skattetrekk.strftime('%d.%m.%Y')}**")
    st.markdown(f"<span style='font-size:1.1rem; font-weight:700;'>⏳ {days} dager igjen</span>", unsafe_allow_html=True)
    st.caption("Overfør fra sperret konto 1925")

with f4:
    days = (d_mva - today).days
    st.markdown(f"**⚖️ MVA Termin-oppgave**")
    st.caption(f"Frist: **{d_mva.strftime('%d.%m.%Y')}**")
    st.markdown(f"<span style='font-size:1.1rem; font-weight:700;'>⏳ {days} dager igjen</span>", unsafe_allow_html=True)
    st.caption("Termininnlevering via Altinn")

with f5:
    days = (d_vinmonopolet - today).days
    st.markdown(f"**🍷 Vinmonopolet Prisfrist**")
    st.caption(f"Frist: **{d_vinmonopolet.strftime('%d.%m.%Y')}**")
    st.markdown(f"<span style='font-size:1.1rem; font-weight:700;'>⏳ {days} dager igjen</span>", unsafe_allow_html=True)
    st.caption("Sperrefrist for prisfilendring")

st.markdown("---")

# --- 2. EXECUTIVE NØKKELTALL (TUFTE DATA-INK RATIO) ---
reskontro_df = engine.reskontro_aldersfordeling()
tot_utestaaende = reskontro_df["Totalt_Utestaaende"].sum() if not reskontro_df.empty else 0.0
over_60d = reskontro_df["Forfalt_over_60d"].sum() if not reskontro_df.empty else 0.0

ap_df = engine.leverandorreskontro_ap()
tot_ap = ap_df["Beløp Inkl MVA (NOK)"].sum() if not ap_df.empty else 0.0

skattetrekk = engine.skattetrekk_verifier()
mva = engine.beregn_netto_mva()
lager_df = engine.avstem_lager_og_avgifter()
tot_saravgift_lager = lager_df["Total_Avgiftsforpliktelse_NOK"].sum() if not lager_df.empty else 0.0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Kundefordringer (AR)", f"{tot_utestaaende:,.0f} NOK")
col2.metric("Forfalt >60 dager", f"{over_60d:,.0f} NOK", delta="-8 500 NOK risiko", delta_color="inverse")
col3.metric("Leverandørgjeld (AP)", f"{tot_ap:,.0f} NOK", delta="6 åpne fakturaer")
col4.metric(
    "Skattetrekk (Konto 1925)", 
    f"{skattetrekk['dekning_prosent']}%", 
    delta=f"{skattetrekk['differanse']:,.0f} NOK mangel" if not skattetrekk["godkjent_100_prosent"] else "Full dekning", 
    delta_color="normal" if skattetrekk["godkjent_100_prosent"] else "inverse"
)
col5.metric("Påløpt Alkoholavgift", f"{tot_saravgift_lager:,.0f} NOK", delta="Fortollet lager")

# Tydelig handlingsvarsel dersom det er dekningsmangel på skattetrekk
if not skattetrekk["godkjent_100_prosent"]:
    st.error(
        f"🚨 **PÅKREVD HANDLING FOR ØK/ADM:** {skattetrekk['status_melding']}! "
        f"Overfør {abs(skattetrekk['differanse']):,.2f} NOK fra driftskonto til sperret skattetrekkskonto 1925 før terminoppgjør."
    )

st.markdown("---")

# --- 3. INTEGRERT SANNTIDS BRØNNØYSUND KREDITTSJEKK ---
st.subheader("🔍 Integrert Kredittsjekk & Brønnøysund-oppslag")
st.caption("Gjør direkte sanntidsoppslag mot Enhetsregisteret (data.brreg.no) for kunder, leverandører og anbudspartnere.")

k1, k2, k3, k4, k5 = st.columns(5)
quick_org = None
if k1.button("🍷 Vinmonopolet"):
    quick_org = "980486190"
if k2.button("🚚 Asko Servering"):
    quick_org = "934567890"
if k3.button("🏨 Grand Hotel Grimstad"):
    quick_org = "912345678"
if k4.button("🍸 Bar & Bistro Oslo"):
    quick_org = "987654321"
if k5.button("🏢 Det Norske Brenneri"):
    quick_org = "996928977"

col_search1, col_search2 = st.columns([3, 1])
with col_search1:
    search_input = st.text_input(
        "Søk på 9-sifret organisasjonsnummer eller firmanavn:",
        value=quick_org or "",
        placeholder="F.eks. 987654321 eller Bar & Bistro Oslo AS"
    )
with col_search2:
    st.write("")
    st.write("")
    btn_search = st.button("Søk i Brønnøysund", type="primary", use_container_width=True)

if search_input and (btn_search or quick_org):
    with st.spinner("Slår opp i Brønnøysundregistrene..."):
        clean_nr = "".join(filter(str.isdigit, search_input))
        enhet = None
        if len(clean_nr) == 9:
            enhet = BrregClient.lookup_orgnr(clean_nr)
        else:
            treff = BrregClient.search_by_name(search_input, size=1)
            if treff:
                enhet = treff[0]

        if enhet:
            risk = BrregClient.evaluate_credit_risk(enhet)
            
            box_color = "#d1e7dd" if risk["farge"] == "success" else "#fff3cd" if risk["farge"] == "warning" else "#f8d7da"
            text_color = "#0f5132" if risk["farge"] == "success" else "#664d03" if risk["farge"] == "warning" else "#842029"

            st.markdown(
                f"""
                <div style='background-color:{box_color}; padding:14px; border-radius:8px; border:1px solid rgba(0,0,0,0.1); margin-bottom:15px;'>
                    <h4 style='color:{text_color}; margin:0;'>{enhet.get('navn')} (Org.nr: {enhet.get('organisasjonsnummer')})</h4>
                    <p style='color:{text_color}; margin:4px 0 0 0;'><strong>Kredittvurdering:</strong> {risk['status']} — {risk['begrunnelse']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            r1, r2, r3, r4 = st.columns(4)
            r1.write(f"**Selskapsform:** {enhet.get('organisasjonsform', {}).get('beskrivelse', 'AS')}")
            r2.write(f"**MVA-registrert:** {'✅ Ja' if enhet.get('registrertIMvaregisteret') else '❌ Nei'}")
            r3.write(f"**Antall ansatte:** {enhet.get('antallAnsatte', 0)}")
            r4.write(f"**Konkurs:** {'🔴 JA (KONKURS)' if enhet.get('konkurs') else '🟢 Ingen konkurs'}")

            adr = enhet.get('forretningsadresse', {})
            post_str = f"{', '.join(adr.get('adresse', []))}, {adr.get('postnummer', '')} {adr.get('poststed', '')}"
            st.caption(f"📍 Forretningsadresse: {post_str}  |  Næringskode: {enhet.get('naeringskode1', {}).get('kode')} - {enhet.get('naeringskode1', {}).get('beskrivelse')}")
        else:
            st.warning(f"Ingen treff i Enhetsregisteret for '{search_input}'.")

st.markdown("---")

# --- 4. SUPERVISOR AGENT CHAT / KOMMANDOSENTER ---
st.subheader("🤖 Supervisor Agent – Autonom Oppgaveløser")
st.caption("Still et spørsmål om MVA, reskontro, særavgifter, kalkyler eller revisjon:")

# Hurtigknapper for vanlige oppgaver
qc1, qc2, qc3, qc4 = st.columns(4)
prompt_chosen = None
if qc1.button("🏦 Sjekk skattetrekk 1925"):
    prompt_chosen = "Kontroller skattetrekksdekning på konto 1925 og gi anbefaling."
if qc2.button("🏷️ Anbudskalkyle Vinmonopolet"):
    prompt_chosen = "Beregn dekningsbidrag og avgift for Harahorn Gin til Vinmonopolet med utsalgspris 420 kr."
if qc3.button("📋 Årsavslutningssjekkliste"):
    prompt_chosen = "Vis fullstendig revisjons- og avstemmingssjekkliste for brenneriet."
if qc4.button("⚖️ MVA på representasjon"):
    prompt_chosen = "Hva er reglene for MVA-fradrag ved representasjon og kundemiddager under Merverdiavgiftsloven § 8-3?"

user_input = st.text_input("Hva ønsker du utført i dag?", value=prompt_chosen or "", placeholder="F.eks: 'Hvor mye skylder vi i skattetrekk?' eller 'Beregn anbudsmargin for Vinmonopolet'")

if st.button("Kjør oppgave", type="primary"):
    if user_input:
        with st.spinner("Supervisor analyserer og dirigerer i 7-Agent DAG..."):
            supervisor = SupervisorAgent(provider=provider)
            response = supervisor.route_and_execute(user_input, provider=provider)
            st.markdown(response)
    else:
        st.warning("Vennligst skriv inn en oppgave eller velg en hurtigknapp.")

st.markdown("---")

# --- 5. OPERATIVE MODULER ---
st.subheader("📚 Operative Moduler i ØkAdmOfficeHub")
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("#### 1️⃣ MVA & Lovverk RAG")
    st.write("Semantisk søk i Lovdata (Merverdiavgiftsloven, Bokføringsforskriften § 8-10-6, Alkoholloven).")
    st.info("Bruk menyen til venstre for å åpne modulen.")

with m2:
    st.markdown("#### 2️⃣ Reskontro, Lager & Betaling")
    st.write("Kundereskontro med 1-klikks purring, leverandørreskontro (AP), særavgifter og fatavdamping (Angels' share).")
    st.info("Bruk menyen til venstre for å åpne modulen.")

with m3:
    st.markdown("#### 3️⃣ Anbud, FP&A & Årsavslutning")
    st.write("Vinmonopolet-kalkyler, 12-måneders S-kurve, 3-Statement prognoser og revisjonsmappe for Cedra.")
    st.info("Bruk menyen til venstre for å åpne modulen.")
