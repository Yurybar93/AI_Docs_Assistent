import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from app.logger import logger
from app.storage import save_document
from app.agents import generate_and_validate_documentation
from app.schemas import SearchRequest, SearchResponse, GenerateRequest, GenerateResponse
from app.rag import initialize_rag_from_docs, add_document_to_index, search_documentation


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Initialisierung RAG aus docs/')

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, initialize_rag_from_docs)

    logger.info('Service ist betriebsbereit')
    yield


app = FastAPI(title='AI Docs Assistant', lifespan=lifespan)


@app.get('/health')
def health_check():
    return {'status': 'ok'}


@app.post('/search', response_model=SearchResponse)
def search_docs(request: SearchRequest):
    """
    Führt eine semantische Suche in der API-Dokumentation durch
    """
    result = search_documentation(request.query)

    if result:
        return SearchResponse(found=True, content=result)
    else:
        return SearchResponse(
            found=False,
            message='Dokumenten nicht gefunden. Verwenden Sie /generate, um eine neue zu erstellen'
        )

@app.post('/generate', response_model=GenerateResponse)
def generate_docs(request: GenerateRequest):
    """
    Generiert neue Dokumentation und speichert sie in docs/.
    """
    if search_documentation(request.query, similarity_threshold=0.75):
        return GenerateResponse(
            success=False,
            message='Dokument existiert bereits. Verwenden Sie /search.'
        )

    try:
        content = generate_and_validate_documentation(request.query)

        if content is None:
            logger.warning(f'Validierung fehlgeschlagen für die Anfrage: {request.query}')
            return GenerateResponse(
                success=False,
                message='Validierung fehlgeschlagen: Das generierte Dokument wurde abgelehnt.'
            )

        if not content.strip().startswith('###'):
            logger.error(f'Das generierte Dokument entspricht nicht dem Format für die Anfrage: {request.query}')
            return GenerateResponse(
                success=False,
                message='Generierungsfehler: ungültiges Dokumentformat.'
            )

        file_path = save_document(content, request.query)

        add_document_to_index(file_path)

        return GenerateResponse(
            success=True,
            message='Dokument wurde erfolgreich erstellt und gespeichert.',
            content=content,
            file_path=file_path
        )

    except Exception as e:
        logger.error(f'Fehler bei der Dokumentgenerierung: {e}', exc_info=True)
        return GenerateResponse(
            success=False,
            message=f'Generierungsfehler: {str(e)}'
        )