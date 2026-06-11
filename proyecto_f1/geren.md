# Distribuidora El Progreso, S.A. — Propuesta ejecutiva integrada

## 1. Nivel del ciclo gerencial con mayor falla

**Falla principal: Control** (con impacto crítico en Planeación y Dirección)

**Justificación:**  
El Progreso no tiene mecanismos integrados para medir, verificar o corregir operaciones en tiempo real.  
- **Control de inventario:** 18% de pedidos cancelados porque el vendedor confirma sin verificar bodega.  
- **Control financiero:** Cierre de 15 días con inconsistencias por consolidación manual.  
- **Control directivo:** Gerente espera 2 horas para saber ventas del día anterior → decisiones con información atrasada.  

Esto impide una planeación confiable y una dirección ágil.

---

## 2. Tres KPIs semanales que no puede obtener hoy

| KPI | Fórmula / Definición | Relevancia |
|-----|----------------------|-------------|
| **Tasa de rotura de stock** | (Pedidos cancelados por falta de stock / Total pedidos solicitados) × 100 | Mide el problema #1. Cada punto porcentual recuperado es venta y confianza del cliente. |
| **Exactitud del inventario** | (Ítems con conteo físico igual al sistema / Total ítems auditados) × 100 | Revela cuánto desvío hay entre cuadernos/Excel y la realidad. Necesario para que vendedor confíe en el sistema. |
| **Margen de ventas diario/semanal** | Ingresos semanales − COGS | Permite al gerente saber si hoy fue rentable, no dentro de 15 días. Base para promociones y reacción rápida. |

Actualmente no pueden obtenerse porque cada área opera en silos (Excel, cuadernos, software sin conexión).

---

## 3. Módulos ERP: orden de activación (6 meses)

| Orden | Módulo | Justificación |
|-------|--------|----------------|
| 1 | **Inventario / Bodega** | Resuelve la hemorragia más grave: pedidos cancelados. Permite stock en tiempo real. |
| 2 | **Ventas / Pedidos** | Se conecta con inventario → vendedor solo confirma si hay stock. Da visibilidad comercial en tiempo real. |
| 3 | **Finanzas / Contabilidad** | Reduce cierre de 15 días a horas, elimina inconsistencias y permite reportes gerenciales confiables. |

*Módulo adicional (mes 7-8):* **RR.HH. / Nómina** – para eliminar los 4 reclamos quincenales por errores manuales.

---

## 4. Flujo de pedido: SIN ERP vs. CON ERP

### Flujo actual (sin ERP)
1. Cliente pide a vendedor.  
2. Vendedor anota en Excel/cuaderno (sin ver stock real).  
3. Confirma pedido.  
4. Bodega revisa después → encuentra faltante.  
5. Pedido cancelado (18% del total).  
6. Cliente insatisfecho.  
7. Ventas, bodega y contabilidad actualizan manualmente → datos duplicados y tardíos.  

**Puntos de error:**  
- Vendedor sin inventario en tiempo real.  
- Bodega no conectada con ventas.  
- Reportes manuales y atrasados.  
- Gerencia decide a ciegas.

### Flujo con ERP (propuesto)
1. Cliente pide a vendedor.  
2. Vendedor ingresa pedido en ERP (desde móvil/tablet).  
3. ERP consulta stock en tiempo real.  
4. Si hay stock → reserva automática.  
5. Bodega recibe orden de despacho.  
6. Se entrega pedido.  
7. ERP actualiza inventario, ventas y cuentas por cobrar automáticamente.  
8. Gerente ve reportes diarios/semanales en tiempo real.

**Resultado:** Cero cancelaciones por falta de stock no detectada a tiempo.

---

## 5. Recomendación ERP

**ERP elegido: Odoo** (iniciar con Community, evaluar Enterprise en 12 meses)

**Por qué:**  
- Empresa mediana (87 empleados, Q28M/año, 3 departamentos).  
- Necesita modularidad para empezar por inventario → ventas → finanzas.  
- SAP Business One y Dynamics 365 son más costosos y rígidos para quien viene de procesos manuales.  
- Odoo permite integración en la nube, información en tiempo real y escalabilidad controlada.

---

## 6. Propuesta de 1 página para el gerente

> **Propuesta ERP para Distribuidora El Progreso, S.A.**
>
> **Problema raíz:** Operación en silos (Excel, cuadernos, software aislado) → pedidos cancelados (18%), cierre financiero de 15 días, decisiones atrasadas, errores en nómina.
>
> **Solución:** Implementación gradual de ERP en 6 meses.
>
> **Módulos prioritarios (orden):**  
> 1. Inventario / Bodega → KPI: % pedidos cancelados por falta de stock.  
> 2. Ventas / Pedidos → KPI: ventas semanales por vendedor y departamento.  
> 3. Finanzas / Contabilidad → KPI: días de cierre financiero.  
>
> **Beneficio medible por módulo:**  
> - Inventario: reducir cancelaciones al <2% en 90 días.  
> - Ventas: tiempo real de ventas para el gerente (de 2 horas a 0 minutos).  
> - Finanzas: cierre semanal en 1 día (vs. 15 días actuales).  
>
> **ERP recomendado:** Odoo (nube, modular, costo controlado).  
> **Tendencia relevante:** ERP en la nube con información en tiempo real para eliminar silos y decisiones reactivas.  
> **Próximo paso:** Auditoría rápida de datos maestros (productos, clientes, proveedores) para iniciar piloto en una bodega y 5 vendedores.