import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates

from app.core.config import DEPARTMENTS, DOCUMENTS_DIR, SUPPORTED_EXTENSIONS, TEMPLATES_DIR
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.loader import load_and_split
from app.rag.vectorstore import index_documents, reset_vectorstore
from app.services.chat_service import chat, clear_session
from app.utils import get_logger

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.cache = None  # Evitar TypeError con dicts no hashables en el cache de Jinja2


logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"departments": DEPARTMENTS})


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/chat", response_model=ChatResponse)
@router.post("/api/chat", response_model=ChatResponse)
async def handle_chat(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El mensaje no puede estar vacío.")

    session_id = req.session_id or str(uuid.uuid4())
    result = chat(question=req.message.strip(), session_id=session_id, department=req.department)
    return result


@router.post("/api/clear")
async def handle_clear_history(session_id: str | None = "default"):
    target_session = session_id or "default"
    clear_session(target_session)
    return {"message": "Historial limpiado exitosamente.", "session_id": target_session}


@router.post("/api/index")
async def handle_reindex():
    try:
        logger.info("🔄 Re-indexación manual solicitada...")
        reset_vectorstore()
        chunks = load_and_split()
        if not chunks:
            return JSONResponse(content={"message": "No se encontraron documentos para indexar.", "count": 0})
        index_documents(chunks, force=True)
        return {"message": f"✅ {len(chunks)} fragmentos indexados exitosamente.", "count": len(chunks)}
    except Exception as e:  # noqa: BLE001
        logger.error(f"❌ Error en re-indexación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/api/departments")
async def get_departments():
    return {"departments": DEPARTMENTS}


@router.get("/api/documents")
async def get_documents():
    """Retorna la lista de todos los documentos organizados por departamento."""
    result = []
    try:
        for dept in DEPARTMENTS:
            dept_path = DOCUMENTS_DIR / dept
            if not dept_path.exists():
                dept_path.mkdir(parents=True, exist_ok=True)
            files = []
            for file_path in dept_path.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    files.append({
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "extension": file_path.suffix.lower(),
                        "path": f"{dept}/{file_path.name}"
                    })
            result.append({
                "department": dept,
                "files": files,
                "count": len(files)
            })
        return {"departments": result}
    except Exception as e:
        logger.error(f"Error obteniendo lista de documentos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form(...)
):
    """Sube un documento a la carpeta del departamento correspondiente."""
    if department not in DEPARTMENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Departamento inválido. Debe ser uno de: {', '.join(DEPARTMENTS)}"
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión no permitida. Formatos soportados: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    safe_filename = Path(file.filename).name
    dept_dir = DOCUMENTS_DIR / department
    dept_dir.mkdir(parents=True, exist_ok=True)
    target_path = dept_dir / safe_filename

    # Validar path traversal
    if not target_path.resolve().is_relative_to(DOCUMENTS_DIR.resolve()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ruta de archivo no válida.")

    try:
        content = await file.read()
        with open(target_path, "wb") as f:
            f.write(content)
        
        logger.info(f"📁 Documento subido con éxito: {target_path}")
        return {
            "message": f"Documento '{safe_filename}' guardado en '{department}' exitosamente.",
            "filename": safe_filename,
            "department": department
        }
    except Exception as e:
        logger.error(f"Error al guardar documento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"No se pudo guardar el archivo: {str(e)}")


@router.delete("/api/documents/{department}/{filename}")
async def delete_document(department: str, filename: str):
    """Elimina un documento de la carpeta de un departamento."""
    if department not in DEPARTMENTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Departamento inválido.")

    safe_filename = Path(filename).name
    target_path = DOCUMENTS_DIR / department / safe_filename

    # Validar path traversal
    if not target_path.resolve().is_relative_to(DOCUMENTS_DIR.resolve()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ruta de archivo no válida.")

    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El archivo no existe.")

    try:
        os.remove(target_path)
        logger.info(f"🗑️ Documento eliminado: {target_path}")
        return {"message": f"Documento '{safe_filename}' eliminado correctamente.", "department": department, "filename": safe_filename}
    except Exception as e:
        logger.error(f"Error al eliminar documento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar archivo: {str(e)}")


@router.get("/health")
@router.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "NovaGPU Assistant API (FastAPI)", "departments_count": len(DEPARTMENTS)}

