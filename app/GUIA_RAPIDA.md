# 🚀 GUÍA RÁPIDA DE INICIO
## Sistema de Gestión HORECA

---

## ✅ PASO 1: PREPARAR ARCHIVOS (YA HECHO)

Has descargado todos los archivos necesarios:

### 📊 Archivos Excel (4):
- ✅ CRM_CLIENTES.xlsx
- ✅ OPERACIONES_ESCANDALLOS.xlsx
- ✅ PROVEEDORES_MERCADO.xlsx
- ✅ EMPRESA_BACKOFFICE.xlsx

### 🐍 Archivos Python (7):
- ✅ main.py (aplicación principal)
- ✅ config.py (configuración)
- ✅ utils.py (funciones)
- ✅ requirements.txt (dependencias)
- ✅ README.md (documentación)
- ✅ INICIAR.bat (Windows)
- ✅ iniciar.sh (Mac/Linux)

---

## 🗂️ PASO 2: ORGANIZAR EN ONEDRIVE

### 2.1 Crear carpeta en OneDrive:

**Windows:**
```
C:\Users\TU_USUARIO\OneDrive\CONSULTORIA_HORECA\datos\
```

**Mac:**
```
/Users/TU_USUARIO/OneDrive/CONSULTORIA_HORECA/datos/
```

### 2.2 Colocar archivos Excel:

Copia los 4 archivos Excel a la carpeta `datos/`:
- CRM_CLIENTES.xlsx
- OPERACIONES_ESCANDALLOS.xlsx
- PROVEEDORES_MERCADO.xlsx
- EMPRESA_BACKOFFICE.xlsx

### 2.3 Colocar archivos Python:

Crea una carpeta para el código, por ejemplo:
```
C:\PROYECTOS\HORECA_APP\
```

Y copia ahí:
- main.py
- config.py
- utils.py
- requirements.txt
- README.md
- INICIAR.bat (o iniciar.sh)

---

## 🔧 PASO 3: INSTALAR PYTHON

### Si NO tienes Python instalado:

**Windows:**
1. Descarga Python desde: https://www.python.org/downloads/
2. Durante instalación, marca "Add Python to PATH"
3. Instala normalmente

**Mac:**
```bash
brew install python3
```

### Verificar instalación:

Abre Terminal/CMD y escribe:
```bash
python --version
```

Deberías ver algo como: `Python 3.11.x`

---

## 📦 PASO 4: INSTALAR DEPENDENCIAS

### 4.1 Abrir Terminal en la carpeta del proyecto:

**Windows:**
1. Abre la carpeta `C:\PROYECTOS\HORECA_APP\`
2. En la barra de dirección, escribe `cmd` y Enter
3. Se abre CMD en esa carpeta

**Mac:**
1. Abre Terminal
2. Navega: `cd /ruta/a/tu/proyecto`

### 4.2 Instalar librerías:

```bash
pip install -r requirements.txt
```

Espera 1-2 minutos mientras se instalan las dependencias.

---

## 🎯 PASO 5: EJECUTAR LA APLICACIÓN

### Opción A: Con script de inicio (RECOMENDADO)

**Windows:**
- Haz doble clic en `INICIAR.bat`

**Mac/Linux:**
- Doble clic en `iniciar.sh`
- O en Terminal: `./iniciar.sh`

### Opción B: Manualmente

En Terminal/CMD:
```bash
streamlit run main.py
```

---

## 🌐 PASO 6: USAR LA APLICACIÓN

### 6.1 Primera vez:

1. Se abrirá tu navegador en `http://localhost:8501`
2. Verás el Dashboard principal
3. Si aparece error de archivos, revisa que los Excel estén en OneDrive

### 6.2 Navegación:

**Sidebar izquierdo:**
- 🏠 Dashboard
- 👥 CRM - Clientes
- 🍽️ Escandallos
- 🏢 Proveedores
- 💼 Empresa
- ⚙️ Configuración

### 6.3 Agregar primer Lead:

1. Ve a: **👥 CRM - Clientes**
2. Tab: **📋 Leads**
3. Clic: **➕ Agregar Nuevo Lead**
4. Rellena formulario
5. **💾 Guardar Lead**

¡El lead se guarda automáticamente en Excel de OneDrive!

---

## 🔄 PASO 7: SINCRONIZACIÓN

### Cómo funciona:

1. **Tu socio** abre la app en su ordenador
2. **Agrega un lead** o modifica datos
3. Los cambios se guardan en **Excel en OneDrive**
4. **OneDrive sincroniza** automáticamente
5. **Tú** refresca la app (botón 🔄)
6. **Ves los cambios** inmediatamente

### Importante:

- ⚠️ **NO** abrir Excel y la app al mismo tiempo
- ✅ Usa el botón 🔄 para refrescar datos
- ✅ Deja OneDrive sincronizando siempre

---

## 📱 USO DIARIO

### Para tu Socio (Comercial):

**Por la mañana:**
1. Abre la app
2. Revisa leads pendientes
3. Planifica visitas del día

**Durante el día:**
1. Tras cada visita, registra:
   - Resultado de la visita
   - Próxima acción
   - Notas importantes

**Por la tarde:**
1. Actualiza estados de leads
2. Programa visitas del día siguiente

### Para ti (Analítico):

**Diariamente:**
1. Revisa Dashboard → Alertas
2. Analiza nuevas compras de clientes
3. Detecta desviaciones de precio

**Semanalmente:**
1. Actualiza precios de mercado
2. Recalcula escandallos
3. Genera informes para clientes

**Mensualmente:**
1. Actualiza KPIs
2. Analiza rentabilidad
3. Planifica estrategia

---

## ⚡ ATAJOS ÚTILES

### Teclado:

- `Ctrl + R` → Refrescar página
- `Ctrl + F5` → Refrescar forzado
- `Ctrl + W` → Cerrar pestaña

### En la app:

- Botón 🔄 → Refrescar datos de Excel
- Filtros → Buscar rápidamente
- Ordenar columnas → Clic en encabezados

---

## 🆘 PROBLEMAS COMUNES

### "No se encuentran los archivos Excel"

**Causa:** Excel no está en la ruta correcta

**Solución:**
1. Ve a ⚙️ Configuración
2. Verifica la ruta mostrada
3. Asegúrate de que los Excel están ahí
4. Si no, muévelos o edita `config.py`

### "Error al guardar"

**Causa:** Excel abierto en otro programa

**Solución:**
1. Cierra Excel si lo tienes abierto
2. Espera que OneDrive termine de sincronizar
3. Intenta de nuevo

### "La app va lenta"

**Causa:** Cache lleno o muchos datos

**Solución:**
1. Clic en botón 🔄 Refrescar
2. Reinicia la app (Ctrl + C en terminal, luego vuelve a ejecutar)
3. Limpia datos antiguos si hay miles de registros

---

## 📞 CONTACTO Y SOPORTE

Si tienes problemas:

1. **Lee el README.md completo** → Soluciones detalladas
2. **Revisa este archivo** → Problemas comunes
3. **Comprueba logs** → Terminal muestra errores
4. **Verifica OneDrive** → Que esté sincronizado

---

## 🎓 PRÓXIMOS PASOS

Una vez que domines lo básico:

1. **Personaliza colores** en `config.py`
2. **Ajusta umbrales** de alerta
3. **Exporta informes** para clientes
4. **Automatiza tareas** recurrentes

---

## 🎉 ¡YA ESTÁS LISTO!

Resumen de comandos:

```bash
# 1. Navegar a la carpeta
cd C:\PROYECTOS\HORECA_APP

# 2. Instalar dependencias (solo primera vez)
pip install -r requirements.txt

# 3. Ejecutar app
streamlit run main.py

# O simplemente doble clic en INICIAR.bat
```

**¡A gestionar tu consultoría como un profesional!** 🚀
