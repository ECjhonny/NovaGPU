"""Módulo de vectorstore para el flujo RAG."""

import time
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import CHROMA_DB_DIR, COLLECTION_NAME, TOP_K_RESULTS
from app.rag.embeddings import get_embeddings
from app.utils import get_logger

logger = get_logger(__name__)

_vectorstore: Chroma | None = None


def get_vectorstore() -> Chroma:
    """Obtiene o crea la instancia del vector store (ChromaDB)."""
    global _vectorstore

    if _vectorstore is not None:
        return _vectorstore

    embeddings = get_embeddings()

    _vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DB_DIR),
    )

    logger.info(f"🗄️ Vector store conectado: {CHROMA_DB_DIR}")
    return _vectorstore


def get_document_count() -> int:
    """Retorna el número de documentos indexados actualmente en ChromaDB."""
    try:
        vectorstore = get_vectorstore()
        return vectorstore._collection.count()
    except Exception as e:  # noqa: BLE001
        logger.warning(f"⚠️ Error al verificar el conteo de documentos: {e}")
        return 0


def index_documents(documents: list[Document], batch_size: int = 15, force: bool = False) -> None:
    """
    Indexa una lista de documentos en el vector store en lotes con reintentos para evitar Rate Limit (429).
    Si force=False y ya existen documentos en la BD, omite la re-indexación para ahorrar tokens.
    """
    if not documents:
        logger.warning("⚠️ No hay documentos para indexar.")
        return

    existing_count = get_document_count()
    if not force and existing_count > 0:
        logger.info(
            f"ℹ️ El vector store ya contiene {existing_count} fragmentos indexados. "
            "Omitiendo re-indexación al inicio para economizar tokens de API."
        )
        return

    try:
        vectorstore = get_vectorstore()
        total = len(documents)
        for i in range(0, total, batch_size):
            batch = documents[i : i + batch_size]
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    vectorstore.add_documents(batch)
                    break
                except Exception as batch_err:
                    err_str = str(batch_err)
                    if "dimension" in err_str.lower() or "expecting embedding" in err_str.lower():
                        logger.warning(
                            "⚠️ Desajuste de dimensiones de embeddings detectado en ChromaDB. Recreando la colección..."
                        )
                        reset_vectorstore()
                        vectorstore = get_vectorstore()
                        vectorstore.add_documents(batch)
                        break
                    elif any(term in err_str.lower() for term in ["429", "resource_exhausted", "rate limit", "ratelimit", "rpm", "tpm"]):
                        if attempt < max_retries - 1:
                            wait_time = 25 * (attempt + 1)
                            logger.warning(
                                f"⚠️ Rate limit alcanzado en batch {i // batch_size + 1}. Esperando {wait_time}s para reintentar (Intento {attempt + 1}/{max_retries})..."
                            )
                            time.sleep(wait_time)
                        else:
                            raise
                    else:
                        raise
            time.sleep(2)

        logger.info(f"✅ {total} documentos indexados exitosamente.")
    except Exception as e:
        logger.error(f"❌ No se pudieron indexar los documentos: {e}")
        raise RuntimeError(
            f"No fue posible indexar los documentos ({e}). Si utilizas el plan gratuito de Gemini, espera unos momentos e intenta de nuevo."
        ) from e


def search_documents(
    query: str, k: int = TOP_K_RESULTS, department: str | None = None
) -> list[Document]:
    """Busca documentos relevantes en el vector store."""
    vectorstore = get_vectorstore()

    search_kwargs: dict[str, Any] = {"k": k}
    if department:
        search_kwargs["filter"] = {"department": department}

    results = vectorstore.similarity_search(query, **search_kwargs)
    logger.info(f"🔍 Búsqueda: '{query[:50]}...' → {len(results)} resultados")

    return results


def get_retriever(k: int = TOP_K_RESULTS, department: str | None = None):
    """Obtiene un retriever configurado del vector store."""
    vectorstore = get_vectorstore()

    search_kwargs: dict[str, Any] = {"k": k}
    if department:
        search_kwargs["filter"] = {"department": department}

    return vectorstore.as_retriever(search_kwargs=search_kwargs)


def reset_vectorstore() -> None:
    """Elimina y recrea la colección del vector store."""
    global _vectorstore

    vectorstore = get_vectorstore()
    vectorstore.delete_collection()
    _vectorstore = None

    logger.info("🗑️ Vector store reiniciado.")
