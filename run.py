"""
Punto de entrada para ejecutar la aplicación NovaGPU Assistant con Uvicorn (FastAPI).
"""

import io
import sys
import uvicorn
from app.core.config import HOST, PORT, DEBUG

# Asegurar codificación UTF-8 en la consola de Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🚀 NovaGPU Assistant - Asistente IA (FastAPI + Groq + RAG)")
    print("=" * 60)
    print(f"  📍 Servidor: http://localhost:{PORT}")
    print(f"  📖 Documentación Swagger: http://localhost:{PORT}/docs")
    print(f"  🔧 Debug / Reload: {DEBUG}")
    print("=" * 60 + "\n")

    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )
