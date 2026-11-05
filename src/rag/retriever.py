import sys
from pathlib import Path

# Sørg for at src-mappen kan importeres
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config import (
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
    OLLAMA_HOST,
    OLLAMA_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL
)

def get_embedding_function():
    base_url = OLLAMA_HOST
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        base_url = f"http://{base_url}"

    return OllamaEmbeddings(
        base_url=base_url,
        model=EMBEDDING_MODEL
    )

def get_llm(provider: str = "ollama"):
    """Returnerer enten Ollama (Llama 3.1) eller Gemini Flash basert på valg."""
    provider = provider.lower()
    
    if provider == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError("❌ GEMINI_API_KEY mangler i .env-filen!")
        print(f"✨ Bruker Google Gemini: '{GEMINI_MODEL}'")
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )
    else:
        base_url = OLLAMA_HOST
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = f"http://{base_url}"

        print(f"🦙 Bruker Ollama lokalt: '{OLLAMA_MODEL}' på {base_url}")
        return ChatOllama(
            base_url=base_url,
            model=OLLAMA_MODEL,
            temperature=0.1
        )

def query_rag(query_text: str, k: int = 4, provider: str = "gemini"):
    """
    Søker i ChromaDB og svarer med enten Gemini eller Ollama.
    
    :param query_text: Spørsmålet du vil stille
    :param k: Antall kildeutdrag som skal hentes fra lovverket
    :param provider: 'gemini' eller 'ollama'
    """
    embeddings = get_embedding_function()
    
    # 1. Sjekk at databasen eksisterer
    if not CHROMA_DB_DIR.exists():
        print(f"❌ Finner ikke vektordatabasen på {CHROMA_DB_DIR}. Kjør ingest.py først!")
        return

    vector_store = Chroma(
        persist_directory=str(CHROMA_DB_DIR),
        embedding_function=embeddings
    )

    # 2. Hent relevante kildedokumenter
    print(f"🔍 Søker i lovverket etter: '{query_text}'...")
    try:
        docs_with_scores = vector_store.similarity_search_with_score(query_text, k=k)
    except Exception as e:
        print(f"\n⚠️ Feil under oppslag i ChromaDB: {e}")
        return

    if not docs_with_scores:
        print("⚠️ Ingen relevante kildetekster ble funnet i databasen.")
        return

    print(f"\n📄 Fant {len(docs_with_scores)} relevante tekstutdrag:")
    formatted_context = []
    for i, (doc, score) in enumerate(docs_with_scores, 1):
        source_name = Path(doc.metadata.get('source', 'Ukjent')).name
        page_num = doc.metadata.get('page', 0) + 1
        print(f"   [{i}] {source_name} (Side {page_num}) - Relevansscore: {score:.4f}")
        formatted_context.append(f"--- KILDE: {source_name} (Side {page_num}) ---\n{doc.page_content}")

    context_str = "\n\n".join(formatted_context)

    # 3. Opprett prompt
    template = """Du er en presis fagassistent innen økonomi, regnskap og MVA for norske bedrifter. 
Din oppgave er å oppsummere og forklare hva den vedlagte lovteksten bestemmer om spørsmålet.
Svar nøyaktig basert på konteksten nedenfor, og oppgi relevante paragrafer/ledd og kildesider.

Kontekst fra lovverket:
{context}

Spørsmål: {question}

Svar (redegjør for hva lovteksten sier):"""

    prompt = ChatPromptTemplate.from_template(template)
    
    # 4. Velg modell (Gemini eller Ollama)
    llm = get_llm(provider=provider)
    chain = prompt | llm | StrOutputParser()

    print(f"\n🤖 Genererer svar...")
    print("-" * 60)
    response = chain.invoke({"context": context_str, "question": query_text})
    print(f"\n💡 Svar:\n{response}\n")
    print("-" * 60)
    return response

if __name__ == "__main__":
    test_query = "Hva er fradragsretten for inngående merverdiavgift ved kjøp av varer?"
    
    # Du kan bytte mellom "gemini" og "ollama" her:
    query_rag(test_query, provider="gemini")