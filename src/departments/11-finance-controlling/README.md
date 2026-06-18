# Departamento 11 — Finance & Controlling (SCM)
## Finanzas y Control de Gestión de Supply Chain

### Misión
Proporcionar visibilidad financiera completa de la cadena de suministro, optimizando
el capital de trabajo, controlando los costos logísticos y de inventario, y asegurando
que cada decisión de SC tenga una base cuantificada de valor.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Controlling de inventario | Valoración FIFO/Costo estándar, varianzas |
| Gestión de cuentas por pagar | DPO, exactitud de facturas, pagos |
| Cash-to-Cash cycle | Optimización DIO + DSO - DPO |
| Análisis de gasto SC | Costo total de la cadena / revenue |
| Presupuesto de SC | CAPEX (equipos) y OPEX (operación) |
| Costos de calidad (CoQ) | Prevención, evaluación, fallos internos/externos |
| Análisis TCO | Total Cost of Ownership por proveedor |

### KPIs financieros de supply chain
| KPI | Fórmula | Benchmark |
|-----|---------|-----------|
| **Cash-to-Cash Cycle Time** | DIO + DSO - DPO | < 30 días (best-in-class) |
| **DIO** (Days Inventory Outstanding) | 365 / Inventory Turnover | < 45 días FMCG |
| **DPO** (Days Payable Outstanding) | AP / (COGS/365) | 45-60 días |
| **DSO** (Days Sales Outstanding) | AR / (Revenue/365) | < 30 días |
| **SC Cost as % Revenue** | Total SC Cost / Revenue | < 10-12% |
| **Inventory Write-off %** | Write-offs / Avg Inventory | < 1% |
| **Procurement Savings %** | Ahorros negociados / Spend | ≥ 3-5% anual |
| **ROLA** (Return on Logistics Assets) | EBIT(SC) / Logistics Assets | > 15% |
| **CoQ %** | Total Cost of Quality / Revenue | < 3% (world-class) |

### Cash-to-Cash Cycle (Chopra & Meindl Ch.1)
```
C2C = DIO + DSO - DPO

Ejemplo best-in-class (Amazon ~C2C negativo):
  DIO = 25 días   (alta rotación)
  DSO = 10 días   (cobro rápido)
  DPO = 60 días   (pago tardío a proveedores)
  C2C = 25 + 10 - 60 = -25 días  → financiado por proveedores
```

### Cuentas contables GL implementadas
| Código | Cuenta | Tipo |
|--------|--------|------|
| 1300 | Inventario — Activo | Balance |
| 1310 | Mercancía en tránsito | Balance |
| 1320 | Trabajo en proceso (WIP) | Balance |
| 5000 | Costo de ventas (COGS) | P&L |
| 5100 | Varianza de inventario | P&L |
| 5200 | Merma y obsolescencia | P&L |

### Costos de calidad (CoQ) — Modelo Juran
```
CoQ = Costos de prevención + Costos de evaluación
    + Costos de fallos internos + Costos de fallos externos

Costos de prevención (más baratos):
  - Capacitación de proveedores
  - SPC y control de proceso
  - Ingeniería de calidad

Costos de fallos externos (más caros):
  - Devoluciones de clientes
  - Garantías
  - Pérdida de reputación
```

### Análisis TCO por proveedor
```
TCO = Precio × Volumen
    + Flete + Seguro + Derechos aduanales
    + Costo de calidad (PPM × costo de defecto)
    + Costo de inventario (safety stock × holding rate)
    + Costo de riesgo (HHI concentration × disruption probability)
    + Costo de gestión (personal procurement × tiempo)
```

### Archivos clave
- `domain/Invoice.ts` — Facturas de proveedor, validación y matching
- `domain/CostCenter.ts` — Centros de costo por departamento
- `domain/CashFlowMetrics.ts` — C2C, DIO, DPO, DSO en tiempo real
- `domain/InventoryValuation.ts` — FIFO, costo estándar, varianzas
- `domain/CostOfQuality.ts` — Modelo Juran de CoQ
- `domain/TCOAnalysis.ts` — Total Cost of Ownership
- `domain/Budget.ts` — Presupuesto y control presupuestal SC
- `services/SpendAnalysis.ts` — Análisis y consolidación de gasto
- `services/VarianceAnalysis.ts` — Varianzas precio, volumen, mezcla
- `reports/SCFinanceDashboard.ts` — Dashboard financiero ejecutivo

### Roles del departamento
- **SC Finance Director** — Estrategia financiera de la cadena
- **Cost Controller** — Análisis y control de costos logísticos
- **AP Specialist** — Cuentas por pagar a proveedores
- **Inventory Accountant** — Valoración y conciliación de inventarios
- **Spend Analyst** — Análisis de gasto y ahorros
- **Budget Analyst** — Presupuesto y forecast financiero

### Referencias
- Chopra & Meindl Ch.1 "Understanding Supply Chain Management"
- Ballou Ch.3 — Logistics cost measurement
- Juran, J.M. "Quality Control Handbook" — Cost of Quality model
- APICS CPIM 9.0 — Supply chain costing
- Gartner SCM Top 25 2026 — Financial metrics methodology (50% weight)
