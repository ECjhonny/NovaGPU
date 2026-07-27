"""
Módulo de chat.
Implementa la cadena conversacional RAG con Groq LLM y memoria de historial.
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import SecretStr

try:
    from langchain_cohere import ChatCohere
except ImportError:
    ChatCohere = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferWindowMemory

from app.core.config import (
    COHERE_API_KEY,
    COHERE_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    TEMPERATURE,
    TOP_K_RESULTS,
)
from app.rag.prompts import CHAT_PROMPT, CONDENSE_QUESTION_PROMPT
from app.rag.vectorstore import get_retriever, search_documents
from app.utils import format_chat_response, format_documents_for_context, get_logger

logger = get_logger(__name__)

_chat_sessions: dict[str, ConversationBufferWindowMemory] = {}


def _is_valid_key(key: str) -> bool:
    """Verifica que una clave de API no esté vacía ni sea una plantilla de ejemplo."""
    if not key or not key.strip():
        return False
    k = key.strip().lower()
    return not ("tu_clave" in k or k == "gsk_tu_clave_groq_aqui")


def _get_all_llms() -> list[tuple[str, Any]]:
    """
    Retorna una lista ordenada de todos los LLMs disponibles.
    El proveedor preferido (LLM_PROVIDER) va primero, seguido de los demás como fallback.
    Cada elemento es una tupla (nombre_proveedor, instancia_llm).
    """
    provider = LLM_PROVIDER.lower()
    available: list[tuple[str, Any]] = []

    # Definir constructores para cada proveedor
    builders: dict[str, tuple[str, Any] | None] = {}

    if _is_valid_key(OPENROUTER_API_KEY) and ChatOpenAI is not None:
        builders["openrouter"] = (
            f"OpenRouter ({OPENROUTER_MODEL})",
            ChatOpenAI(
                model=OPENROUTER_MODEL,
                temperature=TEMPERATURE,
                api_key=SecretStr(OPENROUTER_API_KEY),
                base_url="https://openrouter.ai/api/v1",
            ),
        )

    if _is_valid_key(COHERE_API_KEY) and ChatCohere is not None:
        builders["cohere"] = (
            f"Cohere ({COHERE_MODEL})",
            ChatCohere(
                model=COHERE_MODEL,
                temperature=TEMPERATURE,
                cohere_api_key=SecretStr(COHERE_API_KEY),
            ),
        )

    if _is_valid_key(GEMINI_API_KEY) and ChatGoogleGenerativeAI is not None:
        builders["gemini"] = (
            f"Gemini ({GEMINI_MODEL})",
            ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                temperature=TEMPERATURE,
                google_api_key=GEMINI_API_KEY,
            ),
        )

    if _is_valid_key(GROQ_API_KEY) and ChatGroq is not None:
        builders["groq"] = (
            f"Groq ({GROQ_MODEL})",
            ChatGroq(
                model=GROQ_MODEL,
                temperature=TEMPERATURE,
                api_key=SecretStr(GROQ_API_KEY),
            ),
        )

    # Orden de prioridad según el proveedor seleccionado
    priority_map = {
        "openrouter": ["openrouter", "gemini", "groq", "cohere"],
        "cohere": ["cohere", "openrouter", "gemini", "groq"],
        "gemini": ["gemini", "openrouter", "groq", "cohere"],
        "groq": ["groq", "openrouter", "gemini", "cohere"],
    }
    priority = priority_map.get(
        provider, ["openrouter", "gemini", "groq", "cohere"]
    )

    for p in priority:
        if p in builders and builders[p] is not None:
            available.append(builders[p])  # type: ignore[arg-type]

    if not available:
        logger.error(
            "❌ Ninguna API Key válida configurada para OpenRouter, Gemini, Groq o Cohere. Verifica tu archivo .env"
        )
        raise ValueError(
            "No se encontró ninguna API Key válida configurada. "
            "Agrega OPENROUTER_API_KEY, GEMINI_API_KEY, GROQ_API_KEY o COHERE_API_KEY a tu archivo .env para el LLM."
        )

    logger.info(
        f"⚡ Proveedores LLM disponibles ({len(available)}): "
        + ", ".join(name for name, _ in available)
    )
    return available


def _is_rate_limit_error(error: Exception) -> bool:
    """
    Determina si una excepción es un error de rate limit / cuota excedida.
    Cubre los códigos y mensajes de OpenRouter, Cohere, Gemini y Groq.
    """
    err_str = str(error).lower()
    rate_limit_indicators = [
        "429",
        "rate limit",
        "rate_limit",
        "too many requests",
        "quota exceeded",
        "quota_exceeded",
        "resource_exhausted",
        "resourceexhausted",
        "tokens per minute",
        "requests per minute",
        "rpm limit",
        "tpm limit",
        "try again later",
        "exceeded your current quota",
    ]
    return any(indicator in err_str for indicator in rate_limit_indicators)


def _get_memory(session_id: str) -> ConversationBufferWindowMemory:
    """
    Obtiene o crea la memoria de conversación para una sesión.
    Mantiene las últimas 4 interacciones para optimizar la ventana de tokens.
    """
    if session_id not in _chat_sessions:
        _chat_sessions[session_id] = ConversationBufferWindowMemory(
            k=4,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )
    return _chat_sessions[session_id]


def chat(
    question: str,
    session_id: str = "default",
    department: str | None = None,
) -> dict[str, Any]:
    """
    Procesa una pregunta del usuario y retorna la respuesta.
    Implementa fallback automático: si un proveedor LLM falla por cualquier motivo
    (rate limit, error de cuota o autenticación), conmuta al siguiente proveedor disponible.
    """
    try:
        logger.info(f"💬 Pregunta [{session_id}]: {question[:80]}...")

        all_llms = _get_all_llms()
        last_error: Exception | None = None

        # Pre-calcular datos que no dependen del LLM (evitar repetir trabajo)
        if department:
            docs = search_documents(question, k=TOP_K_RESULTS, department=department)
            context = format_documents_for_context(docs)
        else:
            docs = None
            context = None

        for provider_name, llm in all_llms:
            try:
                logger.info(f"🔄 Intentando con {provider_name}...")

                if department and docs is not None and context is not None:
                    # --- Ruta con filtro de departamento ---
                    memory = _get_memory(session_id)
                    chat_history = (
                        memory.chat_memory.messages
                        if hasattr(memory, "chat_memory")
                        else []
                    )
                    messages = CHAT_PROMPT.format_messages(
                        context=context,
                        chat_history=chat_history,
                        question=question,
                    )
                    response = llm.invoke(messages)
                    raw_content = response.content
                    answer: str = (
                        raw_content
                        if isinstance(raw_content, str)
                        else str(raw_content)
                    )
                    memory.save_context(
                        {"question": question}, {"answer": answer}
                    )
                    source_docs = docs
                else:
                    # --- Ruta general con cadena RAG ---
                    retriever = get_retriever(k=TOP_K_RESULTS)
                    memory = _get_memory(session_id)
                    chain = ConversationalRetrievalChain.from_llm(
                        llm=llm,
                        retriever=retriever,
                        memory=memory,
                        combine_docs_chain_kwargs={"prompt": CHAT_PROMPT},
                        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
                        get_chat_history=lambda h: h,
                        return_source_documents=True,
                        verbose=False,
                    )
                    result = chain.invoke({"question": question})
                    raw_answer = result.get("answer", "")
                    answer = (
                        raw_answer
                        if isinstance(raw_answer, str)
                        else str(raw_answer)
                    )
                    source_docs = result.get("source_documents", [])

                # ✅ Éxito: retornar respuesta
                formatted = format_chat_response(answer, source_docs)
                logger.info(
                    f"✅ Respuesta generada con {provider_name} ({len(answer)} caracteres)"
                )
                return formatted

            except Exception as llm_error:  # noqa: BLE001
                logger.warning(
                    f"⚠️ Fallo en proveedor {provider_name}: {llm_error}. "
                    "Intentando automáticamente con el siguiente proveedor disponible..."
                )
                last_error = llm_error
                continue

        # Si llegamos aquí, TODOS los proveedores alcanzaron su rate limit
        logger.error(
            "❌ Todos los proveedores LLM alcanzaron su límite de consultas."
        )
        return {
            "response": (
                "⏳ **Límite de consultas alcanzado temporalmente**\n\n"
                "Todos los proveedores de IA (OpenRouter, Gemini, Groq, Cohere) han alcanzado "
                "su límite de consultas en este momento.\n\n"
                "Por favor, espera **1-2 minutos** e intenta de nuevo.\n\n"
                "💡 *Consejo: Puedes aumentar los límites usando planes de pago "
                "en los proveedores de API.*"
            ),
            "sources": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": f"Rate limit en todos los proveedores. Último error: {last_error}",
        }

    except Exception as e:  # noqa: BLE001
        err_msg = str(e)
        logger.error(f"❌ Error en chat: {err_msg}")

        if (
            "401" in err_msg
            or "Incorrect API key" in err_msg
            or "Unauthorized" in err_msg
            or "invalid_api_key" in err_msg.lower()
        ):
            user_error = (
                "❌ **Error de Autenticación (API Key Incorrecta o Expirada)**\n\n"
                "La clave de API utilizada no es válida o ha caducado.\n"
                "Por favor, revisa tu archivo `.env` y asegúrate de configurar una API Key válida:\n"
                "- **OpenRouter**: Obtén tu API key en [openrouter.ai/keys](https://openrouter.ai/keys)\n"
                "- **Gemini**: Obtén tu API key en [aistudio.google.com/apikey](https://aistudio.google.com/apikey)\n"
                "- **Groq**: Obtén tu API key en [console.groq.com/keys](https://console.groq.com/keys)\n"
                "- **Cohere**: Obtén tu API key en [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)"
            )
        else:
            user_error = (
                "Lo siento, ocurrió un error al procesar tu pregunta. "
                "Por favor, verifica la configuración en tu archivo `.env` e intenta de nuevo."
            )

        return {
            "response": user_error,
            "sources": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": err_msg,
        }


def clear_session(session_id: str = "default") -> None:
    """Limpia el historial de una sesión de chat."""
    if session_id in _chat_sessions:
        del _chat_sessions[session_id]
        logger.info(f"🧹 Sesión '{session_id}' limpiada.")


def clear_all_sessions() -> None:
    """Limpia todas las sesiones de chat."""
    _chat_sessions.clear()
    logger.info("🧹 Todas las sesiones limpiadas.")
