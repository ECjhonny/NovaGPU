"""Módulo de embeddings para el flujo RAG.

Soporta Voyage AI, OpenRouter, Google Gemini y Cohere como proveedores de embeddings.
"""

from typing import Any
from pydantic import SecretStr

try:
    from langchain_voyageai import VoyageAIEmbeddings
except ImportError:
    VoyageAIEmbeddings = None

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

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
    OPENROUTER_API_KEY,
    OPENROUTER_EMBEDDING_MODEL,
    VOYAGE_API_KEY,
    VOYAGE_EMBEDDING_MODEL,
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    COHERE_API_KEY,
    COHERE_EMBEDDING_MODEL,
)
from app.utils import get_logger

logger = get_logger(__name__)


def _is_valid_key(key: str) -> bool:
    """Verifica que una clave de API no esté vacía ni sea una plantilla de ejemplo."""
    if not key or not key.strip():
        return False
    k = key.strip().lower()
    return not ("tu_clave" in k or k == "gsk_tu_clave_groq_aqui")


def get_embeddings() -> Any:
    """Retorna una instancia configurada del modelo de embeddings (Voyage AI, OpenRouter, Gemini o Cohere)."""
    provider = EMBEDDINGS_PROVIDER.lower()

    def _try_voyage() -> Any | None:
        if _is_valid_key(VOYAGE_API_KEY) and VoyageAIEmbeddings is not None:
            logger.info(
                f"🧠 Modelo de embeddings Voyage AI configurado: {VOYAGE_EMBEDDING_MODEL}"
            )
            return VoyageAIEmbeddings(  # type: ignore # pyright: ignore[reportCallIssue]
                model=VOYAGE_EMBEDDING_MODEL,
                voyage_api_key=SecretStr(VOYAGE_API_KEY),  # pyright: ignore[reportCallIssue]
            )
        return None

    def _try_openrouter() -> Any | None:
        if _is_valid_key(OPENROUTER_API_KEY) and OpenAIEmbeddings is not None:
            logger.info(
                f"🧠 Modelo de embeddings OpenRouter configurado: {OPENROUTER_EMBEDDING_MODEL}"
            )
            return OpenAIEmbeddings(
                model=OPENROUTER_EMBEDDING_MODEL,
                api_key=SecretStr(OPENROUTER_API_KEY),
                base_url="https://openrouter.ai/api/v1",
                check_embedding_ctx_length=False,
            )
        return None

    def _try_gemini() -> Any | None:
        if _is_valid_key(GEMINI_API_KEY) and GoogleGenerativeAIEmbeddings is not None:
            logger.info(
                f"🧠 Modelo de embeddings Gemini configurado: {GEMINI_EMBEDDING_MODEL}"
            )
            return GoogleGenerativeAIEmbeddings(  # pyright: ignore[reportCallIssue]
                model=GEMINI_EMBEDDING_MODEL,
                google_api_key=GEMINI_API_KEY,  # pyright: ignore[reportCallIssue]
            )
        return None

    def _try_cohere() -> Any | None:
        if _is_valid_key(COHERE_API_KEY) and CohereEmbeddings is not None:
            logger.info(
                f"🧠 Modelo de embeddings Cohere configurado: {COHERE_EMBEDDING_MODEL}"
            )
            return CohereEmbeddings(  # pyright: ignore[reportCallIssue]
                model=COHERE_EMBEDDING_MODEL,
                cohere_api_key=SecretStr(COHERE_API_KEY),
                client=None,
                async_client=None,
            )
        return None

    builders = {
        "voyage": _try_voyage,
        "openrouter": _try_openrouter,
        "gemini": _try_gemini,
        "cohere": _try_cohere,
    }

    priority_map = {
        "voyage": ["voyage", "openrouter", "gemini", "cohere"],
        "openrouter": ["openrouter", "voyage", "gemini", "cohere"],
        "gemini": ["gemini", "openrouter", "voyage", "cohere"],
        "cohere": ["cohere", "openrouter", "voyage", "gemini"],
    }
    order = priority_map.get(
        provider, ["voyage", "openrouter", "gemini", "cohere"]
    )

    for p in order:
        instance = builders[p]()
        if instance is not None:
            return instance

    logger.error(
        "❌ Ninguna API Key configurada para Voyage AI, OpenRouter, Gemini o Cohere. Verifica tu archivo .env"
    )
    raise ValueError(
        "No hay API Key configurada para embeddings. "
        "Agrega VOYAGE_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY o COHERE_API_KEY a tu archivo .env."
    )
