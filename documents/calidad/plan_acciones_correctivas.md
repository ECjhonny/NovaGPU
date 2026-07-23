# Plan de Acciones Correctivas y Preventivas (CAPA)

**Código:** CAL-CAPA-2026-04  

## Registro de Incidencias y Soluciones Abiertas

### CAPA-2026-012: Desprendimiento sutil de pad térmico en VRAM Nova Phoenix 8000
- **Causa Raíz:** Presión insuficiente del brazo robotizado en estación #4 de SMT durante el ensamblaje de la placa trasera.
- **Acción Correctiva:** Recalibración del sensor de torque óptico a 0.55 Nm y cambio del proveedor de almohadillas térmicas a Gelid Ultimate 15 W/mK.
- **Estado:** Cerrada exitosamente con verificación del 100% de lotes posteriores.

### CAPA-2026-015: Parpadeo esporádico con DisplayPort 2.1 a 240Hz
- **Causa Raíz:** Bug en el firmware de la controladora DisplayPort bajo estados de ahorro de energía ultrabajos.
- **Acción Correctiva:** Actualización del VBIOS v1.04 distribuido mediante NovaControl Software.
- **Estado:** Implementada y verificada.
