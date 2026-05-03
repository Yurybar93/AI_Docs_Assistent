import uuid
import hashlib
from pathlib import Path
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import VectorParams, Distance

from app.logger import logger
from app.settings import settings


collection_name = settings.QDRANT_COLLECTION_NAME
embedding_model_name = settings.EMBEDDING_MODEL_NAME
vector_size = settings.VECTOR_SIZE

client = QdrantClient(settings.QDRANT_HOST, port=settings.QDRANT_PORT)

if client.collection_exists(collection_name):
    client.delete_collection(collection_name)

client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
)

embeddings = OllamaEmbeddings(model=embedding_model_name)

vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
    distance=Distance.COSINE
)


def initialize_rag_from_docs() -> None:
    """Lädt beim Start alle .md-Dateien aus docs/ in die Vektordatenbank."""
    docs_dir = Path('docs')
    if not docs_dir.exists():
        logger.warning('Das Verzeichnis docs/ wurde nicht gefunden')
        return

    documents = []
    for file_path in docs_dir.glob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    documents.append(
                        Document(page_content=content, metadata={'source': str(file_path)})
                    )
        except Exception as exc:
            logger.error(f'Fehler beim Lesen der Datei {file_path}: {exc}')

    if documents:
        vector_store.add_documents(documents)
        logger.info(f'{len(documents)} Dokumente wurden in den RAG-Speicher geladen')
    else:
        logger.warning('Im Verzeichnis docs/ wurden keine .md-Dateien gefunden')


def add_document_to_index(file_path: str) -> bool:
    """
    Fügt ein einzelnes Dokument inkrementell zur Vektordatenbank hinzu. 
    Gibt bei Erfolg True zurück.
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8").strip()
        if not content:
            return False

        doc = Document(
            page_content=content,
            metadata={"source": str(file_path)}
        )

        hash_hex = hashlib.md5(str(file_path).encode()).hexdigest()
        doc_id = str(uuid.UUID(hash_hex[:32]))

        vector_store.add_documents([doc], ids=[doc_id])

        logger.info(f'Dokument wurde zum Index hinzugefügt: {file_path}')
        return True

    except Exception as exc:
        logger.error(f'Fehler beim Hinzufügen des Dokuments {file_path}: {exc}')
        return False