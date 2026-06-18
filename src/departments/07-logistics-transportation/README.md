# Departamento 07 — Logistics & Transportation (TMS)
## Logística y Transporte

### Misión
Diseñar y ejecutar la red de transporte más eficiente que entregue los productos
correctos en el lugar, tiempo y condiciones acordadas, al menor costo total,
cumpliendo con todas las regulaciones aduaneras y de comercio internacional.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Gestión de transportistas | Selección, contratos, KPI de carriers |
| Optimización de rutas | VRP (Vehicle Routing Problem), multi-parada |
| Coordinación de carga | FTL, LTL, FCL, LCL, aérea, courier |
| Gestión aduanal | Documentación, HS codes, DUA/pedimento |
| Seguimiento en tiempo real | Track & trace, eventos de shipment |
| Logística inversa | Devoluciones, reclamaciones, disposal |
| Gestión de Incoterms | Aplicación correcta por trade term |

### KPIs del departamento
| KPI | Benchmark |
|-----|-----------|
| On-Time Delivery (OTD) | ≥ 95% |
| Transportation Cost / Revenue | < 8-10% (FMCG) |
| Freight Cost per Unit | vs target por modo |
| Carrier OTIF Score | ≥ 95% |
| Claims Rate (daños) | < 0.1% envíos |
| CO₂ por tonelada-km | Reducción anual 5% |
| Customs Clearance Time | < 48 h (AEO) |
| Perfect Delivery Rate | ≥ 97% |

### Modos de transporte y usos
| Modo | Uso típico | Costo relativo |
|------|-----------|---------------|
| ROAD | Distribución nacional, last-mile | Medio |
| SEA (FCL/LCL) | Importaciones/exportaciones intercontinentales | Bajo |
| AIR | Urgentes, alto valor, perecederos | Muy alto |
| RAIL | Rutas medias/largas, materias primas | Bajo-Medio |
| COURIER | Muestras, repuestos, e-commerce | Alto |
| MULTIMODAL | Combinaciones optimizadas | Variable |

### Incoterms® 2020 — Guía de aplicación
| Incoterm | Riesgo pasa a comprador | Recomendado para |
|----------|------------------------|-----------------|
| EXW | En fábrica vendedor | Comprador con logística propia |
| FCA | Entregado al primer carrier | Reemplaza FOB para contenedor |
| CIP | Al primer carrier (+ seguro) | Exportaciones de alto valor |
| DPU | Descargado en destino | Reemplaza DAT (2020) |
| DDP | Destino, derechos pagados | Servicio completo al comprador |
| FOB | Abordo del buque | Solo marítimo/fluvial |

> ⚠️ **DPU reemplaza a DAT** — cambio clave de Incoterms 2020

### Documentos de transporte internacional
| Documento | Modo | Función |
|-----------|------|---------|
| Bill of Lading (B/L) | Marítimo | Título de propiedad + contrato |
| Air Waybill (AWB) | Aéreo | Guía aérea (no negociable) |
| CMR | Carretera Europa | Carta de porte internacional |
| CIM | Ferroviario | Carta de porte ferroviaria |
| Factura Comercial | Todos | Base para aforo aduanal |
| Packing List | Todos | Verificación de contenido |
| Certificado de Origen | Todos | Preferencias arancelarias |
| EUR.1 / Form A | UE | Certificado de origen preferencial |

### WTO TFA Art.7 — Pre-arrival processing
El sistema implementa:
- `Shipment.exportDeclarationRef` — pre-declaración de exportación
- `Shipment.aeoShipperCertified` — operador autorizado AEO/C-TPAT
- `ShipmentLine.hsCode` — clasificación HS para aforo
- Reducción documentaria ≥ 50% para operadores AEO

### Archivos clave
- `domain/Shipment.ts` — Embarque completo con legs, tracking, customs
- `domain/Carrier.ts` — Maestro de transportistas y contratos de flete
- `domain/FreightRate.ts` — Tarifas por modo/ruta/peso/volumen
- `domain/RouteOptimization.ts` — VRP y optimización de rutas
- `services/CarrierManagement.ts` — Selección y evaluación de carriers
- `services/CustomsService.ts` — Generación de documentos aduanales
- `services/TrackingService.ts` — Integración con APIs de tracking
- `customs/HSCodeClassifier.ts` — Clasificación arancelaria HS

### Roles del departamento
- **Logistics Director** — Estrategia de red y contratación
- **Transportation Manager** — Gestión diaria de flota y carriers
- **Customs Broker / Specialist** — Importaciones/exportaciones
- **Freight Coordinator** — Coordinación de embarques
- **Route Planner** — Optimización de rutas VRP
- **TMS Administrator** — Sistema de gestión de transporte

### Referencias
- Chopra & Meindl Ch.13 "Transportation in a Supply Chain"
- Ballou Ch.12 — Transportation fundamentals
- ICC Incoterms® 2020 — ICC Publication 723E
- IMO IMDG Code 2022 (Amendment 41-22)
- ADR 2023 — European Agreement Dangerous Goods Road
- WTO TFA — Article 7, Pre-arrival processing
