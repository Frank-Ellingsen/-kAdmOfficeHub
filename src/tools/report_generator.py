import sys
from pathlib import Path
import pandas as pd
from typing import Dict, Any, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

class TufteReportGenerator:
    """
    Rapportgenerator bygget på Edward Tuftes 'Data-Ink Ratio'-prinsipper:
    - Ingen vertikale gitterlinjer.
    - Venstrejustert tekst, høyrejustert tall, justerte desimaler.
    - Muted fargepalett; markeringer (amber/rød) reservert for faktiske avvik og risiko.
    - Direkte merking fremfor unødvendige tegnforklaringer.
    """

    @staticmethod
    def format_variance(val: float, threshold: float = 0.0) -> str:
        """Formaterer avvik med fargekoding (ASCII/Markdown)."""
        if val < threshold:
            return f"🔴 {val:,.2f}"
        elif val > threshold:
            return f"🟢 +{val:,.2f}"
        return f"⚪ {val:,.2f}"

    @staticmethod
    def dataframe_to_clean_markdown(df: pd.DataFrame) -> str:
        """Konverterer en DataFrame til en ren markdown-tabell uten dekorative elementer."""
        if df.empty:
            return "_Ingen data registrert._"
        return df.to_markdown(index=False)

    @staticmethod
    def generate_controller_brief(
        company_name: str,
        org_nr: str,
        kpis: Dict[str, Any],
        alerts: list[str]
    ) -> str:
        """Genererer en konsis konsernrapport for prosjektcontroller / CFO."""
        lines = [
            f"# Økonomisk Ledelsesrapport – {company_name}",
            f"**Organisasjonsnummer:** {org_nr}  |  **Periode:** YTD 2026",
            "",
            "## 1. Nøkkeltall (Executive KPIs)",
            ""
        ]
        
        for k, v in kpis.items():
            lines.append(f"- **{k}:** {v}")

        lines.append("")
        lines.append("## 2. Aktive Avvik og Risikovarsler (Early Warning)")
        if alerts:
            for a in alerts:
                lines.append(f"- ⚠️ {a}")
        else:
            lines.append("- Ingen kritiske avvik registrert.")

        lines.append("")
        lines.append("---")
        lines.append("_Rapport generert deterministisk av ØkAdmOfficeHub._")
        return "\n".join(lines)

