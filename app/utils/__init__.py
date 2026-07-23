"""Utilidades compartidas del proyecto."""

import io
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List

try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document  # type: ignore[import-not-found]
    except ImportError:  # pragma: no cover - fallback para entornos sin langchain clásico
        Document = Any  # type: ignore[misc,assignment]


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        if isinstance(sys.stdout, io.TextIOWrapper):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def format_documents_for_context(documents: List[Any]) -> str:
    if not documents:
        return "No se encontraron documentos relevantes."

    formatted_parts = []
    for i, doc in enumerate(documents, 1):
        department = doc.metadata.get("department", "Desconocido")
        source = doc.metadata.get("source_file", "Desconocido")
        content = doc.page_content.strip()
        formatted_parts.append(
            f"--- Documento {i} ---\n"
            f"📁 Departamento: {department}\n"
            f"📄 Fuente: {source}\n"
            f"Contenido:\n{content}\n"
        )

    return "\n".join(formatted_parts)


def format_chat_response(response: str, sources: List[Any]) -> Dict[str, Any]:
    source_list = []
    seen = set()

    for doc in sources:
        source_key = (
            doc.metadata.get("department", ""),
            doc.metadata.get("source_file", ""),
        )
        if source_key not in seen:
            seen.add(source_key)
            source_list.append(
                {
                    "department": doc.metadata.get("department", "N/A"),
                    "file": doc.metadata.get("source_file", "N/A"),
                }
            )

    return {
        "response": response,
        "sources": source_list,
        "timestamp": datetime.now().isoformat(),
    }


def validate_api_key(api_key: str) -> bool:
    if not api_key:
        return False
    return api_key.startswith("sk-") and len(api_key) > 20


__all__ = [
    "get_logger",
    "format_documents_for_context",
    "format_chat_response",
    "validate_api_key",
]
