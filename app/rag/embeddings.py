"""Módulo de embeddings para el flujo RAG.

Soporta Voyage AI, Google Gemini y Cohere como proveedores de embeddings.
"""

from typing import Any
from pydantic import SecretStr

try:
    from langchain_voyageai import VoyageAIEmbeddings
except ImportError:
    VoyageAIEmbeddings = None

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    GoogleGenerativeAIEmbeddings = None

try:
    from langchain_cohere import CohereEmbeddings
except ImportError:
    CohereEmbeddings = None

from app.core.config import (
    EMBEDDINGS_PROVIDER,
    VOYAGE_API_KEY,
    VOYAGE_EMBEDDING_MODEL,
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    COHERE_API_KEY,
    COHERE_EMBEDDING_MODEL,
)
from app.utils import get_logger

logger = get_logger(__name__)


def get_embeddings() -> Any:
    """Retorna una instancia configurada del modelo de embeddings (Voyage AI, Cohere o Gemini)."""
    provider = EMBEDDINGS_PROVIDER.lower()

    if provider == "voyage":
        if VOYAGE_API_KEY and VoyageAIEmbeddings is not None:
            embeddings = VoyageAIEmbeddings(  # type: ignore # pyright: ignore[reportCallIssue]
                model=VOYAGE_EMBEDDING_MODEL,
                voyage_api_key=SecretStr(VOYAGE_API_KEY),  # pyright: ignore[reportCallIssue]
            )
            logger.info(f"🧠 Modelo de embeddings Voyage AI configurado: {VOYAGE_EMBEDDING_MODEL}")
            return embeddings
        elif COHERE_API_KEY and CohereEmbeddings is not None:
            embeddings = CohereEmbeddings(  # pyright: ignore[reportCallIssue]
                model=COHERE_EMBEDDING_MODEL,
                cohere_api_key=SecretStr(COHERE_API_KEY),
                client=None,
                async_client=None,
            )
            logger.info(f"🧠 Modelo de embeddings Cohere (fallback) configurado: {COHERE_EMBEDDING_MODEL}")
            return embeddings
        elif GEMINI_API_KEY and GoogleGenerativeAIEmbeddings is not None:
            embeddings = GoogleGenerativeAIEmbeddings(  # pyright: ignore[reportCallIssue]
                model=GEMINI_EMBEDDING_MODEL,
                google_api_key=GEMINI_API_KEY,  # pyright: ignore[reportCallIssue]
            )
            logger.info(f"🧠 Modelo de embeddings Gemini (fallback) configurado: {GEMINI_EMBEDDING_MODEL}")
            return embeddings

    if provider == "gemini":
        if GEMINI_API_KEY and GoogleGenerativeAIEmbeddings is not None:
            embeddings = GoogleGenerativeAIEmbeddings(  # pyright: ignore[reportCallIssue]
                model=GEMINI_EMBEDDING_MODEL,
                google_api_key=GEMINI_API_KEY,  # pyright: ignore[reportCallIssue]
            )
            logger.info(f"🧠 Modelo de embeddings Gemini configurado: {GEMINI_EMBEDDING_MODEL}")
            return embeddings
        elif VOYAGE_API_KEY and VoyageAIEmbeddings is not None:
            embeddings = VoyageAIEmbeddings(  # type: ignore # pyright: ignore[reportCallIssue]
                model=VOYAGE_EMBEDDING_MODEL,
                voyage_api_key=SecretStr(VOYAGE_API_KEY),  # pyright: ignore[reportCallIssue]
            )
            logger.info(f"🧠 Modelo de embeddings Voyage AI (fallback) configurado: {VOYAGE_EMBEDDING_MODEL}")
            return embeddings
        elif COHERE_API_KEY and CohereEmbeddings is not None:
            embeddings = CohereEmbeddings(  # pyright: ignore[reportCallIssue]
                model=COHERE_EMBEDDING_MODEL,
                cohere_api_key=SecretStr(COHERE_API_KEY),
                client=None,
                async_client=None,
            )
            logger.info(f"🧠 Modelo de embeddings Cohere (fallback) configurado: {COHERE_EMBEDDING_MODEL}")
            return embeddings

    # Por defecto / si se especifica cohere
    if VOYAGE_API_KEY and VoyageAIEmbeddings is not None and provider == "voyage":
        embeddings = VoyageAIEmbeddings(  # type: ignore # pyright: ignore[reportCallIssue]
            model=VOYAGE_EMBEDDING_MODEL,
            voyage_api_key=SecretStr(VOYAGE_API_KEY),  # pyright: ignore[reportCallIssue]
        )
        logger.info(f"🧠 Modelo de embeddings Voyage AI configurado: {VOYAGE_EMBEDDING_MODEL}")
        return embeddings
    elif COHERE_API_KEY and CohereEmbeddings is not None:
        embeddings = CohereEmbeddings(  # pyright: ignore[reportCallIssue]
            model=COHERE_EMBEDDING_MODEL,
            cohere_api_key=SecretStr(COHERE_API_KEY),
            client=None,
            async_client=None,
        )
        logger.info(f"🧠 Modelo de embeddings Cohere configurado: {COHERE_EMBEDDING_MODEL}")
        return embeddings
    elif VOYAGE_API_KEY and VoyageAIEmbeddings is not None:
        embeddings = VoyageAIEmbeddings(  # type: ignore # pyright: ignore[reportCallIssue]
            model=VOYAGE_EMBEDDING_MODEL,
            voyage_api_key=SecretStr(VOYAGE_API_KEY),  # pyright: ignore[reportCallIssue]
        )
        logger.info(f"🧠 Modelo de embeddings Voyage AI (fallback) configurado: {VOYAGE_EMBEDDING_MODEL}")
        return embeddings
    elif GEMINI_API_KEY and GoogleGenerativeAIEmbeddings is not None:
        embeddings = GoogleGenerativeAIEmbeddings(  # pyright: ignore[reportCallIssue]
            model=GEMINI_EMBEDDING_MODEL,
            google_api_key=GEMINI_API_KEY,  # pyright: ignore[reportCallIssue]
        )
        logger.info(f"🧠 Modelo de embeddings Gemini (fallback) configurado: {GEMINI_EMBEDDING_MODEL}")
        return embeddings

    if not VOYAGE_API_KEY and not COHERE_API_KEY and not GEMINI_API_KEY:
        logger.error("❌ Ninguna API Key configurada para Voyage AI, Cohere o Gemini. Verifica tu archivo .env")
        raise ValueError(
            "No hay API Key configurada para embeddings. "
            "Agrega VOYAGE_API_KEY, COHERE_API_KEY o GEMINI_API_KEY a tu archivo .env."
        )

    raise ImportError(
        "No se pudo cargar ningún proveedor de embeddings. Asegúrate de instalar "
        "langchain-voyageai, langchain-cohere o langchain-google-genai."
    )
