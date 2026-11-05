import sys
from pathlib import Path
import pandas as pd

# Sørg for at rotmappen kan importeres
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DATA_DIR, ERP_EXPORTS_DIR, FINANCIAL_MODELS_DIR, find_data_file
from src.rag.retriever import query_rag
from src.analytics.duckdb_engine import DuckDBEngine
from src.core.agent_engine import SupervisorAgent

def main_menu():
    current_provider = "gemini"  # Standard LLM ("gemini" eller "ollama")
    analytics_engine = DuckDBEngine()
    supervisor = SupervisorAgent(provider=current_provider)

    print("=" * 75)
    print("🚀 Velkommen til ØkAdmOfficeHub – Det Norske Brenneri AS")
    print("   Orkestrert Multi-Agent System (7 Antigravity Agenter i DAG-topologi)")
    print("=" * 75)

    while True:
        print(f"\n⚙️  Aktiv LLM-leverandør: [{current_provider.upper()}]")
        print("1️⃣   Still spørsmål til lovverket (MVA, Regnskap, Skatt via RAG)")
        print("2️⃣   Kundereskontro analyse (Aldersfordeling 0-30, 31-60, >60 dager)")
        print("3️⃣   Lager- og alkoholavgiftsavstemming (Avgiftsfritt vs Fortollet)")
        print("4️⃣   Skattetrekkskontroll (100% dekningskontroll på Konto 1925)")
        print("5️⃣   MVA-oppgave Termin 1 & Altinn XML-utkast")
        print("6️⃣   12-måneders S-kurve & Early Warning Risk Radar (FP&A)")
        print("7️⃣   Anbudskalkyle & Vinmonopolet marginberegning (Procurement Agent)")
        print("8️⃣   Årsavslutning & revisjonssjekkliste (Audit Year-End Agent)")
        print("9️⃣   Kjør egendefinert SQL-spørring mot ERP-data (DuckDB)")
        print("🔟   Still fritt spørsmål til Supervisor Agent (Autonom ruting)")
        print("1️⃣1️⃣ Bytt LLM-leverandør (Gemini <-> Ollama)")
        print("1️⃣2️⃣ Avslutt")

        valg = input("\n👉 Velg et alternativ (1-12): ").strip()

        if valg == "1":
            print("\n" + "-" * 60)
            sporsmal = input("❓ Skriv inn spørsmålet ditt om lovverket/MVA:\n> ").strip()
            if sporsmal:
                query_rag(sporsmal, k=4, provider=current_provider)
            else:
                print("⚠️ Spørsmålet var tomt.")

        elif valg == "2":
            print("\n📊 Kjører reskontroanalyse (Aldersfordeling)...")
            res_df = analytics_engine.reskontro_aldersfordeling()
            if not res_df.empty:
                print("\n" + res_df.to_string(index=False))
            else:
                print("⚠️ Ingen reskontrodata funnet i data/erp_exports/reskontro.csv.")

        elif valg == "3":
            print("\n📦 Avstemmer lagerbeholdning og beregner særavgifter...")
            lager_df = analytics_engine.avstem_lager_og_avgifter()
            if not lager_df.empty:
                print("\n" + lager_df.to_string(index=False))
            else:
                print("⚠️ Finner ikke lagerdata i data/erp_exports/lager_avstemming.csv.")

        elif valg == "4":
            print("\n🏦 Kontrollerer 100% skattetrekksdekning på bankkonto 1925...")
            saldo_str = input("💵 Tast inn faktisk saldo på Konto 1925 [standard: 125000]: ").strip()
            saldo = float(saldo_str) if saldo_str else 125000.0
            sjekk = analytics_engine.skattetrekk_verifier(bank_1925_balance=saldo)
            print(f"\n{sjekk['status_melding']}")
            print(f" - Saldo skattetrekkskonto: {sjekk['bank_konto_1925_saldo']:,.2f} NOK")
            print(f" - Skyldig skattetrekk:     {sjekk['total_skattetrekk_skyldig']:,.2f} NOK")
            print(f" - Dekningsgrad:            {sjekk['dekning_prosent']}%")
            print(f" - Differanse:              {sjekk['differanse']:,.2f} NOK")

        elif valg == "5":
            print("\n📑 MVA-oppgave Termin 1:")
            mva_summary = analytics_engine.beregn_netto_mva()
            print(f" - Utgående MVA (salg):    {mva_summary['utgaaende_mva']:,.2f} NOK")
            print(f" - Inngående MVA (fradrag): {mva_summary['inngaaende_mva']:,.2f} NOK")
            print(f" - Netto MVA til betaling:  {mva_summary['netto_mva_til_betaling']:,.2f} NOK")
            
            opprett_xml = input("\nVil du generere Altinn XML-utkast? (j/n): ").strip().lower()
            if opprett_xml == "j":
                xml_utkast = supervisor.tax_agent.generate_altinn_xml_draft()
                print("\n" + xml_utkast)

        elif valg == "6":
            print("\n📈 FP&A: 12-Måneders S-Kurve og Risk Radar:")
            radar_df = analytics_engine.early_warning_radar()
            print("\n--- Early Warning Radar ---")
            print(radar_df.to_string(index=False) if not radar_df.empty else "Ingen radardata.")
            
            scurve_df = analytics_engine.cashflow_scurve_analyse()
            print("\n--- 12-Måneders S-Kurve ---")
            print(scurve_df.head(6).to_string(index=False) if not scurve_df.empty else "Ingen S-kurvedata.")

        elif valg == "7":
            print("\n🏷️ Procurement & Anbud – Priskalkyle Vinmonopolet:")
            p_navn = input("Produktnavn [Harahorn Gin]: ").strip() or "Harahorn Gin"
            p_innkjop = float(input("Innkjøpskost ex mva/avgift [45.0]: ").strip() or "45.0")
            p_alk = float(input("Alkoholprosent [46.0]: ").strip() or "46.0")
            p_vol = float(input("Volum i liter [0.5]: ").strip() or "0.5")
            p_utsalg = float(input("Mål utsalgspris i Vinmonopolet inkl mva [420.0]: ").strip() or "420.0")

            kalk = supervisor.procurement_agent.calculate_margin(
                product_name=p_navn,
                cost_price_ex_tax=p_innkjop,
                alcohol_pct=p_alk,
                volume_l=p_vol,
                target_retail_nok=p_utsalg
            )
            print(f"\n📊 Kalkyle for {kalk['produkt']}:")
            print(f" - Alkoholavgift (kr 942.50/L ren alk.): {kalk['alkoholavgift_nok']:,.2f} NOK")
            print(f" - Emballasjeavgift:                     {kalk['emballasjeavgift_nok']:,.2f} NOK")
            print(f" - Estimert Vinmonopolet-påslag:          {kalk['est_vinmonopolet_avanse']:,.2f} NOK")
            print(f" - Netto grossistinntekt:                {kalk['grossistpris_netto']:,.2f} NOK")
            print(f" - Dekningsbidrag (DB):                  {kalk['dekningsbidrag_nok']:,.2f} NOK")
            print(f" - Dekningsgrad (DG):                    {kalk['dekningsgrad_prosent']}%")
            print(f" - Vurdering: {'✅ Godkjent og lønnsomt' if kalk['lonnsomt'] else '❌ Negativ margin'}")

        elif valg == "8":
            print("\n📋 Årsavslutnings- og revisjonssjekkliste:")
            check_df = pd.DataFrame(supervisor.audit_agent.get_audit_closing_checklist())
            print(check_df.to_string(index=False))

        elif valg == "9":
            print("\n📁 Tilgjengelige filer for SQL-spørring:")
            csv_filer = list(ERP_EXPORTS_DIR.glob("*.csv")) + list(FINANCIAL_MODELS_DIR.glob("*.xlsx"))
            for i, f in enumerate(csv_filer, 1):
                print(f" [{i}] {f.name}")

            filnavn = input("\n📝 Skriv inn filnavnet du vil spørre mot:\n> ").strip()
            valgt_fil = find_data_file(filnavn)

            if not valgt_fil or not valgt_fil.exists():
                print(f"❌ Finner ikke filen {filnavn}")
                continue

            sql_template = input("🔎 Skriv SQL-spørring (bruk '{table}' som tabellnavn):\n   Eksempel: SELECT * FROM {table} LIMIT 5\n> ").strip()
            
            if valgt_fil.suffix.lower() == ".csv":
                res_df = analytics_engine.query_csv(valgt_fil, sql_template)
            elif valgt_fil.suffix.lower() in [".xlsx", ".xls"]:
                fane = input("📄 Skriv inn navnet på Excel-fanen (standard: Sheet1): ").strip() or "Sheet1"
                res_df = analytics_engine.query_excel(valgt_fil, sheet_name=fane, sql_query_template=sql_template)
            else:
                print("❌ Kun CSV og Excel-filer støttes.")
                continue

            print("\n📊 Resultat:")
            print(res_df.to_string(index=False) if not res_df.empty else "Ingen rader returnert.")

        elif valg == "10":
            sporsmal = input("\n🤖 Still et fritt spørsmål til Supervisor Agent:\n> ").strip()
            if sporsmal:
                svar = supervisor.route_and_execute(sporsmal, provider=current_provider)
                print("\n" + svar)

        elif valg == "11":
            current_provider = "ollama" if current_provider == "gemini" else "gemini"
            supervisor = SupervisorAgent(provider=current_provider)
            print(f"\n🔄 Endret aktiv LLM-leverandør til: [{current_provider.upper()}]")

        elif valg in ["12", "avslutt", "exit", "q"]:
            print("\n👋 Avslutter ØkAdmOfficeHub. God vakt videre!")
            break

        else:
            print("⚠️ Ugyldig valg. Velg et tall mellom 1 og 12.")

if __name__ == "__main__":
    main_menu()
