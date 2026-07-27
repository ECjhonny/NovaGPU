/**
 * NovaGPU Assistant - Script principal del frontend
 * Maneja la interfaz de chat, comunicación con la API y estado de la UI.
 */

// ============================================================
//  Estado de la aplicación
// ============================================================
const state = {
    currentDepartment: null,
    isLoading: false,
    messageCount: 0,
};

// ============================================================
//  Elementos del DOM
// ============================================================
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const elements = {
    chatForm: $("#chat-form"),
    messageInput: $("#message-input"),
    btnSend: $("#btn-send"),
    messagesContainer: $("#messages"),
    chatContainer: $("#chat-container"),
    welcomeScreen: $("#welcome-screen"),
    sidebar: $("#sidebar"),
    btnMenu: $("#btn-menu"),
    btnClear: $("#btn-clear"),
    btnReindex: $("#btn-reindex"),
    btnDocs: $("#btn-docs"),
    toastContainer: $("#toast-container"),
    departmentTitle: $("#current-department-title"),
    // Modal elementos
    modalDocsBackdrop: $("#modal-docs-backdrop"),
    btnModalClose: $("#btn-modal-close"),
    btnModalReindex: $("#btn-modal-reindex"),
    uploadForm: $("#upload-form"),
    uploadDepartment: $("#upload-department"),
    dropZone: $("#drop-zone"),
    fileInput: $("#file-input"),
    filePreview: $("#file-preview"),
    selectedFileName: $("#selected-file-name"),
    btnRemoveFile: $("#btn-remove-file"),
    btnUpload: $("#btn-upload"),
    docsList: $("#docs-list"),
    totalDocsCount: $("#total-docs-count"),
};

// Variable para el archivo seleccionado
let selectedFile = null;

// ============================================================
//  Inicialización
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    initEventListeners();
    autoResizeTextarea();
});

function initEventListeners() {
    // Enviar mensaje
    elements.chatForm.addEventListener("submit", handleSubmit);

    // Input: habilitar/deshabilitar botón
    elements.messageInput.addEventListener("input", () => {
        elements.btnSend.disabled = !elements.messageInput.value.trim();
        autoResizeTextarea();
    });

    // Enter para enviar, Shift+Enter para nueva línea
    elements.messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (elements.messageInput.value.trim()) {
                elements.chatForm.dispatchEvent(new Event("submit"));
            }
        }
    });

    // Navegación de departamentos
    $$(".nav-item").forEach((item) => {
        item.addEventListener("click", () => {
            selectDepartment(item);
        });
    });

    // Quick actions
    $$(".quick-action").forEach((btn) => {
        btn.addEventListener("click", () => {
            const question = btn.dataset.question;
            elements.messageInput.value = question;
            elements.btnSend.disabled = false;
            elements.chatForm.dispatchEvent(new Event("submit"));
        });
    });

    // Sidebar toggle (mobile)
    elements.btnMenu.addEventListener("click", toggleSidebar);

    // Limpiar chat
    elements.btnClear.addEventListener("click", clearChat);

    // Re-indexar documentos
    elements.btnReindex.addEventListener("click", reindexDocuments);

    // Modal de Gestión de Documentos
    elements.btnDocs.addEventListener("click", openDocsModal);
    elements.btnModalClose.addEventListener("click", closeDocsModal);
    elements.modalDocsBackdrop.addEventListener("click", (e) => {
        if (e.target === elements.modalDocsBackdrop) closeDocsModal();
    });
    elements.btnModalReindex.addEventListener("click", () => {
        reindexDocuments();
        fetchDocuments();
    });

    // Subida de archivos
    initUploadEvents();
}


// ============================================================
//  Chat
// ============================================================
async function handleSubmit(e) {
    e.preventDefault();

    const message = elements.messageInput.value.trim();
    if (!message || state.isLoading) return;

    // Ocultar pantalla de bienvenida
    if (elements.welcomeScreen) {
        elements.welcomeScreen.classList.add("hidden");
    }

    // Agregar mensaje del usuario
    addMessage("user", message);
    elements.messageInput.value = "";
    elements.btnSend.disabled = true;
    autoResizeTextarea();

    // Mostrar indicador de escritura
    const typingId = showTypingIndicator();
    state.isLoading = true;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                department: state.currentDepartment,
            }),
        });

        const data = await response.json();

        // Remover indicador de escritura
        removeTypingIndicator(typingId);

        if (response.ok) {
            addMessage("assistant", data.response, data.sources);
        } else {
            addMessage(
                "assistant",
                data.error || "Ocurrió un error al procesar tu mensaje."
            );
            showToast("Error al obtener respuesta", "error");
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage(
            "assistant",
            "No se pudo conectar con el servidor. Verifica que la aplicación esté ejecutándose."
        );
        showToast("Error de conexión", "error");
    } finally {
        state.isLoading = false;
    }
}

function addMessage(role, content, sources = []) {
    state.messageCount++;
    const id = `msg-${state.messageCount}`;

    const messageEl = document.createElement("div");
    messageEl.className = `message ${role}`;
    messageEl.id = id;

    const avatarEmoji = role === "assistant" ? "⚡" : "👤";
    const formattedContent = role === "assistant" ? formatMarkdown(content) : escapeHTML(content);

    let sourcesHTML = "";
    if (sources && sources.length > 0) {
        const tags = sources
            .map(
                (s) =>
                    `<span class="source-tag">📁 ${capitalize(s.department)} · ${s.file}</span>`
            )
            .join("");
        sourcesHTML = `
            <div class="message-sources">
                <div class="sources-title">Fuentes consultadas</div>
                ${tags}
            </div>`;
    }

    messageEl.innerHTML = `
        <div class="message-avatar">${avatarEmoji}</div>
        <div class="message-content">
            <div class="message-bubble">${formattedContent}</div>
            ${sourcesHTML}
        </div>`;

    elements.messagesContainer.appendChild(messageEl);
    scrollToBottom();
}

function showTypingIndicator() {
    const id = `typing-${Date.now()}`;
    const el = document.createElement("div");
    el.className = "message assistant";
    el.id = id;
    el.innerHTML = `
        <div class="message-avatar">⚡</div>
        <div class="message-content">
            <div class="message-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>`;

    elements.messagesContainer.appendChild(el);
    scrollToBottom();
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// ============================================================
//  Departamentos
// ============================================================
function selectDepartment(item) {
    // Actualizar estado activo
    $$(".nav-item").forEach((el) => el.classList.remove("active"));
    item.classList.add("active");

    const dept = item.dataset.department;
    state.currentDepartment = dept || null;

    // Actualizar título
    const deptNames = {
        "": "NovaGPU Assistant",
        rrhh: "Recursos Humanos",
        finanzas: "Finanzas",
        operaciones: "Operaciones",
        legal: "Legal",
        marketing: "Marketing",
        calidad: "Calidad",
        sistemas: "Sistemas",
        estrategia: "Estratégico",
        investigacion: "Investigación y D.",
        comunicacion: "Comunicación Interna",
    };
    elements.departmentTitle.textContent = deptNames[dept] || "NovaGPU Assistant";

    // Cerrar sidebar en mobile
    closeSidebar();

    showToast(
        dept
            ? `Filtrado por: ${deptNames[dept]}`
            : "Mostrando todos los departamentos",
        "info"
    );
}

// ============================================================
//  Acciones
// ============================================================
async function clearChat() {
    try {
        await fetch("/api/clear", { method: "POST" });
        elements.messagesContainer.innerHTML = "";
        elements.welcomeScreen.classList.remove("hidden");
        state.messageCount = 0;
        showToast("Conversación limpiada", "success");
    } catch (error) {
        showToast("Error al limpiar la conversación", "error");
    }
}

async function reindexDocuments() {
    if (state.isLoading) return;
    state.isLoading = true;

    showToast("Indexando documentos... esto puede tardar unos momentos", "info");

    try {
        const response = await fetch("/api/index", { method: "POST" });
        const data = await response.json();

        if (response.ok) {
            showToast(data.message || "Documentos indexados", "success");
        } else {
            showToast(data.error || "Error en la indexación", "error");
        }
    } catch (error) {
        showToast("Error de conexión al indexar", "error");
    } finally {
        state.isLoading = false;
    }
}

// ============================================================
//  Sidebar (Mobile)
// ============================================================
function toggleSidebar() {
    elements.sidebar.classList.toggle("open");
    toggleOverlay();
}

function closeSidebar() {
    elements.sidebar.classList.remove("open");
    removeOverlay();
}

function toggleOverlay() {
    let overlay = $(".sidebar-overlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.className = "sidebar-overlay active";
        overlay.addEventListener("click", closeSidebar);
        document.body.appendChild(overlay);
    } else {
        overlay.classList.toggle("active");
    }
}

function removeOverlay() {
    const overlay = $(".sidebar-overlay");
    if (overlay) overlay.classList.remove("active");
}

// ============================================================
//  Utilidades
// ============================================================
function scrollToBottom() {
    requestAnimationFrame(() => {
        elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
    });
}

function autoResizeTextarea() {
    const textarea = elements.messageInput;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + "px";
}

function escapeHTML(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function formatMarkdown(text) {
    if (!text) return "";

    let html = escapeHTML(text);

    // Bloques de código
    html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
    // Código inline
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Listas no ordenadas (procesar ANTES de los asteriscos inline)
    html = html.replace(/^[\s]*[-*]\s+(.+)$/gm, "<li>$1</li>");
    // Listas ordenadas
    html = html.replace(/^[\s]*\d+\.\s+(.+)$/gm, "<li>$1</li>");

    // Negritas (doble asterisco)
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    // Asteriscos simples o guiones bajos dentro de la misma línea -> convertir a negrita (NUNCA cursiva)
    html = html.replace(/\*([^\n*]+)\*/g, "<strong>$1</strong>");
    html = html.replace(/_([^\n_]+)_/g, "<strong>$1</strong>");

    // Encabezados
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

    // Agrupar elementos <li> consecutivos en <ul>
    html = html.replace(/(<li>[\s\S]*?<\/li>)/g, function(match) {
        return "<ul>" + match + "</ul>";
    });
    // Limpiar uls anidados consecutivos
    html = html.replace(/<\/ul>\s*<ul>/g, "");

    // Saltos de línea
    html = html.replace(/\n\n/g, "</p><p>");
    html = html.replace(/\n/g, "<br>");

    // Envolver en párrafos si no empieza con un tag de bloque
    if (!html.startsWith("<")) {
        html = `<p>${html}</p>`;
    }

    return html;
}

function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// ============================================================
//  Toast Notifications
// ============================================================
function showToast(message, type = "info", duration = 4000) {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    const icons = {
        success: "✅",
        error: "❌",
        info: "ℹ️",
        warning: "⚠️",
    };

    toast.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${message}</span>`;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = "toastOut 0.3s ease-in forwards";
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================================
//  Gestión de Documentos Modal & Upload
// ============================================================
function openDocsModal() {
    elements.modalDocsBackdrop.classList.add("active");
    fetchDocuments();
    closeSidebar();
}

function closeDocsModal() {
    elements.modalDocsBackdrop.classList.remove("active");
    resetUploadForm();
}

function initUploadEvents() {
    // Click en dropzone para seleccionar archivo
    elements.dropZone.addEventListener("click", () => elements.fileInput.click());

    // Cambio en input file
    elements.fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelected(e.target.files[0]);
        }
    });

    // Drag and drop events
    ["dragenter", "dragover"].forEach((eventName) => {
        elements.dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            elements.dropZone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        elements.dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            elements.dropZone.classList.remove("dragover");
        });
    });

    elements.dropZone.addEventListener("drop", (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelected(e.dataTransfer.files[0]);
        }
    });

    // Quitar archivo seleccionado
    elements.btnRemoveFile.addEventListener("click", resetUploadForm);

    // Form submit upload
    elements.uploadForm.addEventListener("submit", handleUploadSubmit);
}

function handleFileSelected(file) {
    const allowed = [".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx", ".json", ".html", ".pptx"];
    const ext = "." + file.name.split(".").pop().toLowerCase();
    
    if (!allowed.includes(ext)) {
        showToast(`Extensión no permitida. Formatos soportados: ${allowed.join(", ")}`, "error");
        return;
    }

    selectedFile = file;
    elements.selectedFileName.textContent = `${file.name} (${formatBytes(file.size)})`;
    elements.filePreview.classList.remove("hidden");
    elements.dropZone.classList.add("hidden");
    elements.btnUpload.disabled = false;
}

function resetUploadForm() {
    selectedFile = null;
    elements.fileInput.value = "";
    elements.filePreview.classList.add("hidden");
    elements.dropZone.classList.remove("hidden");
    elements.btnUpload.disabled = true;
}

async function handleUploadSubmit(e) {
    e.preventDefault();
    if (!selectedFile) return;

    const department = elements.uploadDepartment.value;
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("department", department);

    elements.btnUpload.disabled = true;
    elements.btnUpload.querySelector("span").textContent = "⏳";

    try {
        const response = await fetch("/api/documents/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            showToast(data.message || "Documento subido con éxito", "success");
            resetUploadForm();
            fetchDocuments();
        } else {
            showToast(data.detail || "Error al subir el documento", "error");
        }
    } catch (error) {
        showToast("Error de conexión al subir documento", "error");
    } finally {
        elements.btnUpload.querySelector("span").textContent = "⬆️";
    }
}

async function fetchDocuments() {
    elements.docsList.innerHTML = `<div class="docs-loading">Cargando documentos...</div>`;
    
    try {
        const response = await fetch("/api/documents");
        const data = await response.json();

        if (!response.ok) {
            elements.docsList.innerHTML = `<div class="docs-empty">Error al cargar la lista de documentos.</div>`;
            return;
        }

        renderDocumentsList(data.departments);
    } catch (error) {
        elements.docsList.innerHTML = `<div class="docs-empty">Error de conexión al obtener documentos.</div>`;
    }
}

function renderDocumentsList(departments) {
    let totalCount = 0;
    let html = "";

    const deptIcons = {
        rrhh: "👥",
        finanzas: "💰",
        operaciones: "⚙️",
        marketing: "📢"
    };

    const deptNames = {
        rrhh: "Recursos Humanos",
        finanzas: "Finanzas",
        operaciones: "Operaciones",
        marketing: "Marketing"
    };

    departments.forEach((d) => {
        totalCount += d.count;
        if (d.files.length === 0) return;

        const filesHTML = d.files
            .map(
                (f) => `
            <div class="doc-item">
                <div class="doc-info">
                    <span>📄</span>
                    <span class="doc-name" title="${escapeHTML(f.name)}">${escapeHTML(f.name)}</span>
                    <span class="doc-size">(${formatBytes(f.size)})</span>
                </div>
                <button class="btn-delete-doc" onclick="confirmDeleteDoc('${escapeHTML(d.department)}', '${escapeHTML(f.name)}')" title="Eliminar documento">
                    🗑️
                </button>
            </div>`
            )
            .join("");

        html += `
            <div class="docs-dept-group">
                <div class="docs-dept-header">
                    <span>${deptIcons[d.department] || "📁"} ${deptNames[d.department] || capitalize(d.department)}</span>
                    <span>${d.count} archivo(s)</span>
                </div>
                <div class="docs-dept-files">
                    ${filesHTML}
                </div>
            </div>`;
    });

    elements.totalDocsCount.textContent = `${totalCount} documento(s)`;

    if (totalCount === 0) {
        elements.docsList.innerHTML = `<div class="docs-empty">No hay documentos cargados en el sistema.</div>`;
    } else {
        elements.docsList.innerHTML = html;
    }
}

async function confirmDeleteDoc(department, filename) {
    if (!confirm(`¿Estás seguro de que deseas eliminar '${filename}' de ${department}?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/documents/${department}/${encodeURIComponent(filename)}`, {
            method: "DELETE",
        });

        const data = await response.json();

        if (response.ok) {
            showToast(data.message || "Documento eliminado", "success");
            fetchDocuments();
        } else {
            showToast(data.detail || "Error al eliminar documento", "error");
        }
    } catch (error) {
        showToast("Error de conexión al eliminar documento", "error");
    }
}

function formatBytes(bytes, decimals = 1) {
    if (!bytes || bytes === 0) return "0 Bytes";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

