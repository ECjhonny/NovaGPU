# Manual de Infraestructura y Despliegue en Cloud (OCI / Oracle Cloud Infrastructure)

**Código:** SYS-INF-2026-03  

## 1. Arquitectura Cloud de NovaGPU Technologies
Nuestra infraestructura principal se hospeda en **Oracle Cloud Infrastructure (OCI)** en la región Ashburn / Sao Paulo por su excelente relación costo-beneficio y soporte de instancias GPU nativas.

### Componentes Principales en OCI:
- **OCI Compute Instances:** Instancias `VM.GPU.A10.1` y `VM.Standard.E4.Flex` para alojar los microservicios de la plataforma y el agente RAG.
- **OCI Object Storage:** Almacenamiento seguro en la nube de imágenes de BIOS, backups de bases de datos y datasets de entrenamiento.
- **OCI Virtual Cloud Network (VCN):** Red privada virtual con Subnets Públicas/Privadas, Internet Gateway y Security Lists estrictas.
- **OCI Autonomous Database / Vector Database:** Base de datos gestionada para almacenamiento de metadatos de telemetría.

## 2. Guía de Despliegue del Agente NovaGPU Assistant en OCI
1. **Creación de Instancia:** Crear Compute Instance en OCI (Ubuntu 22.04 LTS / Oracle Linux 9).
2. **Ingress Rules:** Abrir puerto `5000` (o `80/443` con Reverse Proxy Nginx) en la Security List de la VCN y en iptables/firewalld.
3. **Despliegue del Código:**
   ```bash
   git clone https://github.com/tu-usuario/NovaGPU-Assistant.git
   cd NovaGPU-Assistant
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env # Configurar OPENAI_API_KEY
   python3 run.py
   ```
4. **Demonización:** Configurar `systemd` servicio `novagpu-assistant.service` para ejecución continua 24/7.
