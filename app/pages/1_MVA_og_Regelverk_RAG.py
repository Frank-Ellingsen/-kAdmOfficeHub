import sys
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.rag.retriever import query_rag
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="MVA & Regelverk RAG", page_icon="⚖️", layout="wide")
render_sidebar()

st.title("⚖️ MVA, Skatt & Bokføring – Lovverksassistent (RAG)")
st.markdown("Juridisk forankret søk i Lovdata for Det Norske Brenneri AS. Besvarer spørsmål med direkte paragrafhenvisninger.")

provider = st.session_state.get("llm_provider", "gemini")
st.caption(f"Aktiv modell: **{'Google Gemini 3.8 Flash' if provider == 'gemini' else 'Ollama Llama 3.1'}**  |  Kildedokumenter: **23 Lovdata PDF-er**")

# Hurtigspørsmål tilpasset brenneridrift
st.markdown("##### 💡 Hurtigvalg for vanlige brennerispørsmål:")
hq1, hq2, hq3, hq4 = st.columns(4)
chosen_q = None
if hq1.button("🍽️ Representasjon & MVA (§ 8-3)"):
    chosen_q = "Hva er reglene og vilkårene for MVA-fradrag ved representasjon og kundemiddager under Merverdiavgiftsloven § 8-3?"
if hq2.button("📦 Samlede innkjøp (§ 8-10-6)"):
    chosen_q = "Hvilke krav stiller Bokføringsforskriften § 8-10-6 til dokumentasjon ved samlede innkjøp?"
if hq3.button("🥃 Vareprøver & Reklameforbud"):
    chosen_q = "Hva sier alkoholloven om utlevering av vareprøver og smaking til Horeca og reklameforbudet?"
if hq4.button("🏦 Skattetrekk § 5-12"):
    chosen_q = "Hvilke lovkrav stiller skattebetalingsloven § 5-12 til oppbevaring av skattetrekk på sperret bankkonto?"

sporsmal = st.text_input(
    "Still spørsmål til lovverket:",
    value=chosen_q or "",
    placeholder="F.eks: 'Hva er vilkårene for MVA-fradrag ved representasjon under Merverdiavgiftsloven § 8-3?'"
)

col_k, col_btn = st.columns([1, 4])
with col_k:
    k_val = st.slider("Antall kildeutdrag (k)", min_value=2, max_value=8, value=4)

if st.button("Søk i Lovverket", type="primary"):
    if sporsmal:
        with st.spinner(f"Søker i ChromaDB og analyserer lovparagrafer med {provider.upper()}..."):
            import io
            import contextlib
            
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                query_rag(sporsmal, k=k_val, provider=provider)
            output = buf.getvalue()
            st.markdown(output)
    else:
        st.warning("Vennligst oppgi et spørsmål.")

st.markdown("---")
st.subheader("📚 Tilgjengelige Kildedokumenter i Vektordatabasen")
col_d1, col_d2 = st.columns(2)
with col_d1:
    st.markdown("""
    - **Merverdiavgiftsloven** – Fradragsrett, representasjon (§ 8-3), satser og fritak.
    - **Bokføringsloven & Bokføringsforskriften** – Krav til bilag, oppbevaring, § 8-10-6.
    - **Regnskapsloven** – Årsregnskap, vurderingsregler for anleggsmidler og varelager.
    - **Alkoholloven & Forskrift om alkoholavgift** – Salgsbevillinger, lagring og engros.
    """)
with col_d2:
    st.markdown("""
    - **Skattebetalingsloven** – Skattetrekk konto 1925, terminfrister og ansvar.
    - **Arbeidsmiljøloven & Ferieloven** – Lønn, feriepenger og arbeidstid.
    - **Kjøpsloven & Avtaleloven** – Standard leveransevilkår B2B.
    - **Lov om offentlige anskaffelser** – Anbudsregelverk.
    """)
