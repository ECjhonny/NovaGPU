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
- **Inferencia LLM (Multi-proveedor con Fallback automático por Rate Limit)**:
  - 🥇 **Groq**: `llama-3.3-70b-versatile`
  - 🥈 **Cohere**: `command-a-plus-05-2026`
  - 🥉 **Google Gemini**: `gemini-3.5-flash-lite`
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

> ⚠️ **Importante:** No uses comentarios en la misma línea que un valor (e.g. `LLM_PROVIDER=groq # comentario`). Esto causa errores cuando se ejecuta con `systemd` en servidores Linux.

```env
# --- Selección de Proveedores ---
# Opciones LLM: groq, cohere, gemini
# Opciones Embeddings: voyage, cohere, gemini
LLM_PROVIDER=groq
EMBEDDINGS_PROVIDER=voyage

# --- Cohere (LLM & Embeddings) ---
COHERE_API_KEY=tu_clave_cohere_aqui
COHERE_MODEL=command-a-plus-05-2026
COHERE_EMBEDDING_MODEL=embed-multilingual-v3.0

# --- Gemini (LLM & Embeddings - Fallback) ---
GEMINI_API_KEY=tu_clave_gemini_aqui
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-2

# --- Groq (LLM) ---
GROQ_API_KEY=gsk_tu_clave_groq_aqui
GROQ_MODEL=llama-3.3-70b-versatile

# --- Voyage AI (Embeddings) ---
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
| **Groq** | LLM | `llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| **Cohere** | LLM | `command-a-plus-05-2026` | `COHERE_API_KEY` |
| **Cohere** | Embeddings | `embed-multilingual-v3.0` | `COHERE_API_KEY` |
| **Google Gemini** | LLM | `gemini-3.5-flash-lite` | `GEMINI_API_KEY` |
| **Google Gemini** | Embeddings | `gemini-embedding-2` | `GEMINI_API_KEY` |
| **Voyage AI** | Embeddings | `voyage-3-lite` | `VOYAGE_API_KEY` |

> 🛡️ **Sistema de Fallback Automático con Detección de Rate Limit**: Si un proveedor LLM alcanza su límite de consultas (HTTP 429 / Rate Limit), el sistema conmuta **automáticamente** al siguiente proveedor disponible sin interrumpir el servicio. Para embeddings, se implementan reintentos automáticos con backoff exponencial.

---

## ☁️ Despliegue en Oracle Cloud Infrastructure (OCI)

El proyecto está desplegado y probado en la nube de **Oracle Cloud Infrastructure (OCI)** con Oracle Linux.

### 1. Crear Compute Instance
Crear una máquina virtual en OCI con **Oracle Linux 8/9** o **Ubuntu 22.04 LTS**.

### 2. Configurar Security List (Red)
En la consola de OCI → **Networking** → **VCN** → **Security List**, agregar regla de ingreso:
- **Source CIDR**: `0.0.0.0/0` | **Protocol**: TCP | **Port**: `80, 8000`

### 3. Abrir puertos en el firewall del OS y deshabilitar Apache
```bash
# Oracle Linux: Abrir puertos en firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Detener y deshabilitar Apache (viene activo por defecto en Oracle Linux y ocupa el puerto 80)
sudo systemctl stop httpd
sudo systemctl disable httpd
```

### 4. Instalar dependencias y clonar
```bash
sudo dnf install -y python3 python3-pip git nginx
git clone https://github.com/ECjhonny/NovaGPU.git NovaGPU
cd NovaGPU
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
cp .env.example .env && nano .env   # Configurar API Keys
```

### 5. Configurar servicio systemd (ejecución 24/7)

> ⚠️ **Importante:** ChromaDB usa SQLite internamente, que no soporta accesos concurrentes. Se debe usar `--workers 1` para evitar errores de colección no encontrada.

```bash
sudo nano /etc/systemd/system/novagpu.service
```
```ini
[Unit]
Description=Servicio NovaGPU Assistant (FastAPI)
After=network.target

[Service]
User=opc
WorkingDirectory=/home/opc/NovaGPU
ExecStart=/home/opc/NovaGPU/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=5
EnvironmentFile=/etc/novagpu.env

[Install]
WantedBy=multi-user.target
```
```bash
sudo cp /home/opc/NovaGPU/.env /etc/novagpu.env
sudo systemctl daemon-reload
sudo systemctl enable novagpu
sudo systemctl start novagpu
```

### 6. Configurar Nginx como Reverse Proxy

En Oracle Linux, la configuración de Nginx se gestiona desde `/etc/nginx/conf.d/`.

```bash
# Habilitar SELinux para permitir que Nginx haga proxy a FastAPI
sudo setsebool -P httpd_can_network_connect 1

# Crear archivo de configuración
sudo nano /etc/nginx/conf.d/novagpu.conf
```
```nginx
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
```bash
# Comentar el bloque server por defecto en nginx.conf para evitar conflictos (si existe)
# sudo nano /etc/nginx/nginx.conf → comentar el bloque "server { listen 80; ... }"

sudo nginx -t && sudo systemctl enable nginx && sudo systemctl restart nginx
```

### 7. Verificar
- **Chat**: `http://<IP_PUBLICA_OCI>`
- **Swagger**: `http://<IP_PUBLICA_OCI>/docs`
- **Logs en tiempo real**: `sudo journalctl -u novagpu -f`

---

## 📝 Licencia

Proyecto desarrollado para el desafío de Inteligencia Artificial de **Alura Latam**.
© 2026 NovaGPU Technologies. Todos los derechos reservados.
