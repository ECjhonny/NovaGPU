# 🚀 NovaGPU Assistant - Agente Corporativo de IA Multi-Proveedor (FastAPI + RAG)

**Asistente Virtual Corporativo Inteligente para NovaGPU Technologies**  
*Desarrollado para el Challenge de Inteligencia Artificial de Alura Latam.*

---

## 📋 Descripción General

**NovaGPU Assistant** es un agente de Inteligencia Artificial abierto a todos los colaboradores de **NovaGPU Technologies**, una empresa ficticia dedicada al diseño y fabricación de tarjetas gráficas (GPUs) de alto rendimiento para gaming, estaciones de trabajo y supercómputo de Inteligencia Artificial.

El asistente funciona como una **base de conocimiento conversacional centralizada**, respondiendo preguntas en tiempo real mediante técnicas de **RAG (Retrieval-Augmented Generation)** procesando la documentación oficial de la organización.

---

## ⚡ Tecnologías Principales

- **Backend Web**: FastAPI (Python 3.10+) & Uvicorn Server
- **Inferencia LLM (Multi-proveedor con Fallback)**:
  - 🥇 **Cohere**: `command-r-plus` (Proveedor principal)
  - 🥈 **Google Gemini**: `gemini-2.0-flash`
  - 🥉 **Groq**: `llama-3.3-70b-versatile`
- **Embeddings Vectoriales (Multi-proveedor con Fallback)**:
  - 🧠 **Voyage AI**: `voyage-3-lite`
  - 🧠 **Cohere**: `embed-multilingual-v3.0`
  - 🧠 **Google Gemini**: `gemini-embedding-2`
- **Vector Database**: ChromaDB (Base de datos vectorial persistente con autorecreación ante cambios de dimensión)
- **Orquestación RAG**: LangChain 0.3 (`langchain-cohere`, `langchain-google-genai`, `langchain-groq`, `langchain-voyageai`)
- **Frontend**: HTML5, Vanilla CSS3 (Dark Theme corporativo) & JavaScript ES6+

---

## 📄 Cobertura de Formatos y Categorías de Documentos

El agente comprende y procesa automáticamente 8+ formatos de archivo en 10 áreas clave de la organización:

### 📁 Formatos de Archivo Soportados
- **PDF** (`.pdf`) — Manuales de calidad y políticas
- **Word** (`.docx`) — Procedimientos y contratos
- **Excel** (`.xlsx`) — Estados financieros y presupuestos
- **PowerPoint** (`.pptx`) — Presentaciones de roadmap
- **Markdown** (`.md`) — Documentación técnica, políticas y minutas
- **CSV** (`.csv`) — Organigramas, estados de resultados y catálogo de precios
- **JSON** (`.json`) — Especificación de APIs internas y telemetría
- **HTML** (`.html`) — Newsletters internas y planes de beneficios

### 🏢 Dominios Organizacionales (10 Categorías)
1. **Recursos Humanos (`rrhh`)**: Políticas de vacaciones, onboarding, beneficios (HTML) y estructura organizacional (CSV).
2. **Financiero y Contable (`finanzas`)**: Estados de resultados Q2 (CSV), presupuesto anual y política de reembolsos.
3. **Operacional (`operaciones`)**: Procesos de manufactura de GPUs, control de calidad en línea y logística.
4. **Legal y Compliance (`legal`)**: Términos de garantía, políticas GDPR/LFPDPPP y código de ética.
5. **Marketing y Comercial (`marketing`)**: Catálogo de GPUs (CSV), precios MSRP, manual de marca y pitch deck.
6. **Calidad (`calidad`)**: Plan de auditorías ISO 9001:2015, plan CAPA y estándares de producto.
7. **Datos y Sistemas (`sistemas`)**: API interna (JSON), ciberseguridad y manual de nube OCI.
8. **Estratégico (`estrategia`)**: Plan estratégico 2026-2028 y roadmap tecnológico de GPUs.
9. **Investigación y Desarrollo (`investigacion`)**: Estudio de mercado de GPUs y business case Nova Quantum V2.
10. **Comunicación Interna (`comunicacion`)**: Comunicados ejecutivos, boletín mensual (HTML) y minutas de dirección.

---

## 🛠️ Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone git@github.com:ECjhonny/NovaGPU.git
cd NovaGPU-Assistant
```

### 2. Crear y activar el entorno virtual
```bash
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\activate
# Linux / Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (`.env`)
Copia el archivo `.env.example` a `.env`:
```bash
cp .env.example .env
```

Edita `.env` e ingresa tus claves de API y preferencia de proveedores:
```env
# --- Selección de Proveedores ---
LLM_PROVIDER=cohere          # Opciones: cohere, gemini, groq
EMBEDDINGS_PROVIDER=voyage   # Opciones: voyage, cohere, gemini

# --- API Keys & Modelos LLM / Embeddings ---
COHERE_API_KEY=tu_clave_cohere_aqui
COHERE_MODEL=command-r-plus
COHERE_EMBEDDING_MODEL=embed-multilingual-v3.0

GEMINI_API_KEY=tu_clave_gemini_aqui
GEMINI_MODEL=gemini-2.0-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-2

GROQ_API_KEY=gsk_tu_clave_groq_aqui
GROQ_MODEL=llama-3.3-70b-versatile

VOYAGE_API_KEY=pa-tu_clave_voyage_aqui
VOYAGE_EMBEDDING_MODEL=voyage-3-lite
```

### 5. Ejecutar la aplicación FastAPI con Uvicorn
```bash
# Opción 1: Mediante el ejecutable
python run.py

# Opción 2: Usando Uvicorn directamente
uvicorn app.main:app --reload --port 8000
```

Accede desde tu navegador:
- **Interfaz del Chat**: [http://localhost:8000](http://localhost:8000)
- **Documentación Interactiva Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🤖 Modelos de LLM y Embeddings Soportados

| Proveedor | Tipo | Modelo por Defecto | Variable `.env` |
| :--- | :--- | :--- | :--- |
| **Cohere** | LLM | `command-r-plus` | `COHERE_API_KEY` |
| **Cohere** | Embeddings | `embed-multilingual-v3.0` | `COHERE_API_KEY` |
| **Google Gemini** | LLM | `gemini-2.0-flash` | `GEMINI_API_KEY` |
| **Google Gemini** | Embeddings | `gemini-embedding-2` | `GEMINI_API_KEY` |
| **Groq** | LLM | `llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| **Voyage AI** | Embeddings | `voyage-3-lite` | `VOYAGE_API_KEY` |

> 🛡️ **Sistema de Fallback Automático**: Si el proveedor seleccionado en `LLM_PROVIDER` o `EMBEDDINGS_PROVIDER` no cuenta con API Key configurada o falla, el sistema conmuta automáticamente al siguiente proveedor disponible sin interrumpir el servicio.

---

## ☁️ Despliegue en Oracle Cloud Infrastructure (OCI)

El proyecto está listo para su hospedaje y despliegue en la nube de **Oracle Cloud Infrastructure (OCI)**.

1. **Creación de Compute Instance:** Crear una máquina virtual en OCI (Ubuntu 22.04 LTS u Oracle Linux).
2. **Security List:** Habilitar el puerto `8000` (o `80` mediante proxy Nginx) en la VCN de OCI.
3. **Clonar e Iniciar:** Seguir los pasos de instalación local en el servidor OCI y ejecutar mediante `systemd` para servicio continuo 24/7.

---

## 📝 Licencia

Proyecto desarrollado para el desafío de Inteligencia Artificial de **Alura Latam**.
© 2026 NovaGPU Technologies. Todos los derechos reservados.
