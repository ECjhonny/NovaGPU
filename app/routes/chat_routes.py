"""Rutas HTTP del asistente."""

from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.core.config import DEPARTMENTS, TEMPLATES_DIR
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import chat, clear_session
from app.rag.loader import load_and_split
from app.rag.vectorstore import index_documents, reset_vectorstore
from app.utils import get_logger

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.cache = None  # Evitar TypeError con dicts no hashables en el cache de Jinja2


logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"departments": DEPARTMENTS})


@router.post("/chat", response_model=ChatResponse)
@router.post("/api/chat", response_model=ChatResponse)
async def handle_chat(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El mensaje no puede estar vacío.")

    session_id = req.session_id or str(uuid.uuid4())
    result = chat(question=req.message.strip(), session_id=session_id, department=req.department)
    return result


@router.post("/api/clear")
async def handle_clear_history(session_id: Optional[str] = "default"):
    clear_session(session_id)
    return {"message": "Historial limpiado exitosamente.", "session_id": session_id}


@router.post("/api/index")
async def handle_reindex():
    try:
        logger.info("🔄 Re-indexación manual solicitada...")
        reset_vectorstore()
        chunks = load_and_split()
        if not chunks:
            return JSONResponse(content={"message": "No se encontraron documentos para indexar.", "count": 0})
        index_documents(chunks)
        return {"message": f"✅ {len(chunks)} fragmentos indexados exitosamente.", "count": len(chunks)}
    except Exception as e:
        logger.error(f"❌ Error en re-indexación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/api/departments")
async def get_departments():
    return {"departments": DEPARTMENTS}


@router.get("/health")
@router.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "NovaGPU Assistant API (FastAPI)", "departments_count": len(DEPARTMENTS)}
