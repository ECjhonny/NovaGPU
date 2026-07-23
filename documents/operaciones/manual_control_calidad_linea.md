# Manual de Control de Calidad en Línea de Producción (QC-Line)

**Código:** OP-MAN-QC-01  

## Puntos de Control Obligatorios (Quality Gates)

### Gate 1: Inspección Óptica Automatizada (AOI)
- Verificación del 100% de las soldaduras SMD tras el horno de reflujo.
- Cero tolerancia a cortocircuitos o componentes desplazados más de 0.05 mm.

### Gate 2: Prueba Eléctrica y Frecuencia de Reloj
- Medición de impedancias en rieles de voltaje (VCORE, VMEM, PEX_12V).
- Comprobación de booting de BIOS y handshake PCI Express 5.0 x16.

### Gate 3: Test Térmico y Acústico
- Temperatura máxima permitida en Hotspot durante FurMark (30 min): **82°C**.
- Nivel de ruido máximo permitido a 1 metro: **34 dBA**.
- Ausencia total de ruido eléctrico indeseado (Coil Whine severo causa rechazo inmediato).
