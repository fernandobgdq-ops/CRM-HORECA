# 🍽️ Sistema de Gestión HORECA
## Consultoría para el Canal HORECA

Sistema integral de gestión para consultoría gastronómica con CRM, escandallos, proveedores y backoffice.

---

## 📋 REQUISITOS PREVIOS

1. **Python 3.8+** instalado
2. **OneDrive** instalado y sincronizado
3. Los **4 archivos Excel base** en OneDrive

---

## 🚀 INSTALACIÓN

### Paso 1: Preparar OneDrive

1. Abre tu OneDrive
2. Crea esta estructura de carpetas:
   ```
   OneDrive/
   └── CONSULTORIA_HORECA/
       ├── datos/
       │   ├── CRM_CLIENTES.xlsx
       │   ├── OPERACIONES_ESCANDALLOS.xlsx
       │   ├── PROVEEDORES_MERCADO.xlsx
       │   └── EMPRESA_BACKOFFICE.xlsx
       └── documentos/
   ```

3. Coloca los 4 archivos Excel en la carpeta `datos/`

### Paso 2: Instalar Python y Dependencias

#### En Windows:

```bash
# 1. Abrir PowerShell o CMD
# 2. Navegar a la carpeta del proyecto
cd C:\ruta\a\tu\proyecto

# 3. Instalar dependencias
pip install -r requirements.txt
```

#### En Mac:

```bash
# 1. Abrir Terminal
# 2. Navegar a la carpeta del proyecto
cd /ruta/a/tu/proyecto

# 3. Instalar dependencias
pip3 install -r requirements.txt
```

### Paso 3: Configurar Rutas

El sistema detecta automáticamente tu OneDrive, pero si tienes problemas:

1. Abre `config.py`
2. Modifica manualmente la ruta:
   ```python
   ONEDRIVE_BASE = "C:/Users/TU_USUARIO/OneDrive"  # Windows
   # o
   ONEDRIVE_BASE = "/Users/TU_USUARIO/OneDrive"   # Mac
   ```

---

## 🎯 EJECUTAR LA APLICACIÓN

### Método 1: Desde la Terminal

```bash
streamlit run main.py
```

### Método 2: Script de arranque (Windows)

Crea un archivo `INICIAR.bat` con:
```batch
@echo off
streamlit run main.py
pause
```

Haz doble clic en `INICIAR.bat`

### Método 3: Script de arranque (Mac)

Crea un archivo `iniciar.sh` con:
```bash
#!/bin/bash
streamlit run main.py
```

Hazlo ejecutable y ejecútalo:
```bash
chmod +x iniciar.sh
./iniciar.sh
```

---

## 📱 USAR LA APLICACIÓN

### 1. Primera vez

Al abrir la aplicación verás:
- ✅ Verificación de archivos Excel
- 📊 Dashboard con métricas iniciales
- 🎨 Interfaz visual limpia

### 2. Módulos disponibles

#### 🏠 Dashboard
- Resumen ejecutivo
- Métricas principales (Leads, MRR, Conversión)
- Alertas del sistema

#### 👥 CRM - Clientes
- **Leads**: Agregar, editar, filtrar leads
- **Clientes Activos**: Gestión de clientes
- **Interacciones**: Historial de contactos
- **Servicios**: Servicios prestados con ROI

#### 🍽️ Escandallos
- **Carta**: Menú de cada cliente con márgenes
- **Ingredientes**: Base de datos de precios
- **Compras**: Registro de facturas

#### 🏢 Proveedores
- Catálogo de proveedores
- Comparativa de precios
- Historial de cambios

#### 💼 Empresa
- KPIs mensuales
- Facturación
- Control de gastos

---

## 🔄 SINCRONIZACIÓN CON ONEDRIVE

### Cómo funciona:

1. **Lectura**: La app lee los Excel desde OneDrive
2. **Escritura**: Al guardar cambios, actualiza los Excel
3. **Sincronización**: OneDrive sincroniza automáticamente
4. **Colaboración**: Tu socio ve los cambios en tiempo real

### Buenas prácticas:

✅ **SÍ hacer:**
- Cerrar Excel antes de usar la app
- Refrescar datos con el botón 🔄
- Dejar OneDrive sincronizando

❌ **NO hacer:**
- Editar Excel y la app al mismo tiempo
- Cambiar archivos mientras la app escribe
- Mover archivos de la carpeta `datos/`

---

## 📊 FLUJO DE TRABAJO TÍPICO

### Tu socio (Comercial):

1. Abre la app
2. Va a **CRM → Leads**
3. Clic en **➕ Agregar Nuevo Lead**
4. Rellena el formulario
5. Guarda

El lead aparece automáticamente en tu Excel de OneDrive.

### Tú (Analítico):

1. Ves el nuevo lead en el Excel
2. Realizas el análisis (escandallo)
3. Subes los datos a **Escandallos → Carta**
4. El sistema calcula márgenes automáticamente
5. Genera alertas si detecta problemas

### Retroalimentación automática:

```
Cliente compra ingrediente →
Registras en COMPRAS →
Sistema actualiza precio mercado →
Recalcula TODOS los escandallos →
Genera alerta si hay desviación
```

---

## 🛠️ PERSONALIZACIÓN

### Cambiar colores corporativos

Edita `config.py`:
```python
COLOR_PRIMARIO = "#366092"  # Tu color
COLOR_SECUNDARIO = "#5B9BD5"
```

### Cambiar umbrales de alerta

Edita `config.py`:
```python
UMBRAL_MARGEN_MINIMO = 20  # % mínimo de margen
UMBRAL_DESVIACION_PRECIO = 15  # % desviación para alertar
```

### Agregar nuevos tipos de local

Edita `config.py`:
```python
TIPOS_LOCAL = ["Bar", "Restaurante", "Tu Nuevo Tipo"]
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Problema: "Archivos Excel no encontrados"

**Solución:**
1. Verifica que los 4 Excel estén en OneDrive
2. Comprueba la ruta en `config.py`
3. Asegúrate de que OneDrive está sincronizado

### Problema: "Error al leer Excel"

**Solución:**
1. Cierra Excel si lo tienes abierto
2. Verifica que el archivo no esté corrupto
3. Comprueba permisos de lectura/escritura

### Problema: "Los cambios no se guardan"

**Solución:**
1. Verifica que OneDrive está sincronizando
2. Comprueba que no hay conflictos de versión
3. Espera unos segundos y refresca (🔄)

### Problema: "La app va lenta"

**Solución:**
1. Limpia la caché: botón 🔄 Refrescar
2. Cierra otras apps que usen Excel
3. Reinicia la aplicación

---

## 📈 PRÓXIMAS MEJORAS

### Versión 1.1 (Planeada):
- [ ] Gráficos interactivos con Plotly
- [ ] Exportar informes PDF
- [ ] Notificaciones por email
- [ ] App móvil responsive

### Versión 1.2:
- [ ] Integración con API de proveedores
- [ ] OCR para escanear facturas
- [ ] Sistema de usuarios con login
- [ ] Backup automático

---

## 💡 CONSEJOS DE USO

### Para el Comercial:
- Registra TODAS las visitas (incluso las negativas)
- Actualiza el estado del lead inmediatamente
- Usa el campo "Próxima Acción" para no olvidar seguimientos

### Para el Analítico:
- Actualiza precios de mercado semanalmente
- Revisa alertas a diario
- Mantén los escandallos actualizados

### Para ambos:
- Usa las notas liberalmente
- Revisa el Dashboard a diario
- Comunica alertas importantes

---

## 📞 SOPORTE

Si tienes problemas:

1. **Revisa este README**
2. **Verifica los archivos de configuración**
3. **Comprueba los logs de Streamlit en la terminal**

---

## 📄 ESTRUCTURA DEL PROYECTO

```
CONSULTORIA_HORECA/
│
├── main.py                 # Aplicación principal
├── config.py               # Configuración
├── utils.py                # Funciones utilitarias
├── requirements.txt        # Dependencias
├── README.md              # Este archivo
│
└── OneDrive/CONSULTORIA_HORECA/
    ├── datos/
    │   ├── CRM_CLIENTES.xlsx
    │   ├── OPERACIONES_ESCANDALLOS.xlsx
    │   ├── PROVEEDORES_MERCADO.xlsx
    │   └── EMPRESA_BACKOFFICE.xlsx
    │
    └── documentos/
        ├── facturas/
        ├── contratos/
        └── informes/
```

---

## 🎉 ¡LISTO PARA USAR!

Ya tienes todo configurado. Ejecuta:

```bash
streamlit run main.py
```

Y empieza a gestionar tu consultoría de forma profesional.

**¡Mucho éxito!** 🚀
