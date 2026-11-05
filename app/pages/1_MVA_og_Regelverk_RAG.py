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

sporsmal = st.text_input(
    "Still spørsmål til lovverket:",
    placeholder="F.eks: 'Hva er vilkårene for MVA-fradrag ved representasjon under Merverdiavgiftsloven § 8-3?'"
)

col_k, col_btn = st.columns([1, 4])
with col_k:
    k_val = st.slider("Antall kildeutdrag (k)", min_value=2, max_value=8, value=4)

if st.button("Søk i Lovverket", type="primary"):
    if sporsmal:
        with st.spinner(f"Søker i ChromaDB og formulerer svar med {provider.upper()}..."):
            # Redirect stdout eller fang resultater
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
st.markdown("""
- **Merverdiavgiftsloven (Lov om merverdiavgift)** – Fradragsrett, representasjon (§ 8-3), satser.
- **Bokføringsloven & Forskrift om bokføring** – Krav til bilag, oppbevaring, dokumentasjon.
- **Regnskapsloven** – Årsregnskap, vurderingsregler for varelager.
- **Alkoholloven & Forskrift om alkoholavgift** – Salgsbevillinger, lagring, engros.
- **Skatteloven & Skattebetalingsloven** – Skattetrekk konto 1925, arbeidsgiveravgift.
""")

