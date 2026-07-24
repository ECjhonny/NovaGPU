"""Aplicación principal FastAPI para NovaGPU Assistant."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import STATIC_DIR
from app.rag.loader import load_and_split
from app.rag.vectorstore import get_document_count, index_documents
from app.routes.chat_routes import router
from app.utils import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga e indexa automáticamente la documentación solo si la base vectorial está vacía."""
    logger.info("🚀 Iniciando NovaGPU Assistant (FastAPI)...")

    try:
        existing_count = get_document_count()
        if existing_count > 0:
            logger.info(
                f"✅ Base de conocimiento RAG lista ({existing_count} fragmentos cargados previamente). "
                "Omitiendo auto-indexación al inicio para ahorrar tokens de API."
            )
        else:
            chunks = load_and_split()
            if chunks:
                logger.info(f"📚 Indexando por primera vez {len(chunks)} fragmentos de documentos...")
                index_documents(chunks, force=True)
                logger.info("✅ Base de conocimiento RAG lista.")
            else:
                logger.warning("⚠️ No se encontraron documentos en la carpeta 'documents/'.")
    except Exception as e:  # noqa: BLE001
        logger.error(f"⚠️ Error cargando documentos al iniciar: {e}")
        logger.info("La aplicación se iniciará de todos modos. Revisa la configuración de API keys o la conexión con el servicio de embeddings.")

    yield
    logger.info("👋 Cerrando NovaGPU Assistant...")


app = FastAPI(
    title="NovaGPU Assistant API",
    description="Asistente Corporativo RAG de NovaGPU Technologies (FastAPI + Groq + ChromaDB)",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(router)
