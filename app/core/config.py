"""
Configuración central de la aplicación NovaGPU Assistant.
Carga variables de entorno y define constantes del proyecto.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- Rutas del proyecto ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTS_DIR = BASE_DIR / "documents"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# --- Selección de Proveedores ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()
EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER", "voyage").lower()

# --- Configuración de OpenRouter (LLM & Embeddings) ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
OPENROUTER_EMBEDDING_MODEL = os.getenv("OPENROUTER_EMBEDDING_MODEL", "nvidia/nemotron-3-embed-1b:free")

# --- Configuración de Groq (LLM) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# --- Configuración de Cohere (LLM & Embeddings) ---
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-a-plus-05-2026")
COHERE_EMBEDDING_MODEL = os.getenv("COHERE_EMBEDDING_MODEL", "embed-multilingual-v3.0")

# --- Configuración de Voyage AI (Embeddings) ---
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY", "")
VOYAGE_EMBEDDING_MODEL = os.getenv("VOYAGE_EMBEDDING_MODEL", "voyage-3-lite")

# --- Configuración del servidor FastAPI ---
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# --- Configuración de Gemini (LLM & Embeddings) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")

# --- Configuración de RAG ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

# --- Departamentos disponibles ---
DEPARTMENTS = [
    "rrhh",
    "finanzas",
    "operaciones",
    "marketing",
]

# --- Extensiones de documentos soportadas ---
SUPPORTED_EXTENSIONS = [
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".csv",
    ".xlsx",
    ".json",
    ".html",
    ".pptx",
]

# --- Nombre de la colección de ChromaDB ---
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "novagpu_docs")
