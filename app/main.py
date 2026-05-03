import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from app.logger import logger
from app.schemas import SearchRequest, SearchResponse
from app.rag import initialize_rag_from_docs, search_documentation


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