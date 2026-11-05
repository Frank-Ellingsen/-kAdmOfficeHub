import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.config import SERPER_API_KEY
from src.utils.logger import logger

def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Søker på nettet etter ferske satser, lovendringer eller Vinmonopolet-nyheter.
    Bruker DuckDuckGo som standard lokal løsning, eller Serper dersom API-nøkkel finnes.
    """
    results = []
    
    # 1. Forsøk Serper dersom nøkkel er oppgitt
    if SERPER_API_KEY:
        try:
            import requests
            url = "https://google.serper.dev/search"
            headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
            payload = {"q": query, "num": max_results}
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("organic", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })
                return results
        except Exception as e:
            logger.warning(f"Serper API-feil ({e}), faller tilbake til DuckDuckGo.")

    # 2. Fallback til DuckDuckGo
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for r in raw_results:
                results.append({
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
    except Exception as e:
        logger.error(f"Nett-søk feilet: {e}")

    return results

