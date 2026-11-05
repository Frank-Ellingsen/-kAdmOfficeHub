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

# 1. COMPLIANCE & LEGAL RAG AGENT
class ComplianceRAGAgent(SpecialistAgent):
    """Regelverks- og MVA-spesialist for Det Norske Brenneri AS."""
    def __init__(self, router: LLMRouter):
        prompt = (
            "Du er senior regelverks- og MVA-spesialist for Det Norske Brenneri AS (Org.nr 996 928 977).\n"
            "Retningslinjer:\n"
            "1. Begrunn alle svar i norsk skatte- og regnskapslovgivning (Merverdiavgiftsloven, Bokføringsforskriften, Aksjeloven).\n"
            "2. Henvis spesifikt til lovparagrafer (f.eks. Mva-loven § 8-1, § 8-3 for representasjon, Bokføring § 8-10-6).\n"
            "3. Ta hensyn til bransjespesifikke krav for engroshandel og produksjon av alkoholholdige drikkevarer (Næringskode 46.340).\n"
            "4. Vær presis, profesjonell og gi konkrete råd."
        )
        super().__init__("compliance_rag_agent", prompt, router)

    def ask_legal(self, query: str, provider: str = "gemini") -> str:
        return query_rag(query, k=4, provider=provider)

# 2. ANALYTICS & RESKONTRO DUCKDB AGENT
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

# 3. TAX & EXCISE ALTINN AGENT
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

# 4. CASH & FP&A RADAR AGENT
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

# 5. PROCUREMENT & ANBUD AGENT (NEW - 7-Agent Architecture)
class ProcurementAnbudAgent(SpecialistAgent):
    """Anbuds- og priskalkylespesialist for Vinmonopolet og grossister."""
    def __init__(self, router: LLMRouter, engine: DuckDBEngine):
        prompt = (
            "Du er Procurement & Anbud Agent for Det Norske Brenneri AS.\n"
            "Dine ansvarsområder er:\n"
            "1. Vinmonopolet anbudsbesvarelser og produktlanseringer i basis-, parti- og bestillingsutvalget.\n"
            "2. Grossistprisfiler for Asko, Servicegrossistene og Horeca.\n"
            "3. Kalkylekontroll: Varekost, alkoholavgift (kr 942.50/L ren alkohol), emballasjeavgift, grossistavanse og dekningsbidrag.\n"
            "4. Sikre marginbeskyttelse og lønnsomhet i alle anbud."
        )
        super().__init__("procurement_anbud_agent", prompt, router)
        self.engine = engine

    def calculate_margin(
        self,
        product_name: str,
        cost_price_ex_tax: float,
        alcohol_pct: float,
        volume_l: float,
        target_retail_nok: float,
        packaging_fee: float = 6.20
    ) -> Dict[str, Any]:
        """Beregner dekningsbidrag og avgifter baklengs fra utsalgspris i Vinmonopolet."""
        pure_alcohol_liters = volume_l * (alcohol_pct / 100.0)
        alcohol_excise_duty = pure_alcohol_liters * 942.50
        retail_ex_mva = target_retail_nok / 1.25
        vinmonopolet_markup = (retail_ex_mva * 0.08) + 12.0  # Ca. 8% + kr 12 per enhet
        gross_wholesale_net = retail_ex_mva - vinmonopolet_markup
        dekningsbidrag = gross_wholesale_net - alcohol_excise_duty - packaging_fee - cost_price_ex_tax
        dekningsgrad = (dekningsbidrag / gross_wholesale_net * 100.0) if gross_wholesale_net > 0 else 0.0

        return {
            "produkt": product_name,
            "utsalgspris_vinmonopolet_inkl_mva": round(target_retail_nok, 2),
            "utsalgspris_ex_mva": round(retail_ex_mva, 2),
            "alkoholavgift_nok": round(alcohol_excise_duty, 2),
            "emballasjeavgift_nok": round(packaging_fee, 2),
            "est_vinmonopolet_avanse": round(vinmonopolet_markup, 2),
            "grossistpris_netto": round(gross_wholesale_net, 2),
            "innkjopskost_vare": round(cost_price_ex_tax, 2),
            "dekningsbidrag_nok": round(dekningsbidrag, 2),
            "dekningsgrad_prosent": round(dekningsgrad, 1),
            "lonnsomt": dekningsbidrag > 0
        }

# 6. AUDIT & YEAR-END AGENT (NEW - 7-Agent Architecture)
class AuditYearEndAgent(SpecialistAgent):
    """Årsavslutnings- og revisjonsspesialist."""
    def __init__(self, router: LLMRouter, engine: DuckDBEngine):
        prompt = (
            "Du er Audit & Year-End Agent for Det Norske Brenneri AS.\n"
            "Dine ansvarsområder er:\n"
            "1. Utarbeide dokumentasjonsmapper og revisjonsunderlag for ekstern revisor.\n"
            "2. Balanseavstemming (Konto 1925 skattetrekk, varelager, anleggsmidler, periodiseringer).\n"
            "3. Årsavslutningssjekkliste iht. regnskapsloven og god regnskapsskikk (NRS).\n"
            "4. Avskrivningsplaner for produksjonsutstyr, fat og destillasjonsapparater."
        )
        super().__init__("audit_year_end_agent", prompt, router)
        self.engine = engine

    def get_audit_closing_checklist(self) -> List[Dict[str, str]]:
        """Returnerer standard årsavslutningssjekkliste for brenneriet."""
        return [
            {"Område": "Bank & Skattetrekk", "Konto": "1925", "Krav": "100% sperret dekning mot terminoppgjør", "Status": "PÅKREVD"},
            {"Område": "Varelager (Fat & Flasker)", "Konto": "1400/1420", "Krav": "Fysisk varetelling, skille ufortollet/fortollet lager", "Status": "PÅKREVD"},
            {"Område": "Kundereskontro", "Konto": "1500", "Krav": "Aldersfordelt saldo, vurdering av tapsavsetning", "Status": "PÅKREVD"},
            {"Område": "Leverandørreskontro", "Konto": "2400", "Krav": "Avstemt mot åpne poster og leverandørkontoutdrag", "Status": "PÅKREVD"},
            {"Område": "Særavgifter Alkohol", "Konto": "2770", "Krav": "Avstemming av innrapportert til Skatteetaten vs produksjon", "Status": "PÅKREVD"},
            {"Område": "Merverdiavgift", "Konto": "2700-2740", "Krav": "Avstemt mot 6 terminer MVA-meldinger i Altinn", "Status": "PÅKREVD"},
            {"Område": "Lønn & AGA", "Konto": "5000/2770", "Krav": "Avstemt mot A07 A-meldinger for hele regnskapsåret", "Status": "PÅKREVD"}
        ]

# 7. SUPERVISOR AGENT (MASTER ORCHESTRATOR - 7 AGENT SYSTEM)
class SupervisorAgent:
    """
    Master Orchestrator og Supervisor Agent for Office Hub (7-Agent Topology).
    Evaluerer intensjon og koordinerer oppgaver mellom alle spesialistene.
    """
    def __init__(self, provider: str = "gemini"):
        self.router = LLMRouter(default_provider=provider)
        self.engine = DuckDBEngine()
        
        # Registrer alle 6 underordnede spesialistagenter
        self.compliance_agent = ComplianceRAGAgent(self.router)
        self.analytics_agent = AnalyticsReskontroAgent(self.router, self.engine)
        self.tax_agent = TaxExciseAgent(self.router, self.engine)
        self.cash_radar_agent = CashFPARadarAgent(self.router, self.engine)
        self.procurement_agent = ProcurementAnbudAgent(self.router, self.engine)
        self.audit_agent = AuditYearEndAgent(self.router, self.engine)

    def route_and_execute(self, user_query: str, provider: Optional[str] = None) -> str:
        """Klassifiserer henvendelse og dirigerer til rett spesialist."""
        p = provider or self.router.default_provider
        q_lower = user_query.lower()

        logger.info(f"Supervisor (7-Agent DAG) evaluerer oppgave: '{user_query}'")

        # 1. Compliance & Legal
        if any(term in q_lower for term in ["mva", "lov", "paragraf", "fradrag", "representasjon", "regnskapslov"]):
            logger.info("Ruter til ComplianceRAGAgent")
            return self.compliance_agent.ask_legal(user_query, provider=p)

        # 2. Reskontro & AR Aging
        elif any(term in q_lower for term in ["reskontro", "kunde", "utestående", "forfalt", "aldersfordeling"]):
            logger.info("Ruter til AnalyticsReskontroAgent")
            res = self.analytics_agent.analyse_reskontro()
            df = res["tabell"]
            return f"📊 **Kundereskontro Analyse**\n\nTotalt utestående: {res['totalt_utestaaende']:,.2f} NOK\nForfalt >60 dager: {res['forfalt_over_60_dager']:,.2f} NOK\n\n```\n{df.to_string(index=False)}\n```"

        # 3. Tax, Altinn & Skattetrekk
        elif any(term in q_lower for term in ["skattetrekk", "konto 1925", "lønn", "aga", "a-melding"]):
            logger.info("Ruter til TaxExciseAgent (Skattetrekk)")
            res = self.tax_agent.verify_skattetrekk()
            return f"🏦 **Skattetrekkskontroll (Konto 1925)**\n\nStatus: {res['status_melding']}\nSaldo konto 1925: {res['bank_konto_1925_saldo']:,.2f} NOK\nSkyldig skattetrekk: {res['total_skattetrekk_skyldig']:,.2f} NOK\nDekningsgrad: {res['dekning_prosent']}%\nDifferanse: {res['differanse']:,.2f} NOK"

        # 4. Alkohol- og Særavgifter / Lager
        elif any(term in q_lower for term in ["særavgift", "alkoholavgift", "lager", "harahorn", "arvesølvet", "emballasje"]):
            logger.info("Ruter til Analytics/Tax (Lager & Avgifter)")
            df = self.analytics_agent.analyse_lager()
            return f"📦 **Lager- og Særavgiftsoversikt**\n\n```\n{df.to_string(index=False)}\n```"

        # 5. Cash Flow, S-Kurve & FP&A Radar
        elif any(term in q_lower for term in ["cash flow", "kontantstrøm", "s-kurve", "radar", "prognose", "likviditet"]):
            logger.info("Ruter til CashFPARadarAgent")
            df = self.cash_radar_agent.get_radar_metrics()
            return f"📈 **FP&A Likviditet & Risk Radar**\n\n```\n{df.to_string(index=False)}\n```"

        # 6. Procurement & Anbud / Prising (NEW)
        elif any(term in q_lower for term in ["anbud", "vinmonopolet", "prisfil", "grossist", "kalkyle", "dekningsbidrag", "dekningsgrad", "margin"]):
            logger.info("Ruter til ProcurementAnbudAgent")
            kalkyle = self.procurement_agent.calculate_margin(
                product_name="Harahorn Premium Gin 0.5L",
                cost_price_ex_tax=45.0,
                alcohol_pct=46.0,
                volume_l=0.5,
                target_retail_nok=420.0
            )
            return (
                f"🏷️ **Procurement & Anbud – Priskalkyle Vinmonopolet**\n\n"
                f"Produkt: **{kalkyle['produkt']}**\n"
                f"- Utsalgspris Vinmonopolet (inkl. MVA): {kalkyle['utsalgspris_vinmonopolet_inkl_mva']:,.2f} NOK\n"
                f"- Alkoholavgift (kr 942.50/L ren alk.): {kalkyle['alkoholavgift_nok']:,.2f} NOK\n"
                f"- Emballasjeavgift: {kalkyle['emballasjeavgift_nok']:,.2f} NOK\n"
                f"- Estimert Vinmonopolet-påslag: {kalkyle['est_vinmonopolet_avanse']:,.2f} NOK\n"
                f"- Netto innkjøpskost varelager: {kalkyle['innkjopskost_vare']:,.2f} NOK\n"
                f"- **Dekningsbidrag (DB):** {kalkyle['dekningsbidrag_nok']:,.2f} NOK\n"
                f"- **Dekningsgrad (DG):** {kalkyle['dekningsgrad_prosent']}%\n"
                f"- Status: {'✅ LØNNSOMT ANBUD' if kalkyle['lonnsomt'] else '❌ UTILSTREKKELIG MARGIN'}"
            )

        # 7. Audit & Årsavslutning (NEW)
        elif any(term in q_lower for term in ["revisjon", "revisor", "årsavslutning", "balanseavstemming", "avskrivning", "sjekkliste"]):
            logger.info("Ruter til AuditYearEndAgent")
            checklist = self.audit_agent.get_audit_closing_checklist()
            df_check = pd.DataFrame(checklist)
            return f"📋 **Årsavslutnings- og Revisjonssjekkliste**\n\n```\n{df_check.to_string(index=False)}\n```"

        else:
            # Generell økonomisk henvendelse håndteres av Supervisor LLM
            prompt = (
                f"Bruker spør: '{user_query}'\n"
                "Svar som Lead Financial Controller for Det Norske Brenneri AS innen 7-Agent Antigravity-arkitekturen. "
                "Bruk en profesjonell, strukturert tone iht. Edward Tufte Data-Ink-prinsipper."
            )
            return self.compliance_agent.run_llm(prompt, provider=p)
