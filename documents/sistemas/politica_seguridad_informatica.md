# Política de Ciberseguridad y Seguridad de la Información

**Código:** SYS-POL-2026-01  
**Responsable:** CISO / Equipo de Seguridad TI  

## 1. Autenticación y Control de Accesos
- Es obligatorio el uso de Autenticación de Múltiples Factores (**MFA/2FA**) con clave de seguridad hardware (YubiKey) o aplicación de autenticador para todos los servicios de la empresa.
- Gestión de contraseñas: Longitud mínima de 16 caracteres, renovadas cada 90 días o utilizando el gestor de contraseñas corporativo 1Password.

## 2. Política de Red y Acceso Remoto
- El acceso a los entornos de desarrollo, producción e infraestructura de nube en **Oracle Cloud Infrastructure (OCI)** solo está permitido a través de la VPN Corporativa con túnel cifrado IPsec / WireGuard.
- Queda estrictamente prohibido conectar dispositivos personales a la VLAN de Ingeniería sin autorización previa del SOC.
