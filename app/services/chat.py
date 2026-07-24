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
    TEMPERATURE,
    TOP_K_RESULTS,
)
from app.rag.prompts import CHAT_PROMPT, CONDENSE_QUESTION_PROMPT
from app.rag.vectorstore import get_retriever, search_documents
from app.utils import format_chat_response, format_documents_for_context, get_logger

logger = get_logger(__name__)

_chat_sessions: dict[str, ConversationBufferWindowMemory] = {}


def _get_llm():
    """
    Crea y retorna una instancia del modelo de lenguaje.
    Soporta tres proveedores: Cohere (principal por defecto), Gemini (secundario), Groq (tercer opción).
    """
    provider = LLM_PROVIDER.lower()

    if provider == "groq":
        if GROQ_API_KEY and ChatGroq is not None:
            logger.info(f"⚡ Usando Groq LLM: {GROQ_MODEL}")
            return ChatGroq(
                model=GROQ_MODEL,
                temperature=TEMPERATURE,
                api_key=SecretStr(GROQ_API_KEY),
            )
        elif COHERE_API_KEY and ChatCohere is not None:
            logger.info(f"⚡ Usando Cohere LLM (fallback): {COHERE_MODEL}")
            return ChatCohere(
                model=COHERE_MODEL,
                temperature=TEMPERATURE,
                cohere_api_key=SecretStr(COHERE_API_KEY),
            )
        elif GEMINI_API_KEY and ChatGoogleGenerativeAI is not None:
            logger.info(f"⚡ Usando Gemini LLM (fallback): {GEMINI_MODEL}")
            return ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                temperature=TEMPERATURE,
                google_api_key=GEMINI_API_KEY,
            )

    if provider == "gemini":
        if GEMINI_API_KEY and ChatGoogleGenerativeAI is not None:
            logger.info(f"⚡ Usando Gemini LLM: {GEMINI_MODEL}")
            return ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                temperature=TEMPERATURE,
                google_api_key=GEMINI_API_KEY,
            )
        elif COHERE_API_KEY and ChatCohere is not None:
            logger.info(f"⚡ Usando Cohere LLM (fallback): {COHERE_MODEL}")
            return ChatCohere(
                model=COHERE_MODEL,
                temperature=TEMPERATURE,
                cohere_api_key=SecretStr(COHERE_API_KEY),
            )
        elif GROQ_API_KEY and ChatGroq is not None:
            logger.info(f"⚡ Usando Groq LLM (fallback): {GROQ_MODEL}")
            return ChatGroq(
                model=GROQ_MODEL,
                temperature=TEMPERATURE,
                api_key=SecretStr(GROQ_API_KEY),
            )

    # Por defecto se utiliza Cohere (con fallback a Gemini o Groq)
    if COHERE_API_KEY and ChatCohere is not None:
        logger.info(f"⚡ Usando Cohere LLM: {COHERE_MODEL}")
        return ChatCohere(
            model=COHERE_MODEL,
            temperature=TEMPERATURE,
            cohere_api_key=SecretStr(COHERE_API_KEY),
        )
    elif GEMINI_API_KEY and ChatGoogleGenerativeAI is not None:
        logger.info(f"⚡ Usando Gemini LLM (fallback): {GEMINI_MODEL}")
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=TEMPERATURE,
            google_api_key=GEMINI_API_KEY,
        )
    elif GROQ_API_KEY and ChatGroq is not None:
        logger.info(f"⚡ Usando Groq LLM (fallback): {GROQ_MODEL}")
        return ChatGroq(
            model=GROQ_MODEL,
            temperature=TEMPERATURE,
            api_key=SecretStr(GROQ_API_KEY),
        )
    else:
        logger.error("❌ Ninguna API Key válida configurada para Cohere, Gemini o Groq. Verifica tu archivo .env")
        raise ValueError(
            "No se encontró ninguna API Key válida configurada. "
            "Agrega COHERE_API_KEY, GEMINI_API_KEY o GROQ_API_KEY a tu archivo .env para el LLM."
        )


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


def get_chat_chain(session_id: str = "default") -> ConversationalRetrievalChain:
    """
    Crea una cadena conversacional RAG con retriever y memoria.
    """
    llm = _get_llm()
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

    return chain


def chat(
    question: str,
    session_id: str = "default",
    department: str | None = None,
) -> dict[str, Any]:
    """
    Procesa una pregunta del usuario y retorna la respuesta.
    """
    try:
        logger.info(f"💬 Pregunta [{session_id}]: {question[:80]}...")

        if department:
            docs = search_documents(question, k=TOP_K_RESULTS, department=department)
            context = format_documents_for_context(docs)
            llm = _get_llm()
            memory = _get_memory(session_id)

            chat_history = memory.chat_memory.messages if hasattr(memory, "chat_memory") else []

            messages = CHAT_PROMPT.format_messages(
                context=context,
                chat_history=chat_history,
                question=question,
            )
            response = llm.invoke(messages)
            raw_content = response.content
            answer: str = raw_content if isinstance(raw_content, str) else str(raw_content)
            memory.save_context({"question": question}, {"answer": answer})
            source_docs = docs
        else:
            chain = get_chat_chain(session_id)
            result = chain.invoke({"question": question})
            raw_answer = result.get("answer", "")
            answer: str = raw_answer if isinstance(raw_answer, str) else str(raw_answer)
            source_docs = result.get("source_documents", [])

        formatted = format_chat_response(answer, source_docs)
        logger.info(f"✅ Respuesta generada ({len(answer)} caracteres)")

        return formatted

    except Exception as e:  # noqa: BLE001
        err_msg = str(e)
        logger.error(f"❌ Error en chat: {err_msg}")
        
        if "401" in err_msg or "Incorrect API key" in err_msg or "Unauthorized" in err_msg or "invalid_api_key" in err_msg.lower():
            user_error = (
                "❌ **Error de Autenticación (API Key Incorrecta o Expirada)**\n\n"
                "La clave de API utilizada no es válida o ha caducado.\n"
                "Por favor, revisa tu archivo `.env` y asegúrate de configurar una API Key válida:\n"
                "- **Cohere**: Obtén tu API key en [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)\n"
                "- **Gemini**: Obtén tu API key en [aistudio.google.com/apikey](https://aistudio.google.com/apikey)\n"
                "- **Groq**: Obtén tu API key en [console.groq.com/keys](https://console.groq.com/keys)"
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
