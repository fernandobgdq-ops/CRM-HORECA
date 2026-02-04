# 📊 MÓDULO ESCANDALLOS - Guía Completa

## 🎯 ¿QUÉ ES UN ESCANDALLO?

Un **Escandallo** (o Escandallo de Cocina) es un **desglose detallado de costes e ingredientes por plato**. Te muestra:

- 💰 **Ingresos** que genera cada plato
- 📦 **Ingredientes exactos** que lleva cada plato
- 📊 **Margen de ganancia** real
- 📈 **Proyecciones** de rentabilidad

---

## 📁 UBICACIÓN EN EL CÓDIGO

```
app/
├── main.py                    ← MÓDULO PRINCIPAL
├── modulo_clientes_nuevo.py   ← Módulo de clientes
└── utils.py                   ← Funciones auxiliares
```

---

## 🔄 FLUJO DE DATOS

```
CLIENTES_ACTIVOS (Excel)
    ↓
    ├─ ID Cliente
    ├─ Nombre
    └─ Servicios
        ↓
    ESCANDALLOS (Cálculos)
        ├─ Ingredientes por plato
        ├─ Costes unitarios
        ├─ Margen por plato
        └─ Rentabilidad total
            ↓
    DASHBOARD / INFORMES
```

---

## 📋 ESTRUCTURA DE DATOS

### Tabla: CLIENTES_ACTIVOS
```
ID | Nombre Comercial | Servicio | Precio Mensual
1  | Legarejo         | Básico   | 250€
2  | Bar El Rincón    | Completo | 500€
3  | Hamburguesa      | Estándar | 350€
```

### Tabla: CARTA_CLIENTES (Platos)
```
ID Plato | ID Cliente | Nombre Plato | Precio Venta | Coste Total
1        | 1          | Cachopo      | 18€          | 6.50€
2        | 1          | Salmón       | 22€          | 8€
3        | 2          | Hamburguesa  | 12€          | 4€
```

### Tabla: ESCANDALLOS (Ingredientes por plato)
```
ID Esc | ID Plato | Ingrediente | Cantidad | Precio Unit | Coste Total
1      | 1        | Ternera     | 200g     | 18€/kg      | 3.60€
2      | 1        | Pan         | 1 ud     | 0.50€       | 0.50€
3      | 1        | Queso       | 50g      | 12€/kg      | 0.60€
```

---

## 🛠️ COMPONENTES PRINCIPALES

### **1. Vista Principal (Dashboard)**

```python
def modulo_escandallos():
    """
    - Selector de cliente
    - 8 pestañas de análisis
    - Filtros y búsqueda
    - Exportación a Excel/PDF
    """
```

### **2. Cálculos Automáticos**

```python
def calcular_metrics(plato):
    """
    Calcula:
    - MRR (Monthly Recurring Revenue)
    - ARR (Annual Recurring Revenue)
    - Margen = Precio - Coste
    - Food Cost %
    - Clasificación BCG
    """
```

### **3. Selector de Cliente**

```python
cliente_seleccionado = st.selectbox(
    "Selecciona Cliente:",
    options=df_clientes['Nombre Comercial']
)
```

---

## 📊 LAS 8 PESTAÑAS EXPLICADAS

### **1️⃣ PESTAÑA: 🍴 CARTA**

**¿Qué ves?**
- Lista de TODOS los platos del cliente guardados
- Nombre, categoría, precio, margen, estado
- Métricas: Total platos, Activos, Margen medio, Estrellas

**¿Qué puedes hacer?**

```
✅ AGREGAR NUEVO PLATO:
   • Botón: ➕ Agregar Plato a la Carta
   • Se abre formulario expandible con:
   
   Columna 1:
   - Nombre del Plato* (?)
     → Tooltip: "Nombre que sale en la carta"
     → Ejemplo: "Cachopo de Ternera"
   
   - Categoría*
     → Principales / Entrantes / Postres / etc.
   
   - Precio de Venta (€)* (?)
     → Tooltip: "IVA INCLUIDO"
     → Ejemplo: 18.00€
   
   Columna 2:
   - Coste Total (€) 🔒 [DESHABILITADO]
     → Se calcula AUTOMÁTICAMENTE al agregar ingredientes
     → Suma de todos los ingredientes del escandallo
     → No se puede editar manualmente
   
   - Ventas/Mes Estimadas
     → Ejemplo: 85 uds
   
   - Estado
     → Activo / Inactivo (antes era Sí/No)
   
   - Notas (opcional)
   
   • Botones: 💾 Guardar | ❌ Cancelar

✅ VER PLATOS GUARDADOS:
   • Tabla con todos los platos creados
   • Columnas: Nombre, Categoría, Precio, Coste, Margen €, Margen %, Ventas/Mes, Clasificación, Estado
   • Los platos SE QUEDAN GUARDADOS permanentemente
   • Puedes verlos y editarlos después

✅ MÉTRICAS AUTOMÁTICAS:
   Cuando guardas un plato, el sistema CALCULA:
   ✅ Margen € = Precio Venta - Coste Total
   ✅ Margen % = (Margen € / Precio Venta) × 100
   ✅ Food Cost % = (Coste Total / Precio Venta) × 100
   ✅ Clasificación BCG (Estrella/Caballo/Rompecabezas/Perro)
   ✅ Precio Recomendado (basado en coste × 3)

✅ FLUJO COMPLETO:
   1. Creas plato: "Salmón a la Mantequilla"
      - Precio: 22€
      - Coste: 0€ (todavía sin ingredientes)
   
   2. Guardas → Plato aparece en la tabla
   
   3. Vas a pestaña "Escandallos"
   
   4. Agregas ingredientes:
      - Salmón 180g → 3.24€
      - Mantequilla 50g → 0.20€
      - Limón 1ud → 0.30€
      → COSTE TOTAL: 3.74€
   
   5. El sistema ACTUALIZA AUTOMÁTICAMENTE:
      - Coste Total en Carta: 3.74€
      - Margen €: 18.26€
      - Margen %: 83%
      - Clasificación: ⭐ ESTRELLA
```

**Ejemplo de plato guardado:**
```
SALMÓN A LA MANTEQUILLA
├─ Categoría: Principales
├─ Precio Venta: 22€ (IVA incluido)
├─ Coste Total: 3.74€ (suma automática)
├─ Margen: 18.26€ (83%)
├─ Ventas/Mes: 85 uds
├─ Clasificación: ⭐ ESTRELLA
└─ Estado: Activo
```

---

### **2️⃣ PESTAÑA: 🔍 ESCANDALLOS** ← LA MÁS IMPORTANTE

**¿Qué ves?**
- Desglose DETALLADO de ingredientes de cada plato
- Cantidad de cada ingrediente
- Coste unitario
- Coste total del ingrediente
- Porcentaje que representa en el plato

**¿Qué puedes hacer?**

```
✅ AGREGAR MÚLTIPLES INGREDIENTES A UN PLATO:
   
   Flujo optimizado:
   
   1. Botón: ➕ Agregar Ingrediente a Plato
   
   2. Se abre panel expandible que muestra:
      
      Columna 1:
      • Selecciona Plato: "Salmón a la Mantequilla"
      • Selecciona Ingrediente: "Salmón Noruego"
      
      Columna 2:
      • Cantidad (180g)
      • Coste Unitario: 18€/kg (automático)
      • Coste Total: 3.24€ (calculo automático)
      • Proveedor (opcional)
      
      📋 Ingredientes ya agregados:
      • (Lista de lo que ya tiene el plato)
      • Total Coste Actual: X.XX€
   
   3. Clic en "💾 Agregar Ingrediente"
      → ✅ Ingrediente guardado
      → ♻️ Coste del plato actualizado automáticamente
      → La pantalla se MANTIENE ABIERTA para agregar más
   
   4. Puedes seguir agregando ingredientes:
      • Cambias a "Mantequilla"
      • Cantidad: 50g
      • Agregar → Se suma al plato
      
   5. Cada vez que agregas:
      ✅ Se guarda inmediatamente en Excel
      ✅ El coste total del plato se ACTUALIZA en la Carta
      ✅ Los márgenes se RECALCULAN automáticamente
      ✅ La pantalla se REFRESCA mostrando los cambios
   
   6. Cuando termines, clic en "❌ Cancelar" para cerrar

✅ VER INGREDIENTES YA AGREGADOS:
   
   Mientras agregas ingredientes, ves en tiempo real:
   • Lista de ingredientes del plato
   • Cantidades y costes
   • Coste total acumulado
   
   Previene duplicados:
   → Si intentas agregar un ingrediente que ya está
   → Sistema avisa: "⚠️ Este ingrediente ya está en el plato"

✅ ACTUALIZACIÓN AUTOMÁTICA:
   
   Cada ingrediente que agregas:
   1. Se guarda en ESCANDALLOS (Excel)
   2. Se suma al coste total del plato
   3. Se actualiza en CARTA_CLIENTES (Excel)
   4. Se recalculan márgenes automáticamente
   5. La pantalla se refresca mostrando cambios
```

**Ejemplo de Flujo Completo:**

```
PLATO: Salmón a la Mantequilla (22€)

Paso 1: Agregar Salmón
├─ Ingrediente: Salmón Noruego (180g @ 18€/kg)
├─ Coste: 3.24€
└─ 💾 Agregar → ✅ Guardado
    → Coste Plato actualizado: 3.24€

Paso 2: Agregar Mantequilla (pantalla sigue abierta)
├─ Ingrediente: Mantequilla (50g @ 4€/kg)
├─ Coste: 0.20€
├─ Ya agregados: Salmón 3.24€
└─ 💾 Agregar → ✅ Guardado
    → Coste Plato actualizado: 3.44€

Paso 3: Agregar Limón
├─ Ingrediente: Limón (1 ud @ 0.30€)
├─ Coste: 0.30€
├─ Ya agregados: Salmón 3.24€, Mantequilla 0.20€
└─ 💾 Agregar → ✅ Guardado
    → Coste Plato actualizado: 3.74€

Paso 4: Cerrar
└─ ❌ Cancelar

RESULTADO FINAL:
┌──────────────────────────────────┐
│ SALMÓN A LA MANTEQUILLA          │
├──────────────────────────────────┤
│ INGREDIENTES:                    │
│                                  │
│ Salmón        180g  @ 18€/kg     │
│ Coste: 3.24€ (86.6%)             │
│                                  │
│ Mantequilla   50g   @ 4€/kg      │
│ Coste: 0.20€ (5.3%)              │
│                                  │
│ Limón         1ud   @ 0.30€      │
│ Coste: 0.30€ (8.0%)              │
│                                  │
│ ────────────────────────────────│
│ COSTE TOTAL: 3.74€ ✅            │
│ PRECIO VENTA: 22€                │
│ MARGEN: 18.26€ (83%)             │
│ CLASIFICACIÓN: ⭐ ESTRELLA        │
└──────────────────────────────────┘

Todo actualizado automáticamente en:
• Excel ESCANDALLOS
• Excel CARTA_CLIENTES
• Márgenes recalculados
• Clasificación BCG actualizada
```

**Ventajas del nuevo sistema:**

✅ **Agrega múltiples ingredientes** sin cerrar la ventana
✅ **Se actualiza en tiempo real** - ves los cambios inmediatamente  
✅ **Previene errores** - avisa si intentas duplicar ingredientes
✅ **Calcula todo automáticamente** - costes, márgenes, clasificación
✅ **Persiste los datos** - todo queda guardado en Excel
✅ **Vista previa** - ves lo que ya agregaste mientras trabajas

---

### **3️⃣ PESTAÑA: 📊 INGREDIENTES**

**¿Qué ves?**
- Ingredientes asignados a ESTE cliente
- Precio que paga este cliente
- Comparativa con precio de mercado
- Si está caro o barato

**¿Qué puedes hacer?**

```
✅ ASIGNAR INGREDIENTE A CLIENTE:
   
   Cada cliente tiene PRECIOS DIFERENTES
   
   Ejemplo: Salmón
   ├─ Bar A: 18€/kg (de su proveedor A)
   ├─ Bar B: 16€/kg (de su proveedor B)
   └─ Bar C: 20€/kg (de su proveedor C)
   
   Cuando asignas:
   1. Seleccionas el ingrediente de la lista
   2. El sistema muestra automáticamente:
      • Precio Mercado Medio (Referencia): 17€/kg ✅ Se actualiza al cambiar ingrediente
      • Unidad del ingrediente
   3. Introduces:
      • Precio del cliente: 18€/kg
      • Proveedor (opcional)
   4. El sistema calcula y actualiza automáticamente en TIEMPO REAL:
      • Desviación: +5.9% MÁS CARO ✅ Se actualiza mientras escribes el precio
   
   ALERTA AUTOMÁTICA: Si está >10% más caro
   → Sistema muestra en ROJO: "⚠️ +X% MÁS CARO que el mercado"
   → Si está >10% más barato: en VERDE "✅ -X% MÁS BARATO"
   → Si está dentro del rango: en AZUL "📊 Desviación: +X%"

✅ CREAR NUEVO INGREDIENTE EN BASE MAESTRO:
   
   Si no existe un ingrediente, lo creas aquí:
   1. Introduces:
      • Nombre: "Salmón Noruego Fresco"
      • Categoría: Pescados Frescos
      • Unidad: Kg
      • Marca (opcional): "Pescanova"
   
   2. El sistema CALCULA AUTOMÁTICAMENTE el Precio Mercado Medio:
      • Busca ingredientes con nombre similar en todos los clientes
      • Calcula la media de todos los precios encontrados
      • Muestra: "✅ Calculado automáticamente (media de X precio(s))"
      
      Si NO hay datos:
      • Muestra: "⚠️ No disponemos de datos suficientes para realizar el cálculo"
      • El campo queda en 0.00€
      • ✅ PUEDES CREARLO IGUAL sin inventar un precio
      • Se actualizará automáticamente cuando asignes a clientes
   
   3. El campo "Precio Mercado Medio" es OPCIONAL:
      • Si hay datos → Se autocompleta con el cálculo
      • Si NO hay datos → Déjalo en 0€ y créalo igual
      • Se actualizará después con datos reales
   
   Ejemplo CON datos:
   • Escribes: "Salmón"
   • Sistema encuentra: 18€, 16€, 20€, 17€ (4 clientes)
   • Calcula: (18+16+20+17)/4 = 17.75€
   • Muestra: "✅ Calculado automáticamente (media de 4 precio(s))"
   • Campo: 17.75€ (autocompletado)
   
   Ejemplo SIN datos (ingrediente nuevo):
   • Escribes: "Trufa Negra"
   • Sistema no encuentra nada
   • Muestra: "⚠️ No disponemos de datos suficientes"
   • Campo: 0.00€
   • ✅ Créalo igual → Asígnalo a clientes → Precio se calculará después

✅ ACTUALIZACIÓN RÁPIDA DE PRECIO:
   
   Si cambias el precio del salmón para este cliente:
   → Se recalculan automáticamente los escandallos
   → Se actualizan márgenes de todos los platos
   → Se genera alerta de cambios significativos
```

**Matriz de Sobreprecios:**

```
Cliente: Bar El Rincón

Ingrediente    | Precio Mercado | Precio Cliente | Desviación
Salmón         | 17€/kg         | 18€/kg         | +5.9% ✅
Ternera        | 12€/kg         | 13.50€/kg      | +12.5% ⚠️
Pollo          | 6€/kg          | 5.50€/kg       | -8.3% ✅
Verduras       | 2€/kg          | 2.50€/kg       | +25% ❌❌❌
```

---

### **4️⃣ PESTAÑA: 💰 COMPRAS**

**¿Qué ves?**
- Historial de compras que ha hecho el cliente
- Qué compró, cuándo, a qué precio
- Cantidad
- Total gastado

**¿Qué puedes hacer?**
- Ver análisis de compras históricas
- Detectar patrones de compra
- Identificar temporadas altas/bajas

---

### **5️⃣ PESTAÑA: 💵 SIMULADOR DE PRECIOS** ← MUY ÚTIL

**¿Qué ves?**
- Simulador interactivo de cambios de precio

**¿Qué puedes hacer?**

```
EJEMPLO: "¿Qué pasa si subo el Salmón de 22€ a 24€?"

1. Selecciona el plato: Salmón a la Mantequilla
2. Cambio de precio: +2€ (de 22€ a 24€)
3. Cambio en demanda: -5% (pierdes algo de demanda)

SISTEMA CALCULA AUTOMÁTICAMENTE:

Escenario Actual:
├─ Precio: 22€
├─ Ventas: 85 uds/mes
├─ Ingresos: 1.870€/mes
├─ Margen: 14€/plato
└─ Beneficio: 1.190€/mes

Escenario Propuesto:
├─ Precio: 24€ (+2€)
├─ Ventas: 81 uds/mes (-5%)
├─ Ingresos: 1.944€/mes
├─ Margen: 16€/plato
└─ Beneficio: 1.264€/mes

ANÁLISIS DE IMPACTO:

Diferencia Beneficio: +74€/mes (+6.2%)
Impacto Anual: +888€

RECOMENDACIÓN: ✅ FAVORABLE
"La subida genera más beneficio incluso
perdiendo 4 clientes por mes"
```

**Gráfico de Comparación:**

```
                    Actual      Propuesto
Precio              22€    →    24€
Ventas/mes          85     →    81
Ingresos Totales    1.870€ →    1.944€ (+74€)
Beneficio Mensual   1.190€ →    1.264€ (+6.2%)
Beneficio Anual     14.280€→    15.168€ (+888€)
```

---

### **6️⃣ PESTAÑA: 🛒 PEDIDO INTELIGENTE**

**¿Qué ves?**
- Herramienta para calcular pedidos óptimos
- Considerando stock, consumo, crecimiento

**¿Qué puedes hacer?**

```
ESCENARIO: Es viernes, tienes que calcular qué comprar

1. ACTUALIZAR STOCK (lo que hay AHORA):
   ├─ Salmón: 12 kg en stock
   ├─ Mantequilla: 5 kg
   ├─ Limones: 50 ud
   └─ Sal: 2 kg

2. CONSUMO SEMANAL ESTIMADO:
   ├─ Salmón: 8 kg/semana
   ├─ Mantequilla: 2 kg/semana
   ├─ Limones: 30 ud/semana
   └─ Sal: 0.5 kg/semana

3. CONFIGURAR PEDIDO:
   • Periodo: 2 semanas (hasta próxima visita)
   • Crecimiento: +10% (espero vender más)
   • Stock de seguridad: 15% extra

4. SISTEMA CALCULA:

   ┌─────────────────────────────────────┐
   │ PEDIDO RECOMENDADO:                 │
   ├─────────────────────────────────────┤
   │ Salmón: 20 kg          @ 18€/kg     │
   │                        = 360€       │
   │                                     │
   │ Mantequilla: 5 kg      @ 4€/kg      │
   │                        = 20€        │
   │                                     │
   │ Limones: 65 ud         @ 0.30€/ud   │
   │                        = 19.50€     │
   │                                     │
   │ Sal: 1.2 kg            @ 0.50€/kg   │
   │                        = 0.60€      │
   │                                     │
   │ ────────────────────────────────── │
   │ TOTAL PEDIDO: 400.10€               │
   │                                     │
   │ [📥 Descargar Excel] [💾 Guardar]   │
   └─────────────────────────────────────┘

5. GUARDAR SNAPSHOT:
   → Registra el estado en esa fecha
   → Puedes ver evolución de stock a lo largo del tiempo
```

**Fórmula Cálculo:**

```
Pedido Sugerido = 
  (Consumo Semanal × Semanas × (1 + % Crecimiento))
  × (1 + % Seguridad)
  - Stock Actual

Ejemplo Salmón:
= (8 kg × 2 semanas × 1.10) × 1.15 - 12 kg
= (17.6 kg) × 1.15 - 12 kg
= 20.24 kg - 12 kg
= 8.24 kg a pedir
```

---

### **7️⃣ PESTAÑA: 🎯 INGENIERÍA DE MENÚ** ← LA MÁS ESTRATÉGICA

**¿Qué ves?**
- **Matriz BCG** (Boston Consulting Group) de todos los platos
- Clasificación en 4 cuadrantes

**¿Qué es cada cuadrante?**

```
                 MARGEN ALTO
                     ▲
                     │
        🧩 ROMPECABEZAS │ ⭐ ESTRELLA
           (Alto margen  │ (Alto margen +
            Bajas ventas)│  Altas ventas)
                     │
    ─────────────────┼───────────────── VENTAS
                     │
        🐕 PERRO      │  🐴 CABALLO
      (Bajo margen +  │  (Bajo margen +
       Bajas ventas)  │   Altas ventas)
                     │
                     ▼
                 MARGEN BAJO
```

**EXPLICACIÓN DE CADA TIPO:**

#### **⭐ ESTRELLAS** (Alto margen + Altas ventas)

```
Ejemplo: Salmón a la Mantequilla
├─ Ventas: 85/mes
├─ Margen: 63%
├─ Beneficio: 1.190€/mes
│
ESTRATEGIA:
✅ DESTACAR EN LA CARTA (posición privilegiada)
✅ Invertir en FOTOGRAFÍA profesional
✅ Mantener PRECIO y CALIDAD constante
✅ Usar como GANCHO en marketing
✅ Realizar UPSELL ("¿Quieres añadir ensalada?")

ACCIÓN INMEDIATA:
→ Pon en la TAPA de la carta
→ Haz foto profesional
→ Entrena al personal para venderlo
→ Crea combo con otro plato
```

#### **🐴 CABALLOS DE BATALLA** (Bajo margen + Altas ventas)

```
Ejemplo: Hamburguesa Clásica
├─ Ventas: 120/mes
├─ Margen: 22%
├─ Beneficio: 440€/mes (bajo)
│
PROBLEMA:
❌ Vende mucho pero poco margen
❌ Genera volumen pero poca ganancia

ESTRATEGIA:
✅ SUBIR PRECIO gradualmente (0.50€ - 1€)
✅ REVISAR COSTES (renegociar proveedores)
✅ REDUCIR PORCIONES ligeramente
⚠️ CUIDADO: Si subes mucho → pierdes clientes

ACCIÓN INMEDIATA:
→ Sube +0.50€ la próxima semana
→ Observa si pierdes ventas
→ Si no pierdes → sube +0.50€ más
```

#### **🧩 ROMPECABEZAS** (Alto margen + Bajas ventas)

```
Ejemplo: Tabla de Quesos Premium
├─ Ventas: 8/mes
├─ Margen: 75%
├─ Beneficio: 300€/mes (bajo por volumen)
│
PROBLEMA:
❌ Rentable pero nadie lo pide
❌ Potencial desaprovechado

ESTRATEGIA:
✅ PROMOCIONAR en redes sociales
✅ BAJAR PRECIO ligeramente para atraer
✅ REPOSICIONAR en la carta (lugar visible)
✅ ENTRENAR PERSONAL para recomendarlo
✅ CREAR COMBOS con otros platos

ACCIÓN INMEDIATA:
→ Publica foto en Instagram
→ Baja precio -1€ para probar
→ Entrena camareros para recomendarlo
→ Crea "Tabla Premium + Vino" a precio combo
```

#### **🐕 PERROS** (Bajo margen + Bajas ventas)

```
Ejemplo: Sopa de Cebolla
├─ Ventas: 3/mes
├─ Margen: 18%
├─ Beneficio: 18€/mes
│
PROBLEMA:
❌ NO VENDE
❌ NO DEJA MARGEN
❌ Ocupa espacio en la carta

ESTRATEGIA:
🗑️ ELIMINAR de la carta (decisión difícil)
🔄 REFORMULAR completamente (nuevo concepto)
💰 SUBIR PRECIO drásticamente (si decides mantenerlo)
📊 ANALIZAR POR QUÉ NO VENDE

ACCIÓN INMEDIATA:
→ QUÍTALO de la carta ya
→ Libera espacio para otro plato
→ O reformúlalo completamente (Sopa de marisco)
→ Pregunta al personal por qué no vende
```

**¿Qué puedes hacer en este tab?**

```
1️⃣ VER GRÁFICO INTERACTIVO:
   • Cada círculo es un plato
   • Tamaño = facturación que genera
   • Posición = margen vs. ventas
   • Color = cuadrante (Estrella/Caballo/etc)

2️⃣ VER ANÁLISIS DETALLADO:
   Para cada cuadrante:
   ├─ Lista de platos
   ├─ Ventas mensuales
   ├─ Margen %
   ├─ Beneficio total
   └─ Recomendaciones específicas

3️⃣ GENERAR INFORME PDF:
   Con análisis completo para el cliente

4️⃣ CREAR RECOMENDACIONES:
   Genera mensaje WhatsApp con acciones claras:
   
   "📊 RECOMENDACIONES - Bar El Rincón
   
   ✅ ACCIONES PRIORITARIAS:
   
   1️⃣ SUBIR PRECIOS (+0.50€):
      • Hamburguesa Clásica
      • Sopa de Cebolla
      → Impacto: +125€/mes
   
   2️⃣ PROMOCIONAR EN RRSS:
      • Tabla de Quesos Premium
      • Ceviche de Mero
   
   3️⃣ ELIMINAR DE CARTA:
      • Sopa de Repollo
      • Ensalada Mixta
   
   4️⃣ DESTACAR EN CARTA:
      • Salmón a la Mantequilla
      • Pez Espada a la Sal"
```

---

### **8️⃣ PESTAÑA: 📄 INFORMES PDF**

**¿Qué puedes hacer?**

```
GENERAR 3 TIPOS DE INFORMES PROFESIONALES:

1️⃣ INFORME DE INGENIERÍA DE MENÚ:
   ✅ Incluye gráfico BCG
   ✅ Análisis de cada cuadrante
   ✅ Recomendaciones específicas
   ✅ Proyección financiera
   → Formato: PDF profesional para entregar al cliente

2️⃣ REPORTE MENSUAL:
   ✅ KPIs del mes
   ✅ Top 5 platos
   ✅ Alertas
   ✅ Plan de acción
   → Formato: Automático con fecha

3️⃣ ANÁLISIS COMPLETO:
   ✅ Ingeniería de Menú + Reporte Mensual
   ✅ Análisis de Proveedores
   ✅ Proyecciones financieras
   ✅ Gráficos de tendencias
   → Formato: Informe ejecutivo completo
```

---

## ⬇️ DESCARGAS DISPONIBLES

### **1. EXCEL DE PEDIDO** 📊

```
Cuando usas "🛒 Pedido Inteligente"

Descarga: Pedido_[Cliente]_[Fecha].xlsx

Contiene:
├─ Ingrediente
├─ Cantidad a Pedir
├─ Unidad
├─ Precio Unitario
├─ Coste Total
└─ TOTAL PEDIDO

Puedes usar DIRECTAMENTE para pedir al proveedor
```

### **2. PDF DE INGENIERÍA DE MENÚ** 📄

```
Desde pestaña "🎯 Ingeniería de Menú"

Descarga: Informe_Ingenieria_Menu_[Cliente]_[Fecha].pdf

Contiene:
├─ Portada profesional
├─ Gráfico BCG en color
├─ Análisis de cada cuadrante
├─ Tabla de platos con métricas
├─ Recomendaciones por tipo
└─ Plan de acción

Formato: Listo para entregar al cliente
```

### **3. PDF DE REPORTE MENSUAL** 📄

```
Desde pestaña "📄 Informes PDF"

Descarga: Reporte_Mensual_[Mes]_[Año]_[Cliente].pdf

Contiene:
├─ Mes analizado
├─ KPIs (ingresos, beneficio, margen)
├─ Top 5 platos del mes
├─ Alertas
├─ Recomendaciones
└─ Plan para próximo mes

Formato: Resumen ejecutivo
```

### **4. MENSAJES WHATSAPP** 💬

```
Desde pestaña "🎯 Ingeniería de Menú"

Botón: "📧 Crear Recomendaciones para Cliente"

Genera: Mensaje WhatsApp listo para copiar/pegar

Contiene:
├─ Acciones prioritarias
├─ Impacto financiero
├─ Platos específicos
└─ Cambios recomendados

Ideal para enviar rápidamente al cliente
```

---

## 🎯 FLUJO TÍPICO DE TRABAJO

```
DÍA 1: PRIMERA VISITA AL CLIENTE
└─ Creas carta del cliente (pestaña 1: 🍴 Carta)
└─ Añades ingredientes a cada plato (pestaña 2: 🔍 Escandallos)
└─ Registras datos de proveedores (pestaña 3: 📊 Ingredientes)

DÍA 2-7: ANÁLISIS
└─ Ves gráfico BCG (pestaña 7: 🎯 Ingeniería de Menú)
└─ Identificas problemas
└─ Generas informe PDF (pestaña 8: 📄 Informes PDF)

DÍA 8: REUNIÓN CON CLIENTE
└─ Muestras informe
└─ Explicas recomendaciones
└─ Envías mensaje WhatsApp con acciones

DÍA 15: SEGUNDA VISITA
└─ Actualizas stock (pestaña 6: 🛒 Pedido Inteligente)
└─ Calculas pedido inteligente
└─ Descargas Excel para pedir
└─ Actualiza precios de ingredientes (pestaña 3: 📊 Ingredientes)

CICLO CONTINUO:
└─ Cada 15 días: Visita + Actualización
└─ Cada mes: Genera Reporte Mensual
└─ Cada trimestre: Análisis Completo
```

---

## 💡 CASOS DE USO REALES

### **CASO 1: Descubrir Sobreprecio**

```
SITUACIÓN:
Un cliente paga 20€/kg el salmón
El mercado está a 17€/kg
→ AHORRO POTENCIAL: 3€/kg × consumo

CÓMO:
1. Ir a pestaña "📊 Ingredientes"
2. Ver columna "Desviación %"
3. Filtra por "Más caros"
4. Renegociar con proveedor
5. Actualizar precio (se recalculan escandallos)
```

### **CASO 2: Optimizar Carta**

```
SITUACIÓN:
Cliente tiene muchos "Perros" (bajo margen + bajas ventas)

CÓMO:
1. Ir a pestaña "🎯 Ingeniería de Menú"
2. Ver qué platos son "Perros"
3. Decidir: ¿Eliminar o reformular?
4. Generar informe con recomendaciones
5. Enviar a cliente
```

### **CASO 3: Subida de Precios Inteligente**

```
SITUACIÓN:
Quieres subir precios pero no perder ventas

CÓMO:
1. Ir a pestaña "💵 Simulador de Precios"
2. Seleccionar un plato "Caballo" (bajo margen, muchas ventas)
3. Simular +0.50€ en precio
4. Sistema calcula impacto
5. Si sale positivo → APLICA
```

### **CASO 4: Calcular Pedido Óptimo**

```
SITUACIÓN:
Es viernes, tienes que pedir para 15 días

CÓMO:
1. Ir a pestaña "🛒 Pedido Inteligente"
2. Actualizar stock actual
3. Ajustar parámetros (período, crecimiento, seguridad)
4. Sistema calcula pedido óptimo
5. Descargar Excel
6. Enviar al proveedor
```

---

## 📋 RESUMEN RÁPIDO POR ACCIÓN

| Función | Pestaña | Qué Hace |
|---------|---------|----------|
| **Crear Plato** | 🍴 Carta | Agrega nuevo plato a la carta |
| **Agregar Ingrediente** | 🔍 Escandallos | Desglose de costes por plato |
| **Asignar Precios Cliente** | 📊 Ingredientes | Comparación cliente vs mercado |
| **Simular Cambios** | 💵 Simulador | Impacto financiero de cambios |
| **Calcular Pedido** | 🛒 Pedido | Cantidad óptima a comprar |
| **Analizar Rentabilidad** | 🎯 Ingeniería | Clasificación BCG de platos |
| **Generar Informe** | 📄 Informes | PDF profesional para cliente |

---

## 🚀 VENTAJAS DEL MÓDULO ESCANDALLOS

✅ **Control total de costes**: Sabes exactamente cuánto cuesta cada plato

✅ **Identificar sobreprecios**: Detecta automáticamente si pagan de más a proveedores

✅ **Optimizar carta**: Sabe qué platos son rentables y cuáles no

✅ **Simular cambios**: Prueba subidas de precio sin riesgos

✅ **Presupuestos precisos**: Calcula pedidos óptimos automáticamente

✅ **Informes profesionales**: Genera PDFs para entregar al cliente

✅ **Ahorro directo**: Detecta ahorros potenciales mensales/anuales

---

## 📞 SOPORTE RÁPIDO

**¿No sé cómo...?**

- Crear un plato → Pestaña **🍴 Carta**
- Añadir ingredientes → Pestaña **🔍 Escandallos**
- Ver si pago caro → Pestaña **📊 Ingredientes**
- Subir precios → Pestaña **💵 Simulador**
- Hacer un pedido → Pestaña **🛒 Pedido**
- Optimizar menú → Pestaña **🎯 Ingeniería**
- Generar informe → Pestaña **📄 Informes**

---

**¡Listo! Este es tu módulo ESCANDALLOS completo.**
