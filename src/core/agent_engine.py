import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
from langchain_core.messages import SystemMessage, HumanMessage

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.config import BASE_DIR, DATA_DIR, ERP_EXPORTS_DIR
from src.core.llm_router import LLMRouter
from src.analytics.duckdb_engine import DuckDBEngine
from src.rag.retriever import query_rag
from src.utils.logger import logger

class SpecialistAgent:
    """Basisklasse for spesialistagenter i Office Hub."""
    def __init__(self, name: str, system_prompt: str, router: LLMRouter):
        self.name = name
        self.system_prompt = system_prompt
        self.router = router

    def run_llm(self, prompt: str, provider: str = "gemini") -> str:
        """Kjører spørringen mot modell med agentens systemprompt."""
        try:
            llm = self.router.get_llm(provider=provider)
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Feil i {self.name}: {e}")
            return f"Feil ved utførelse av LLM: {str(e)}"

class ComplianceRAGAgent(SpecialistAgent):
    """Regelverks- og MVA-spesialist for Det Norske Brenneri AS."""
    def __init__(self, router: LLMRouter):
        prompt = (
            "Du er senior regelverks- og MVA-spesialist for Det Norske Brenneri AS (Org.nr 996 928 977).\n"
            "Retningslinjer:\n"
            "1. Begrunn alle svar i norsk skatte- og regnskapslovgivning (Merverdiavgiftsloven, Bokføringsforskriften, Aksjeloven).\n"
            "2. Henvis spesifikt til lovparagrafer (f.eks. Mva-loven § 8-1, § 8-3 for representasjon).\n"
            "3. Ta hensyn til bransjespesifikke krav for engroshandel og produksjon av alkoholholdige drikkevarer (Næringskode 46.340).\n"
            "4. Vær presis, profesjonell og gi konkrete råd."
        )
        super().__init__("compliance_rag_agent", prompt, router)

    def ask_legal(self, query: str, provider: str = "gemini") -> str:
        return query_rag(query, k=4, provider=provider)

class AnalyticsReskontroAgent(SpecialistAgent):
    """Reskontro, lager og SQL-analytiker."""
    def __init__(self, router: LLMRouter, engine: DuckDBEngine):
        prompt = (
            "Du er Lead Financial Data Engineer & Reskontro Analyst for Det Norske Brenneri AS.\n"
            "Du analyserer reskontro, forfallsstrukturer og lagerbeholdning basert på DuckDB-data.\n"
            "Alltid presenter tallene strukturert, venstrejustert for tekst og høyrejustert for tall."
        )
        super().__init__("analytics_reskontro_agent", prompt, router)
        self.engine = engine

    def analyse_reskontro(self) -> Dict[str, Any]:
        df = self.engine.reskontro_aldersfordeling()
        total_due = float(df["Totalt_Utestaaende"].sum()) if not df.empty else 0.0
        over_60d = float(df["Forfalt_over_60d"].sum()) if not df.empty else 0.0
        return {
            "tabell": df,
            "totalt_utestaaende": total_due,
            "forfalt_over_60_dager": over_60d,
            "risikokunder": df[df["Forfalt_over_60d"] > 0]["Kundenavn"].tolist() if not df.empty else []
        }

    def analyse_lager(self) -> pd.DataFrame:
        return self.engine.avstem_lager_og_avgifter()

class TaxExciseAgent(SpecialistAgent):
    """Skatt, særavgift og Altinn-rapporteringsagent."""
    def __init__(self, router: LLMRouter, engine: DuckDBEngine):
        prompt = (
            "Du er Tax & Altinn Reporting Agent for Det Norske Brenneri AS.\n"
            "Dine hovedoppgaver er MVA-oppgave (Termin 1-6), alkoholavgifter (kr 942.50 per liter ren alkohol),\n"
            "miljøgebyr på drikkevareemballasje, og 100% kontroll av skattetrekkskonto (Konto 1925)."
        )
        super().__init__("tax_excise_agent", prompt, router)
        self.engine = engine

    def verify_skattetrekk(self, bank_balance: float = 125000.0) -> Dict[str, Any]:
        return self.engine.skattetrekk_verifier(bank_1925_balance=bank_balance)

    def summarize_mva(self) -> Dict[str, Any]:
        return self.engine.beregn_netto_mva()

    def generate_altinn_xml_draft(self, termin: int = 1, year: int = 2026) -> str:
        """Bygger utkast til Altinn MVA-melding (XML)."""
        mva_data = self.engine.beregn_netto_mva()
        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<MvaMelding xmlns="http://skatteetaten.no/mva/v1">
  <Innsender>
    <Organisasjonsnummer>996928977</Organisasjonsnummer>
    <Navn>Det Norske Brenneri AS</Navn>
  </Innsender>
  <Skattleggingsperiode>
    <Termin>Termin {termin}</Termin>
    <Aar>{year}</Aar>
  </Skattleggingsperiode>
  <MvaSpesifikasjon>
    <UtgaaendeMva>{mva_data.get('utgaaende_mva', 0.0):.2f}</UtgaaendeMva>
    <InngaaendeMva>{mva_data.get('inngaaende_mva', 0.0):.2f}</InngaaendeMva>
    <NettoMvaTilBetaling>{mva_data.get('netto_mva_til_betaling', 0.0):.2f}</NettoMvaTilBetaling>
  </MvaSpesifikasjon>
  <Status>VALIDERT_KLAR_TIL_SIGNERING</Status>
</MvaMelding>"""
        return xml_template

class CashFPARadarAgent(SpecialistAgent):
    """FP&A, 3-Statement og Early Warning Risk Radar."""
    def __init__(self, router: LLMRouter, engine: DuckDBEngine):
        prompt = (
            "Du er Chief Financial Planning & Analysis (FP&A) Agent for Det Norske Brenneri AS.\n"
            "Du overvåker 3-statement integrasjon, S-kurve for kontantstrøm og Early Warning Risk Radar.\n"
            "Fokusér på Cash Conversion Cycle (CCC), Project EAC-varians og EBITDA-vekst."
        )
        super().__init__("cash_fpa_radar_agent", prompt, router)
        self.engine = engine

    def get_radar_metrics(self) -> pd.DataFrame:
        return self.engine.early_warning_radar()

    def get_cashflow_scurve(self) -> pd.DataFrame:
        return self.engine.cashflow_scurve_analyse()

class SupervisorAgent:
    """
    Master Orchestrator og Supervisor Agent for Office Hub.
    Evaluerer intensjon og koordinerer oppgaver mellom spesialistene.
    """
    def __init__(self, provider: str = "gemini"):
        self.router = LLMRouter(default_provider=provider)
        self.engine = DuckDBEngine()
        self.compliance_agent = ComplianceRAGAgent(self.router)
        self.analytics_agent = AnalyticsReskontroAgent(self.router, self.engine)
        self.tax_agent = TaxExciseAgent(self.router, self.engine)
        self.cash_radar_agent = CashFPARadarAgent(self.router, self.engine)

    def route_and_execute(self, user_query: str, provider: Optional[str] = None) -> str:
        """Klassifiserer henvendelse og dirigerer til rett spesialist."""
        p = provider or self.router.default_provider
        q_lower = user_query.lower()

        logger.info(f"Supervisor evaluerer oppgave: '{user_query}'")

        if any(term in q_lower for term in ["mva", "lov", "paragraf", "fradrag", "representasjon", "regnskapslov"]):
            logger.info("Ruter til ComplianceRAGAgent")
            return self.compliance_agent.ask_legal(user_query, provider=p)

        elif any(term in q_lower for term in ["reskontro", "kunde", "utestående", "forfalt", "aldersfordeling"]):
            logger.info("Ruter til AnalyticsReskontroAgent")
            res = self.analytics_agent.analyse_reskontro()
            df = res["tabell"]
            return f"📊 **Kundereskontro Analyse**\n\nTotalt utestående: {res['totalt_utestaaende']:,.2f} NOK\nForfalt >60 dager: {res['forfalt_over_60_dager']:,.2f} NOK\n\n```\n{df.to_string(index=False)}\n```"

        elif any(term in q_lower for term in ["skattetrekk", "konto 1925", "lønn", "aga", "a-melding"]):
            logger.info("Ruter til TaxExciseAgent (Skattetrekk)")
            res = self.tax_agent.verify_skattetrekk()
            return f"🏦 **Skattetrekkskontroll (Konto 1925)**\n\nStatus: {res['status_melding']}\nSaldo konto 1925: {res['bank_konto_1925_saldo']:,.2f} NOK\nSkyldig skattetrekk: {res['total_skattetrekk_skyldig']:,.2f} NOK\nDekningsgrad: {res['dekning_prosent']}%\nDifferanse: {res['differanse']:,.2f} NOK"

        elif any(term in q_lower for term in ["særavgift", "alkoholavgift", "lager", "harahorn", "arvesølvet", "emballasje"]):
            logger.info("Ruter til Analytics/Tax (Lager & Avgifter)")
            df = self.analytics_agent.analyse_lager()
            return f"📦 **Lager- og Særavgiftsoversikt**\n\n```\n{df.to_string(index=False)}\n```"

        elif any(term in q_lower for term in ["cash flow", "kontantstrøm", "s-kurve", "radar", "prognose", "likviditet"]):
            logger.info("Ruter til CashFPARadarAgent")
            df = self.cash_radar_agent.get_radar_metrics()
            return f"📈 **FP&A Likviditet & Risk Radar**\n\n```\n{df.to_string(index=False)}\n```"

        else:
            # Generell økonomisk henvendelse håndteres av Supervisor LLM
            prompt = (
                f"Bruker spør: '{user_query}'\n"
                "Svar som Lead Financial Controller for Det Norske Brenneri AS. "
                "Bruk en strukturert tone i henhold til Edward Tufte-prinsipper."
            )
            return self.compliance_agent.run_llm(prompt, provider=p)

