import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# API-nøkler
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# Ollama & Gemini
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Embeddings
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# Mappedirektiver
DATA_DIR = BASE_DIR / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_documents"
ERP_EXPORTS_DIR = DATA_DIR / "erp_exports"
FINANCIAL_MODELS_DIR = DATA_DIR / "financial_models"
DUCKDB_PATH = DATA_DIR / "duckdb" / "okonomi_analytics.duckdb"
DOCS_DIR = BASE_DIR / "docs"
DASHBOARDS_DIR = BASE_DIR / "dashboards"

# Sjekk lokal vector_store-mappe i repoet først, deretter env
_local_vector_store = BASE_DIR / "vector_store" / "chroma_db"
_configured_chroma_dir = os.getenv("CHROMA_DB_DIR")

if _local_vector_store.exists():
    CHROMA_DB_DIR = _local_vector_store
elif _configured_chroma_dir:
    CHROMA_DB_DIR = Path(_configured_chroma_dir).expanduser()
    if not CHROMA_DB_DIR.is_absolute():
        CHROMA_DB_DIR = BASE_DIR / CHROMA_DB_DIR
elif os.name == "nt" and os.getenv("LOCALAPPDATA"):
    CHROMA_DB_DIR = Path(os.environ["LOCALAPPDATA"]) / "OkAdmOfficeHub" / "chroma_db"
else:
    CHROMA_DB_DIR = (
        Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        / "okadmofficehub"
        / "chroma_db"
    )

def find_data_file(filename: str) -> Path | None:
    """Finner en datafil på tvers av data/, erp_exports/ og financial_models/."""
    candidates = [
        ERP_EXPORTS_DIR / filename,
        FINANCIAL_MODELS_DIR / filename,
        DATA_DIR / filename,
        RAW_DOCS_DIR / filename
    ]
    for c in candidates:
        if c.exists():
            return c
    return None
