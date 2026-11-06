import urllib.request
import urllib.parse
import json
from typing import Dict, Any, Optional, List
from src.utils.logger import logger

class BrregClient:
    """
    Klient for direkte sanntidsoppslag mot Brønnøysundregistrenes åpne REST API:
    - Enhetsregisteret (grunndata, konkursstatus, MVA-status)
    - Regnskapsregisteret (årsregnskap 2023-2025)
    - Roller (styre, ledelse, revisor)
    """

    BASE_ENHET = "https://data.brreg.no/enhetsregisteret/api"
    BASE_REGNSKAP = "https://data.brreg.no/regnskapsregisteret"
    HEADERS = {
        "Accept": "application/json",
        "User-Agent": "OkAdmOfficeHub/2.4 (Det Norske Brenneri AS; Controller Tool)"
    }

    @classmethod
    def lookup_orgnr(cls, orgnr: str) -> Optional[Dict[str, Any]]:
        """Slår opp 9-sifret organisasjonsnummer i Enhetsregisteret."""
        clean_orgnr = "".join(filter(str.isdigit, str(orgnr)))
        if len(clean_orgnr) != 9:
            return None

        url = f"{cls.BASE_ENHET}/enheter/{clean_orgnr}"
        try:
            req = urllib.request.Request(url, headers=cls.HEADERS)
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Feil ved oppslag i Enhetsregisteret for {clean_orgnr}: {e}")
        return None

    @classmethod
    def search_by_name(cls, name: str, size: int = 5) -> List[Dict[str, Any]]:
        """Søker etter selskaper etter navn i Enhetsregisteret."""
        query = urllib.parse.quote(name.strip())
        url = f"{cls.BASE_ENHET}/enheter?navn={query}&size={size}"
        try:
            req = urllib.request.Request(url, headers=cls.HEADERS)
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("_embedded", {}).get("enheter", [])
        except Exception as e:
            logger.error(f"Feil ved navnesøk i Enhetsregisteret for '{name}': {e}")
        return []

    @classmethod
    def lookup_roles(cls, orgnr: str) -> Optional[Dict[str, Any]]:
        """Henter registrerte roller (styre, revisor, daglig leder)."""
        clean_orgnr = "".join(filter(str.isdigit, str(orgnr)))
        url = f"{cls.BASE_ENHET}/enheter/{clean_orgnr}/roller"
        try:
            req = urllib.request.Request(url, headers=cls.HEADERS)
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Feil ved rolleoppslag for {clean_orgnr}: {e}")
        return None

    @classmethod
    def lookup_regnskap(cls, orgnr: str) -> List[Dict[str, Any]]:
        """Henter offisielle årsregnskaper fra Regnskapsregisteret."""
        clean_orgnr = "".join(filter(str.isdigit, str(orgnr)))
        url = f"{cls.BASE_REGNSKAP}/regnskap/{clean_orgnr}"
        try:
            req = urllib.request.Request(url, headers=cls.HEADERS)
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Feil ved regnskapsoppslag for {clean_orgnr}: {e}")
        return []

    @classmethod
    def evaluate_credit_risk(cls, enhet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gjør en rask forhåndsevaluering av kredittrisiko basert på registerdata."""
        if not enhet_data:
            return {"status": "UKJENT", "farge": "secondary", "begrunnelse": "Ingen registerdata funnet"}

        konkurs = enhet_data.get("konkurs", False)
        avvikling = enhet_data.get("underAvvikling", False)
        tvangsavvikling = enhet_data.get("underTvangsavviklingEllerTvangsopplosning", False)
        mva_reg = enhet_data.get("registrertIMvaregisteret", False)
        formaal = enhet_data.get("formaal", "")

        if konkurs or avvikling or tvangsavvikling:
            return {
                "status": "KRITISK RISIKO",
                "farge": "danger",
                "begrunnelse": "Selskapet er registrert som konkurs, under avvikling eller tvangsoppløsning!"
            }

        if not mva_reg:
            return {
                "status": "OBS",
                "farge": "warning",
                "begrunnelse": "Ikke registrert i MVA-registeret (kan være nystiftet eller fritatt)."
            }

        return {
            "status": "GODKJENT (LAV RISIKO)",
            "farge": "success",
            "begrunnelse": "Aktivt norsk selskap, MVA-registrert, ingen konkurser eller avviklinger registrert."
        }
