import sys
from pathlib import Path
import duckdb
import pandas as pd
from typing import Optional, Dict, Any

# Sørg for at src-mappen kan importeres
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.config import BASE_DIR, DATA_DIR, ERP_EXPORTS_DIR, FINANCIAL_MODELS_DIR, find_data_file
from src.utils.logger import logger

class DuckDBEngine:
    """
    Analytisk motor drevet av DuckDB for lynraske spørringer mot 
    reskontro, lagertall, særavgifter, skattetrekk, og 3-statement modeller.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialiserer enten en in-memory DB eller en lokal DuckDB-fil."""
        if db_path:
            self.conn = duckdb.connect(str(db_path))
            logger.info(f"Koblet til DuckDB-database på: {db_path}")
        else:
            self.conn = duckdb.connect(database=":memory:")
            logger.info("Opprettet DuckDB i minnet (In-Memory Analytics Engine).")

    def query_df(self, sql_query: str) -> pd.DataFrame:
        """Kjører en SQL-spørring og returnerer resultatet som en Pandas DataFrame."""
        try:
            return self.conn.execute(sql_query).df()
        except Exception as e:
            logger.error(f"SQL-feil: {e}")
            return pd.DataFrame()

    def query_csv(self, csv_path: Path, sql_query_template: str) -> pd.DataFrame:
        """
        Kjører SQL direkte mot en CSV-fil uten manuell import.
        Bruk '{table}' i SQL-strengen som plassholder for CSV-filen.
        """
        if not csv_path.exists():
            logger.warning(f"Finner ikke filen: {csv_path}")
            return pd.DataFrame()

        formatted_query = sql_query_template.format(table=f"read_csv_auto('{csv_path.as_posix()}')")
        return self.query_df(formatted_query)

    def query_excel(self, excel_path: Path, sheet_name: str = "Sheet1", sql_query_template: Optional[str] = None) -> pd.DataFrame:
        """
        Laster en Excel-fane inn i DuckDB og kjører SQL-spørring mot den.
        """
        if not excel_path.exists():
            logger.warning(f"Finner ikke Excel-filen: {excel_path}")
            return pd.DataFrame()

        df_excel = pd.read_excel(excel_path, sheet_name=sheet_name)
        self.conn.register("excel_table", df_excel)
        
        if sql_query_template:
            query = sql_query_template.format(table="excel_table")
            return self.query_df(query)
        return df_excel

    # --- DOMENESPESIFIKKE ANALYSER FOR DET NORSKE BRENNERI AS ---

    def reskontro_aldersfordeling(self, reskontro_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Kundereskontro aldersfordeling (0-30 dager, 31-60 dager, >60 dager).
        """
        if reskontro_df is None:
            file_path = find_data_file("reskontro.csv")
            if file_path and file_path.exists():
                reskontro_df = pd.read_csv(file_path)
            else:
                return pd.DataFrame()

        self.conn.register("reskontro", reskontro_df)
        
        # Standardiser kolonnenavn (Belop vs Belop_NOK)
        amount_col = "Belop_NOK" if "Belop_NOK" in reskontro_df.columns else "Belop"

        query = f"""
        SELECT 
            Kundenavn,
            ROUND(SUM({amount_col}), 2) AS Totalt_Utestaaende,
            ROUND(SUM(CASE WHEN Dager_Forfalt <= 0 THEN {amount_col} ELSE 0 END), 2) AS Ikke_Forfalt,
            ROUND(SUM(CASE WHEN Dager_Forfalt BETWEEN 1 AND 30 THEN {amount_col} ELSE 0 END), 2) AS Forfalt_1_30d,
            ROUND(SUM(CASE WHEN Dager_Forfalt BETWEEN 31 AND 60 THEN {amount_col} ELSE 0 END), 2) AS Forfalt_31_60d,
            ROUND(SUM(CASE WHEN Dager_Forfalt > 60 THEN {amount_col} ELSE 0 END), 2) AS Forfalt_over_60d
        FROM reskontro
        GROUP BY Kundenavn
        ORDER BY Totalt_Utestaaende DESC
        """
        return self.query_df(query)

    def avstem_lager_og_avgifter(self, lager_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Lageravstemming med beregnet alkoholavgift og emballasjeavgift for sprit og drikkevarer.
        """
        if lager_df is None:
            file_path = find_data_file("lager_avstemming.csv")
            if file_path and file_path.exists():
                lager_df = pd.read_csv(file_path)
            else:
                return pd.DataFrame()

        self.conn.register("lager", lager_df)

        query = """
        SELECT 
            Produkt_ID,
            Produktnavn,
            Alkohol_Prosent,
            Volum_Liter,
            Antall_Avgiftsfritt_Ulaste AS Ulast_Lager,
            Antall_Fortollet_Lager AS Fortollet_Lager,
            (Antall_Avgiftsfritt_Ulaste + Antall_Fortollet_Lager) AS Totalt_Volum_Enheter,
            ROUND(Antall_Fortollet_Lager * Alkoholavgift_Pr_Enhet, 2) AS Paloopt_Alkoholavgift_NOK,
            ROUND(Antall_Fortollet_Lager * Emballasjeavgift_Pr_Enhet, 2) AS Paloopt_Emballasjeavgift_NOK,
            ROUND(Antall_Fortollet_Lager * (Alkoholavgift_Pr_Enhet + Emballasjeavgift_Pr_Enhet), 2) AS Total_Avgiftsforpliktelse_NOK
        FROM lager
        ORDER BY Total_Avgiftsforpliktelse_NOK DESC
        """
        return self.query_df(query)

    def skattetrekk_verifier(self, payroll_df: Optional[pd.DataFrame] = None, bank_1925_balance: float = 125000.0) -> Dict[str, Any]:
        """
        Kontrollerer 100% skattetrekksdekning på bankkonto 1925 iht. skattebetalingsloven.
        """
        if payroll_df is None:
            file_path = find_data_file("lonn_aga_avstemming.csv")
            if file_path and file_path.exists():
                payroll_df = pd.read_csv(file_path)
            else:
                return {"status": "ERROR", "message": "Finner ikke lonn_aga_avstemming.csv"}

        total_skattetrekk = float(payroll_df["Skattetrekk"].sum())
        total_aga = float(payroll_df["AGA_14_1"].sum())
        total_bruttolonn = float(payroll_df["Bruttolonn"].sum())
        differanse = bank_1925_balance - total_skattetrekk
        dekning_prosent = (bank_1925_balance / total_skattetrekk * 100) if total_skattetrekk > 0 else 100.0

        godkjent = differanse >= 0

        return {
            "bank_konto_1925_saldo": bank_1925_balance,
            "total_skattetrekk_skyldig": total_skattetrekk,
            "total_aga_skyldig": total_aga,
            "total_bruttolonn": total_bruttolonn,
            "differanse": differanse,
            "dekning_prosent": round(dekning_prosent, 2),
            "godkjent_100_prosent": godkjent,
            "status_melding": "✅ 100% FULL DEKNING PÅ SKATTETREKKSKONTO" if godkjent else f"❌ DEKNINGSMANGEL: Må overføre {abs(differanse):,.2f} NOK til konto 1925",
            "detaljert_tabell": payroll_df
        }

    def mva_oppgave_sammendrag(self, mva_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Sammendrag av MVA-melding (Termin 1) med inn- og utgående MVA.
        """
        if mva_df is None:
            file_path = find_data_file("mva_oppgave_termin1.csv")
            if file_path and file_path.exists():
                mva_df = pd.read_csv(file_path)
            else:
                return pd.DataFrame()

        self.conn.register("mva", mva_df)

        query = """
        SELECT 
            MVA_Kode,
            Beskrivelse,
            Konto,
            Grunnlag_NOK,
            MVA_Beregnet_NOK,
            CASE 
                WHEN MVA_Kode LIKE '%Kode 3%' OR MVA_Kode LIKE '%Kode 5%' THEN 'Utgående (Skyldig)'
                WHEN MVA_Kode LIKE '%Kode 1%' THEN 'Inngående (Fradrag)'
                ELSE 'Fritatt/Annet'
            END AS Retning
        FROM mva
        """
        return self.query_df(query)

    def beregn_netto_mva(self, mva_df: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """Beregner netto MVA til betaling eller tilgodehavende."""
        df = self.mva_oppgave_sammendrag(mva_df)
        if df.empty:
            return {"utgaaende_mva": 0.0, "inngaaende_mva": 0.0, "netto_mva_til_betaling": 0.0}

        utgaaende = float(df[df["Retning"] == "Utgående (Skyldig)"]["MVA_Beregnet_NOK"].sum())
        inngaaende = float(df[df["Retning"] == "Inngående (Fradrag)"]["MVA_Beregnet_NOK"].sum())
        netto = utgaaende - inngaaende

        return {
            "utgaaende_mva": utgaaende,
            "inngaaende_mva": inngaaende,
            "netto_mva_til_betaling": netto
        }

    def cashflow_scurve_analyse(self, scurve_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Henter og analyserer 12-måneders S-kurve for likviditetsrealisering (Baseline vs AI Prognose).
        """
        if scurve_df is None:
            file_path = find_data_file("scurve_cashflow_12m.csv")
            if file_path and file_path.exists():
                scurve_df = pd.read_csv(file_path)
            else:
                return pd.DataFrame()

        return scurve_df

    def early_warning_radar(self, prog_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Henter nøkkeltall for risikoovervåking (Working Capital, Free Cash Flow, EAC Variance).
        """
        if prog_df is None:
            file_path = find_data_file("financial_prognosis.csv")
            if file_path and file_path.exists():
                prog_df = pd.read_csv(file_path)
            else:
                return pd.DataFrame()

        return prog_df
