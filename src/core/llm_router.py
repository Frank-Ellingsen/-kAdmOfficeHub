import sys
from pathlib import Path
from typing import Optional, Any
from langchain_core.language_models.chat_models import BaseChatModel

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OLLAMA_HOST,
    OLLAMA_MODEL
)
from src.utils.logger import logger

class LLMRouter:
    """
    Ruter og forvalter LLM-kall mellom lokale modeller (Ollama Llama 3.1)
    og skyløsninger (Google Gemini Flash) for kostnadseffektiv og fleksibel drift.
    """

    def __init__(self, default_provider: str = "gemini"):
        self.default_provider = default_provider.lower()

    def get_llm(self, provider: Optional[str] = None, temperature: float = 0.1) -> BaseChatModel:
        """Returnerer initialisert LangChain Chat-modell."""
        target_provider = (provider or self.default_provider).lower()

        if target_provider == "gemini":
            if not GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY ikke funnet. Bytter automatisk til lokal Ollama.")
                return self._get_ollama_llm(temperature)
            
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                logger.info(f"Initialiserer Google Gemini [{GEMINI_MODEL}]...")
                return ChatGoogleGenerativeAI(
                    model=GEMINI_MODEL,
                    google_api_key=GEMINI_API_KEY,
                    temperature=temperature
                )
            except Exception as e:
                logger.error(f"Kunne ikke laste Gemini ({e}). Fallback til Ollama.")
                return self._get_ollama_llm(temperature)
        else:
            return self._get_ollama_llm(temperature)

    def _get_ollama_llm(self, temperature: float = 0.1) -> BaseChatModel:
        """Initialiserer lokal Ollama LLM."""
        from langchain_ollama import ChatOllama
        base_url = OLLAMA_HOST
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = f"http://{base_url}"

        logger.info(f"Initialiserer lokal Ollama [{OLLAMA_MODEL}] på {base_url}...")
        return ChatOllama(
            base_url=base_url,
            model=OLLAMA_MODEL,
            temperature=temperature
        )

