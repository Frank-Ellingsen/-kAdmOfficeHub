import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils.logger import logger

class ExcelCleaner:
    """
    Renser og standardiserer regnskapsfiler og Excel-ark (f.eks. Visma/Tripletex-eksporter)
    slik at de kan analyseres deterministisk i DuckDB eller presenteres i dashboards.
    """

    @staticmethod
    def inspect_sheets(file_path: Path) -> List[str]:
        """Returnerer liste over alle faner i en Excel-arbeidsbok."""
        try:
            excel = pd.ExcelFile(file_path)
            return excel.sheet_names
        except Exception as e:
            logger.error(f"Kunne ikke lese faner fra {file_path}: {e}")
            return []

    @staticmethod
    def clean_sheet(
        file_path: Path,
        sheet_name: str,
        header_row: int = 0,
        drop_empty_rows: bool = True
    ) -> pd.DataFrame:
        """
        Laster inn og renser et Excel-ark:
        - Fjerner overflødige tomme rader og kolonner
        - Fjerner innledende/avsluttende mellomrom fra kolonnenavn
        - Standardiserer numeriske verdier
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            if drop_empty_rows:
                df = df.dropna(how="all").dropna(axis=1, how="all")

            # Rens kolonnenavn
            df.columns = [str(col).strip() for col in df.columns]

            # Fiks eventuelle norske tallformater (komma -> punktum, mellomrom i tusener)
            for col in df.select_dtypes(include=["object"]).columns:
                try:
                    cleaned_series = df[col].astype(str).str.replace(" ", "").str.replace(",", ".")
                    numeric_series = pd.to_numeric(cleaned_series)
                    df[col] = numeric_series
                except (ValueError, TypeError):
                    pass

            return df
        except Exception as e:
            logger.error(f"Feil under rensing av {file_path} (fane: {sheet_name}): {e}")
            return pd.DataFrame()

    @staticmethod
    def workbook_to_dict(file_path: Path) -> Dict[str, pd.DataFrame]:
        """Laster alle faner i en Excel-fil som en ordbok av rensede DataFrames."""
        sheets = ExcelCleaner.inspect_sheets(file_path)
        data = {}
        for s in sheets:
            df = ExcelCleaner.clean_sheet(file_path, sheet_name=s)
            if not df.empty:
                data[s] = df
        return data

