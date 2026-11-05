import argparse
from datetime import datetime
import sys
from pathlib import Path

# Sørg for at src-mappen kan importeres
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config import (
    RAW_DOCS_DIR,
    CHROMA_DB_DIR,
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    OLLAMA_HOST
)

def get_embedding_function():
    """Velger og returnerer embedding-modellen basert på config."""
    base_url = OLLAMA_HOST
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        base_url = f"http://{base_url}"

    if EMBEDDING_PROVIDER.lower() == "ollama":
        print(f"🔄 Bruker Ollama Embedding-modell: '{EMBEDDING_MODEL}' på {base_url}")
        return OllamaEmbeddings(
            base_url=base_url,
            model=EMBEDDING_MODEL
        )
    else:
        print(f"🔄 Bruker HuggingFace Embedding-modell: '{EMBEDDING_MODEL}'")
        return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def run_ingestion(rebuild: bool = False):
    """Laster inn PDF-er, deler opp teksten og bygger/oppdaterer ChromaDB i puljer (batches)."""
    print(f"📂 Laster PDF-dokumenter fra: {RAW_DOCS_DIR}")
    
    if not RAW_DOCS_DIR.exists() or not any(RAW_DOCS_DIR.glob("*.pdf")):
        print(f"⚠️ Ingen PDF-filer funnet i {RAW_DOCS_DIR}. Legg til noen PDF-er der før du kjører på nytt.")
        return

    # 1. Last inn alle PDF-er i mappen
    loader = PyPDFDirectoryLoader(str(RAW_DOCS_DIR))
    raw_documents = loader.load()
    print(f"📄 Fant {len(raw_documents)} sider fordelt på PDF-dokumentene.")

    # 2. Del opp teksten i tilpassede biter (chunking) for juridiske tekster
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n§", "\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(raw_documents)
    total_chunks = len(chunks)
    print(f"🧩 Delte opp dokumentene i {total_chunks} kildeblokker (chunks).")

    # 3. Klargjør embedding-funksjon
    embeddings = get_embedding_function()

    if rebuild and CHROMA_DB_DIR.exists():
        backup_dir = CHROMA_DB_DIR.with_name(
            f"{CHROMA_DB_DIR.name}.backup-{datetime.now():%Y%m%d-%H%M%S-%f}"
        )
        CHROMA_DB_DIR.rename(backup_dir)
        print(f"📦 Eksisterende database er bevart som: {backup_dir}")

    # 4. Klargjør ChromaDB og legg til dokumenter i puljer (batching)
    batch_size = 50
    print(
        f"💾 Indekserer {total_chunks} kildeblokker i ChromaDB "
        f"(puljer på {batch_size}) i {CHROMA_DB_DIR}..."
    )

    CHROMA_DB_DIR.parent.mkdir(parents=True, exist_ok=True)
    vector_store = Chroma(
        persist_directory=str(CHROMA_DB_DIR),
        embedding_function=embeddings
    )

    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]
        vector_store.add_documents(documents=batch)
        print(f"   ⏳ Lagret chunk {min(i + batch_size, total_chunks)} / {total_chunks}...")

    print("✅ Vektordatabasen er opprettet og lagret med suksess!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bygg eller oppdater ChromaDB-indeksen.")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Bygg databasen på nytt, og behold eksisterende database som sikkerhetskopi.",
    )
    run_ingestion(rebuild=parser.parse_args().rebuild)