import streamlit as st

def render_sidebar():
    """Rendrer en standardisert, ryddig sidebar for Det Norske Brenneri AS."""
    with st.sidebar:
        st.markdown("### 🏢 Det Norske Brenneri AS")
        st.caption("Org.nr: **996 928 977**  \nBransje: **46.340 Engroshandel med drikkevarer**")
        st.markdown("---")

        st.subheader("⚙️ Agent & LLM-innstillinger")
        provider = st.selectbox(
            "Velg LLM-leverandør",
            options=["gemini", "ollama"],
            format_func=lambda x: "Google Gemini 3.8 Flash (Cloud)" if x == "gemini" else "Ollama Llama 3.1 (Lokal)",
            index=0
        )
        st.session_state["llm_provider"] = provider

        st.markdown("---")
        st.subheader("📁 Hurtiglenker")
        st.markdown("- [🌐 Brønnøysund AI Lookup & Financial S-Curve Prognosis](https://frank-ellingsen.github.io/br-nn-ysund-oppslag/)")
        st.markdown("- [📊 Cash Flow Dashboard (HTML)](file:///G:/My%20Drive/ØkAdmOfficeHub/dashboards/cash_flow_management_dashboard.html)")
        st.markdown("- [🏛️ Executive AI Cockpit (HTML)](file:///G:/My%20Drive/ØkAdmOfficeHub/dashboards/ai_cockpit_fiscal_ledger.html)")

        st.markdown("---")
        st.caption("ØkAdmOfficeHub v2.4  \nUtviklet for Frank Ellingsen")

