# Departamento 13 — Order Management & Customer Service
## Gestión de Pedidos y Servicio al Cliente

### Misión
Gestionar el ciclo completo Order-to-Cash (O2C) asegurando que cada pedido del
cliente sea procesado con precisión, cumplido en tiempo y forma, y que cualquier
incidencia se resuelva proactivamente preservando la relación comercial.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Captura y validación de pedidos | EDI, portal, email, API |
| Verificación de disponibilidad | ATP (Available-to-Promise) en tiempo real |
| Coordinación de cumplimiento | Interface con warehouse y logistics |
| Gestión de backorders | Promesas de entrega, comunicación cliente |
| Customer master data | Datos de cliente, contratos, condiciones |
| Returns & claims (RMA) | Proceso de devoluciones y créditos |
| KPI de servicio al cliente | OTIF, Perfect Order Rate |

### KPIs del departamento
| KPI | Fórmula | Benchmark |
|-----|---------|-----------|
| **OTIF** (On-Time In-Full) | (Pedidos OTIF / Total pedidos) × 100 | ≥ 98% (Walmart: 98%) |
| **Perfect Order Rate** | Tiempo × Cantidad × Calidad × Documentos | ≥ 95% |
| Order Accuracy Rate | Pedidos sin error / Total | ≥ 99.5% |
| Order Cycle Time | Hora pedido → Hora entrega | Varía por canal |
| Backorder Rate | Líneas en backorder / Total líneas | < 2% |
| CSAT (Customer Satisfaction) | Encuesta post-entrega | ≥ 90% |
| First Contact Resolution | Incidencias resueltas en 1er contacto | ≥ 80% |
| Claims Processing Time | Días para resolver reclamación | < 5 días hábiles |

### Ciclo Order-to-Cash (O2C)
```
Recepción pedido (EDI ORDERS / API)
  ↓ Validación: cliente activo, precio, condiciones
  ↓ ATP check: stock disponible o fecha disponible
  ↓ Confirmación al cliente (Order Acknowledgement)
  ↓ Picking + Packing (WMS)
  ↓ Despacho + ASN (EDI DESADV)
  ↓ Entrega + POD
  ↓ Facturación (EDI INVOIC)
  ↓ Cobro → Cierre O2C
```

### ATP — Available to Promise
```
ATP = Stock disponible
    + Recepciones comprometidas (POs confirmados)
    - Reservas existentes (pedidos en proceso)
    - Safety stock mínimo

Cálculo por horizonte temporal (daily buckets)
```

### Perfect Order Rate (POR)
```
POR = OTD% × In-Full% × Damage-Free% × Invoice-Accuracy%

Ejemplo: 97% × 99% × 99.5% × 99% = 94.6%
```
> Cada 1% de mejora en POR puede generar 2-5% de aumento en satisfacción del cliente

### EDI — Mensajes implementados
| Mensaje UN/EDIFACT | Función |
|-------------------|---------|
| ORDERS | Pedido de compra del cliente |
| ORDRSP | Confirmación / modificación del pedido |
| DESADV | Aviso de despacho (ASN) |
| RECADV | Confirmación de recepción |
| INVOIC | Factura comercial |
| REMADV | Aviso de pago |

### Archivos clave
- `domain/SalesOrder.ts` — Pedido de venta con líneas y ATP
- `domain/OrderFulfillment.ts` — Asignación, picking, despacho
- `domain/CustomerMaster.ts` — Datos maestros de cliente
- `domain/RMARequest.ts` — Return Merchandise Authorization
- `domain/BackorderRecord.ts` — Seguimiento de backorders
- `services/ATPService.ts` — Cálculo de disponibilidad en tiempo real
- `services/OrderOrchestrator.ts` — Orquestación O2C
- `services/EDIProcessor.ts` — Procesamiento de mensajes EDI

### Roles del departamento
- **Order Management Manager** — Estrategia O2C y KPIs
- **Customer Service Representative** — Contacto directo con clientes
- **Order Analyst** — Validación y procesamiento
- **Backorder Coordinator** — Gestión de pedidos pendientes
- **EDI Specialist** — Integración electrónica de pedidos

### Referencias
- Chopra & Meindl Ch.3 "Customer Value in Supply Chains"
- APICS CPIM 9.0 — Order Management
- GS1 UN/EDIFACT messaging standards
- Walmart OTIF Policy (2018) — Benchmark de la industria
