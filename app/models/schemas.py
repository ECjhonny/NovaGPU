"""Modelos Pydantic reutilizables del proyecto."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="Pregunta del colaborador", example="¿Cuáles son los precios de las GPUs?")
    department: Optional[str] = Field(None, description="Filtro opcional por departamento", example="marketing")
    session_id: Optional[str] = Field(None, description="ID de la sesión de chat")


class SourceItem(BaseModel):
    department: str
    file: str


class ChatResponse(BaseModel):
    response: str
    sources: List[SourceItem]
    timestamp: str
    error: Optional[str] = None
