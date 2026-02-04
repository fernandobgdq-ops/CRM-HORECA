"""
MAIN.PY - Aplicación Principal
Sistema de Gestión Integral - Consultoría HORECA
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
import config
import utils
import modulo_clientes_nuevo as mod_clientes

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Consultoría HORECA - Sistema de Gestión",
    page_icon="fer.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #366092;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #366092;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# VERIFICACIÓN DE ARCHIVOS
# ============================================================================

def verificar_sistema():
    """Verifica que todo esté correctamente configurado"""
    archivos_faltantes = config.verificar_archivos_excel()
    
    if archivos_faltantes:
        st.error("⚠️ Archivos Excel no encontrados")
        st.markdown(config.MENSAJE_PRIMERA_VEZ.format(ruta=config.RUTA_DATOS))
        for archivo in archivos_faltantes:
            st.write(f"❌ {archivo}")
        st.stop()
    
    return True

# ============================================================================
# SIDEBAR - NAVEGACIÓN
# ============================================================================

def mostrar_sidebar():
    """Renderiza el menú lateral"""
    with st.sidebar:
        st.image("fer.png")
        
        st.markdown("---")
        
        # Selector de módulo
        modulo = st.radio(
            "📍 MÓDULOS",
            [
                "📊 Dashboard",
                "👥 Clientes",
                "🍽️ Escandallos",
                "📦 Proveedores",
                "🏢 Empresa",
                "📈 Informes",
                "⚙️ Configuración"
            ],
            label_visibility="visible"
        )
        
        st.markdown("---")
        
        # Información del sistema
        st.caption(f"**Sistema:** {config.NOMBRE_EMPRESA}")
        st.caption(f"**Versión:** 1.0.0")
        st.caption(f"**Última sync:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Botón de refresco
        if st.button("🔄 Refrescar Datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    return modulo

# ============================================================================
# MÓDULO: DASHBOARD
# ============================================================================

def modulo_dashboard():
    """Dashboard principal con resumen ejecutivo"""
    st.markdown('<h1 class="main-header">Dashboard Ejecutivo</h1>', unsafe_allow_html=True)
    
    # LIMPIAR CACHÉ Y LEER DATOS FRESCOS
    st.cache_data.clear()
    import utils
    
    # Leer CLIENTES_ACTIVOS para contar clientes reales
    df_clientes_activos = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'CLIENTES_ACTIVOS')
    
    # Leer LEADS para información de leads
    df_leads = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'LEADS')
    
    if df_clientes_activos.empty and df_leads.empty:
        st.info("No hay datos para contar.")
        return

    # Calcular métricas con datos frescos (SIN CACHE)
    total_clientes = len(df_clientes_activos)
    total_leads = len(df_leads)
    
    # DEBUG: Mostrar conteos
    print(f"[DEBUG] CLIENTES_ACTIVOS: {total_clientes} filas")
    print(f"[DEBUG] LEADS: {total_leads} filas")
    
    # Buscar bajas y pausados en LEADS (si tienen la columna Estado Lead)
    total_bajas = 0
    total_pausados = 0
    if 'Estado Lead' in df_leads.columns:
        total_bajas = len(df_leads[df_leads['Estado Lead'] == 'Baja'])
        total_pausados = len(df_leads[df_leads['Estado Lead'] == 'Pausado'])
    
    # ===== GAUGE CHART - GAMIFICACIÓN =====
   
    
    col_gauge, col_stats = st.columns([2, 1])
    
    with col_gauge:
        # Gauge Chart para meta de 10 clientes activos
        import plotly.graph_objects as go
        
        meta = 10
        valor = total_clientes
        porcentaje = (valor / meta) * 100 if meta > 0 else 0
        
        # Determinar color según rango
        if valor <= 4:
            color_gauge = "red"
            estado_texto = "🔴 CRÍTICO"
        elif valor <= 8:
            color_gauge = "orange"
            estado_texto = "🟡 EN PROGRESO"
        else:
            color_gauge = "green"
            estado_texto = "🟢 OBJETIVO CUMPLIDO!"
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=valor,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "🎯 Meta de Clientes Activos"},
            delta={'reference': meta, 'suffix': " clientes faltantes"},
            gauge={
                'axis': {'range': [None, meta]},
                'bar': {'color': color_gauge},
                'steps': [
                    {'range': [0, 4], 'color': "rgba(255, 0, 0, 0.2)"},
                    {'range': [4, 8], 'color': "rgba(255, 165, 0, 0.2)"},
                    {'range': [8, 10], 'color': "rgba(0, 255, 0, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 10
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(size=14)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_stats:
        st.metric("📋 Leads", total_leads)
        st.metric("🟢 Clientes Activos", total_clientes)
        st.metric("❌ Bajas", total_bajas)
        
        # Mostrar estado de progreso
        st.markdown(f"**Progreso:** {porcentaje:.1f}%")
    
    st.markdown("---")
    
    # ===== ALERTA DE DATOS INCOMPLETOS =====
    # Leer CLIENTES_ACTIVOS para verificar si hay clientes sin dirección
    try:
        df_check_direcciones = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'CLIENTES_ACTIVOS')
        clientes_sin_dir = df_check_direcciones[
            (df_check_direcciones['Dirección'].isna()) | 
            (df_check_direcciones['Dirección'] == '')
        ]
        clientes_sin_ciudad = df_check_direcciones[
            (df_check_direcciones['Ciudad'].isna()) | 
            (df_check_direcciones['Ciudad'] == '')
        ]
        
        if not clientes_sin_dir.empty or not clientes_sin_ciudad.empty:
            col_alerta1, col_alerta2 = st.columns(2)
            
            with col_alerta1:
                if not clientes_sin_dir.empty:
                    st.error(f"⚠️ **{len(clientes_sin_dir)} cliente(s) sin DIRECCIÓN**")
                    for idx, row in clientes_sin_dir.iterrows():
                        st.caption(f"• {row['Nombre Comercial']}")
            
            with col_alerta2:
                if not clientes_sin_ciudad.empty:
                    st.error(f"⚠️ **{len(clientes_sin_ciudad)} cliente(s) sin CIUDAD**")
                    for idx, row in clientes_sin_ciudad.iterrows():
                        st.caption(f"• {row['Nombre Comercial']}")
    except:
        pass
    
    # ===== MAPA DE GEOLOCALIZACIÓN - SOLO CLIENTES ACTIVOS =====
    st.markdown("### 🗺️ Geolocalización de Clientes Activos")
    
    # Leer CLIENTES_ACTIVOS Y INTERACCIONES - SIEMPRE FRESCOS
    df_clientes = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'CLIENTES_ACTIVOS')
    df_interacciones = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'INTERACCIONES')
    
    # Preparar datos para el mapa - LEER COORDENADAS DE EXCEL (SIN REQUESTS)
    mapa_datos = []
    
    for idx, row in df_clientes.iterrows():
        # Validar que la dirección Y la ciudad no estén vacías (igual que el selector)
        direccion = row.get('Dirección', '')
        ciudad = row.get('Ciudad', '')
        
        # Solo incluir en el mapa si tiene AMBAS: Dirección y Ciudad
        if (pd.isna(direccion) or direccion == '') or (pd.isna(ciudad) or ciudad == ''):
            continue
        
        nombre = row.get('Nombre Comercial', 'Sin nombre')
        id_cliente = row.get('ID', None)
        encargado = row.get('Encargado', 'No asignado')
        contrato = row.get('Servicio Contratado', 'Sin contrato')
        
        # Buscar próxima acción en INTERACCIONES
        proxima_accion = 'Sin acción pendiente'
        if not df_interacciones.empty and id_cliente is not None:
            interacciones_cliente = df_interacciones[df_interacciones['ID Cliente'] == id_cliente]
            if not interacciones_cliente.empty:
                # Filtrar las que tienen próxima acción
                con_proxima = interacciones_cliente[interacciones_cliente['Próxima Acción'].notna()]
                if not con_proxima.empty:
                    proxima_accion = str(con_proxima.iloc[-1]['Próxima Acción'])
        
        # LEER COORDENADAS DEL EXCEL
        lat = row.get('Latitud', None)
        lon = row.get('Longitud', None)
        
        # Si no hay coordenadas guardadas O son coordenadas genéricas de Madrid, geocodificar la dirección
        es_madrid_generico = (lat == 40.4168 and lon == -3.7038) or pd.isna(lat) or pd.isna(lon)
        
        if es_madrid_generico:
            try:
                from geopy.geocoders import Nominatim
                
                geolocator = Nominatim(user_agent="horeca_crm", timeout=3)
                # Construir dirección completa para geocodificación
                direccion_completa = f"{direccion.strip()}, {ciudad.strip()}, España"
                
                try:
                    location = geolocator.geocode(direccion_completa, language='es')
                    if location:
                        lat = location.latitude
                        lon = location.longitude
                    else:
                        # Si no encuentra, usar centro de la ciudad
                        ciudades_cache = {'madrid': (40.4168, -3.7038), 'barcelona': (41.3874, 2.1686), 'valencia': (39.4699, -0.3763)}
                        ciudad_lower = ciudad.lower().strip() if isinstance(ciudad, str) else ''
                        lat, lon = ciudades_cache.get(ciudad_lower, (40.4168, -3.7038))
                except Exception as e_geo:
                    # Fallback a caché
                    ciudades_cache = {'madrid': (40.4168, -3.7038), 'barcelona': (41.3874, 2.1686), 'valencia': (39.4699, -0.3763)}
                    ciudad_lower = ciudad.lower().strip() if isinstance(ciudad, str) else ''
                    lat, lon = ciudades_cache.get(ciudad_lower, (40.4168, -3.7038))
            except ImportError:
                # Si no tiene geopy, usar caché
                ciudades_cache = {'madrid': (40.4168, -3.7038), 'barcelona': (41.3874, 2.1686), 'valencia': (39.4699, -0.3763)}
                ciudad_lower = ciudad.lower().strip() if isinstance(ciudad, str) else ''
                lat, lon = ciudades_cache.get(ciudad_lower, (40.4168, -3.7038))
        
        mapa_datos.append({
            'lat': lat,
            'lon': lon,
            'nombre': nombre,
            'direccion': direccion,
            'ciudad': ciudad,
            'encargado': encargado,
            'contrato': contrato,
            'proxima_accion': proxima_accion
        })
    
    if mapa_datos:
        # Crear mapa
        try:
            import folium
            from streamlit_folium import st_folium
            
            # Calcular centro del mapa
            lats = [d['lat'] for d in mapa_datos]
            lons = [d['lon'] for d in mapa_datos]
            center_lat = sum(lats) / len(lats) if lats else 40.4168
            center_lon = sum(lons) / len(lons) if lons else -3.7038
            
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=13,
                tiles="OpenStreetMap"
            )
            
            for dato in mapa_datos:
                # Todos son Clientes Activos - color verde
                color_pin = 'green'
                
                # Crear tooltip enriquecido con HTML
                tooltip_html = f"""
                <div style="font-family: Arial; font-size: 13px; line-height: 1.8; min-width: 200px;">
                    <b>🏪 {dato['nombre']}</b><br>
                    <b>👤 Encargado:</b> {dato['encargado']}<br>
                    <b>⚙️ Contrato:</b> {dato['contrato']}<br>
                    <b>📅 Próxima Acción:</b> {dato['proxima_accion']}
                </div>
                """
                
                folium.CircleMarker(
                    location=[dato['lat'], dato['lon']],
                    radius=10,
                    popup=f"<b>{dato['nombre']}</b><br>📍 {dato['direccion']}<br>🏙️ {dato['ciudad']}",
                    tooltip=folium.Tooltip(tooltip_html, sticky=True),
                    color=color_pin,
                    fill=True,
                    fillColor=color_pin,
                    fillOpacity=0.7
                ).add_to(m)
            
            # Mostrar mapa
            col_mapa, col_info = st.columns([3, 1])
            
            with col_mapa:
                st_folium(m, width=700, height=400)
            
            with col_info:
                st.markdown("**Información del Mapa:**")
                st.metric("✅ Clientes Activos", len(mapa_datos))
                
                sin_direccion = len(df_clientes) - len(mapa_datos)
                if sin_direccion > 0:
                    st.warning(f"⚠️ {sin_direccion} cliente(s) sin dirección")
                    # Mostrar cuáles son
                    clientes_sin_dir = df_clientes[
                        (df_clientes['Dirección'].isna()) | (df_clientes['Dirección'] == '')
                    ]['Nombre Comercial'].tolist()
                    if clientes_sin_dir:
                        st.caption("Sin dirección:")
                        for cliente_sin_dir in clientes_sin_dir:
                            st.caption(f"• {cliente_sin_dir}")
        except ImportError:
            st.warning("⚠️ Instala 'geopy' para usar geocodificación: pip install geopy")
    else:
        st.warning("⚠️ No hay direcciones registradas para mostrar en el mapa")
    
    # Debug: mostrar qué clientes no tienen datos completos
    with st.expander("🔍 Debug: Clientes incompletos"):
        clientes_incompletos = []
        for idx, row in df_clientes.iterrows():
            direccion = row.get('Dirección', '')
            ciudad = row.get('Ciudad', '')
            nombre = row.get('Nombre Comercial', 'Sin nombre')
            
            if (pd.isna(direccion) or direccion == ''):
                clientes_incompletos.append(f"• {nombre}: **Sin Dirección**")
            if (pd.isna(ciudad) or ciudad == ''):
                clientes_incompletos.append(f"• {nombre}: **Sin Ciudad**")
        
        if clientes_incompletos:
            st.write("**Clientes sin datos completos:**")
            for item in clientes_incompletos:
                st.write(item)
        else:
            st.success("✅ Todos los clientes tienen datos completos")
    
    # ===== KANBAN SEMANAL - PRÓXIMAS ACCIONES =====
    st.markdown("### 📋 Kanban Semanal - Próximas Acciones")
    
    # Botón para añadir nueva acción
    col_titulo, col_boton = st.columns([4, 1])
    with col_boton:
        if st.button("➕ Nueva Acción", use_container_width=True):
            st.session_state['mostrar_modal_accion'] = True
    
    # Leer interacciones (ya se leyó arriba, reutilizar)
    if 'df_interacciones' not in locals():
        try:
            df_interacciones = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'INTERACCIONES')
        except:
            df_interacciones = pd.DataFrame()
    
    if not df_interacciones.empty:
        from datetime import datetime, timedelta
        
        # Filtrar solo las que tienen Próxima Acción
        df_acciones = df_interacciones[df_interacciones['Próxima Acción'].notna()].copy()
        
        if not df_acciones.empty:
            hoy = datetime.now().date()
            
            # Agrupar por urgencia
            vencidas = []
            hoy_acciones = []
            esta_semana = []
            proximamente = []
            
            for idx, row in df_acciones.iterrows():
                fecha_accion = row.get('Fecha Próxima Acción', None)
                
                if pd.notna(fecha_accion):
                    try:
                        if isinstance(fecha_accion, str):
                            fecha_accion = pd.to_datetime(fecha_accion).date()
                        elif hasattr(fecha_accion, 'date'):
                            fecha_accion = fecha_accion.date()
                        
                        dias_diferencia = (fecha_accion - hoy).days
                        
                        if dias_diferencia < 0:
                            vencidas.append(row)
                        elif dias_diferencia == 0:
                            hoy_acciones.append(row)
                        elif dias_diferencia <= 7:
                            esta_semana.append(row)
                        else:
                            proximamente.append(row)
                    except:
                        proximamente.append(row)
                else:
                    proximamente.append(row)
            
            # Crear 4 columnas para el Kanban
            col1, col2, col3, col4 = st.columns(4)
            
            grupos = [
                (col1, "🔴 Vencidas", vencidas, "#FF4444"),
                (col2, "🟠 Hoy", hoy_acciones, "#FFAA00"),
                (col3, "🟡 Esta Semana", esta_semana, "#FFD700"),
                (col4, "🟢 Próximamente", proximamente, "#4CAF50")
            ]
            
            for col, titulo, acciones, color in grupos:
                with col:
                    st.markdown(f"**{titulo}** ({len(acciones)})")
                    st.markdown("---")
                    
                    if acciones:
                        # Leer clientes activos para obtener encargados
                        try:
                            df_clientes_encargados = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'CLIENTES_ACTIVOS')
                            dict_encargados = dict(zip(df_clientes_encargados['ID'], df_clientes_encargados['Encargado']))
                        except:
                            dict_encargados = {}
                        
                        for idx_list, accion in enumerate(acciones):
                            cliente = accion.get('Nombre Cliente', 'Sin cliente')
                            descripcion_accion = accion.get('Próxima Acción', 'Sin descripción')
                            fecha = accion.get('Fecha Próxima Acción', '')
                            tipo = accion.get('Tipo', 'General')
                            id_accion = accion.get('ID Interacción', None)
                            completada = accion.get('Completada', False)
                            id_cliente = accion.get('ID Cliente', None)
                            
                            # Obtener encargado del cliente
                            encargado = dict_encargados.get(id_cliente, 'Sin asignar')
                            
                            # Formatear fecha
                            if pd.notna(fecha):
                                try:
                                    if isinstance(fecha, str):
                                        fecha_dt = pd.to_datetime(fecha)
                                    else:
                                        fecha_dt = fecha
                                    fecha_str = fecha_dt.strftime('%d/%m/%Y')
                                except:
                                    fecha_str = str(fecha)
                            else:
                                fecha_str = 'Sin fecha'
                            
                            # Crear card con botones interactivos
                            import hashlib
                            key_base = f"{id_accion}|{id_cliente}|{fecha_str}|{descripcion_accion}|{idx_list}"
                            key_suffix = hashlib.md5(key_base.encode("utf-8")).hexdigest()[:10]
                            col_card, col_acciones = st.columns([4, 1])
                            
                            with col_card:
                                estado_check = "✅" if completada else "⭕"
                                st.markdown(
                                    f"""
                                    <div style="
                                        border-left: 4px solid {color};
                                        padding: 10px;
                                        margin: 8px 0;
                                        background-color: {'#e8f5e9' if completada else '#f9f9f9'};
                                        border-radius: 4px;
                                        opacity: {'0.6' if completada else '1'};
                                    ">
                                        <strong><span style="font-size: 14px;">🏢</span> {cliente}</strong><br>
                                        <small><span style="font-size: 12px;">👤</span> {encargado}</small><br>
                                        <small><span style="font-size: 12px;">📝</span> {descripcion_accion}</small><br>
                                        <small><span style="font-size: 12px;">📅</span> {fecha_str} | <span style="font-size: 12px;">🏷️</span> {tipo}</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            with col_acciones:
                                col_check, col_delete = st.columns(2)
                                
                                with col_check:
                                    if st.button(
                                        "✅" if not completada else "↩️",
                                        key=f"check_{key_suffix}",
                                        help="Marcar como completada" if not completada else "Desmarcar",
                                        use_container_width=True
                                    ):
                                        try:
                                            # Leer interacciones
                                            df_int_actualizar = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'INTERACCIONES')
                                            
                                            # Actualizar fila
                                            mask = df_int_actualizar['ID Interacción'] == id_accion
                                            df_int_actualizar.loc[mask, 'Completada'] = not completada
                                            
                                            # Guardar
                                            if utils.escribir_excel(config.ARCHIVO_CRM, 'INTERACCIONES', df_int_actualizar):
                                                st.success("✅ Actualizado" if not completada else "↩️ Desmarcado")
                                                time.sleep(0.5)
                                                st.rerun()
                                            else:
                                                st.error("Error al guardar")
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                                
                                with col_delete:
                                    if st.button(
                                        "🗑️",
                                        key=f"delete_{key_suffix}",
                                        help="Eliminar acción",
                                        use_container_width=True
                                    ):
                                        st.session_state[f'confirmar_delete_{id_accion}'] = True
                                
                                # Confirmación de eliminación
                                if st.session_state.get(f'confirmar_delete_{id_accion}', False):
                                    st.warning(f"¿Eliminar esta acción?")
                                    col_si, col_no = st.columns(2)
                                    
                                    with col_si:
                                        if st.button("Sí, eliminar", key=f"confirm_yes_{key_suffix}"):
                                            try:
                                                df_int_eliminar = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'INTERACCIONES')
                                                df_int_eliminar = df_int_eliminar[df_int_eliminar['ID Interacción'] != id_accion]
                                                
                                                if utils.escribir_excel(config.ARCHIVO_CRM, 'INTERACCIONES', df_int_eliminar):
                                                    st.success("🗑️ Eliminado")
                                                    st.session_state[f'confirmar_delete_{id_accion}'] = False
                                                    time.sleep(0.5)
                                                    st.rerun()
                                                else:
                                                    st.error("Error al eliminar")
                                            except Exception as e:
                                                st.error(f"Error: {str(e)}")
                                    
                                    with col_no:
                                        if st.button("No, cancelar", key=f"confirm_no_{key_suffix}"):
                                            st.session_state[f'confirmar_delete_{id_accion}'] = False
                                            st.rerun()
                    else:
                        st.markdown('<div style="padding: 20px; text-align: center; color: #999;">—</div>', 
                                   unsafe_allow_html=True)
        else:
            st.info("📝 No hay próximas acciones registradas.")
    else:
        st.info("📝 No hay interacciones registradas. Accede a 'Próximas Acciones' para crear nuevas.")
    
    # ===== MODAL PARA AÑADIR NUEVA ACCIÓN =====
    if st.session_state.get('mostrar_modal_accion', False):
        with st.form(key='form_nueva_accion_kanban'):
            st.markdown("### ➕ Añadir Nueva Acción")
            
            # Leer clientes activos
            try:
                df_clientes = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'CLIENTES_ACTIVOS')
                opciones_clientes = df_clientes['Nombre Comercial'].tolist()
                ids_clientes = df_clientes['ID'].tolist()
                dict_clientes = dict(zip(opciones_clientes, ids_clientes))
            except:
                opciones_clientes = []
                dict_clientes = {}
                st.error("No se pudieron cargar los clientes activos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cliente_seleccionado = st.selectbox(
                    "Cliente *",
                    options=opciones_clientes,
                    help="Selecciona el cliente para esta acción"
                )
                
                tipo_accion = st.selectbox(
                    "Tipo de Acción *",
                    options=['Llamada', 'Email', 'Reunión', 'Visita', 'Seguimiento', 'Otro'],
                    help="Tipo de acción a realizar"
                )
            
            with col2:
                fecha_accion = st.date_input(
                    "Fecha Próxima Acción *",
                    value=datetime.now().date(),
                    help="¿Cuándo se debe realizar esta acción?"
                )
                
                prioridad = st.selectbox(
                    "Prioridad",
                    options=['Alta', 'Media', 'Baja'],
                    index=1
                )
            
            descripcion_accion = st.text_area(
                "Descripción de la Acción *",
                placeholder="Describe qué hay que hacer...",
                help="Detalla la acción a realizar"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button("✅ Guardar Acción", use_container_width=True)
            with col_btn2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submit:
                if cliente_seleccionado and descripcion_accion:
                    try:
                        # Leer interacciones
                        try:
                            df_interacciones = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'INTERACCIONES')
                        except:
                            df_interacciones = pd.DataFrame(columns=[
                                'ID Interacción', 'ID Cliente', 'Nombre Cliente', 'Fecha',
                                'Tipo', 'Resultado', 'Descripción', 'Próxima Acción', 'Fecha Próxima Acción',
                                'Responsable', 'Prioridad', 'Completada', 'Fecha Fin Prevista', 'ID'
                            ])
                        
                        # Crear nueva interacción
                        nuevo_id = int(df_interacciones['ID Interacción'].max()) + 1 if not df_interacciones.empty else 1
                        id_cliente = dict_clientes.get(cliente_seleccionado, None)
                        
                        nueva_accion = pd.DataFrame([{
                            'ID Interacción': nuevo_id,
                            'ID Cliente': id_cliente,
                            'Nombre Cliente': cliente_seleccionado,
                            'Fecha': datetime.now().strftime('%Y-%m-%d'),
                            'Tipo': tipo_accion,
                            'Resultado': '',
                            'Descripción': descripcion_accion,
                            'Próxima Acción': descripcion_accion,
                            'Fecha Próxima Acción': fecha_accion.strftime('%Y-%m-%d'),
                            'Responsable': st.session_state.get('usuario', 'Sistema'),
                            'Prioridad': prioridad,
                            'Completada': False,
                            'Fecha Fin Prevista': '',
                            'ID': nuevo_id
                        }])
                        
                        # Concatenar
                        df_interacciones = pd.concat([df_interacciones, nueva_accion], ignore_index=True)
                        
                        # Guardar
                        if utils.escribir_excel(config.ARCHIVO_CRM, 'INTERACCIONES', df_interacciones):
                            st.success("✅ Acción añadida correctamente")
                            st.session_state['mostrar_modal_accion'] = False
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar la acción")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Completa todos los campos obligatorios (*)")
            
            if cancel:
                st.session_state['mostrar_modal_accion'] = False
                st.rerun()
    
    st.markdown("---")
    
    # Fila 2: Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribución de Leads por Estado")
        # Forzar recálculo con datos frescos
        df_leads = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'LEADS')
        if not df_leads.empty and 'Estado' in df_leads.columns:
            estados = df_leads['Estado'].value_counts()
            st.bar_chart(estados)
        else:
            st.info("No hay datos de leads todavía")
    
    with col2:
        st.subheader("📅 Próximas Acciones")
        mostrar_proximas_acciones_dashboard()
    
    st.markdown("---")
    
 
# ============================================================================
# FUNCIÓN: PRÓXIMAS ACCIONES (DASHBOARD)
# ============================================================================

def mostrar_proximas_acciones_dashboard():
    """Muestra las próximas acciones en el dashboard"""
    try:
        df_int = utils.leer_excel(config.ARCHIVO_CRM, "INTERACCIONES")
        
        if df_int.empty or 'Próxima Acción' not in df_int.columns:
            st.info("Sin acciones programadas")
            return
        
        # Filtrar solo con próxima acción
        df_acciones = df_int[
            (df_int['Próxima Acción'].notna()) & 
            (df_int['Próxima Acción'] != '')
        ].copy()
        
        if df_acciones.empty:
            st.info("✅ Sin acciones pendientes")
            return
        
        # Calcular urgencia
        hoy = datetime.now().date()
        
        def calcular_urgencia(fecha):
            if pd.isna(fecha):
                return 4
            try:
                fecha_dt = pd.to_datetime(fecha).date()
                dias = (fecha_dt - hoy).days
                if dias < 0:
                    return 1  # Vencida
                elif dias == 0:
                    return 2  # Hoy
                elif dias <= 7:
                    return 3  # Esta semana
                else:
                    return 4  # Futura
            except:
                return 4
        
        df_acciones['Urgencia'] = df_acciones['Fecha Próxima Acción'].apply(calcular_urgencia)
        df_acciones = df_acciones.sort_values('Urgencia')
        
        # VENCIDAS
        vencidas = df_acciones[df_acciones['Urgencia'] == 1]
        if not vencidas.empty:
            st.error(f"🔴 **{len(vencidas)} VENCIDAS**")
            for _, row in vencidas.iterrows():
                st.write(f"  • **{row.get('Nombre Cliente', 'N/A')}** - {row.get('Próxima Acción', 'N/A')}")
        
        # HOY
        hoy_acciones = df_acciones[df_acciones['Urgencia'] == 2]
        if not hoy_acciones.empty:
            st.warning(f"🟡 **{len(hoy_acciones)} PARA HOY**")
            for _, row in hoy_acciones.iterrows():
                st.write(f"  • **{row.get('Nombre Cliente', 'N/A')}** - {row.get('Próxima Acción', 'N/A')}")
        
        # ESTA SEMANA
        semana = df_acciones[df_acciones['Urgencia'] == 3]
        if not semana.empty:
            st.info(f"🟢 **{len(semana)} ESTA SEMANA**")
            for _, row in semana.iterrows():
                try:
                    fecha = pd.to_datetime(row.get('Fecha Próxima Acción')).strftime('%d/%m')
                except:
                    fecha = str(row.get('Fecha Próxima Acción', 'N/A'))
                st.write(f"  • **{fecha}** - {row.get('Nombre Cliente', 'N/A')} - {row.get('Próxima Acción', 'N/A')}")
        
        # PRÓXIMAMENTE
        futuras = df_acciones[df_acciones['Urgencia'] == 4]
        if not futuras.empty:
            with st.expander(f"🔵 {len(futuras)} PRÓXIMAMENTE"):
                for _, row in futuras.iterrows():
                    try:
                        fecha = pd.to_datetime(row.get('Fecha Próxima Acción')).strftime('%d/%m')
                    except:
                        fecha = str(row.get('Fecha Próxima Acción', 'N/A'))
                    st.write(f"  • **{fecha}** - {row.get('Nombre Cliente', 'N/A')} - {row.get('Próxima Acción', 'N/A')}")
        
        if len(vencidas) == 0 and len(hoy_acciones) == 0 and len(semana) == 0 and len(futuras) == 0:
            st.success("✅ Todo al día")
    
    except Exception as e:
        st.warning(f"⚠️ Error al cargar acciones: {str(e)}")

# ============================================================================
# MÓDULO: CLIENTES
# ============================================================================
def modulo_crm():
    pass

# ============================================================================
# MÓDULO: ESCANDALLOS
# ============================================================================

def modulo_escandallos():
    """Módulo de gestión de escandallos y carta - Por Cliente"""
    st.markdown('<h1 class="main-header">🍽️ Gestión de Escandallos</h1>', unsafe_allow_html=True)
    
    # Cargar TODOS los clientes (lectura forzada sin caché)
    df_clientes_todos = utils.leer_excel_forzado(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
    
    # Filtrar SOLO clientes ACTIVOS para el selector
    if 'Estado' in df_clientes_todos.columns:
        df_clientes = df_clientes_todos[df_clientes_todos['Estado'] == 'Activo'].copy()
    else:
        df_clientes = df_clientes_todos.copy()
    
    if df_clientes.empty or len(df_clientes) == 0:
        st.warning("⚠️ No hay clientes activos.")
        
        # Mostrar info si hay clientes pausados/baja
        if not df_clientes_todos.empty:
            pausados = len(df_clientes_todos[df_clientes_todos['Estado'] == 'Pausado']) if 'Estado' in df_clientes_todos.columns else 0
            bajas = len(df_clientes_todos[df_clientes_todos['Estado'] == 'Baja']) if 'Estado' in df_clientes_todos.columns else 0
            
            if pausados > 0 or bajas > 0:
                st.info(f"ℹ️ Tienes {pausados} cliente(s) pausado(s) y {bajas} de baja. Sus datos se conservan y volverán a aparecer aquí si los reactivas desde CRM → Pausados/Baja.")
        
        st.info("💡 **Cómo empezar:**")
        st.write("1. Ve a **CRM → Leads**")
        st.write("2. Agrega un Lead o cambia el estado de uno existente a **'Cliente'**")
        st.write("3. El sistema lo convertirá automáticamente a Cliente Activo")
        st.write("4. Vuelve aquí para gestionar sus escandallos")
        return
    
    # ========== SELECTOR DE CLIENTE ==========
    st.markdown("### 👤 Selecciona el Cliente")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # Solo mostrar clientes ACTIVOS
        opciones_clientes = [f"{row['ID']} - {row['Nombre Comercial']}" 
                            for _, row in df_clientes.iterrows()]
        
        # Recordar el cliente seleccionado
        if 'cliente_escandallo_actual' not in st.session_state:
            st.session_state.cliente_escandallo_actual = 0
        
        # Validar que el índice no se salga de rango
        indice_default = min(st.session_state.cliente_escandallo_actual, len(opciones_clientes) - 1)
        
        cliente_seleccionado = st.selectbox(
            "Trabajar con:",
            opciones_clientes,
            index=indice_default,
            key="selector_cliente_escandallos",
            help="Solo se muestran clientes ACTIVOS. Los datos de pausados/baja se conservan."
        )
        
        # Guardar índice seleccionado
        st.session_state.cliente_escandallo_actual = opciones_clientes.index(cliente_seleccionado)
        
        id_cliente = int(float(cliente_seleccionado.split(" - ")[0]))
        nombre_cliente = cliente_seleccionado.split(" - ")[1]
    
    with col2:
        # Info del cliente
        cliente_info = df_clientes[df_clientes['ID'] == id_cliente].iloc[0]
        st.metric("Tipo", cliente_info.get('Tipo Local', 'N/A'))
    
    with col3:
        st.metric("Ciudad", cliente_info.get('Ciudad', 'N/A'))
    
    st.markdown("---")
    
    # ========== TABS DEL CLIENTE ==========
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🍴 Carta", 
        "🔍 Escandallos", 
        "📊 Ingredientes", 
        "💰 Compras",
        "💵 Simulador Precios",
        "🛒 Pedido Inteligente",
        "🎯 Ingeniería de Menú",
        "📄 Informes PDF"
    ])
    
    with tab1:
        mostrar_carta_cliente(id_cliente, nombre_cliente)
    
    with tab2:
        mostrar_escandallos_cliente(id_cliente, nombre_cliente)
    
    with tab3:
        mostrar_ingredientes_cliente(id_cliente, nombre_cliente)
    
    with tab4:
        mostrar_compras_cliente(id_cliente, nombre_cliente)
    
    with tab5:
        mostrar_simulador_precios(id_cliente, nombre_cliente)
    
    with tab6:
        mostrar_pedido_inteligente(id_cliente, nombre_cliente)
    
    with tab7:
        mostrar_ingenieria_menu(id_cliente, nombre_cliente)
        mostrar_compras_cliente(id_cliente, nombre_cliente)
    
    with tab8:
        mostrar_informes_pdf(id_cliente, nombre_cliente)

def mostrar_carta_cliente(id_cliente, nombre_cliente):
    """Carta del cliente seleccionado"""
    st.subheader(f"🍴 Carta de {nombre_cliente}")
    
    # Cargar platos solo de este cliente
    df_carta_completa = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_carta = df_carta_completa[df_carta_completa['ID Cliente'] == id_cliente] if not df_carta_completa.empty else pd.DataFrame()
    
    # Botón agregar
    if st.button("➕ Agregar Plato a la Carta", type="primary", key="btn_agregar_plato"):
        st.session_state.agregar_plato = True
    
    # Formulario nuevo plato
    if st.session_state.get('agregar_plato', False):
        with st.expander("➕ **Nuevo Plato**", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_plato = st.text_input("Nombre del Plato*", 
                    placeholder="Ej: Cachopo de ternera", 
                    key="nombre_plato_form",
                    help="Nombre que sale en la carta")
                
                categoria = st.selectbox("Categoría*", config.CATEGORIAS_PLATO, key="cat_plato_form")
                
                precio_venta = st.number_input("Precio de Venta (€)*", 
                    min_value=0.0, value=0.0, step=0.5, format="%.2f", 
                    key="precio_plato_form",
                    help="IVA INCLUIDO")
            
            with col2:
                coste_total = st.number_input("Coste Total (€)", 
                    min_value=0.0, value=0.0, step=0.1, format="%.2f",
                    help="Suma automática de ingredientes desde escandallos", 
                    key="coste_plato_form",
                    disabled=True)  # Deshabilitado porque se calcula automáticamente
                
                ventas_mes = st.number_input("Ventas/Mes Estimadas", 
                    min_value=0, value=0, step=5, key="ventas_plato_form")
                
                activo = st.selectbox("Estado", ["Activo", "Inactivo"], key="activo_plato_form")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Guardar", use_container_width=True, type="primary", key="btn_guardar_plato"):
                    if not nombre_plato:
                        st.error("El nombre es obligatorio")
                    elif precio_venta <= 0:
                        st.error("El precio debe ser mayor que 0")
                    else:
                        nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
                        
                        margen_euros = precio_venta - coste_total
                        margen_pct = (margen_euros / precio_venta * 100) if precio_venta > 0 else 0
                        food_cost = (coste_total / precio_venta * 100) if precio_venta > 0 else 0
                        
                        if margen_pct >= 60 and ventas_mes >= 50:
                            clasificacion = "Estrella"
                        elif margen_pct >= 60 and ventas_mes < 50:
                            clasificacion = "Rompecabezas"
                        elif margen_pct < 60 and ventas_mes >= 50:
                            clasificacion = "Caballo"
                        else:
                            clasificacion = "Perro"
                        
                        # Convertir "Activo"/"Inactivo" a "Sí"/"No" para compatibilidad
                        activo_valor = "Sí" if activo == "Activo" else "No"
                        
                        nuevo_plato = {
                            'ID Plato': nuevo_id,
                            'ID Cliente': id_cliente,
                            'Nombre Cliente': nombre_cliente,
                            'Nombre Plato': nombre_plato,
                            'Categoría': categoria,
                            'Precio Venta': precio_venta,
                            'Coste Total': coste_total,
                            'Margen €': margen_euros,
                            'Margen %': margen_pct,
                            'Food Cost %': food_cost,
                            'Ventas/Mes': ventas_mes,
                            'Clasificación': clasificacion,
                            'Precio Recomendado': coste_total * 3 if coste_total > 0 else precio_venta * 1.5,
                            'Activo': activo_valor,
                            'Notas': ''
                        }
                        
                        if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", nuevo_plato):
                            st.success(f"✅ '{nombre_plato}' agregado")
                            st.info("💡 Ahora ve a la pestaña 'Escandallos' para agregar ingredientes")
                            st.session_state.agregar_plato = False
                            time.sleep(0.5)
                            st.rerun()
            with col2:
                if st.button("❌ Cancelar", use_container_width=True, key="btn_cancelar_plato"):
                    st.session_state.agregar_plato = False
                    st.rerun()
    
    # Mostrar tabla de platos guardados
    st.markdown("---")
    st.subheader("Platos en la Carta")
    
    if not df_carta.empty:
        # Convertir "Sí"/"No" a "Activo"/"Inactivo" para mostrar
        df_carta_display = df_carta.copy()
        if 'Activo' in df_carta_display.columns:
            df_carta_display['Activo'] = df_carta_display['Activo'].apply(
                lambda x: "Activo" if x == "Sí" else "Inactivo"
            )
        
        # ALERTAS: Food Cost incorrecto
        platos_alerta = []
        for _, plato in df_carta.iterrows():
            if plato['Coste Total'] > 0 and plato['Precio Venta'] > 0:
                food_cost = (plato['Coste Total'] / plato['Precio Venta']) * 100
                if food_cost > 35:
                    precio_recomendado = (plato['Coste Total'] / 0.28) if plato['Coste Total'] > 0 else plato['Precio Venta'] * 1.5
                    platos_alerta.append({
                        'nombre': plato['Nombre Plato'],
                        'food_cost': food_cost,
                        'precio_actual': plato['Precio Venta'],
                        'precio_recomendado': precio_recomendado,
                        'id_plato': plato['ID Plato']
                    })
        
        if platos_alerta:
            st.subheader("🚨 ALERTAS - Precios Incorrectos")
            for alerta in platos_alerta:
                col_alerta1, col_alerta2 = st.columns([4, 1.2])
                with col_alerta1:
                    st.error(f"⚠️ **{alerta['nombre']}** - Precio actual: {alerta['precio_actual']:.2f}€ → Recomendado: **{alerta['precio_recomendado']:.2f}€**")
                with col_alerta2:
                    if st.button("💾 Actualizar", key=f"update_alert_{alerta['id_plato']}", use_container_width=True):
                        df_carta_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
                        mask = df_carta_temp['ID Plato'] == alerta['id_plato']
                        coste_total = float(df_carta_temp.loc[mask, 'Coste Total'].values[0] or 0)
                        nuevo_precio = alerta['precio_recomendado']
                        margen_euros = nuevo_precio - coste_total
                        margen_pct = (margen_euros / nuevo_precio * 100) if nuevo_precio > 0 else 0
                        food_cost = (coste_total / nuevo_precio * 100) if nuevo_precio > 0 else 0
                        
                        if margen_pct >= 60:
                            clasificacion = "Estrella" if df_carta_temp.loc[mask, 'Ventas/Mes'].values[0] >= 50 else "Rompecabezas"
                        else:
                            clasificacion = "Caballo" if df_carta_temp.loc[mask, 'Ventas/Mes'].values[0] >= 50 else "Perro"
                        
                        df_carta_temp.loc[mask, 'Precio Venta'] = nuevo_precio
                        df_carta_temp.loc[mask, 'Margen €'] = margen_euros
                        df_carta_temp.loc[mask, 'Margen %'] = margen_pct
                        df_carta_temp.loc[mask, 'Food Cost %'] = food_cost
                        df_carta_temp.loc[mask, 'Clasificación'] = clasificacion
                        df_carta_temp.loc[mask, 'Precio Recomendado'] = nuevo_precio
                        
                        if utils.escribir_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", df_carta_temp):
                            st.success(f"✅ {alerta['nombre']} actualizado a {nuevo_precio:.2f}€")
                            time.sleep(0.5)
                            st.rerun()
            
            # ========== ENVÍO A WHATSAPP ==========
            st.markdown("---")
            st.subheader("📱 Enviar Alertas por WhatsApp")
            
            # Obtener número de teléfono del cliente
            df_clientes_all = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
            cliente_info = df_clientes_all[df_clientes_all['ID'] == id_cliente]
            
            if not cliente_info.empty:
                numero_telefono = cliente_info.iloc[0].get('Teléfono', '')
                
                if numero_telefono and numero_telefono != '':
                    from whatsapp_sender import mostrar_boton_enviar_whatsapp
                    mostrar_boton_enviar_whatsapp(
                        nombre_cliente,
                        numero_telefono,
                        platos_alerta,
                        id_cliente=id_cliente,
                        key_suffix=f"{id_cliente}"
                    )
                else:
                    st.warning("⚠️ Este cliente no tiene teléfono registrado")
                    st.info("📱 Actualiza el teléfono en 👥 Clientes para poder enviar alertas por WhatsApp")
            
            st.markdown("---")
        
        # Métricas rápidas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Platos", len(df_carta))
        with col2:
            activos = len(df_carta[df_carta['Activo'] == 'Sí'])
            st.metric("Activos", activos)
        with col3:
            if 'Margen %' in df_carta.columns:
                margen_medio = df_carta['Margen %'].mean()
                st.metric("Margen Medio", f"{margen_medio:.1f}%")
        with col4:
            if 'Clasificación' in df_carta.columns:
                estrellas = len(df_carta[df_carta['Clasificación'] == 'Estrella'])
                st.metric("⭐ Estrellas", estrellas)
        
        st.markdown("---")
        
        # Listado con botones por fila
        for _, plato in df_carta.iterrows():
            col_a, col_b, col_c, col_d, col_e, col_f = st.columns([3, 1.5, 1.5, 1.2, 0.5, 0.5])
            
            with col_a:
                estado_icon = "✅" if plato.get('Activo') == 'Sí' else "⏸️"
                clasificacion_icon = {"Estrella": "⭐", "Caballo": "🐴", "Rompecabezas": "🧩", "Perro": "🐕"}.get(plato.get('Clasificación', ''), '')
                st.write(f"{estado_icon} **{plato['Nombre Plato']}** {clasificacion_icon}")
                st.caption(f"{plato.get('Categoría', '')}")
            
            with col_b:
                st.write(f"**{plato['Precio Venta']:.2f}€**")
                st.caption(f"Coste: {plato['Coste Total']:.2f}€")
            
            with col_c:
                st.write(f"Margen: {plato['Margen %']:.1f}%")
                st.caption(f"Ventas: {plato.get('Ventas/Mes', 0)}/mes")
            
            with col_d:
                st.write(f"{plato.get('Clasificación', '')}")
                st.caption(f"Recom.: {plato.get('Precio Recomendado', 0):.2f}€")
            
            with col_e:
                if st.button("✏️", key=f"edit_plato_{plato['ID Plato']}", help="Editar plato"):
                    st.session_state.editando_plato = plato['ID Plato']
            
            with col_f:
                if st.button("🗑️", key=f"del_plato_{plato['ID Plato']}", help="Eliminar plato"):
                    st.session_state.eliminar_plato = plato['ID Plato']
            
            # Edición inline
            if st.session_state.get('editando_plato') == plato['ID Plato']:
                st.markdown("---")
                st.markdown(f"**✏️ Editando: {plato['Nombre Plato']}**")
                col_e1, col_e2, col_e3 = st.columns(3)
                
                with col_e1:
                    nuevo_precio = st.number_input(
                        "Precio Venta (€)",
                        min_value=0.01,
                        value=float(plato['Precio Venta']),
                        step=0.5,
                        format="%.2f",
                        key=f"edit_precio_{plato['ID Plato']}"
                    )
                    nuevo_estado = st.selectbox(
                        "Estado",
                        ["Activo", "Inactivo"],
                        index=0 if plato['Activo'] == 'Sí' else 1,
                        key=f"edit_estado_{plato['ID Plato']}"
                    )
                
                with col_e2:
                    nuevas_ventas = st.number_input(
                        "Ventas/Mes",
                        min_value=0,
                        value=int(plato.get('Ventas/Mes', 0) or 0),
                        step=5,
                        key=f"edit_ventas_{plato['ID Plato']}"
                    )
                    st.caption(f"Coste Total: {plato['Coste Total']:.2f}€ (calculado)")
                
                with col_e3:
                    st.write("")
                    if st.button("💾 Guardar", key=f"save_plato_{plato['ID Plato']}"):
                        df_carta_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
                        mask = df_carta_temp['ID Plato'] == plato['ID Plato']
                        coste_total = float(df_carta_temp.loc[mask, 'Coste Total'].values[0] or 0)
                        margen_euros = nuevo_precio - coste_total
                        margen_pct = (margen_euros / nuevo_precio * 100) if nuevo_precio > 0 else 0
                        food_cost = (coste_total / nuevo_precio * 100) if nuevo_precio > 0 else 0
                        
                        if margen_pct >= 60 and nuevas_ventas >= 50:
                            clasificacion = "Estrella"
                        elif margen_pct >= 60 and nuevas_ventas < 50:
                            clasificacion = "Rompecabezas"
                        elif margen_pct < 60 and nuevas_ventas >= 50:
                            clasificacion = "Caballo"
                        else:
                            clasificacion = "Perro"
                        
                        # Precio recomendado apuntando a 28% Food Cost (🟢 verde)
                        precio_recomendado = (coste_total / 0.28) if coste_total > 0 else nuevo_precio * 1.5
                        
                        df_carta_temp.loc[mask, 'Precio Venta'] = nuevo_precio
                        df_carta_temp.loc[mask, 'Ventas/Mes'] = nuevas_ventas
                        df_carta_temp.loc[mask, 'Activo'] = "Sí" if nuevo_estado == "Activo" else "No"
                        df_carta_temp.loc[mask, 'Margen €'] = margen_euros
                        df_carta_temp.loc[mask, 'Margen %'] = margen_pct
                        df_carta_temp.loc[mask, 'Food Cost %'] = food_cost
                        df_carta_temp.loc[mask, 'Clasificación'] = clasificacion
                        df_carta_temp.loc[mask, 'Precio Recomendado'] = precio_recomendado
                        
                        if utils.escribir_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", df_carta_temp):
                            st.success("✅ Plato actualizado")
                            st.session_state.editando_plato = None
                            time.sleep(0.5)
                            st.rerun()
                    if st.button("❌ Cancelar", key=f"cancel_plato_{plato['ID Plato']}"):
                        st.session_state.editando_plato = None
                        st.rerun()
            
            # Eliminar
            if st.session_state.get('eliminar_plato') == plato['ID Plato']:
                st.warning("¿Eliminar este plato?")
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    if st.button("Sí, eliminar", key=f"confirm_del_{plato['ID Plato']}"):
                        df_carta_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
                        df_carta_temp = df_carta_temp[df_carta_temp['ID Plato'] != plato['ID Plato']]
                        if utils.escribir_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", df_carta_temp):
                            st.success("🗑️ Plato eliminado")
                            st.session_state.eliminar_plato = None
                            time.sleep(0.5)
                            st.rerun()
                with col_del2:
                    if st.button("No, cancelar", key=f"cancel_del_{plato['ID Plato']}"):
                        st.session_state.eliminar_plato = None
                        st.rerun()
    else:
        st.info("🍽️ No hay platos registrados. ¡Agrega el primero!")

def mostrar_escandallos_cliente(id_cliente, nombre_cliente):
    """Escandallos del cliente seleccionado"""
    st.subheader(f"🔍 Escandallos de {nombre_cliente}")
    
    df_esc_completo = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
    df_platos_completo = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_ing = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
    
    # Filtrar platos de este cliente
    df_platos = df_platos_completo[df_platos_completo['ID Cliente'] == id_cliente] if not df_platos_completo.empty else pd.DataFrame()
    
    if df_platos.empty:
        st.warning(f"⚠️ {nombre_cliente} no tiene platos. Agrega platos en la pestaña 'Carta' primero.")
        return
    
    # Lista de platos del cliente
    platos_cliente = [f"{row['ID Plato']} - {row['Nombre Plato']}" for _, row in df_platos.iterrows()]
    ingredientes_disp = [f"{row['ID Ingrediente']} - {row['Nombre']}" for _, row in df_ing.iterrows()] if not df_ing.empty else []
    
    # Selector de plato
    col1, col2 = st.columns([3, 1])
    with col1:
        plato_ver = st.selectbox("Ver escandallo de:", ["📋 Todos"] + platos_cliente, key="ver_escandallo")
    with col2:
        st.caption("Edición en bloque")
    
    # Mostrar escandallos
    st.markdown("---")
    
    # Filtrar escandallos por platos del cliente
    ids_platos_cliente = df_platos['ID Plato'].tolist()
    df_esc = df_esc_completo[df_esc_completo['ID Plato'].isin(ids_platos_cliente)] if not df_esc_completo.empty else pd.DataFrame()
    
    if plato_ver == "📋 Todos":
        if not df_esc.empty:
            st.dataframe(df_esc, use_container_width=True, hide_index=True)
        else:
            st.info("🔍 No hay escandallos. Selecciona un plato para empezar.")
        return
    
    id_plato_filtro = int(float(plato_ver.split(" - ")[0]))
    plato_info = df_platos[df_platos['ID Plato'] == id_plato_filtro].iloc[0]
    nombre_plato = plato_info.get('Nombre Plato', '')
    
    df_esc_plato = df_esc[df_esc['ID Plato'] == id_plato_filtro].copy() if not df_esc.empty else pd.DataFrame()
    
    # ===== PVP + MÉTRICAS =====
    precio_venta_actual = float(plato_info.get('Precio Venta', 0))
    col_pvp, col_coste, col_margen, col_food = st.columns(4)
    
    with col_pvp:
        pvp = st.number_input(
            "💵 PVP (con IVA)",
            min_value=0.01,
            value=precio_venta_actual if precio_venta_actual > 0 else 0.01,
            step=0.5,
            format="%.2f",
            key=f"pvp_plato_{id_plato_filtro}"
        )
        if abs(pvp - precio_venta_actual) > 0.001:
            if st.button("💾 Guardar PVP", key=f"guardar_pvp_{id_plato_filtro}"):
                df_carta_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
                mask = df_carta_temp['ID Plato'] == id_plato_filtro
                df_carta_temp.loc[mask, 'Precio Venta'] = pvp
                utils.escribir_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", df_carta_temp)
                st.success("✅ PVP actualizado")
                time.sleep(0.3)
                st.rerun()
    
    # ===== PRECIOS CLIENTE + SUB-RECETAS =====
    df_precios_cliente = utils.leer_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
    df_precios_cliente = df_precios_cliente[df_precios_cliente['ID Cliente'] == id_cliente] if not df_precios_cliente.empty else pd.DataFrame()
    
    opciones = {}
    if not df_precios_cliente.empty:
        for _, row in df_precios_cliente.iterrows():
            label = f"ING|{row['ID Ingrediente']} - {row['Nombre Ingrediente']}"
            # Merma del ingrediente (nivel base). Si no existe, usar 0%.
            merma_base = float(row.get('Merma %', 0)) if 'Merma %' in row and pd.notna(row.get('Merma %')) else 0.0
            rendimiento_base = max(0.0, 100.0 - merma_base)
            
            opciones[label] = {
                'tipo': 'ingrediente',
                'id': row['ID Ingrediente'],
                'nombre': row['Nombre Ingrediente'],
                'precio': row['Precio Cliente'],
                'unidad': row['Unidad'],
                'merma': merma_base,
                'rendimiento': rendimiento_base,
                'id_proveedor': row.get('ID Proveedor')
            }
    
    for _, row in df_platos.iterrows():
        if row['ID Plato'] != id_plato_filtro:
            label = f"REC|{row['ID Plato']} - {row['Nombre Plato']}"
            opciones[label] = {
                'tipo': 'subreceta',
                'id': row['ID Plato'],
                'nombre': f"SUB-RECETA: {row['Nombre Plato']}",
                'precio': float(row.get('Coste Total', 0)),
                'unidad': 'ud',
                'merma': 0.0,
                'rendimiento': 100.0,  # Las sub-recetas siempre tienen 100% de rendimiento
                'id_proveedor': None
            }
    
    opciones_labels = [""] + list(opciones.keys())
    
    # ===== CONSTRUIR LISTA DE INGREDIENTES ACTUALES =====
    ingredientes_actuales = []
    if not df_esc_plato.empty:
        for idx, row in df_esc_plato.iterrows():
            id_ing = row.get('ID Ingrediente')
            nombre_ing = str(row.get('Nombre Ingrediente', ''))
            label = None
            if nombre_ing.startswith("SUB-RECETA") and id_ing is not None:
                label = f"REC|{id_ing} - {nombre_ing.replace('SUB-RECETA:', '').strip()}"
            else:
                label = f"ING|{id_ing} - {nombre_ing}"
            
            if label not in opciones:
                # Si no está en opciones, crear entrada con datos del escandallo
                rendimiento_guardado = row.get('Rendimiento %', row.get('Rendimiento_Pct', 100))
                rendimiento_guardado = 100 if rendimiento_guardado in [None, 0, ""] else float(rendimiento_guardado)
                merma_guardada = max(0.0, 100.0 - rendimiento_guardado)
                
                opciones[label] = {
                    'tipo': 'ingrediente',
                    'id': id_ing,
                    'nombre': nombre_ing,
                    'precio': row.get('Coste Unitario', 0),
                    'unidad': row.get('Unidad', ''),
                    'merma': merma_guardada,
                    'rendimiento': rendimiento_guardado,
                    'id_proveedor': row.get('ID Proveedor')
                }
                if label not in opciones_labels:
                    opciones_labels.append(label)
            
            # Usar el rendimiento del ingrediente base (de opciones)
            rendimiento = opciones[label].get('rendimiento', 100)
            merma_pct = opciones[label].get('merma', 0)
            precio_unit = opciones[label]['precio'] if label in opciones else row.get('Coste Unitario', 0)
            
            # CANTIDAD NETA: Lo que dice la receta (lo que está guardado)
            cantidad_neta = float(row.get('Cantidad', 0))
            
            # CANTIDAD BRUTA: Lo que se descuenta del stock = Neta / (Rendimiento/100)
            cantidad_bruta = cantidad_neta / (rendimiento / 100) if rendimiento > 0 else cantidad_neta
            
            # COSTE REAL: Precio × Cantidad Bruta
            coste_real = cantidad_bruta * precio_unit
            
            ingredientes_actuales.append({
                'idx': idx,
                'Ingrediente': label,
                'Cantidad_Neta': cantidad_neta,  # Lo que va en el plato
                'Cantidad_Bruta': cantidad_bruta,  # Lo que se descuenta del stock
                'Unidad': opciones[label].get('unidad', row.get('Unidad', '')),
                'Precio Unitario': float(precio_unit) if precio_unit is not None else 0,
                'Merma_Pct': float(merma_pct),
                'Rendimiento_Pct': float(rendimiento),
                'Coste Real': float(coste_real)
            })
    
    # Calcular totales
    coste_total = sum([ing['Coste Real'] for ing in ingredientes_actuales])
    base_imponible = pvp / 1.10
    margen_neto = base_imponible - coste_total
    food_cost_pct = (coste_total / base_imponible * 100) if base_imponible > 0 else 0
    # Precio recomendado apuntando a 28% Food Cost (🟢 verde)
    precio_recomendado = (coste_total / 0.28) if coste_total > 0 else pvp * 1.5
    ingredientes_count = len(ingredientes_actuales)
    
    with col_coste:
        st.metric("💰 Coste Total", f"{coste_total:.2f} €")
    with col_margen:
        st.metric("💵 Margen Neto", f"{margen_neto:.2f} €")
    with col_food:
        if food_cost_pct > 35:
            st.markdown(f"<h3 style='color: red;'>🔴 {food_cost_pct:.1f}%</h3>", unsafe_allow_html=True)
        elif food_cost_pct >= 30:
            st.markdown(f"<h3 style='color: orange;'>🟠 {food_cost_pct:.1f}%</h3>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h3 style='color: green;'>🟢 {food_cost_pct:.1f}%</h3>", unsafe_allow_html=True)
        st.caption("Food Cost %")
    
    # EXPLICACIÓN FOOD COST - Pequeño expander a la izquierda
    with st.expander("📖 ¿Cómo se calcula el Food Cost %?"):
        st.markdown("""
        **Cálculo del Food Cost %**
        
        `Food Cost % = (Coste Total / Base Imponible) × 100`
        
        - **Coste Total**: Suma ingredientes (con merma)
        - **Base Imponible**: PVP ÷ 1.10
        
        **Umbrales:**
        - 🟢 < 30%: Excelente
        - 🟠 30-35%: Aceptable
        - 🔴 > 35%: Revisar
        """)
    
    st.markdown("---")
    
    # TARJETA RESUMEN DEL ESCANDALLO
    st.markdown(
        f"""
        <div class="metric-card">
            <strong>📋 Escandallo actual de: {nombre_plato}</strong><br/>
            🥘 Ingredientes: {ingredientes_count}<br/>
            💰 Coste Total: {coste_total:.2f}€<br/>
            💵 Precio Venta: {pvp:.2f}€<br/>
            📊 Margen: {((pvp - coste_total) / pvp * 100) if pvp > 0 else 0:.1f}%<br/>
            💡 Precio Recomendado: {precio_recomendado:.2f}€
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # LISTA DE INGREDIENTES EN FORMATO VISUAL
    st.subheader("🥘 Ingredientes del Escandallo")
    
    # Botón para agregar ingrediente
    if st.button("➕ Agregar Ingrediente", type="primary", key=f"btn_add_ing_{id_plato_filtro}"):
        st.session_state[f'agregar_ingrediente_{id_plato_filtro}'] = True
    
    # Formulario para agregar nuevo ingrediente
    if st.session_state.get(f'agregar_ingrediente_{id_plato_filtro}', False):
        with st.expander("➕ **Nuevo Ingrediente**", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_ing = st.selectbox(
                    "Ingrediente*",
                    opciones_labels,
                    key=f"nuevo_ing_sel_{id_plato_filtro}",
                    help="Selecciona un ingrediente o sub-receta"
                )
            
            with col2:
                nueva_cantidad_neta = st.number_input(
                    "Cantidad Neta (en el plato)*",
                    min_value=0.01,
                    value=1.0,
                    step=0.1,
                    format="%.3f",
                    key=f"nueva_cantidad_{id_plato_filtro}",
                    help="Peso neto que lleva el plato según la receta"
                )
            
            # Mostrar info del ingrediente seleccionado
            if nuevo_ing and nuevo_ing in opciones:
                info = opciones[nuevo_ing]
                merma_ing = info.get('merma', 0)
                rendimiento_ing = max(0.0, 100.0 - merma_ing)
                cantidad_bruta_calc = nueva_cantidad_neta / (rendimiento_ing / 100) if rendimiento_ing > 0 else nueva_cantidad_neta
                coste_calc = cantidad_bruta_calc * info.get('precio', 0)
                
                st.info(f"""
                📊 **Cálculo automático:**
                - Merma del ingrediente: **{merma_ing:.0f}%** (Rendimiento: {rendimiento_ing:.0f}%)
                - Cantidad Bruta (a descontar): **{cantidad_bruta_calc:.3f} {info.get('unidad', '')}**
                - Coste Real: **{coste_calc:.3f}€**
                """)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 Guardar", type="primary", use_container_width=True, key=f"guardar_nuevo_ing_{id_plato_filtro}"):
                    if not nuevo_ing or nuevo_ing == "":
                        st.error("Debes seleccionar un ingrediente")
                    else:
                        info = opciones.get(nuevo_ing)
                        merma_base = info.get('merma', 0)
                        rendimiento_base = max(0.0, 100.0 - merma_base)
                        precio_unit = float(info.get('precio', 0) or 0)
                        cantidad_bruta = nueva_cantidad_neta / (rendimiento_base / 100) if rendimiento_base > 0 else nueva_cantidad_neta
                        coste_real = cantidad_bruta * precio_unit
                        
                        nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                        nueva_fila = {
                            'ID Escandallo': nuevo_id,
                            'ID Plato': id_plato_filtro,
                            'Nombre Plato': nombre_plato,
                            'ID Ingrediente': info.get('id'),
                            'Nombre Ingrediente': info.get('nombre'),
                            'Cantidad': nueva_cantidad_neta,  # Guardamos la cantidad NETA
                            'Unidad': info.get('unidad'),
                            'Coste Unitario': precio_unit,
                            'Rendimiento %': rendimiento_base,  # Guardamos el rendimiento del ingrediente
                            'Coste Total': coste_real,
                            '% del Plato': 0,
                            'ID Proveedor': info.get('id_proveedor'),
                            'Última Actualización': datetime.now().date()
                        }
                        
                        if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", nueva_fila):
                            utils.recalcular_costes_platos(utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS"))
                            st.success("✅ Ingrediente agregado")
                            st.session_state[f'agregar_ingrediente_{id_plato_filtro}'] = False
                            time.sleep(0.5)
                            st.rerun()
            
            with col_btn2:
                if st.button("❌ Cancelar", use_container_width=True, key=f"cancelar_nuevo_ing_{id_plato_filtro}"):
                    st.session_state[f'agregar_ingrediente_{id_plato_filtro}'] = False
                    st.rerun()
    
    st.markdown("---")
    
    if ingredientes_actuales:
        for ing in ingredientes_actuales:
            col_a, col_b, col_c, col_d, col_e, col_f = st.columns([4, 1.5, 1.5, 1.2, 0.5, 0.5])
            
            # Limpiar nombre del ingrediente
            ingrediente_nombre = str(ing['Ingrediente'])
            if ingrediente_nombre.startswith("REC|"):
                # Sub-receta: quitar REC|número - y dejar solo el nombre
                ingrediente_nombre = ingrediente_nombre.split(" - ", 1)[-1] if " - " in ingrediente_nombre else ingrediente_nombre.replace("REC|", "")
                ingrediente_nombre = f"🔁 {ingrediente_nombre}"
            elif ingrediente_nombre.startswith("ING|"):
                # Ingrediente: quitar ING|número - y dejar solo el nombre
                ingrediente_nombre = ingrediente_nombre.split(" - ", 1)[-1] if " - " in ingrediente_nombre else ingrediente_nombre.replace("ING|", "")
            else:
                ingrediente_nombre = ingrediente_nombre.split(" - ", 1)[-1] if " - " in ingrediente_nombre else ingrediente_nombre
            
            with col_a:
                st.write(f"**{ingrediente_nombre}**")
                st.caption(f"{ing.get('Unidad', '')}")
            
            with col_b:
                # Mostrar CANTIDAD NETA (receta) y CANTIDAD BRUTA (stock)
                st.write(f"📋 Neta: {ing.get('Cantidad_Neta', 0):.3f} {ing.get('Unidad', '')}")
                st.caption(f"📦 Bruta: {ing.get('Cantidad_Bruta', 0):.3f} {ing.get('Unidad', '')}")
            
            with col_c:
                merma_val = ing.get('Merma_Pct', 0)
                rendimiento_val = max(0.0, 100.0 - merma_val)
                if merma_val > 0:
                    st.write(f"🔻 Merma {merma_val:.0f}%")
                    st.caption(f"Rend.: {rendimiento_val:.0f}%")
                else:
                    st.write("✅ Sin merma")
                    st.caption("Rend. 100%")
            
            with col_d:
                st.write(f"**{ing.get('Coste Real', 0):.3f}€**")
                pct_del_plato = (ing.get('Coste Real', 0) / coste_total * 100) if coste_total > 0 else 0
                st.caption(f"{pct_del_plato:.1f}% del plato")
            
            with col_e:
                if st.button("✏️", key=f"edit_ing_{id_plato_filtro}_{ing['idx']}", help="Editar ingrediente"):
                    st.session_state[f'editando_ingrediente_{id_plato_filtro}'] = ing['idx']
            
            with col_f:
                if st.button("🗑️", key=f"del_ing_{id_plato_filtro}_{ing['idx']}", help="Eliminar ingrediente"):
                    st.session_state[f'eliminar_ingrediente_{id_plato_filtro}'] = ing['idx']
            
            # Edición inline
            if st.session_state.get(f'editando_ingrediente_{id_plato_filtro}') == ing['idx']:
                st.markdown("---")
                st.markdown(f"**✏️ Editando: {ingrediente_nombre}**")
                col_e1, col_e2 = st.columns(2)
                
                with col_e1:
                    edit_ing = st.selectbox(
                        "Ingrediente",
                        opciones_labels,
                        index=opciones_labels.index(ing['Ingrediente']) if ing['Ingrediente'] in opciones_labels else 0,
                        key=f"edit_ing_sel_{id_plato_filtro}_{ing['idx']}"
                    )
                
                with col_e2:
                    edit_cantidad_neta = st.number_input(
                        "Cantidad Neta (en el plato)",
                        min_value=0.01,
                        value=float(ing['Cantidad_Neta']),
                        step=0.1,
                        format="%.3f",
                        key=f"edit_cant_{id_plato_filtro}_{ing['idx']}",
                        help="Peso neto que lleva el plato según la receta"
                    )
                
                # Mostrar info calculada
                if edit_ing and edit_ing in opciones:
                    info_edit = opciones[edit_ing]
                    merma_edit = info_edit.get('merma', 0)
                    rendimiento_edit = max(0.0, 100.0 - merma_edit)
                    cantidad_bruta_edit = edit_cantidad_neta / (rendimiento_edit / 100) if rendimiento_edit > 0 else edit_cantidad_neta
                    coste_edit = cantidad_bruta_edit * info_edit.get('precio', 0)
                    
                    st.info(f"""
                    📊 **Cálculo automático:**
                    - Merma: **{merma_edit:.0f}%** (Rendimiento: {rendimiento_edit:.0f}%)
                    - Cantidad Bruta: **{cantidad_bruta_edit:.3f} {info_edit.get('unidad', '')}**
                    - Coste Real: **{coste_edit:.3f}€**
                    """)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Guardar", type="primary", use_container_width=True, key=f"save_ing_{id_plato_filtro}_{ing['idx']}"):
                        df_esc_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                        mask = df_esc_temp.index == ing['idx']
                        
                        info = opciones.get(edit_ing)
                        merma_base = info.get('merma', 0)
                        rendimiento_base = max(0.0, 100.0 - merma_base)
                        precio_unit = float(info.get('precio', 0) or 0)
                        cantidad_bruta = edit_cantidad_neta / (rendimiento_base / 100) if rendimiento_base > 0 else edit_cantidad_neta
                        coste_real = cantidad_bruta * precio_unit
                        
                        df_esc_temp.loc[mask, 'ID Ingrediente'] = info.get('id')
                        df_esc_temp.loc[mask, 'Nombre Ingrediente'] = info.get('nombre')
                        df_esc_temp.loc[mask, 'Cantidad'] = edit_cantidad_neta  # Guardamos cantidad NETA
                        df_esc_temp.loc[mask, 'Unidad'] = info.get('unidad')
                        df_esc_temp.loc[mask, 'Coste Unitario'] = precio_unit
                        df_esc_temp.loc[mask, 'Rendimiento %'] = rendimiento_base  # Rendimiento del ingrediente
                        df_esc_temp.loc[mask, 'Coste Total'] = coste_real
                        df_esc_temp.loc[mask, 'ID Proveedor'] = info.get('id_proveedor')
                        df_esc_temp.loc[mask, 'Última Actualización'] = datetime.now().date()
                        
                        if utils.escribir_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", df_esc_temp):
                            utils.recalcular_costes_platos(df_esc_temp)
                            st.success("✅ Ingrediente actualizado")
                            st.session_state[f'editando_ingrediente_{id_plato_filtro}'] = None
                            time.sleep(0.5)
                            st.rerun()
                
                with col_btn2:
                    if st.button("❌ Cancelar", use_container_width=True, key=f"cancel_ing_{id_plato_filtro}_{ing['idx']}"):
                        st.session_state[f'editando_ingrediente_{id_plato_filtro}'] = None
                        st.rerun()
            
            # Confirmación de eliminación
            if st.session_state.get(f'eliminar_ingrediente_{id_plato_filtro}') == ing['idx']:
                st.warning(f"⚠️ ¿Eliminar **{ingrediente_nombre}**?")
                col_conf1, col_conf2 = st.columns(2)
                with col_conf1:
                    if st.button("✅ Sí, eliminar", type="primary", use_container_width=True, key=f"confirm_del_{id_plato_filtro}_{ing['idx']}"):
                        df_esc_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                        df_esc_temp = df_esc_temp.drop(index=ing['idx']).reset_index(drop=True)
                        
                        if utils.escribir_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", df_esc_temp):
                            utils.recalcular_costes_platos(df_esc_temp)
                            st.success("✅ Ingrediente eliminado")
                            st.session_state[f'eliminar_ingrediente_{id_plato_filtro}'] = None
                            time.sleep(0.5)
                            st.rerun()
                
                with col_conf2:
                    if st.button("❌ Cancelar", use_container_width=True, key=f"cancel_del_{id_plato_filtro}_{ing['idx']}"):
                        st.session_state[f'eliminar_ingrediente_{id_plato_filtro}'] = None
                        st.rerun()
            
            st.markdown("---")
    else:
        st.info("No hay ingredientes en este escandallo. Haz clic en ➕ Agregar Ingrediente para empezar.")
    
    st.markdown("---")
    
    # ===== PARETO COSTES =====
    st.subheader("📊 Pareto de Costes")
    
    if ingredientes_actuales:
        df_pareto_data = []
        for ing in ingredientes_actuales:
            ingrediente_nombre = str(ing['Ingrediente']).replace("ING|", "").replace("REC|", "SUB-RECETA: ")
            ingrediente_nombre = ingrediente_nombre.split(" - ")[-1] if " - " in ingrediente_nombre else ingrediente_nombre
            
            df_pareto_data.append({
                'Ingrediente': ingrediente_nombre,
                'Coste Real': ing['Coste Real']
            })
        
        df_pareto = pd.DataFrame(df_pareto_data)
        df_pareto = df_pareto[df_pareto['Coste Real'] > 0].copy()
        
        if not df_pareto.empty:
            df_pareto['% Coste'] = (df_pareto['Coste Real'] / df_pareto['Coste Real'].sum() * 100).round(1)
            try:
                import plotly.express as px
                fig = px.bar(
                    df_pareto,
                    x='Ingrediente',
                    y='% Coste',
                    text='% Coste',
                    title='Peso porcentual por ingrediente'
                )
                fig.update_traces(texttemplate='%{text}%', textposition='outside')
                fig.update_layout(height=350, xaxis_title='', yaxis_title='% del coste')
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                st.dataframe(df_pareto[['Ingrediente', 'Coste Real', '% Coste']], hide_index=True, use_container_width=True)
        else:
            st.info("No hay costes para analizar.")
    else:
        st.info("No hay ingredientes para analizar.")

def mostrar_compras_cliente(id_cliente, nombre_cliente):
    """Compras del cliente seleccionado"""
    st.subheader(f"💰 Compras de {nombre_cliente}")
    
    df_compras_completo = utils.leer_excel(config.ARCHIVO_OPERACIONES, "COMPRAS_CLIENTE")
    df_compras = df_compras_completo[df_compras_completo['ID Cliente'] == id_cliente] if not df_compras_completo.empty else pd.DataFrame()
    
    if not df_compras.empty:
        st.dataframe(df_compras, use_container_width=True, hide_index=True)
    else:
        st.info(f"💰 {nombre_cliente} no tiene compras registradas todavía.")

def mostrar_simulador_precios(id_cliente, nombre_cliente):
    """Simulador de cambios de precio por plato"""
    st.subheader(f"💵 Simulador de Precios - {nombre_cliente}")
    
    st.info("🎯 **¿Qué pasa si subo/bajo el precio de un plato?** Simula el impacto en tu beneficio considerando la posible caída de demanda.")
    
    # Cargar carta del cliente
    df_carta_completa = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_carta = df_carta_completa[df_carta_completa['ID Cliente'] == id_cliente] if not df_carta_completa.empty else pd.DataFrame()
    
    if df_carta.empty:
        st.warning(f"⚠️ {nombre_cliente} no tiene platos en la carta. Ve al tab 'Carta' para agregar.")
        return
    
    # Filtrar solo platos activos
    if 'Activo' in df_carta.columns:
        df_carta = df_carta[df_carta['Activo'] == 'Sí']
    
    if df_carta.empty:
        st.warning("⚠️ No hay platos activos para simular.")
        return
    
    st.markdown("---")
    
    col_controles, col_resultados = st.columns([1, 2])
    
    with col_controles:
        st.markdown("### 🎛️ Parámetros de Simulación")
        
        # Selector de plato
        opciones_platos = [f"{row['ID Plato']} - {row['Nombre Plato']}" 
                          for _, row in df_carta.iterrows()]
        
        plato_seleccionado = st.selectbox(
            "Plato a Simular",
            opciones_platos,
            key=f"plato_sim_{id_cliente}"
        )
        
        id_plato = int(float(plato_seleccionado.split(" - ")[0]))
        plato_info = df_carta[df_carta['ID Plato'] == id_plato].iloc[0]
        
        st.markdown("---")
        
        # Datos actuales del plato
        precio_actual = float(plato_info.get('Precio Venta', 0))
        coste_actual = float(plato_info.get('Coste Total', 0))
        ventas_mes = int(plato_info.get('Ventas/Mes', 0))
        
        st.write("**📊 Datos Actuales:**")
        st.write(f"• Precio: {precio_actual:.2f}€")
        st.write(f"• Coste: {coste_actual:.2f}€")
        st.write(f"• Ventas/mes: {ventas_mes} uds")
        
        if ventas_mes == 0:
            st.warning("⚠️ No hay datos de ventas mensuales. Introduce un valor en la carta.")
            ventas_mes = st.number_input("Ventas/Mes Estimadas", min_value=1, value=100, step=10)
        
        st.markdown("---")
        st.markdown("### 🚀 Simulación de Cambio")
        
        # Cambio de precio propuesto
        cambio_precio = st.slider(
            "📈 Cambio de Precio (€)",
            min_value=-10.0,
            max_value=10.0,
            value=0.0,
            step=0.25,
            help="Positivo = subida, Negativo = bajada",
            key=f"cambio_precio_{id_cliente}"
        )
        
        # Caída/aumento de demanda esperada
        cambio_demanda = st.slider(
            "📉 Cambio en Demanda (%)",
            min_value=-50,
            max_value=50,
            value=-5 if cambio_precio > 0 else 5,
            step=5,
            help="Negativo = pierdes clientes, Positivo = ganas clientes",
            key=f"cambio_demanda_{id_cliente}"
        )
    
    with col_resultados:
        st.markdown("### 📊 Análisis de Impacto")
        
        # ESCENARIO ACTUAL
        margen_actual = precio_actual - coste_actual
        beneficio_mensual_actual = margen_actual * ventas_mes
        ingreso_actual = precio_actual * ventas_mes
        
        # ESCENARIO NUEVO
        precio_nuevo = precio_actual + cambio_precio
        volumen_nuevo = int(ventas_mes * (1 + cambio_demanda / 100))
        margen_nuevo = precio_nuevo - coste_actual
        beneficio_mensual_nuevo = margen_nuevo * volumen_nuevo
        ingreso_nuevo = precio_nuevo * volumen_nuevo
        
        # DIFERENCIAS
        incremento_beneficio = beneficio_mensual_nuevo - beneficio_mensual_actual
        porcentaje_incremento = (incremento_beneficio / beneficio_mensual_actual * 100) if beneficio_mensual_actual > 0 else 0
        
        # MÉTRICAS
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💰 Beneficio Actual",
                f"{beneficio_mensual_actual:.2f}€/mes",
                help=f"Margen: {margen_actual:.2f}€ × {ventas_mes} ventas"
            )
        
        with col2:
            st.metric(
                "🚀 Beneficio Proyectado",
                f"{beneficio_mensual_nuevo:.2f}€/mes",
                delta=f"{incremento_beneficio:+.2f}€ ({porcentaje_incremento:+.1f}%)",
                help=f"Margen: {margen_nuevo:.2f}€ × {volumen_nuevo} ventas"
            )
        
        with col3:
            anual = incremento_beneficio * 12
            st.metric(
                "📅 Impacto Anual",
                f"{anual:+.2f}€",
                help="Proyección a 12 meses"
            )
        
        st.markdown("---")
        
        # GRÁFICO COMPARATIVO
        try:
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            categorias = ['Actual', 'Propuesto']
            
            fig.add_trace(go.Bar(
                name='Ingresos',
                x=categorias,
                y=[ingreso_actual, ingreso_nuevo],
                marker_color='#2ecc71',
                text=[f"{ingreso_actual:.0f}€", f"{ingreso_nuevo:.0f}€"],
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='Costes',
                x=categorias,
                y=[coste_actual * ventas_mes, coste_actual * volumen_nuevo],
                marker_color='#e74c3c',
                text=[f"{coste_actual * ventas_mes:.0f}€", f"{coste_actual * volumen_nuevo:.0f}€"],
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='Beneficio',
                x=categorias,
                y=[beneficio_mensual_actual, beneficio_mensual_nuevo],
                marker_color='#3498db',
                text=[f"{beneficio_mensual_actual:.0f}€", f"{beneficio_mensual_nuevo:.0f}€"],
                textposition='outside'
            ))
            
            fig.update_layout(
                title='Comparativa: Actual vs Propuesto',
                xaxis_title='Escenario',
                yaxis_title='Importe (€)',
                barmode='group',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except ImportError:
            st.warning("📊 Instala plotly para ver gráficos: `pip install plotly`")
            
            # Tabla alternativa
            df_comparativa = pd.DataFrame({
                'Escenario': ['Actual', 'Propuesto'],
                'Precio': [f"{precio_actual:.2f}€", f"{precio_nuevo:.2f}€"],
                'Ventas': [ventas_mes, volumen_nuevo],
                'Ingresos': [f"{ingreso_actual:.2f}€", f"{ingreso_nuevo:.2f}€"],
                'Beneficio': [f"{beneficio_mensual_actual:.2f}€", f"{beneficio_mensual_nuevo:.2f}€"]
            })
            st.dataframe(df_comparativa, use_container_width=True, hide_index=True)
        
        # RECOMENDACIÓN
        st.markdown("---")
        st.markdown("### 💡 Recomendación")
        
        if incremento_beneficio > 0:
            st.success(f"✅ **FAVORABLE:** El cambio aumentaría tu beneficio en {incremento_beneficio:.2f}€/mes ({anual:.2f}€/año)")
        elif incremento_beneficio < 0:
            st.error(f"❌ **DESFAVORABLE:** El cambio reduciría tu beneficio en {abs(incremento_beneficio):.2f}€/mes ({abs(anual):.2f}€/año)")
        else:
            st.info("➖ **NEUTRO:** El cambio no afectaría significativamente tu beneficio")

def mostrar_pedido_inteligente(id_cliente, nombre_cliente):
    """Calculadora de Pedidos - Simplificada para Consultoría Quincenal"""
    st.subheader(f"🛒 Pedido Inteligente - {nombre_cliente}")
    
    st.info("📦 **Herramienta para tus visitas quincenales:** Actualiza stock, calcula pedido óptimo y guarda snapshot.")
    
    # Cargar inventario del cliente
    df_inventario = utils.obtener_inventario_cliente(id_cliente)
    
    # Si no tiene inventario
    if df_inventario.empty:
        st.warning(f"⚠️ {nombre_cliente} no tiene inventario configurado.")
        
        st.markdown("### 🚀 Primera Visita")
        st.write("Crea el inventario inicial con los datos que te dé el cliente.")
        
        if st.button("➕ Crear Inventario Inicial", type="primary", key=f"crear_inv_pedido_{id_cliente}"):
            st.session_state.crear_inventario_inicial = True
        
        if st.session_state.get('crear_inventario_inicial', False):
            st.markdown("---")
            mostrar_formulario_inventario_inicial(id_cliente, nombre_cliente)
        
        return
    
    # ========== INTERFAZ PRINCIPAL ==========
    st.markdown("---")
    
    col_edicion, col_calculo = st.columns([3, 2])
    
    with col_edicion:
        st.markdown("### ✏️ Actualizar Datos (Visita Quincenal)")
        
        # Tabla editable
        st.write("**Edita directamente:** stock actual y consumo semanal estimado")
        
        df_editable = df_inventario[[
            'ID Ingrediente',
            'Nombre Ingrediente',
            'Stock Actual',
            'Consumo Semanal',
            'Unidad',
            'Precio Unitario'
        ]].copy()
        
        # Editor de datos
        df_editado = st.data_editor(
            df_editable,
            column_config={
                "ID Ingrediente": st.column_config.NumberColumn(
                    "ID",
                    disabled=True,
                    width="small"
                ),
                "Nombre Ingrediente": st.column_config.TextColumn(
                    "Ingrediente",
                    disabled=True,
                    width="medium"
                ),
                "Stock Actual": st.column_config.NumberColumn(
                    "Stock Actual",
                    help="Lo que el cliente tiene AHORA",
                    min_value=0,
                    format="%.1f"
                ),
                "Consumo Semanal": st.column_config.NumberColumn(
                    "Consumo/Semana",
                    help="Promedio que gasta por semana",
                    min_value=0,
                    format="%.1f"
                ),
                "Unidad": st.column_config.TextColumn(
                    "Unidad",
                    disabled=True,
                    width="small"
                ),
                "Precio Unitario": st.column_config.NumberColumn(
                    "Precio €",
                    disabled=True,
                    format="%.2f",
                    width="small"
                )
            },
            hide_index=True,
            use_container_width=True,
            key="editor_inventario"
        )
        
        st.markdown("---")
        
        # Botones de acción
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Guardar Cambios", type="primary", use_container_width=True, key=f"guardar_cambios_pedido_{id_cliente}"):
                # Actualizar inventario completo
                df_actualizado = df_inventario.copy()
                df_actualizado['Stock Actual'] = df_editado['Stock Actual'].values
                df_actualizado['Consumo Semanal'] = df_editado['Consumo Semanal'].values
                df_actualizado['Última Actualización'] = datetime.now().date()
                
                if utils.guardar_inventario_cliente(df_actualizado):
                    st.success("✅ Inventario actualizado")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Error al guardar")
        
        with col2:
            if st.button("📸 Guardar Snapshot", use_container_width=True, help="Guarda estado actual para histórico", key=f"guardar_snapshot_pedido_{id_cliente}"):
                observaciones = f"Visita {datetime.now().strftime('%d/%m/%Y')}"
                if utils.guardar_snapshot(id_cliente, nombre_cliente, df_editado, observaciones):
                    st.success("✅ Snapshot guardado")
                    time.sleep(0.5)
                    st.rerun()
    
    with col_calculo:
        st.markdown("### 📊 Cálculo de Pedido")
        
        # Configuración
        periodo = st.selectbox(
            "📅 Periodo",
            ["1 Semana", "2 Semanas", "1 Mes"],
            index=1,
            key=f"periodo_pedido_{id_cliente}"
        )
        
        multiplicador = {"1 Semana": 1, "2 Semanas": 2, "1 Mes": 4}[periodo]
        
        crecimiento = st.slider(
            "📈 Crecimiento",
            -50, 100, 0, 5,
            help="% más/menos de lo normal",
            format="%d%%",
            key=f"crecimiento_pedido_{id_cliente}"
        )
        
        seguridad = st.slider(
            "🛡️ Seguridad",
            0, 50, 15, 5,
            help="Stock extra",
            format="%d%%",
            key=f"seguridad_pedido_{id_cliente}"
        )
        
        st.markdown("---")
        
        # Calcular pedido
        df_pedido = df_editado.copy()
        
        df_pedido['Consumo Previsto'] = (
            df_pedido['Consumo Semanal'] * 
            multiplicador * 
            (1 + crecimiento / 100)
        ).round(1)
        
        df_pedido['Pedido Sugerido'] = (
            df_pedido['Consumo Previsto'] * 
            (1 + seguridad / 100) - 
            df_pedido['Stock Actual']
        ).clip(lower=0).round(1)
        
        df_pedido['Coste'] = (
            df_pedido['Pedido Sugerido'] * 
            df_pedido['Precio Unitario']
        ).round(2)
        
        # Mostrar resultado
        st.markdown("**📦 Pedido Recomendado:**")
        
        df_resultado = df_pedido[df_pedido['Pedido Sugerido'] > 0][[
            'Nombre Ingrediente',
            'Pedido Sugerido',
            'Unidad',
            'Coste'
        ]].copy()
        
        if not df_resultado.empty:
            df_resultado.columns = ['Ingrediente', 'Cantidad', 'Unidad', 'Coste €']
            st.dataframe(df_resultado, hide_index=True, use_container_width=True)
            
            # Total
            total = df_resultado['Coste €'].sum()
            st.metric("💰 Total Pedido", f"{total:.2f}€")
            
            # Botón exportar
            if st.button("📄 Exportar a Excel", use_container_width=True, key=f"exportar_pedido_excel_{id_cliente}"):
                # Crear Excel en memoria
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_resultado.to_excel(writer, index=False, sheet_name='Pedido')
                    
                    # Info adicional
                    df_info = pd.DataFrame({
                        'Cliente': [nombre_cliente],
                        'Fecha': [datetime.now().strftime('%d/%m/%Y')],
                        'Periodo': [periodo],
                        'Total': [f"{total:.2f}€"]
                    })
                    df_info.to_excel(writer, index=False, sheet_name='Info')
                
                st.download_button(
                    label="⬇️ Descargar Excel",
                    data=output.getvalue(),
                    file_name=f"Pedido_{nombre_cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.success("✅ No necesita pedir nada. Stock suficiente.")
    
    # ========== HISTORIAL DE SNAPSHOTS ==========
    st.markdown("---")
    st.markdown("### 📅 Histórico de Visitas")
    
    df_snapshots = utils.obtener_snapshots_cliente(id_cliente, limite=10)
    
    if not df_snapshots.empty:
        # Agrupar por fecha
        fechas_unicas = df_snapshots['Fecha'].unique()
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.write(f"**{len(fechas_unicas)} visitas registradas**")
            
            for fecha in sorted(fechas_unicas, reverse=True)[:5]:
                fecha_str = pd.to_datetime(fecha).strftime('%d/%m/%Y')
                st.write(f"• {fecha_str}")
        
        with col2:
            # Gráfico de evolución (si hay suficientes datos)
            if len(fechas_unicas) >= 2:
                # Tomar primer ingrediente para ejemplo
                primer_ingrediente = df_snapshots['ID Ingrediente'].iloc[0]
                df_evol = df_snapshots[df_snapshots['ID Ingrediente'] == primer_ingrediente].copy()
                df_evol = df_evol.sort_values('Fecha')
                
                if len(df_evol) >= 2:
                    st.write(f"**Evolución: {df_evol['Nombre Ingrediente'].iloc[0]}**")
                    
                    fig_evol = go.Figure()
                    fig_evol.add_trace(go.Scatter(
                        x=df_evol['Fecha'],
                        y=df_evol['Stock'],
                        mode='lines+markers',
                        name='Stock',
                        line=dict(color='#3498db', width=2),
                        marker=dict(size=8)
                    ))
                    
                    fig_evol.update_layout(
                        height=200,
                        margin=dict(l=0, r=0, t=20, b=0),
                        showlegend=False,
                        xaxis_title="",
                        yaxis_title="Stock"
                    )
                    
                    st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("📝 No hay snapshots guardados. Usa el botón '📸 Guardar Snapshot' en cada visita.")

def mostrar_formulario_inventario_inicial(id_cliente, nombre_cliente):
    """Formulario simplificado para crear inventario inicial"""
    st.subheader("📦 Crear Inventario Inicial")
    
    st.write(f"**Cliente:** {nombre_cliente}")
    st.write("Introduce los datos que te dé el cliente en la primera visita.")
    
    # Obtener ingredientes con precios
    df_precios = utils.leer_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
    df_precios_cliente = df_precios[df_precios['ID Cliente'] == id_cliente] if not df_precios.empty else pd.DataFrame()
    
    if df_precios_cliente.empty:
        st.warning("⚠️ Primero asigna precios a ingredientes en el tab 'Ingredientes'")
        if st.button("◀️ Cancelar", key=f"cancelar_inv_form_{id_cliente}"):
            st.session_state.crear_inventario_inicial = False
            st.rerun()
        return
    
    with st.form("form_inventario_inicial"):
        st.write("### Ingredientes")
        
        inventario_data = []
        
        st.write("**Ingrediente | Stock Actual | Consumo/Semana | ✓**")
        
        for _, row in df_precios_cliente.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            
            with col1:
                st.write(f"**{row['Nombre Ingrediente']}**")
            
            with col2:
                stock = st.number_input(
                    "Stock",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key=f"stock_{row['ID Ingrediente']}",
                    label_visibility="collapsed"
                )
            
            with col3:
                consumo = st.number_input(
                    "Consumo",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                    key=f"consumo_{row['ID Ingrediente']}",
                    label_visibility="collapsed"
                )
            
            with col4:
                st.write(f"{row.get('Unidad', 'UDS')}")
            
            with col5:
                incluir = st.checkbox("✓", value=True, key=f"inc_{row['ID Ingrediente']}", label_visibility="collapsed")
            
            if incluir:
                inventario_data.append({
                    'ID Cliente': id_cliente,
                    'Nombre Cliente': nombre_cliente,
                    'ID Ingrediente': row['ID Ingrediente'],
                    'Nombre Ingrediente': row['Nombre Ingrediente'],
                    'Stock Actual': stock,
                    'Consumo Semanal': consumo,
                    'Unidad': row.get('Unidad', 'UDS'),
                    'Precio Unitario': row.get('Precio Cliente', 0),
                    'Última Actualización': datetime.now().date(),
                    'Notas': 'Inventario inicial'
                })
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Crear Inventario", use_container_width=True, type="primary")
        with col2:
            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submitted:
            if not inventario_data:
                st.error("❌ Selecciona al menos un ingrediente")
            else:
                # Crear DataFrame y guardar
                df_nuevo_inventario = pd.DataFrame(inventario_data)
                
                # Añadir IDs únicos
                for idx, row in df_nuevo_inventario.iterrows():
                    df_nuevo_inventario.at[idx, 'ID'] = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "INVENTARIO") + idx
                
                if utils.guardar_inventario_cliente(df_nuevo_inventario):
                    st.success(f"✅ Inventario creado con {len(inventario_data)} ingredientes")
                    st.session_state.crear_inventario_inicial = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Error al crear inventario")
        
        if cancelar:
            st.session_state.crear_inventario_inicial = False
            st.rerun()

def mostrar_ingenieria_menu(id_cliente, nombre_cliente):
    """Matriz de Ingeniería de Menú - Análisis Boston Consulting"""
    st.subheader(f"  Ingeniería de Menú - {nombre_cliente}")
    
    st.info("📊 **Análisis estratégico de tu carta** - Clasifica platos según rentabilidad y popularidad para tomar decisiones basadas en datos.")
    
    # Cargar carta del cliente
    df_carta_completa = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_carta = df_carta_completa[df_carta_completa['ID Cliente'] == id_cliente] if not df_carta_completa.empty else pd.DataFrame()
    
    if df_carta.empty:
        st.warning(f"⚠️ {nombre_cliente} no tiene platos en la carta. Ve al tab 'Carta' para agregar.")
        return
    
    # Filtrar solo platos activos con datos completos
    if 'Activo' in df_carta.columns:
        df_carta = df_carta[df_carta['Activo'] == 'Sí']
    
    # Verificar columnas necesarias
    columnas_necesarias = ['Precio Venta', 'Coste Total', 'Ventas/Mes']
    for col in columnas_necesarias:
        if col not in df_carta.columns:
            st.error(f"❌ Falta la columna '{col}' en la carta. Verifica la configuración.")
            return
    
    # Limpiar datos
    df_carta = df_carta.copy()
    df_carta['Precio Venta'] = pd.to_numeric(df_carta['Precio Venta'], errors='coerce').fillna(0)
    df_carta['Coste Total'] = pd.to_numeric(df_carta['Coste Total'], errors='coerce').fillna(0)
    df_carta['Ventas/Mes'] = pd.to_numeric(df_carta['Ventas/Mes'], errors='coerce').fillna(0)
    df_carta['Food Cost %'] = pd.to_numeric(df_carta['Food Cost %'], errors='coerce').fillna(0)
    
    # Filtrar platos con datos válidos
    df_carta = df_carta[
        (df_carta['Precio Venta'] > 0) & 
        (df_carta['Coste Total'] > 0) & 
        (df_carta['Ventas/Mes'] > 0)
    ]
    
    if df_carta.empty:
        st.warning("⚠️ No hay platos con datos completos (Precio, Coste, Ventas). Actualiza la carta primero.")
        return
    
    st.markdown("---")
    
    # ========== CÁLCULOS ==========
    
    # Calcular métricas
    df_carta['Margen'] = df_carta['Precio Venta'] - df_carta['Coste Total']
    df_carta['Margen %'] = (df_carta['Margen'] / df_carta['Precio Venta'] * 100).round(1)
    df_carta['Facturación'] = df_carta['Precio Venta'] * df_carta['Ventas/Mes']
    df_carta['Beneficio'] = df_carta['Margen'] * df_carta['Ventas/Mes']
    
    # Calcular promedios (líneas divisorias)
    ventas_media = df_carta['Ventas/Mes'].median()
    margen_medio = df_carta['Margen %'].median()
    
    # Clasificar en cuadrantes
    def clasificar_plato(row):
        if row['Ventas/Mes'] >= ventas_media and row['Margen %'] >= margen_medio:
            return '⭐ ESTRELLA'
        elif row['Ventas/Mes'] >= ventas_media and row['Margen %'] < margen_medio:
            return '🐴 CABALLO'
        elif row['Ventas/Mes'] < ventas_media and row['Margen %'] >= margen_medio:
            return '❓ ROMPECABEZAS'
        else:
            return '🐕 PERRO'
    
    df_carta['Cuadrante'] = df_carta.apply(clasificar_plato, axis=1)
    
    # Colores por cuadrante
    color_map = {
        '⭐ ESTRELLA': '#70AD47',      # Verde
        '🐴 CABALLO': '#4472C4',       # Azul
        '❓ ROMPECABEZAS': '#FFC000',  # Amarillo
        '🐕 PERRO': '#C00000'          # Rojo
    }
    
    df_carta['Color'] = df_carta['Cuadrante'].map(color_map)
    
    # ========== TABS PRINCIPALES ==========
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Matriz Simple",
        "🎯 Matriz Avanzada",
        "💡 Oportunidades",
        "🎯 Plan de Acción"
    ])
    
    # ========== TAB 1: MATRIZ SIMPLE ==========
    with tab1:
        col_grafico, col_resumen = st.columns([3, 2])
        st.markdown("### 📊 Matriz Boston Consulting")
        
        if PLOTLY_AVAILABLE:
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            # Añadir burbujas por cuadrante
            for cuadrante in df_carta['Cuadrante'].unique():
                df_cuad = df_carta[df_carta['Cuadrante'] == cuadrante]
                
                fig.add_trace(go.Scatter(
                    x=df_cuad['Ventas/Mes'],
                    y=df_cuad['Margen %'],
                    mode='markers+text',
                    name=cuadrante,
                    text=df_cuad['Nombre Plato'],
                    textposition='top center',
                    textfont=dict(size=10),
                    marker=dict(
                        size=df_cuad['Facturación'] / 50,  # Tamaño proporcional a facturación
                        color=df_cuad['Color'],
                        line=dict(width=2, color='white'),
                        opacity=0.8
                    ),
                    hovertemplate='<b>%{text}</b><br>' +
                                  'Ventas: %{x} uds/mes<br>' +
                                  'Margen: %{y}%<br>' +
                                  '<extra></extra>'
                ))
            
            # Líneas divisorias
            fig.add_hline(
                y=margen_medio, 
                line_dash="dash", 
                line_color="gray",
                annotation_text=f"Margen Medio: {margen_medio:.1f}%",
                annotation_position="right"
            )
            
            fig.add_vline(
                x=ventas_media, 
                line_dash="dash", 
                line_color="gray",
                annotation_text=f"Ventas Medias: {ventas_media:.0f} uds",
                annotation_position="top"
            )
            
            # Layout
            fig.update_layout(
                height=500,
                xaxis_title="Ventas/Mes (unidades)",
                yaxis_title="Margen (%)",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("📊 Instala plotly para ver el gráfico: `pip install plotly`")
            
            # Tabla alternativa
            df_display = df_carta[['Nombre Plato', 'Cuadrante', 'Ventas/Mes', 'Margen %']].copy()
            df_display = df_display.sort_values('Cuadrante')
            st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    with col_resumen:
        st.markdown("### 📈 Resumen General")
        
        # Métricas globales
        total_facturacion = df_carta['Facturación'].sum()
        total_beneficio = df_carta['Beneficio'].sum()
        margen_general = (total_beneficio / total_facturacion * 100) if total_facturacion > 0 else 0
        
        st.metric("💰 Facturación/Mes", f"{total_facturacion:.2f}€")
        st.metric("💵 Beneficio/Mes", f"{total_beneficio:.2f}€")
        st.metric("📊 Margen General", f"{margen_general:.1f}%")
        
        st.markdown("---")
        
        # Distribución por cuadrante
        st.markdown("**📊 Distribución:**")
        
        for cuadrante in ['⭐ ESTRELLA', '🐴 CABALLO', '🧩 ROMPECABEZAS', '🐕 PERRO']:
            count = len(df_carta[df_carta['Cuadrante'] == cuadrante])
            if count > 0:
                porcentaje = (count / len(df_carta) * 100)
                st.write(f"{cuadrante}: **{count}** platos ({porcentaje:.0f}%)")
    
    
    # ========== TAB 2: MATRIZ AVANZADA ==========
    with tab2:
        st.markdown("### 🎯 Análisis Detallado - Matriz BCG Avanzada")
        
        st.info("📊 Scatter plot interactivo: Tamaño = Facturación | Color = Food Cost % | Ejes = Ventas vs Margen %")
        
        if PLOTLY_AVAILABLE:
            import plotly.graph_objects as go
            
            # Calcular Food Cost si no existe
            if 'Food Cost %' not in df_carta.columns or df_carta['Food Cost %'].isna().all():
                df_carta['Food Cost %'] = (df_carta['Coste Total'] / df_carta['Precio Venta'] * 100).round(1)
            
            # Crear figura avanzada
            fig = go.Figure()
            
            # Paleta de colores para Food Cost %
            for cuadrante in df_carta['Cuadrante'].unique():
                df_cuad = df_carta[df_carta['Cuadrante'] == cuadrante]
                
                # Crear escala de colores basada en Food Cost %
                colors = []
                for fc in df_cuad['Food Cost %']:
                    if fc < 28:
                        colors.append('#70AD47')  # Verde
                    elif fc < 35:
                        colors.append('#FFC000')  # Amarillo
                    else:
                        colors.append('#C00000')  # Rojo
                
                fig.add_trace(go.Scatter(
                    x=df_cuad['Ventas/Mes'],
                    y=df_cuad['Margen %'],
                    mode='markers+text',
                    name=cuadrante,
                    text=df_cuad['Nombre Plato'],
                    textposition='top center',
                    textfont=dict(size=9, color='black'),
                    marker=dict(
                        size=df_cuad['Facturación'] / 25,  # Tamaño por facturación
                        color=colors,
                        line=dict(width=2, color='white'),
                        opacity=0.85,
                        showscale=False
                    ),
                    hovertemplate='<b>%{text}</b><br>' +
                                  'Ventas: %{x} uds/mes<br>' +
                                  'Margen: %{y}%<br>' +
                                  'Facturación: {}<br>' +
                                  'Tamaño burbuja = Facturación<br>' +
                                  'Color = Food Cost %<br>' +
                                  '<extra></extra>',
                    customdata=df_cuad['Facturación']
                ))
            
            # Líneas divisorias
            fig.add_hline(
                y=margen_medio, 
                line_dash="dash", 
                line_color="rgba(128,128,128,0.3)",
                annotation_text=f"Margen Medio: {margen_medio:.1f}%",
                annotation_position="right"
            )
            
            fig.add_vline(
                x=ventas_media, 
                line_dash="dash", 
                line_color="rgba(128,128,128,0.3)",
                annotation_text=f"Ventas Medias: {ventas_media:.0f} uds",
                annotation_position="top"
            )
            
            # Actualizar layout para mejor visualización
            fig.update_layout(
                height=600,
                xaxis_title="Ventas/Mes (unidades)",
                yaxis_title="Margen (%)",
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                hovermode='closest',
                plot_bgcolor='rgba(240,240,240,0.5)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("📊 Instala plotly: `pip install plotly`")
        
        # Tabla detallada
        st.markdown("### 📋 Tabla Detallada - Ordenada por Cuadrante")
        
        df_tabla = df_carta[['Nombre Plato', 'Cuadrante', 'Ventas/Mes', 'Margen %', 'Margen', 'Facturación', 'Beneficio', 'Food Cost %']].copy()
        df_tabla['Ventas/Mes'] = df_tabla['Ventas/Mes'].astype(int)
        df_tabla['Margen %'] = df_tabla['Margen %'].round(1)
        df_tabla['Margen'] = df_tabla['Margen'].round(2)
        df_tabla['Facturación'] = df_tabla['Facturación'].round(2)
        df_tabla['Beneficio'] = df_tabla['Beneficio'].round(2)
        df_tabla['Food Cost %'] = df_tabla['Food Cost %'].round(1)
        df_tabla = df_tabla.sort_values('Cuadrante')
        
        st.dataframe(df_tabla, use_container_width=True, hide_index=True)
        
        # Resumen estadístico
        st.markdown("### 📊 Estadísticas por Cuadrante")
        
        stats_cols = st.columns(4)
        
        for idx, cuadrante in enumerate(['⭐ ESTRELLA', '🐴 CABALLO', '❓ ROMPECABEZAS', '🐕 PERRO']):
            with stats_cols[idx]:
                df_cuad = df_carta[df_carta['Cuadrante'] == cuadrante]
                
                if not df_cuad.empty:
                    count = len(df_cuad)
                    facturacion = df_cuad['Facturación'].sum()
                    beneficio = df_cuad['Beneficio'].sum()
                    margen_promedio = df_cuad['Margen %'].mean()
                    
                    with st.expander(f"{cuadrante} ({count} platos)"):
                        st.metric("Platos", count)
                        st.metric("Facturación/Mes", f"{facturacion:,.0f}€")
                        st.metric("Beneficio/Mes", f"{beneficio:,.0f}€")
                        st.metric("Margen Promedio", f"{margen_promedio:.1f}%")
    
    # ========== TAB 3: OPORTUNIDADES ==========
    with tab3:
        st.markdown("### 💡 Análisis de Oportunidades")
        
        st.info("🎯 Identifica platos que pueden mejorar rápidamente con acciones específicas")
        
        # Oportunidad 1: Caballos de batalla
        st.markdown("#### 1️⃣ 📈 AUMENTAR MARGEN - Platos Populares con Bajo Margen")
        
        df_caballos = df_carta[df_carta['Cuadrante'] == '🐴 CABALLO'].sort_values('Ventas/Mes', ascending=False)
        
        if not df_caballos.empty:
            st.warning("⚠️ **Estos platos venden MUCHO pero tienen POCO margen.** Subir precio +0.50€ a +1€ es fácil y muy rentable.")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Platos a trabajar", len(df_caballos))
            with col2:
                impacto_caballos = (df_caballos['Ventas/Mes'].sum() * 0.50)
                st.metric("Impacto +0.50€", f"+{impacto_caballos:.0f}€/mes")
            with col3:
                impacto_caballos_1 = (df_caballos['Ventas/Mes'].sum() * 1.00)
                st.metric("Impacto +1€", f"+{impacto_caballos_1:.0f}€/mes")
            
            st.markdown("**Platos prioritarios:**")
            for idx, (_, plato) in enumerate(df_caballos.head(5).iterrows(), 1):
                col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 2, 2])
                with col1:
                    st.write(f"**{idx}. {plato['Nombre Plato']}**")
                with col2:
                    st.write(f"📊 {plato['Ventas/Mes']:.0f} u/mes")
                with col3:
                    st.write(f"Margen: {plato['Margen %']:.1f}%")
                with col4:
                    st.write(f"Precio actual: {plato['Precio Venta']:.2f}€")
                with col5:
                    nuevo_precio = plato['Precio Venta'] + 0.75
                    st.write(f"→ Sugerir: {nuevo_precio:.2f}€")
        else:
            st.success("✅ ¡No hay Caballos de Batalla! Tu carta está bien balanceada.")
        
        st.markdown("---")
        
        # Oportunidad 2: Rompecabezas
        st.markdown("#### 2️⃣ 📢 PROMOCIONAR - Platos Rentables pero Poco Vendidos")
        
        df_rompecabezas = df_carta[df_carta['Cuadrante'] == '❓ ROMPECABEZAS'].sort_values('Margen %', ascending=False)
        
        if not df_rompecabezas.empty:
            st.info("💡 **Estos platos tienen buen margen pero nadie los pide.** Invertir en marketing es la solución.")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Platos a promocionar", len(df_rompecabezas))
            with col2:
                impacto_rompecabezas = (df_rompecabezas['Margen %'].mean() * df_rompecabezas['Ventas/Mes'].mean() * 5)
                st.metric("Impacto potencial (5x ventas)", f"+{impacto_rompecabezas:.0f}€/mes")
            with col3:
                st.metric("Margen promedio", f"{df_rompecabezas['Margen %'].mean():.1f}%")
            
            st.markdown("**Platos a promocionar:**")
            for idx, (_, plato) in enumerate(df_rompecabezas.head(5).iterrows(), 1):
                col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 2.5])
                with col1:
                    st.write(f"**{idx}. {plato['Nombre Plato']}**")
                with col2:
                    st.write(f"📉 Solo {plato['Ventas/Mes']:.0f} u/mes")
                with col3:
                    st.write(f"Margen: {plato['Margen %']:.1f}%")
                with col4:
                    st.write("→ Post Instagram, menú del día, etc.")
        else:
            st.success("✅ ¡Todos tus platos se venden bien!")
        
        st.markdown("---")
        
        # Oportunidad 3: Perros
        st.markdown("#### 3️⃣ 🗑️ ELIMINAR - Platos No Rentables")
        
        df_perros = df_carta[df_carta['Cuadrante'] == '🐕 PERRO'].sort_values('Beneficio', ascending=True)
        
        if not df_perros.empty:
            st.error("❌ **Estos platos no se venden y no dejan margen.** Candidatos a eliminar de la carta.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Platos a eliminar", len(df_perros))
            with col2:
                impacto_perros = -df_perros['Beneficio'].sum()
                st.metric("Ahorras eliminándolos", f"{impacto_perros:.0f}€/mes")
            
            st.markdown("**Perros - Decisión difícil pero necesaria:**")
            for idx, (_, plato) in enumerate(df_perros.iterrows(), 1):
                col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 2])
                with col1:
                    st.write(f"**{idx}. {plato['Nombre Plato']}**")
                with col2:
                    st.write(f"📉 {plato['Ventas/Mes']:.0f} u/mes")
                with col3:
                    st.write(f"⚠️ Margen: {plato['Margen %']:.1f}%")
                with col4:
                    st.write(f"Pérdida: -{abs(plato['Beneficio']):.0f}€/mes")
        else:
            st.success("✅ ¡No hay Perros! Todos tus platos son viables.")
        
        st.markdown("---")
        
        # Oportunidad 4: Food Cost
        st.markdown("#### 4️⃣ 💸 MEJORAR FOOD COST - Platos con Food Cost > 35%")
        
        df_alto_fc = df_carta[df_carta['Food Cost %'] > 35].sort_values('Food Cost %', ascending=False)
        
        if not df_alto_fc.empty:
            st.warning(f"⚠️ **{len(df_alto_fc)} platos tienen Food Cost > 35%.** Target es 28% para márgenes saludables.")
            
            st.markdown("**Acciones para reducir Food Cost:**")
            st.write("• 🔍 Renegociar precios con proveedores")
            st.write("• 📏 Estandarizar porciones (reducir ligeramente)")
            st.write("• 🥘 Sustituir ingredientes costosos")
            st.write("• 💰 Subir precio de venta")
            
            st.markdown("**Platos prioritarios:**")
            for idx, (_, plato) in enumerate(df_alto_fc.head(5).iterrows(), 1):
                col1, col2, col3 = st.columns([2, 1.5, 2.5])
                with col1:
                    st.write(f"**{idx}. {plato['Nombre Plato']}**")
                with col2:
                    st.write(f"🔴 FC: {plato['Food Cost %']:.1f}%")
                with col3:
                    target_pvp = plato['Coste Total'] / 0.28
                    incremento = target_pvp - plato['Precio Venta']
                    if incremento > 0:
                        st.write(f"💡 Subir a {target_pvp:.2f}€ (+{incremento:.2f}€)")
                    else:
                        st.write(f"💡 Reducir coste a {plato['Precio Venta'] * 0.28:.2f}€")
        else:
            st.success("✅ ¡Excelente! Todos tus Food Cost están bajo control (<35%).")
    
    # ========== TAB 4: PLAN DE ACCIÓN ==========
    with tab4:
        st.markdown("### 🎯 Plan de Acción - Roadmap de Mejora")
        
        st.info("📅 Calendario de acciones ordenado por impacto y facilidad. Implementa en este orden.")
        
        # Calcular oportunidades totales
        impacto_total = 0
        acciones = []
        
        # Acción 1: Subir caballos
        if not df_caballos.empty:
            for _, plato in df_caballos.iterrows():
                impacto = plato['Ventas/Mes'] * 0.75
                acciones.append({
                    'prioridad': 1,
                    'urgencia': '🚨 INMEDIATA',
                    'accion': f"Subir precio de '{plato['Nombre Plato']}'",
                    'detalles': f"De {plato['Precio Venta']:.2f}€ a {plato['Precio Venta'] + 0.75:.2f}€ (+{0.75:.2f}€)",
                    'impacto': impacto,
                    'dificultad': '⭐ Fácil',
                    'timeline': '📍 Esta semana',
                    'plato_name': plato['Nombre Plato']
                })
        
        # Acción 2: Promocionar rompecabezas
        if not df_rompecabezas.empty:
            for idx, (_, plato) in enumerate(df_rompecabezas.iterrows()):
                if idx < 3:  # Solo top 3
                    impacto = plato['Margen'] * 3  # Asumir 3 ventas más
                    acciones.append({
                        'prioridad': 2,
                        'urgencia': '📌 SEMANAL',
                        'accion': f"Promocionar '{plato['Nombre Plato']}'",
                        'detalles': "Post Instagram + Menú del día + Recomendación personal",
                        'impacto': impacto,
                        'dificultad': '⭐ Fácil',
                        'timeline': '📍 Esta semana',
                        'plato_name': plato['Nombre Plato']
                    })
        
        # Acción 3: Eliminar perros
        if not df_perros.empty:
            for _, plato in df_perros.iterrows():
                impacto = abs(plato['Beneficio'])  # Ahorro de espacio en carta
                acciones.append({
                    'prioridad': 3,
                    'urgencia': '⏰ MENSUAL',
                    'accion': f"Eliminar '{plato['Nombre Plato']}'",
                    'detalles': f"Libera espacio en carta. Hoy vende {plato['Ventas/Mes']:.0f} u/mes = {plato['Beneficio']:.0f}€",
                    'impacto': impacto,
                    'dificultad': '⭐⭐ Moderado',
                    'timeline': '📍 Esta semana (opcional)',
                    'plato_name': plato['Nombre Plato']
                })
        
        # Acción 4: Mejorar Food Cost
        if not df_alto_fc.empty:
            for idx, (_, plato) in enumerate(df_alto_fc.iterrows()):
                if idx < 3:  # Solo top 3
                    ahorro_potencial = (plato['Food Cost %'] - 28) * plato['Precio Venta'] * plato['Ventas/Mes'] / 100
                    acciones.append({
                        'prioridad': 4,
                        'urgencia': '📌 SEMANAL',
                        'accion': f"Reducir Food Cost de '{plato['Nombre Plato']}'",
                        'detalles': f"FC actual {plato['Food Cost %']:.1f}% → Target 28%. Ahorro potencial: {ahorro_potencial:.0f}€/mes",
                        'impacto': ahorro_potencial,
                        'dificultad': '⭐⭐⭐ Complejo',
                        'timeline': '📍 Este mes',
                        'plato_name': plato['Nombre Plato']
                    })
        
        # Ordenar por impacto
        acciones.sort(key=lambda x: -x['impacto'])
        
        # Mostrar roadmap
        if acciones:
            st.markdown("#### 📊 Impacto Total Potencial")
            impacto_total = sum(a['impacto'] for a in acciones)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Ingresos adicionales/mes", f"+{impacto_total:.0f}€")
            with col2:
                st.metric("📈 % de aumento", f"+{impacto_total/df_carta['Beneficio'].sum()*100:.1f}%")
            with col3:
                st.metric("📅 Timeline", "Este mes")
            
            st.markdown("---")
            
            st.markdown("#### 🎯 Acciones Priorizadas")
            
            for idx, accion in enumerate(acciones, 1):
                with st.container():
                    col1, col2 = st.columns([0.5, 9.5])
                    
                    with col1:
                        st.markdown(f"### {idx}")
                    
                    with col2:
                        st.markdown(f"**{accion['accion']}**")
                        
                        col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 2])
                        
                        with col_a:
                            st.write(f"{accion['urgencia']}")
                        with col_b:
                            st.write(f"{accion['dificultad']}")
                        with col_c:
                            st.write(f"💰 +{accion['impacto']:.0f}€/mes")
                        with col_d:
                            st.write(f"{accion['timeline']}")
                        
                        st.caption(accion['detalles'])
                    
                    st.divider()
        else:
            st.success("✅ ¡Tu carta está perfectamente balanceada! No hay acciones urgentes.")
        


def mostrar_escandallos():
    """Vista y gestión de escandallos (ingredientes por plato)"""
    st.subheader("🔍 Escandallos - Desglose por Plato")
    
    # Cargar datos
    df_esc = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
    df_platos = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_ing = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
    
    # Crear listas
    platos_disponibles = []
    if not df_platos.empty and 'ID Plato' in df_platos.columns and 'Nombre Plato' in df_platos.columns:
        for _, row in df_platos.iterrows():
            platos_disponibles.append(f"{row['ID Plato']} - {row['Nombre Plato']} ({row['Nombre Cliente']})")
    
    ingredientes_disponibles = []
    if not df_ing.empty and 'ID Ingrediente' in df_ing.columns and 'Nombre' in df_ing.columns:
        for _, row in df_ing.iterrows():
            ingredientes_disponibles.append(f"{row['ID Ingrediente']} - {row['Nombre']}")
    
    # Botón agregar
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Agregar Ingrediente a Plato", type="primary", use_container_width=True):
            st.session_state.agregar_escandallo = True
    
    # Formulario - PRIMERO seleccionar el plato (FUERA del expander)
    if st.session_state.get('agregar_escandallo', False):
        st.markdown("### 🍽️ Selecciona el Plato")
        
        if platos_disponibles:
            plato_sel = st.selectbox("¿A qué plato le vas a agregar ingredientes?", 
                platos_disponibles, key="plato_esc_sel")
            id_plato = int(float(plato_sel.split(" - ")[0]))
            nombre_plato = plato_sel.split(" - ")[1].split(" (")[0]
            
            # Obtener información del plato
            if not df_platos.empty:
                plato_info = df_platos[df_platos['ID Plato'] == id_plato].iloc[0]
                nombre_cliente = plato_info.get('Nombre Cliente', '')
                precio_venta = plato_info.get('Precio Venta', 0)
        else:
            st.error("No hay platos. Agrega uno primero en 'Carta'")
            id_plato = 0
            nombre_plato = ""
            nombre_cliente = ""
            precio_venta = 0
        
        # Mostrar escandallo actual del plato ANTES de agregar más
        if platos_disponibles and id_plato > 0:
            ingredientes_actuales = df_esc[df_esc['ID Plato'] == id_plato]
            
            if not ingredientes_actuales.empty:
                st.markdown("---")
                st.markdown(f"### 📋 Escandallo actual de: **{nombre_plato}**")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🥘 Ingredientes", len(ingredientes_actuales))
                with col2:
                    coste_actual = ingredientes_actuales['Coste Total'].sum()
                    st.metric("💰 Coste Total", f"{coste_actual:.2f}€")
                with col3:
                    st.metric("💵 Precio Venta", f"{precio_venta:.2f}€")
                with col4:
                    if precio_venta > 0:
                        margen = ((precio_venta - coste_actual) / precio_venta) * 100
                        delta_color = "normal" if margen >= 60 else "inverse"
                        st.metric("📊 Margen", f"{margen:.1f}%", delta=None)
                
                # Tabla de ingredientes con opciones de edición
                st.caption("🔧 **Haz clic en un ingrediente para editarlo o eliminarlo**")
                
                for idx, ingrediente in ingredientes_actuales.iterrows():
                    col_a, col_b, col_c, col_d, col_e, col_f = st.columns([3, 1, 1, 1, 1, 1])
                    
                    with col_a:
                        st.write(f"**{ingrediente['Nombre Ingrediente']}**")
                    with col_b:
                        st.write(f"{ingrediente['Cantidad']:.3f} {ingrediente['Unidad']}")
                    with col_c:
                        st.write(f"{ingrediente['Coste Unitario']:.4f}€")
                    with col_d:
                        st.write(f"**{ingrediente['Coste Total']:.2f}€**")
                    with col_e:
                        if st.button("✏️", key=f"edit_esc_{ingrediente['ID Escandallo']}", help="Editar cantidad"):
                            st.session_state.editando_escandallo = ingrediente['ID Escandallo']
                            st.rerun()
                    with col_f:
                        if st.button("🗑️", key=f"del_esc_{ingrediente['ID Escandallo']}", help="Eliminar ingrediente"):
                            # Eliminar ingrediente del escandallo
                            df_esc_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                            df_esc_temp = df_esc_temp[df_esc_temp['ID Escandallo'] != ingrediente['ID Escandallo']]
                            utils.escribir_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", df_esc_temp)
                            
                            # Recalcular costes
                            utils.recalcular_costes_platos(df_esc_temp)
                            
                            st.success(f"✅ {ingrediente['Nombre Ingrediente']} eliminado del escandallo")
                            time.sleep(1)
                            st.rerun()
                    
                    # Formulario de edición si está activo
                    if st.session_state.get('editando_escandallo') == ingrediente['ID Escandallo']:
                        with st.container():
                            st.markdown("---")
                            st.markdown(f"**✏️ Editando: {ingrediente['Nombre Ingrediente']}**")
                            
                            col_edit1, col_edit2 = st.columns(2)
                            
                            with col_edit1:
                                nueva_cantidad = st.number_input(
                                    f"Nueva Cantidad ({ingrediente['Unidad']})", 
                                    min_value=0.001, 
                                    value=float(ingrediente['Cantidad']), 
                                    step=0.01, 
                                    format="%.3f",
                                    key=f"nueva_cant_{ingrediente['ID Escandallo']}"
                                )
                                
                                nuevo_coste = nueva_cantidad * ingrediente['Coste Unitario']
                                st.caption(f"Nuevo Coste Total: **{nuevo_coste:.2f}€**")
                            
                            with col_edit2:
                                st.write("")
                                st.write("")
                                col_btn1, col_btn2 = st.columns(2)
                                
                                with col_btn1:
                                    if st.button("💾 Guardar", key=f"save_esc_{ingrediente['ID Escandallo']}", use_container_width=True, type="primary"):
                                        # Actualizar cantidad
                                        df_esc_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                                        mascara = df_esc_temp['ID Escandallo'] == ingrediente['ID Escandallo']
                                        df_esc_temp.loc[mascara, 'Cantidad'] = nueva_cantidad
                                        df_esc_temp.loc[mascara, 'Coste Total'] = nuevo_coste
                                        df_esc_temp.loc[mascara, 'Última Actualización'] = datetime.now().date()
                                        
                                        utils.escribir_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", df_esc_temp)
                                        
                                        # Recalcular costes del plato
                                        utils.recalcular_costes_platos(df_esc_temp)
                                        
                                        st.success(f"✅ Cantidad actualizada: {nueva_cantidad:.3f} {ingrediente['Unidad']}")
                                        st.session_state.editando_escandallo = None
                                        time.sleep(1)
                                        st.rerun()
                                
                                with col_btn2:
                                    if st.button("❌ Cancelar", key=f"cancel_esc_{ingrediente['ID Escandallo']}", use_container_width=True):
                                        st.session_state.editando_escandallo = None
                                        st.rerun()
                            
                            st.markdown("---")
                
                st.markdown("---")
            else:
                st.info(f"ℹ️ El plato **{nombre_plato}** aún no tiene ingredientes. ¡Agrega el primero!")
                st.markdown("---")
        
        # AHORA sí, el expander para agregar múltiples ingredientes A ESE PLATO
        if platos_disponibles:
            with st.expander(f"➕ **Agregar Ingrediente a: {nombre_plato}**", expanded=True):
                st.caption("💡 Agrega ingredientes uno por uno. Cada uno se suma al escandallo y actualiza el coste automáticamente.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if ingredientes_disponibles:
                        ing_sel = st.selectbox("Ingrediente*", ingredientes_disponibles, key="ing_esc_sel")
                        id_ing = int(float(ing_sel.split(" - ")[0]))
                        nombre_ing = ing_sel.split(" - ")[1]
                        
                        # Obtener precio actual del ingrediente
                        precio_ing = df_ing[df_ing['ID Ingrediente'] == id_ing]['Precio Mercado Medio'].values[0]
                        unidad_ing = df_ing[df_ing['ID Ingrediente'] == id_ing]['Unidad Compra'].values[0]
                    else:
                        st.error("No hay ingredientes. Agrega uno primero")
                        id_ing = 0
                        nombre_ing = ""
                        precio_ing = 0
                        unidad_ing = "KG"
                
                with col2:
                    if ingredientes_disponibles:
                        cantidad = st.number_input(f"Cantidad ({unidad_ing})*", 
                            min_value=0.0, value=0.0, step=0.01, format="%.3f",
                            help=f"Cantidad en {unidad_ing}", key="cantidad_esc_input")
                        
                        st.caption(f"💰 Coste Unitario: {precio_ing:.4f} €/{unidad_ing}")
                        
                        if cantidad > 0:
                            coste_calculado = cantidad * precio_ing
                            st.write(f"**Coste de este ingrediente: {coste_calculado:.2f} €**")
                        
                        # Proveedor opcional
                        dict_proveedores = utils.obtener_dict_proveedores()
                        proveedores_opciones = ["Sin asignar"] + [f"{id_p} - {nombre}" for id_p, nombre in dict_proveedores.items()]
                        proveedor_seleccionado = st.selectbox("Proveedor (opcional)", 
                            proveedores_opciones, key="prov_esc_sel")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Agregar Ingrediente", use_container_width=True, type="primary", key="btn_agregar_esc"):
                        if not ingredientes_disponibles:
                            st.error("Necesitas tener al menos un ingrediente")
                        elif cantidad <= 0:
                            st.error("La cantidad debe ser mayor que 0")
                        else:
                            # Verificar si ya existe este ingrediente en el plato
                            existe = df_esc[
                                (df_esc['ID Plato'] == id_plato) & 
                                (df_esc['ID Ingrediente'] == id_ing)
                            ]
                            
                            if not existe.empty:
                                st.warning(f"⚠️ Este ingrediente ya está en el plato. Edítalo o elimínalo primero.")
                            else:
                                nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                                coste_total = cantidad * precio_ing
                                
                                # Parsear ID proveedor
                                if proveedor_seleccionado == "Sin asignar":
                                    id_proveedor = None
                                else:
                                    id_proveedor = int(float(proveedor_seleccionado.split(" - ")[0]))
                                
                                nuevo_escandallo = {
                                    'ID Escandallo': nuevo_id,
                                    'ID Plato': id_plato,
                                    'Nombre Plato': nombre_plato,
                                    'ID Ingrediente': id_ing,
                                    'Nombre Ingrediente': nombre_ing,
                                    'Cantidad': cantidad,
                                    'Unidad': unidad_ing,
                                    'Coste Unitario': precio_ing,
                                    'Coste Total': coste_total,
                                    '% del Plato': 0,  # Se calculará después
                                    'ID Proveedor': id_proveedor,
                                    'Última Actualización': datetime.now().date()
                                }
                                
                                if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", nuevo_escandallo):
                                    st.success(f"✅ {nombre_ing} agregado al escandallo: {cantidad:.2f} {unidad_ing} = {coste_total:.2f}€")
                                    
                                    # Recalcular coste total del plato en CARTA_CLIENTES
                                    df_esc_actualizado = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                                    utils.recalcular_costes_platos(df_esc_actualizado)
                                    
                                    st.info("♻️ Coste y márgenes del plato actualizados en la Carta")
                                    time.sleep(1.5)
                                    st.rerun()
                
                with col2:
                    if st.button("✅ Terminar Escandallo", use_container_width=True, key="btn_cancelar_esc"):
                        st.session_state.agregar_escandallo = False
                        st.rerun()
    
    # Mostrar escandallos
    st.markdown("---")
    
    if not df_esc.empty:
        # Filtro por plato
        if 'Nombre Plato' in df_esc.columns:
            platos_unicos = df_esc['Nombre Plato'].unique()
            plato_filtro = st.selectbox("Filtrar por Plato", ["Todos"] + list(platos_unicos))
            
            if plato_filtro != "Todos":
                df_filtrado = df_esc[df_esc['Nombre Plato'] == plato_filtro]
                
                # Mostrar resumen del plato
                if not df_filtrado.empty:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_ingredientes = len(df_filtrado)
                        st.metric("Ingredientes", total_ingredientes)
                    
                    with col2:
                        if 'Coste Total' in df_filtrado.columns:
                            coste_plato = df_filtrado['Coste Total'].sum()
                            st.metric("Coste Total Plato", f"{coste_plato:.2f} €")
                    
                    with col3:
                        # Buscar precio de venta del plato
                        if not df_platos.empty:
                            plato_info = df_platos[df_platos['Nombre Plato'] == plato_filtro]
                            if not plato_info.empty and 'Precio Venta' in plato_info.columns:
                                precio_venta = plato_info['Precio Venta'].values[0]
                                st.metric("Precio Venta", f"{precio_venta:.2f} €")
                    
                    with col4:
                        if 'coste_plato' in locals() and 'precio_venta' in locals() and precio_venta > 0:
                            margen = ((precio_venta - coste_plato) / precio_venta) * 100
                            st.metric("Margen", f"{margen:.1f}%")
                    
                    st.markdown("---")
                    
                    # Mostrar ingredientes con opciones de edición
                    st.subheader("📝 Ingredientes del Escandallo")
                    
                    for idx, ingrediente in df_filtrado.iterrows():
                        col_a, col_b, col_c, col_d, col_e, col_f = st.columns([3, 1.5, 1.5, 1, 0.5, 0.5])
                        
                        with col_a:
                            st.write(f"**{ingrediente['Nombre Ingrediente']}**")
                        with col_b:
                            st.write(f"{ingrediente['Cantidad']:.3f} {ingrediente['Unidad']}")
                        with col_c:
                            st.write(f"{ingrediente['Coste Unitario']:.4f} €/{ingrediente['Unidad']}")
                        with col_d:
                            st.write(f"**{ingrediente['Coste Total']:.2f} €**")
                        with col_e:
                            if st.button("✏️", key=f"edit_table_{ingrediente['ID Escandallo']}", help="Editar cantidad"):
                                st.session_state.editando_tabla_esc = ingrediente['ID Escandallo']
                                st.rerun()
                        with col_f:
                            if st.button("🗑️", key=f"del_table_{ingrediente['ID Escandallo']}", help="Eliminar ingrediente"):
                                df_esc_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                                df_esc_temp = df_esc_temp[df_esc_temp['ID Escandallo'] != ingrediente['ID Escandallo']]
                                utils.escribir_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", df_esc_temp)
                                utils.recalcular_costes_platos(df_esc_temp)
                                st.success(f"✅ {ingrediente['Nombre Ingrediente']} eliminado")
                                time.sleep(1)
                                st.rerun()
                        
                        # Formulario inline de edición
                        if st.session_state.get('editando_tabla_esc') == ingrediente['ID Escandallo']:
                            with st.container():
                                st.markdown(f"**✏️ Editando: {ingrediente['Nombre Ingrediente']}**")
                                col_e1, col_e2, col_e3 = st.columns([2, 1, 1])
                                
                                with col_e1:
                                    nueva_cant = st.number_input(
                                        f"Nueva Cantidad ({ingrediente['Unidad']})", 
                                        min_value=0.001, 
                                        value=float(ingrediente['Cantidad']), 
                                        step=0.01,
                                        format="%.3f",
                                        key=f"edit_cant_table_{ingrediente['ID Escandallo']}"
                                    )
                                    st.caption(f"Nuevo coste: **{nueva_cant * ingrediente['Coste Unitario']:.2f}€**")
                                
                                with col_e2:
                                    if st.button("💾 Guardar", key=f"save_table_{ingrediente['ID Escandallo']}", type="primary", use_container_width=True):
                                        df_esc_temp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                                        mascara = df_esc_temp['ID Escandallo'] == ingrediente['ID Escandallo']
                                        df_esc_temp.loc[mascara, 'Cantidad'] = nueva_cant
                                        df_esc_temp.loc[mascara, 'Coste Total'] = nueva_cant * ingrediente['Coste Unitario']
                                        df_esc_temp.loc[mascara, 'Última Actualización'] = datetime.now().date()
                                        utils.escribir_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", df_esc_temp)
                                        utils.recalcular_costes_platos(df_esc_temp)
                                        st.success(f"✅ Actualizado")
                                        st.session_state.editando_tabla_esc = None
                                        time.sleep(1)
                                        st.rerun()
                                
                                with col_e3:
                                    if st.button("❌", key=f"cancel_table_{ingrediente['ID Escandallo']}", use_container_width=True):
                                        st.session_state.editando_tabla_esc = None
                                        st.rerun()
                                
                                st.markdown("---")
            else:
                df_filtrado = df_esc
        else:
            df_filtrado = df_esc
        
        # Mostrar tabla completa cuando no hay filtro
        if plato_filtro == "Todos":
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Coste Unitario": st.column_config.NumberColumn(
                        "Coste Unitario",
                        format="%.4f €"
                    ),
                    "Coste Total": st.column_config.NumberColumn(
                        "Coste Total",
                        format="%.2f €"
                    ),
                    "Cantidad": st.column_config.NumberColumn(
                        "Cantidad",
                        format="%.3f"
                    ),
                    "% del Plato": st.column_config.NumberColumn(
                        "% del Plato",
                        format="%.1f%%"
                    )
                }
            )
            
            st.caption(f"Mostrando {len(df_filtrado)} ingredientes")
    else:
        st.info("🔍 No hay escandallos registrados. ¡Agrega ingredientes a tus platos!")

def mostrar_carta():
    """Vista de carta de clientes"""
    st.subheader("🍴 Carta de Clientes")
    
    # Cargar datos
    df_carta = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
    
    # Crear lista de clientes
    clientes_disponibles = []
    if not df_clientes.empty and 'ID' in df_clientes.columns and 'Nombre Comercial' in df_clientes.columns:
        for _, row in df_clientes.iterrows():
            clientes_disponibles.append(f"{row['ID']} - {row['Nombre Comercial']}")
    
    # Selector de cliente para filtrar
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if not df_carta.empty and 'Nombre Cliente' in df_carta.columns:
            clientes_unicos = df_carta['Nombre Cliente'].unique()
            cliente_filtro = st.selectbox("Filtrar por Cliente", ["Todos"] + list(clientes_unicos))
        else:
            cliente_filtro = "Todos"
    
    with col2:
        if st.button("➕ Agregar Plato", type="primary", use_container_width=True):
            st.session_state.agregar_plato = True
    
    # Formulario de nuevo plato
    if st.session_state.get('agregar_plato', False):
        with st.form("form_nuevo_plato"):
            st.write("**🍽️ Agregar Nuevo Plato a la Carta**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if clientes_disponibles:
                    cliente_sel = st.selectbox("Cliente*", clientes_disponibles)
                    id_cliente = int(float(cliente_sel.split(" - ")[0]))
                    nombre_cliente = cliente_sel.split(" - ")[1]
                else:
                    st.error("No hay clientes activos. Agrega uno primero.")
                    id_cliente = 0
                    nombre_cliente = ""
                
                nombre_plato = st.text_input("Nombre del Plato*", 
                    placeholder="Ej: Cachopo de ternera")
                
                categoria = st.selectbox("Categoría*", config.CATEGORIAS_PLATO)
                
                precio_venta = st.number_input("Precio de Venta (€)*", 
                    min_value=0.0, value=0.0, step=0.5, format="%.2f")
            
            with col2:
                coste_total = st.number_input("Coste Total (€)*", 
                    min_value=0.0, value=0.0, step=0.1, format="%.2f",
                    help="Suma de todos los ingredientes. Se puede calcular automáticamente desde Escandallos")
                
                ventas_mes = st.number_input("Ventas/Mes Estimadas", 
                    min_value=0, value=0, step=5)
                
                activo = st.selectbox("¿Activo en carta?", ["Sí", "No"])
            
            descripcion = st.text_area("Descripción del Plato", 
                placeholder="Opcional: descripción del plato para la carta")
            
            notas = st.text_area("Notas Internas", 
                placeholder="Notas sobre el plato, ingredientes especiales, etc.")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar Plato", use_container_width=True)
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if not clientes_disponibles:
                    st.error("No puedes agregar platos sin clientes activos")
                elif not nombre_plato:
                    st.error("El nombre del plato es obligatorio")
                elif precio_venta <= 0:
                    st.error("El precio de venta debe ser mayor que 0")
                else:
                    nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
                    
                    # Calcular márgenes
                    margen_euros = precio_venta - coste_total
                    margen_pct = (margen_euros / precio_venta * 100) if precio_venta > 0 else 0
                    food_cost = (coste_total / precio_venta * 100) if precio_venta > 0 else 0
                    
                    # Clasificar según ingeniería de menú
                    if margen_pct >= 60 and ventas_mes >= 50:
                        clasificacion = "Estrella"
                    elif margen_pct >= 60 and ventas_mes < 50:
                        clasificacion = "Rompecabezas"
                    elif margen_pct < 60 and ventas_mes >= 50:
                        clasificacion = "Caballo"
                    else:
                        clasificacion = "Perro"
                    
                    # Precio recomendado apuntando a 28% Food Cost (🟢 verde)
                    precio_recomendado = (coste_total / 0.28) if coste_total > 0 else 0
                    
                    nuevo_plato = {
                        'ID Plato': nuevo_id,
                        'ID Cliente': id_cliente,
                        'Nombre Cliente': nombre_cliente,
                        'Nombre Plato': nombre_plato,
                        'Categoría': categoria,
                        'Precio Venta': precio_venta,
                        'Coste Total': coste_total,
                        'Margen €': margen_euros,
                        'Margen %': margen_pct,
                        'Food Cost %': food_cost,
                        'Ventas/Mes': ventas_mes,
                        'Clasificación': clasificacion,
                        'Precio Recomendado': precio_recomendado,
                        'Activo': activo,
                        'Notas': notas
                    }
                    
                    if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", nuevo_plato):
                        st.success(f"✅ Plato '{nombre_plato}' agregado correctamente")
                        st.info(f"📊 Margen: {margen_pct:.1f}% | Food Cost: {food_cost:.1f}% | Clasificación: {clasificacion}")
                        st.session_state.agregar_plato = False
                        st.cache_data.clear()
                        st.rerun()
            
            if cancelar:
                st.session_state.agregar_plato = False
                st.rerun()
    
    # Mostrar platos
    st.markdown("---")
    
    if not df_carta.empty:
        # Aplicar filtro de cliente
        df_filtrado = df_carta.copy()
        if cliente_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Nombre Cliente'] == cliente_filtro]
        
        # Métricas rápidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Platos", len(df_filtrado))
        
        with col2:
            if 'Margen %' in df_filtrado.columns:
                margen_medio = df_filtrado['Margen %'].mean()
                st.metric("Margen Medio", f"{margen_medio:.1f}%")
        
        with col3:
            if 'Clasificación' in df_filtrado.columns:
                estrellas = len(df_filtrado[df_filtrado['Clasificación'] == 'Estrella'])
                st.metric("⭐ Estrellas", estrellas)
        
        with col4:
            if 'Activo' in df_filtrado.columns:
                activos = len(df_filtrado[df_filtrado['Activo'] == 'Sí'])
                st.metric("Platos Activos", activos)
        
        st.markdown("---")
        
        # Alertas de márgenes bajos
        if 'Margen %' in df_filtrado.columns:
            platos_bajo_margen = df_filtrado[df_filtrado['Margen %'] < config.UMBRAL_MARGEN_MINIMO]
            if not platos_bajo_margen.empty:
                st.warning(f"⚠️ {len(platos_bajo_margen)} platos con margen bajo (<{config.UMBRAL_MARGEN_MINIMO}%)")
        
        # Mostrar tabla con formato condicional
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Margen %": st.column_config.NumberColumn(
                    "Margen %",
                    format="%.1f%%"
                ),
                "Food Cost %": st.column_config.NumberColumn(
                    "Food Cost %",
                    format="%.1f%%"
                ),
                "Precio Venta": st.column_config.NumberColumn(
                    "Precio Venta",
                    format="%.2f €"
                ),
                "Coste Total": st.column_config.NumberColumn(
                    "Coste Total",
                    format="%.2f €"
                ),
                "Margen €": st.column_config.NumberColumn(
                    "Margen €",
                    format="%.2f €"
                )
            }
        )
        
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_carta)} platos")
    else:
        st.info("🍽️ No hay platos registrados. ¡Agrega el primero!")

def mostrar_ingredientes():
    """Vista de ingredientes maestro (compartido) pero no se usa directamente"""
    st.info("ℹ️ **Nota:** Los ingredientes maestro son solo referencia. Cada cliente tiene sus propios precios.")
    
    if st.button("📊 Ver Base de Ingredientes Maestro", key="ver_ingredientes_maestro"):
        st.session_state.ver_ingredientes_maestro = not st.session_state.get('ver_ingredientes_maestro', False)
    
    if st.session_state.get('ver_ingredientes_maestro', False):
        df_ing = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
        
        if not df_ing.empty:
            st.caption("**Base de datos de referencia** (precio promedio del mercado)")
            st.dataframe(df_ing, use_container_width=True, hide_index=True)
        else:
            st.info("No hay ingredientes en la base maestra")

def mostrar_ingredientes_cliente(id_cliente, nombre_cliente):
    """Ingredientes con precios específicos del cliente seleccionado"""
    st.subheader(f"📊 Ingredientes de {nombre_cliente}")
    
    # Cargar datos
    df_ing_maestro = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
    df_precios_todos = utils.leer_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
    
    # Filtrar precios de este cliente
    df_precios_cliente = df_precios_todos[df_precios_todos['ID Cliente'] == id_cliente] if not df_precios_todos.empty else pd.DataFrame()
    
    st.write("---")
    
    # Botones de acción
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Asignar Ingrediente a este Cliente", type="primary", key="btn_asignar_ing"):
            st.session_state.asignar_ingrediente_cliente = True
    
    with col2:
        if st.button("🆕 Crear Nuevo Ingrediente en Base", key="btn_nuevo_ing_base"):
            st.session_state.crear_ingrediente_base = True
    
    # Formulario: Asignar ingrediente existente al cliente
    if st.session_state.get('asignar_ingrediente_cliente', False):
        with st.expander(f"➕ **Asignar Ingrediente a {nombre_cliente}**", expanded=True):
            if df_ing_maestro.empty:
                st.error("No hay ingredientes en la base. Crea uno primero.")
                if st.button("❌ Cancelar", key="cancelar_asignar_ing_vacio"):
                    st.session_state.asignar_ingrediente_cliente = False
                    st.rerun()
            else:
                # Selección de ingrediente
                opciones_ing = [f"{row['ID Ingrediente']} - {row['Nombre']}" 
                               for _, row in df_ing_maestro.iterrows()]
                
                ing_sel = st.selectbox("Ingrediente*", opciones_ing, key="ing_asignar_form")
                id_ing = int(float(ing_sel.split(" - ")[0]))
                nombre_ing = ing_sel.split(" - ")[1]
                
                # Datos del ingrediente seleccionado
                ing_data = df_ing_maestro[df_ing_maestro['ID Ingrediente'] == id_ing].iloc[0]
                precio_mercado = ing_data['Precio Mercado Medio']
                unidad = ing_data['Unidad Compra']
                
                # Layout compacto en 4 columnas
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                
                with col1:
                    st.caption("📊 Precio Mercado")
                    st.write(f"**{precio_mercado:.2f} €/{unidad}**")
                
                with col2:
                    precio_cliente = st.number_input(f"Precio {nombre_cliente} (€/{unidad})*", 
                        min_value=0.0, value=float(precio_mercado), step=0.1, format="%.2f", 
                        key="precio_asignar_form", label_visibility="visible")
                
                with col3:
                    dict_proveedores = utils.obtener_dict_proveedores()
                    proveedores_opciones = ["Sin asignar"] + [f"{id_p} - {nombre}" for id_p, nombre in dict_proveedores.items()]
                    proveedor_seleccionado = st.selectbox("Proveedor", proveedores_opciones, key="prov_asignar_form")

                with col4:
                    merma_pct = st.number_input(
                        "Merma %",
                        min_value=0.0,
                        max_value=95.0,
                        value=0.0,
                        step=1.0,
                        format="%.0f",
                        key="merma_asignar_form",
                        help="Merma estimada del ingrediente (0% = sin merma)"
                    )
                
                # Desviación compacta
                if precio_mercado > 0:
                    desviacion = ((precio_cliente - precio_mercado) / precio_mercado) * 100
                    
                    if desviacion > 10:
                        st.error(f"⚠️ +{desviacion:.1f}% MÁS CARO")
                    elif desviacion < -10:
                        st.success(f"✅ {abs(desviacion):.1f}% MÁS BARATO")
                    else:
                        st.info(f"📊 {desviacion:+.1f}%")
                
                # Botones compactos
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Asignar", use_container_width=True, type="primary", key="btn_submit_asignar"):
                        # Parsear ID de proveedor
                        if proveedor_seleccionado == "Sin asignar":
                            id_proveedor_asignar = None
                        else:
                            id_proveedor_asignar = int(float(proveedor_seleccionado.split(" - ")[0]))
                        
                        if precio_cliente <= 0:
                            st.error("El precio debe ser mayor que 0")
                        else:
                            # Verificar si ya existe
                            existe = df_precios_cliente[
                                (df_precios_cliente['ID Cliente'] == id_cliente) & 
                                (df_precios_cliente['ID Ingrediente'] == id_ing)
                            ]
                            
                            if not existe.empty:
                                st.warning(f"⚠️ {nombre_cliente} ya tiene este ingrediente.")
                            else:
                                nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
                                desviacion = ((precio_cliente - precio_mercado) / precio_mercado * 100) if precio_mercado > 0 else 0
                                
                                nuevo_precio = {
                                    'ID Precio': nuevo_id,
                                    'ID Cliente': id_cliente,
                                    'Nombre Cliente': nombre_cliente,
                                    'ID Ingrediente': id_ing,
                                    'Nombre Ingrediente': nombre_ing,
                                    'Precio Cliente': precio_cliente,
                                    'Unidad': unidad,
                                    'Precio Mercado Referencia': precio_mercado,
                                    'Desviación %': desviacion,
                                    'Última Actualización': datetime.now().date(),
                                    'ID Proveedor': id_proveedor_asignar,
                                    'Merma %': merma_pct,
                                    'Notas': ''
                                }
                                
                                if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE", nuevo_precio):
                                    st.success(f"✅ {nombre_ing} asignado a {precio_cliente:.2f}€")
                                    st.session_state.asignar_ingrediente_cliente = False
                                    time.sleep(0.5)
                                    st.rerun()
                
                with col2:
                    if st.button("❌ Cancelar", use_container_width=True, key="btn_cancel_asignar"):
                        st.session_state.asignar_ingrediente_cliente = False
                        st.rerun()
    
    # Formulario: Crear nuevo ingrediente en la base
    if st.session_state.get('crear_ingrediente_base', False):
        st.write("**Crear nuevo ingrediente en Base Maestro**")
        st.caption("Después podrás asignarlo a clientes con sus precios específicos")
        
        # INPUTS FUERA DEL FORMULARIO para poder buscar ingredientes similares
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_ing = st.text_input("Nombre*", key="nombre_ing_base_form")
            categoria = st.selectbox("Categoría*", config.CATEGORIAS_INGREDIENTE, key="cat_ing_base_form")
            unidad = st.selectbox("Unidad*", ["KG", "Litro", "Unidad", "Docena", "Gramos", "ML"], key="unidad_ing_base_form")
        
        with col2:
            # Calcular precio medio automáticamente de ingredientes similares
            precio_mercado_calculado = None
            mensaje_calculo = ""
            
            if nombre_ing:  # Solo buscar si hay nombre
                # Buscar en PRECIOS_POR_CLIENTE ingredientes con nombre similar
                df_precios_todos = utils.leer_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
                
                if not df_precios_todos.empty and 'Nombre Ingrediente' in df_precios_todos.columns:
                    # Buscar ingredientes con nombre similar (case insensitive)
                    nombre_lower = nombre_ing.lower()
                    similares = df_precios_todos[
                        df_precios_todos['Nombre Ingrediente'].str.lower().str.contains(nombre_lower, na=False)
                    ]
                    
                    if len(similares) >= 1:  # Si hay al menos 1 precio
                        precio_mercado_calculado = similares['Precio Cliente'].mean()
                        mensaje_calculo = f"✅ Calculado automáticamente (media de {len(similares)} precio(s) de '{nombre_ing}')"
                    else:
                        mensaje_calculo = "⚠️ No disponemos de datos suficientes para realizar el cálculo"
                else:
                    mensaje_calculo = "⚠️ No disponemos de datos suficientes para realizar el cálculo"
            else:
                mensaje_calculo = "💡 Introduce un nombre para calcular el precio automáticamente"
            
            # Mostrar mensaje
            if precio_mercado_calculado:
                st.success(mensaje_calculo)
            elif "No disponemos" in mensaje_calculo:
                st.warning(mensaje_calculo)
            else:
                st.info(mensaje_calculo)
            
            # Input de precio (autocompletado si existe cálculo)
            valor_inicial = precio_mercado_calculado if precio_mercado_calculado else 0.0
            precio_mercado = st.number_input("Precio Mercado Medio (€) - Opcional", 
                min_value=0.0, step=0.1, format="%.2f", key="precio_ing_base_form",
                value=float(valor_inicial),
                help="Se calcula automáticamente. Si no hay datos, déjalo en 0 y se actualizará después")
            
            marca = st.text_input("Marca (opcional)", key="marca_ing_base_form")
        
        st.markdown("---")
        
        # Botones de acción
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Crear en Base", use_container_width=True, type="primary", key="btn_crear_ing_base"):
                if not nombre_ing:
                    st.error("El nombre es obligatorio")
                elif precio_mercado < 0:
                    st.error("El precio no puede ser negativo")
                else:
                    # Crear ingrediente (precio puede ser 0 si no hay datos)
                    nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
                    
                    nuevo_ing = {
                        'ID Ingrediente': nuevo_id,
                        'Nombre': nombre_ing,
                        'Categoría': categoria,
                        'Unidad Compra': unidad,
                        'Precio Mercado Medio': precio_mercado,
                        'Var % Semana': 0,
                        'Var % Mes': 0,
                        'Última Actualización': datetime.now().date(),
                        'Estacionalidad': '',
                        'Marca': marca if marca else '',
                        'Notas': ''
                    }
                    
                    if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO", nuevo_ing):
                        if precio_mercado == 0:
                            st.success(f"✅ '{nombre_ing}' creado (sin precio de referencia)")
                            st.info("💡 Asígnalo a clientes y el precio medio se calculará automáticamente")
                        else:
                            st.success(f"✅ '{nombre_ing}' creado con precio medio de {precio_mercado:.2f}€")
                        st.session_state.crear_ingrediente_base = False
                        time.sleep(0.5)
                        st.rerun()
        
        with col2:
            if st.button("❌ Cancelar", use_container_width=True, key="btn_cancelar_ing_base"):
                st.session_state.crear_ingrediente_base = False
                st.rerun()
    
    # Mostrar ingredientes del cliente
    st.markdown("---")
    st.subheader(f"Ingredientes asignados a {nombre_cliente}")
    
    if not df_precios_cliente.empty:
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Ingredientes", len(df_precios_cliente))
        
        with col2:
            if 'Precio Cliente' in df_precios_cliente.columns:
                precio_medio = df_precios_cliente['Precio Cliente'].mean()
                st.metric("Precio Medio", f"{precio_medio:.2f} €")
        
        with col3:
            if 'Desviación %' in df_precios_cliente.columns:
                desv_media = df_precios_cliente['Desviación %'].mean()
                color = "normal" if abs(desv_media) < 5 else "inverse"
                st.metric("Desviación Media", f"{desv_media:+.1f}%", delta_color=color)
        
        with col4:
            if 'Desviación %' in df_precios_cliente.columns:
                caros = len(df_precios_cliente[df_precios_cliente['Desviación %'] > 10])
                st.metric("⚠️ Más Caros", caros)
        
        st.markdown("---")
        
        # Actualización rápida de precio
        with st.expander("⚡ Actualización Rápida de Precio"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                opciones_ing_cliente = [f"{row['ID Ingrediente']} - {row['Nombre Ingrediente']}" 
                                       for _, row in df_precios_cliente.iterrows()]
                ing_actualizar = st.selectbox("Ingrediente", opciones_ing_cliente, key="ing_actualizar_select")
                id_ing_act = int(float(ing_actualizar.split(" - ")[0]))
            
            with col2:
                precio_actual = df_precios_cliente[df_precios_cliente['ID Ingrediente'] == id_ing_act]['Precio Cliente'].values[0]
                nuevo_precio = st.number_input("Nuevo Precio (€)", value=float(precio_actual), 
                                              min_value=0.0, step=0.1, format="%.2f", key="nuevo_precio_act")
            
            with col3:
                st.write("")
                st.write("")
                if st.button("🔄 Actualizar", use_container_width=True, key="btn_actualizar_precio"):
                    if nuevo_precio > 0:
                        # Actualizar en PRECIOS_POR_CLIENTE
                        df_precios_actualizado = df_precios_todos.copy()
                        mascara = (df_precios_actualizado['ID Cliente'] == id_cliente) & \
                                 (df_precios_actualizado['ID Ingrediente'] == id_ing_act)
                        
                        precio_mercado_ref = df_precios_actualizado.loc[mascara, 'Precio Mercado Referencia'].values[0]
                        nueva_desv = ((nuevo_precio - precio_mercado_ref) / precio_mercado_ref * 100) if precio_mercado_ref > 0 else 0
                        
                        df_precios_actualizado.loc[mascara, 'Precio Cliente'] = nuevo_precio
                        df_precios_actualizado.loc[mascara, 'Desviación %'] = nueva_desv
                        df_precios_actualizado.loc[mascara, 'Última Actualización'] = datetime.now().date()
                        
                        if utils.escribir_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE", df_precios_actualizado):
                            st.success(f"✅ Precio actualizado a {nuevo_precio:.2f}€")
                            
                            # Recalcular escandallos
                            st.info("♻️ Recalculando escandallos de este cliente...")
                            utils.recalcular_costes_platos(utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS"))
                            
                            time.sleep(1)
                            st.rerun()
        
        # Tabla de ingredientes
        st.dataframe(
            df_precios_cliente,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Precio Cliente": st.column_config.NumberColumn("Precio Cliente", format="%.2f €"),
                "Precio Mercado Referencia": st.column_config.NumberColumn("Ref. Mercado", format="%.2f €"),
                "Desviación %": st.column_config.NumberColumn("Desviación", format="%+.1f%%")
            }
        )
        
    else:
        st.info(f"📊 {nombre_cliente} no tiene ingredientes asignados. Usa el botón '➕ Asignar Ingrediente' arriba.")
def mostrar_compras():
    """Vista de compras de clientes"""
    st.subheader("💰 Registro de Compras")
    
    df_comp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "COMPRAS_CLIENTE")
    
    if not df_comp.empty:
        st.dataframe(
            df_comp,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay compras registradas")

# ============================================================================
# FUNCIÓN: INFORMES PDF
# ============================================================================

def mostrar_informes_pdf(id_cliente, nombre_cliente):
    """Generación de informes PDF profesionales"""
    st.header(f"📄 Informes PDF - {nombre_cliente}")
    
    st.info("""
    💡 **Genera informes profesionales en PDF** para entregar a tus clientes.
    Incluye gráficos, análisis y recomendaciones personalizadas.
    """)
    
    st.markdown("---")
    
    # Selector de tipo de informe
    col1, col2 = st.columns([1, 2])
    
    with col1:
        tipo_informe = st.selectbox(
            "Tipo de Informe",
            [
                "🎯 Ingeniería de Menú",
                "📊 Reporte Mensual",
                "📈 Análisis Completo"
            ],
            key=f"tipo_informe_{id_cliente}"
        )
    
    st.markdown("---")
    
    # ========================================================================
    # INFORME DE INGENIERÍA DE MENÚ
    # ========================================================================
    
    if tipo_informe == "🎯 Ingeniería de Menú":
        st.subheader("🎯 Informe de Ingeniería de Menú")
        
        st.markdown("""
        Este informe incluye:
        - 📊 Clasificación BCG de todos los platos
        - 📈 Gráfico de burbujas interactivo (opcional)
        - 💡 Recomendaciones específicas por cuadrante
        - 📉 Proyección de impacto financiero
        """)
        
        # Verificar que hay datos
        df_carta = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
        df_carta_cliente = df_carta[df_carta['ID Cliente'] == id_cliente].copy()
        
        if df_carta_cliente.empty:
            st.warning("⚠️ No hay platos en la carta para generar el informe.")
        else:
            # Calcular métricas
            df_carta_cliente['Margen'] = df_carta_cliente['Precio Venta'] - df_carta_cliente['Coste Total']
            df_carta_cliente['Margen %'] = (df_carta_cliente['Margen'] / df_carta_cliente['Precio Venta'] * 100).round(1)
            df_carta_cliente['Facturación'] = df_carta_cliente['Precio Venta'] * df_carta_cliente['Ventas/Mes']
            df_carta_cliente['Beneficio'] = df_carta_cliente['Margen'] * df_carta_cliente['Ventas/Mes']
            
            # Preview de métricas
            col1, col2, col3 = st.columns(3)
            
            total_facturacion = df_carta_cliente['Facturación'].sum()
            total_beneficio = df_carta_cliente['Beneficio'].sum()
            margen_general = (total_beneficio / total_facturacion * 100) if total_facturacion > 0 else 0
            
            with col1:
                st.metric("💰 Facturación/Mes", f"{total_facturacion:,.2f}€")
            with col2:
                st.metric("💵 Beneficio/Mes", f"{total_beneficio:,.2f}€")
            with col3:
                st.metric("📊 Margen General", f"{margen_general:.1f}%")
            
            st.markdown("---")
            
            # Opciones del informe
            col1, col2 = st.columns(2)
            
            with col1:
                incluir_grafico = st.checkbox(
                    "📊 Incluir Gráfico BCG",
                    value=False,
                    help="Requiere kaleido instalado",
                    key=f"incluir_grafico_{id_cliente}"
                )
            
            with col2:
                incluir_proyeccion = st.checkbox(
                    "📈 Incluir Proyección Financiera",
                    value=True,
                    key=f"incluir_proyeccion_{id_cliente}"
                )
            
            st.markdown("---")
            
            # Botón generar
            if st.button("📄 Generar Informe PDF", type="primary", use_container_width=True, key=f"gen_pdf_menu_{id_cliente}"):
                with st.spinner("Generando informe PDF..."):
                    try:
                        import pdf_generator
                        import tempfile
                        import os
                        
                        # Crear archivo temporal
                        temp_dir = tempfile.gettempdir()
                        filename = os.path.join(temp_dir, f"Informe_Ingenieria_Menu_{nombre_cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf")
                        
                        # Generar gráfico si se requiere
                        grafico_path = None
                        if incluir_grafico and PLOTLY_AVAILABLE:
                            try:
                                # Crear gráfico BCG
                                ventas_media = df_carta_cliente['Ventas/Mes'].median()
                                margen_medio = df_carta_cliente['Margen %'].median()
                                
                                def clasificar_plato(ventas, margen):
                                    if ventas >= ventas_media and margen >= margen_medio:
                                        return '⭐ ESTRELLA', '#70AD47'
                                    elif ventas >= ventas_media and margen < margen_medio:
                                        return '🐴 CABALLO', '#4472C4'
                                    elif ventas < ventas_media and margen >= margen_medio:
                                        return '🧩 ROMPECABEZAS', '#FFC000'
                                    else:
                                        return '🐕 PERRO', '#C00000'
                                
                                df_carta_cliente['Cuadrante'], df_carta_cliente['Color'] = zip(*df_carta_cliente.apply(
                                    lambda row: clasificar_plato(row['Ventas/Mes'], row['Margen %']), axis=1
                                ))
                                
                                fig = go.Figure()
                                
                                for cuadrante in df_carta_cliente['Cuadrante'].unique():
                                    df_cuad = df_carta_cliente[df_carta_cliente['Cuadrante'] == cuadrante]
                                    
                                    fig.add_trace(go.Scatter(
                                        x=df_cuad['Ventas/Mes'],
                                        y=df_cuad['Margen %'],
                                        mode='markers+text',
                                        name=cuadrante,
                                        text=df_cuad['Nombre Plato'],
                                        textposition='top center',
                                        marker=dict(
                                            size=df_cuad['Facturación'] / 50,
                                            color=df_cuad['Color'],
                                            line=dict(width=2, color='white')
                                        )
                                    ))
                                
                                fig.add_hline(y=margen_medio, line_dash="dash", line_color="gray")
                                fig.add_vline(x=ventas_media, line_dash="dash", line_color="gray")
                                
                                fig.update_layout(
                                    xaxis_title="Ventas/Mes (unidades)",
                                    yaxis_title="Margen (%)",
                                    showlegend=True,
                                    width=1200,
                                    height=800
                                )
                                
                                # Guardar gráfico
                                grafico_path = os.path.join(temp_dir, "grafico_bcg_temp.png")
                                fig.write_image(grafico_path)
                                
                            except Exception as e:
                                st.warning(f"⚠️ No se pudo generar el gráfico: {str(e)}")
                        
                        # Generar PDF
                        pdf_generator.generar_pdf_ingenieria_menu(
                            filename,
                            nombre_cliente,
                            df_carta_cliente,
                            grafico_path
                        )
                        
                        # Leer PDF generado
                        with open(filename, 'rb') as f:
                            pdf_bytes = f.read()
                        
                        # Botón de descarga
                        st.success("✅ ¡Informe generado exitosamente!")
                        
                        st.download_button(
                            label="⬇️ Descargar Informe PDF",
                            data=pdf_bytes,
                            file_name=f"Informe_Ingenieria_Menu_{nombre_cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        # Limpiar archivos temporales
                        try:
                            os.remove(filename)
                            if grafico_path and os.path.exists(grafico_path):
                                os.remove(grafico_path)
                        except:
                            pass
                        
                    except Exception as e:
                        st.error(f"❌ Error al generar el informe: {str(e)}")
                        st.write("**Detalles:**")
                        st.write("- Verifica que `pdf_generator.py` esté en la carpeta del proyecto")
                        st.write("- Instala: `pip install reportlab --break-system-packages`")
                        st.write("- Para gráficos: `pip install kaleido --break-system-packages`")
    
    # ========================================================================
    # REPORTE MENSUAL
    # ========================================================================
    
    elif tipo_informe == "📊 Reporte Mensual":
        st.subheader("📊 Reporte Mensual Automático")
        
        st.markdown("""
        Este informe incluye:
        - 📅 KPIs del mes seleccionado
        - 🏆 Top 5 platos más vendidos
        - ⚠️ Alertas y recomendaciones
        - 🎯 Plan de acción para próximo mes
        """)
        
        # Selector de mes
        col1, col2 = st.columns(2)
        
        with col1:
            mes = st.selectbox(
                "Mes",
                list(range(1, 13)),
                format_func=lambda x: [
                    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
                ][x-1],
                index=datetime.now().month - 1,
                key=f"mes_reporte_{id_cliente}"
            )
        
        with col2:
            año = st.number_input(
                "Año",
                min_value=2020,
                max_value=2030,
                value=datetime.now().year,
                key=f"año_reporte_{id_cliente}"
            )
        
        st.markdown("---")
        
        # Botón generar
        if st.button("📄 Generar Reporte Mensual", type="primary", use_container_width=True, key=f"gen_pdf_mensual_{id_cliente}"):
            with st.spinner("Generando reporte mensual..."):
                try:
                    import pdf_generator
                    import tempfile
                    import os
                    
                    # Preparar datos del mes
                    df_carta = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
                    df_carta_cliente = df_carta[df_carta['ID Cliente'] == id_cliente].copy()
                    
                    if df_carta_cliente.empty:
                        st.warning("⚠️ No hay datos suficientes para generar el reporte.")
                    else:
                        # Calcular datos del mes
                        df_carta_cliente['Facturación'] = df_carta_cliente['Precio Venta'] * df_carta_cliente['Ventas/Mes']
                        df_carta_cliente['Margen'] = df_carta_cliente['Precio Venta'] - df_carta_cliente['Coste Total']
                        df_carta_cliente['Beneficio'] = df_carta_cliente['Margen'] * df_carta_cliente['Ventas/Mes']
                        
                        datos_mes = {
                            'facturacion': df_carta_cliente['Facturación'].sum(),
                            'beneficio': df_carta_cliente['Beneficio'].sum(),
                            'clientes_activos': 1,
                            'platos_vendidos': int(df_carta_cliente['Ventas/Mes'].sum()),
                            'top_platos': df_carta_cliente.sort_values('Ventas/Mes', ascending=False),
                            'alertas': [
                                "Revisar precios de platos con margen <20%",
                                "Actualizar costes de proveedores",
                                "Realizar inventario quincenal"
                            ]
                        }
                        
                        # Crear archivo temporal
                        temp_dir = tempfile.gettempdir()
                        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
                        filename = os.path.join(temp_dir, f"Reporte_Mensual_{meses[mes-1]}_{año}_{nombre_cliente.replace(' ', '_')}.pdf")
                        
                        # Generar PDF
                        pdf_generator.generar_reporte_mensual(
                            filename,
                            nombre_cliente,
                            mes,
                            año,
                            datos_mes
                        )
                        
                        # Leer PDF generado
                        with open(filename, 'rb') as f:
                            pdf_bytes = f.read()
                        
                        # Botón de descarga
                        st.success("✅ ¡Reporte generado exitosamente!")
                        
                        st.download_button(
                            label="⬇️ Descargar Reporte Mensual",
                            data=pdf_bytes,
                            file_name=f"Reporte_Mensual_{meses[mes-1]}_{año}_{nombre_cliente.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        # Limpiar archivo temporal
                        try:
                            os.remove(filename)
                        except:
                            pass
                        
                except Exception as e:
                    st.error(f"❌ Error al generar el reporte: {str(e)}")
                    st.write("**Detalles:**")
                    st.write("- Verifica que `pdf_generator.py` esté en la carpeta del proyecto")
                    st.write("- Instala: `pip install reportlab --break-system-packages`")
    
    # ========================================================================
    # ANÁLISIS COMPLETO
    # ========================================================================
    
    elif tipo_informe == "📈 Análisis Completo":
        st.subheader("📈 Análisis Completo")
        
        st.info("🚧 Próximamente: Informe completo que combina Ingeniería de Menú + Reporte Mensual + Análisis de Proveedores")
        
        st.markdown("""
        **Incluirá:**
        - 🎯 Análisis de Ingeniería de Menú
        - 📊 KPIs mensuales y evolución
        - 🏢 Análisis de proveedores
        - 💰 Proyecciones financieras
        - 📈 Gráficos de tendencias
        """)

# ============================================================================
# MÓDULO: INFORMES
# ============================================================================

# ============================================================================
# MÓDULO: INFORMES
# ============================================================================

def modulo_informes():
    """Módulo independiente de generación de informes"""
    st.markdown('<h1 class="main-header">📊 Generación de Informes</h1>', unsafe_allow_html=True)
    
    # Cargar clientes activos
    df_clientes_todos = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
    
    # Filtrar solo activos
    if 'Estado' in df_clientes_todos.columns:
        df_clientes = df_clientes_todos[df_clientes_todos['Estado'] == 'Activo'].copy()
    else:
        df_clientes = df_clientes_todos.copy()
    
    if df_clientes.empty:
        st.warning("⚠️ No hay clientes activos.")
        st.info("Ve a CRM → Clientes Activos para gestionar clientes antes de generar informes.")
        return
    
    # ========== SELECTOR DE CLIENTE ==========
    st.markdown("### 👤 Selecciona el Cliente")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        opciones_clientes = [f"{row['ID']} - {row['Nombre Comercial']}" 
                            for _, row in df_clientes.iterrows()]
        
        cliente_seleccionado = st.selectbox(
            "Cliente para generar informe:",
            opciones_clientes,
            help="Selecciona el cliente para el cual quieres generar el informe"
        )
        
        id_cliente = int(float(cliente_seleccionado.split(" - ")[0]))
        nombre_cliente = cliente_seleccionado.split(" - ")[1]
        cliente_info = df_clientes[df_clientes['ID'] == id_cliente].iloc[0]
    
    with col2:
        st.metric("Tipo", cliente_info.get('Tipo Local', 'N/A'))
    
    st.markdown("---")
    
    # ========== TIPOS DE INFORMES ==========
    st.subheader("📋 Tipos de Informes Disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Informe de Apertura")
        st.caption("Análisis inicial de compras y presencia digital")
        if st.button("Generar", key="btn_apertura", use_container_width=True, type="primary"):
            st.session_state.tipo_informe = "apertura"
            st.rerun()
    
    with col2:
        st.markdown("### 📈 Informe de Seguimiento")
        st.caption("Evolución y seguimiento mensual")
        if st.button("Próximamente", key="btn_seguimiento", use_container_width=True, disabled=True):
            pass
    
    with col3:
        st.markdown("### 🎯 Informe Ejecutivo")
        st.caption("Resumen ejecutivo para dirección")
        if st.button("Próximamente", key="btn_ejecutivo", use_container_width=True, disabled=True):
            pass
    
    st.markdown("---")
    
    # ========== GENERACIÓN DEL INFORME ==========
    if st.session_state.get('tipo_informe') == "apertura":
        generar_informe_apertura(id_cliente, nombre_cliente, cliente_info)


def mostrar_generador_informes():
    """Función legacy - redirige al módulo de informes"""
    st.info("ℹ️ La funcionalidad de informes se ha movido al módulo 📊 Informes en el menú principal.")
    st.markdown("Por favor, usa el módulo **📊 Informes** del menú lateral para generar informes.")


def generar_informe_apertura(id_cliente, nombre_cliente, cliente_info):
    """Genera el informe de apertura para un cliente específico"""
    st.header(f"📊 Informe de Apertura - {nombre_cliente}")
    
    st.success("✅ Cliente seleccionado correctamente")
    
    # Tabs del informe
    tab1, tab2, tab3, tab4 = st.tabs([
        "1️⃣ Datos Básicos",
        "2️⃣ Análisis de Compras",
        "3️⃣ Análisis Digital",
        "4️⃣ Generar PDF"
    ])
    
    with tab1:
        st.subheader("📋 Datos del Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Información General**")
            st.write(f"• Nombre Comercial: {cliente_info.get('Nombre Comercial', 'N/A')}")
            st.write(f"• CIF: {cliente_info.get('CIF', 'N/A')}")
            st.write(f"• Tipo de Local: {cliente_info.get('Tipo Local', 'N/A')}")
            st.write(f"• Dirección: {cliente_info.get('Dirección', 'N/A')}")
            st.write(f"• Ciudad: {cliente_info.get('Ciudad', 'N/A')}, {cliente_info.get('CP', 'N/A')}")
        
        with col2:
            st.write("**Datos de Contacto**")
            st.write(f"• Teléfono: {cliente_info.get('Teléfono', 'N/A')}")
            st.write(f"• Email: {cliente_info.get('Email', 'N/A')}")
            st.write(f"• Contacto: {cliente_info.get('Nombre Contacto', 'N/A')}")
            
            st.write("**Servicio**")
            st.write(f"• Contratado: {cliente_info.get('Servicio Contratado', 'N/A')}")
            st.write(f"• Precio Mensual: {cliente_info.get('Precio Mensual', 0):.2f}€")
        
        st.markdown("---")
        
        st.write("**📝 Datos Adicionales para el Informe**")
        
        telefono_comercial = st.text_input("Teléfono Comercial (Consultoría)", 
            placeholder="ej: +34 600 000 000",
            help="Tu teléfono de contacto que aparecerá en el informe",
            key="tel_comercial_apertura")
        
        email_comercial = st.text_input("Email Comercial (Consultoría)", 
            placeholder="ej: info@consultoria.com",
            help="Tu email que aparecerá en el informe",
            key="email_comercial_apertura")
    
    with tab2:
        st.subheader("💰 Análisis de Compras y Proveedores")
        st.info("📊 Aquí podrás analizar productos y detectar sobreprecios")
        
        st.write("**Funcionalidad:** Comparar precios del cliente vs. mercado")
        st.caption("🚧 En desarrollo - Próximamente podrás:")
        st.write("• Añadir productos que compra el cliente")
        st.write("• Comparar con precios de mercado")
        st.write("• Detectar sobreprecios automáticamente")
        st.write("• Calcular ahorro potencial mensual/anual")
    
    with tab3:
        st.subheader("🌐 Análisis de Presencia Digital")
        st.info("📱 Análisis de Google My Business y redes sociales")
        
        st.write("**Funcionalidad:** Detectar problemas en presencia digital")
        st.caption("🚧 En desarrollo - Próximamente podrás:")
        st.write("• Subir capturas de Google My Business")
        st.write("• Detectar problemas (fotos antiguas, reseñas sin responder)")
        st.write("• Analizar competencia local")
        st.write("• Estimar pérdidas por mala gestión digital")
    
    with tab4:
        st.subheader("📄 Generar Informe PDF")
        st.info("🎯 Genera el informe profesional en PDF")
        
        st.write("**Estado del informe:**")
        st.write(f"✅ Datos del cliente: Completos")
        st.write(f"⏳ Análisis de compras: Pendiente")
        st.write(f"⏳ Análisis digital: Pendiente")
        
        st.markdown("---")
        
        if st.button("📄 GENERAR INFORME PDF (Preview)", type="primary", use_container_width=True, key="gen_pdf_apertura"):
            st.success("✅ Generación de PDF implementada próximamente")
            st.info("El informe incluirá:")
            st.write("• Portada con datos del cliente")
            st.write("• Análisis de sobreprecios en compras")
            st.write("• Detección de problemas digitales")
            st.write("• Recomendaciones y plan de acción")
            st.write("• Estimación de ahorro mensual/anual")
            st.balloons()
    
    # Botón para volver
    st.markdown("---")
    if st.button("◀️ Volver a Selección de Informes", key="volver_informes"):
        if 'tipo_informe' in st.session_state:
            del st.session_state.tipo_informe
        st.rerun()

# ============================================================================
# MÓDULO: PROVEEDORES
# ============================================================================

def modulo_proveedores():
    """Módulo de gestión de proveedores"""
    st.markdown('<h1 class="main-header">🏢 Gestión de Proveedores</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Listado", "➕ Agregar/Editar", "📊 Comparativa"])
    
    with tab1:
        mostrar_listado_proveedores()
    
    with tab2:
        mostrar_formulario_proveedor()
    
    with tab3:
        mostrar_comparativa_proveedores()

def mostrar_listado_proveedores():
    """Lista de todos los proveedores"""
    st.subheader("📋 Proveedores Registrados")
    
    df_prov = utils.leer_excel(config.ARCHIVO_PROVEEDORES, "PROVEEDORES")
    
    if not df_prov.empty:
        # Métricas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            total = len(df_prov)
            st.metric("Total Proveedores", total)
        with col2:
            activos = len(df_prov[df_prov['Activo'] == 'Sí']) if 'Activo' in df_prov.columns else 0
            st.metric("Activos", activos)
        with col3:
            if 'Calidad (1-5)' in df_prov.columns:
                media_calidad = df_prov['Calidad (1-5)'].mean()
                st.metric("Calidad Media", f"{media_calidad:.1f}/5")
        
        st.markdown("---")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_tipo = st.multiselect(
                "Filtrar por Tipo",
                options=df_prov['Tipo'].unique() if 'Tipo' in df_prov.columns else [],
                key="filtro_tipo_prov"
            )
        with col2:
            filtro_activo = st.selectbox(
                "Estado",
                ["Todos", "Solo Activos", "Solo Inactivos"],
                key="filtro_activo_prov"
            )
        
        # Aplicar filtros
        df_filtrado = df_prov.copy()
        
        if filtro_tipo:
            df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(filtro_tipo)]
        
        if filtro_activo == "Solo Activos":
            df_filtrado = df_filtrado[df_filtrado['Activo'] == 'Sí']
        elif filtro_activo == "Solo Inactivos":
            df_filtrado = df_filtrado[df_filtrado['Activo'] == 'No']
        
        # Mostrar tabla
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_prov)} proveedores")
    else:
        st.info("📝 No hay proveedores registrados. Ve al tab 'Agregar/Editar' para crear el primero.")

def mostrar_formulario_proveedor():
    """Formulario para agregar/editar proveedores"""
    st.subheader("➕ Agregar Nuevo Proveedor")
    
    df_prov = utils.leer_excel(config.ARCHIVO_PROVEEDORES, "PROVEEDORES")
    
    # Selector: Nuevo o Editar existente
    modo = st.radio(
        "Modo",
        ["Crear Nuevo", "Editar Existente"],
        horizontal=True,
        key="modo_proveedor"
    )
    
    if modo == "Editar Existente":
        if df_prov.empty:
            st.warning("No hay proveedores para editar. Cambia a 'Crear Nuevo'.")
            return
        
        opciones_prov = [f"{row['ID Proveedor']} - {row['Nombre Comercial']}" 
                        for _, row in df_prov.iterrows()]
        prov_seleccionado = st.selectbox(
            "Selecciona Proveedor a Editar",
            opciones_prov,
            key="prov_editar_select"
        )
        
        id_prov_editar = int(float(prov_seleccionado.split(" - ")[0]))
        datos_existentes = df_prov[df_prov['ID Proveedor'] == id_prov_editar].iloc[0].to_dict()
    else:
        datos_existentes = {}
    
    st.markdown("---")
    
    # Formulario
    with st.form("form_proveedor"):
        st.write("### Datos del Proveedor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input(
                "Nombre Comercial*",
                value=datos_existentes.get('Nombre Comercial', ''),
                placeholder="Ej: Distribuciones Alimentarias SA",
                key="nombre_prov_form"
            )
            
            cif = st.text_input(
                "CIF*",
                value=datos_existentes.get('CIF', ''),
                placeholder="Ej: A12345678",
                key="cif_prov_form"
            )
            
            tipo = st.selectbox(
                "Tipo*",
                config.TIPOS_PROVEEDOR,
                index=config.TIPOS_PROVEEDOR.index(datos_existentes.get('Tipo', config.TIPOS_PROVEEDOR[0])) if datos_existentes.get('Tipo') in config.TIPOS_PROVEEDOR else 0,
                key="tipo_prov_form"
            )
            
            especialidad = st.text_input(
                "Especialidad",
                value=datos_existentes.get('Especialidad', ''),
                placeholder="Ej: Carnes, Pescados, General",
                key="espec_prov_form"
            )
        
        with col2:
            telefono = st.text_input(
                "Teléfono",
                value=datos_existentes.get('Teléfono', ''),
                placeholder="948123456",
                key="tel_prov_form"
            )
            
            email = st.text_input(
                "Email",
                value=datos_existentes.get('Email', ''),
                placeholder="info@proveedor.com",
                key="email_prov_form"
            )
            
            contacto = st.text_input(
                "Persona de Contacto",
                value=datos_existentes.get('Contacto', ''),
                placeholder="Nombre Apellidos",
                key="contacto_prov_form"
            )
            
            activo = st.selectbox(
                "Estado",
                ["Sí", "No"],
                index=0 if datos_existentes.get('Activo', 'Sí') == 'Sí' else 1,
                key="activo_prov_form"
            )
        
        st.markdown("### Condiciones Comerciales")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            condiciones_pago = st.text_input(
                "Condiciones de Pago",
                value=datos_existentes.get('Condiciones Pago', ''),
                placeholder="Ej: 30 días",
                key="pago_prov_form"
            )
            
            pedido_min = st.number_input(
                "Pedido Mínimo (€)",
                min_value=0.0,
                value=float(datos_existentes.get('Pedido Mínimo', 0)),
                step=10.0,
                key="pedmin_prov_form"
            )
        
        with col2:
            envio_gratis = st.selectbox(
                "Envío Gratis",
                ["Sí", "No"],
                index=0 if datos_existentes.get('Envío Gratis', 'No') == 'Sí' else 1,
                key="envio_prov_form"
            )
            
            coste_envio = st.number_input(
                "Coste Envío (€)",
                min_value=0.0,
                value=float(datos_existentes.get('Coste Envío', 0)),
                step=5.0,
                key="cenvio_prov_form"
            )
        
        with col3:
            dias_entrega = st.text_input(
                "Días de Entrega",
                value=datos_existentes.get('Días Entrega', ''),
                placeholder="Ej: L,X,V",
                key="dias_prov_form"
            )
        
        st.markdown("### Valoración")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            calidad = st.slider(
                "Calidad (1-5)",
                1.0, 5.0,
                float(datos_existentes.get('Calidad (1-5)', 3.0)),
                0.5,
                key="cal_prov_form"
            )
        
        with col2:
            servicio = st.slider(
                "Servicio (1-5)",
                1.0, 5.0,
                float(datos_existentes.get('Servicio (1-5)', 3.0)),
                0.5,
                key="serv_prov_form"
            )
        
        with col3:
            precio = st.slider(
                "Precio (1-5)",
                1.0, 5.0,
                float(datos_existentes.get('Precio (1-5)', 3.0)),
                0.5,
                key="prec_prov_form"
            )
        
        notas = st.text_area(
            "Notas",
            value=datos_existentes.get('Notas', ''),
            placeholder="Información adicional sobre el proveedor",
            key="notas_prov_form"
        )
        
        # Botones
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                "💾 Guardar Proveedor" if modo == "Crear Nuevo" else "💾 Actualizar Proveedor",
                use_container_width=True,
                type="primary"
            )
        with col2:
            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submitted:
            # Validaciones
            if not nombre or not cif or not tipo:
                st.error("❌ Rellena todos los campos obligatorios (*)")
            else:
                if modo == "Crear Nuevo":
                    # Verificar que no exista CIF duplicado
                    if not df_prov.empty and cif in df_prov['CIF'].values:
                        st.error(f"❌ Ya existe un proveedor con el CIF {cif}")
                    else:
                        nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_PROVEEDORES, "PROVEEDORES")
                        
                        nuevo_proveedor = {
                            'ID Proveedor': nuevo_id,
                            'Nombre Comercial': nombre,
                            'CIF': cif,
                            'Tipo': tipo,
                            'Especialidad': especialidad,
                            'Teléfono': telefono,
                            'Email': email,
                            'Contacto': contacto,
                            'Condiciones Pago': condiciones_pago,
                            'Pedido Mínimo': pedido_min,
                            'Envío Gratis': envio_gratis,
                            'Coste Envío': coste_envio,
                            'Días Entrega': dias_entrega,
                            'Calidad (1-5)': calidad,
                            'Servicio (1-5)': servicio,
                            'Precio (1-5)': precio,
                            'Activo': activo,
                            'Notas': notas
                        }
                        
                        if utils.agregar_fila(config.ARCHIVO_PROVEEDORES, "PROVEEDORES", nuevo_proveedor):
                            st.success(f"✅ Proveedor '{nombre}' creado con ID {nuevo_id}")
                            # Limpiar caché para que se actualice
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                else:
                    # Modo editar
                    df_actualizado = df_prov.copy()
                    mascara = df_actualizado['ID Proveedor'] == id_prov_editar
                    
                    df_actualizado.loc[mascara, 'Nombre Comercial'] = nombre
                    df_actualizado.loc[mascara, 'CIF'] = cif
                    df_actualizado.loc[mascara, 'Tipo'] = tipo
                    df_actualizado.loc[mascara, 'Especialidad'] = especialidad
                    df_actualizado.loc[mascara, 'Teléfono'] = telefono
                    df_actualizado.loc[mascara, 'Email'] = email
                    df_actualizado.loc[mascara, 'Contacto'] = contacto
                    df_actualizado.loc[mascara, 'Condiciones Pago'] = condiciones_pago
                    df_actualizado.loc[mascara, 'Pedido Mínimo'] = pedido_min
                    df_actualizado.loc[mascara, 'Envío Gratis'] = envio_gratis
                    df_actualizado.loc[mascara, 'Coste Envío'] = coste_envio
                    df_actualizado.loc[mascara, 'Días Entrega'] = dias_entrega
                    df_actualizado.loc[mascara, 'Calidad (1-5)'] = calidad
                    df_actualizado.loc[mascara, 'Servicio (1-5)'] = servicio
                    df_actualizado.loc[mascara, 'Precio (1-5)'] = precio
                    df_actualizado.loc[mascara, 'Activo'] = activo
                    df_actualizado.loc[mascara, 'Notas'] = notas
                    
                    if utils.escribir_excel(config.ARCHIVO_PROVEEDORES, "PROVEEDORES", df_actualizado):
                        st.success(f"✅ Proveedor '{nombre}' actualizado")
                        # Limpiar caché
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()

def mostrar_comparativa_proveedores():
    """Comparativa de precios entre proveedores"""
    st.subheader("📊 Comparativa de Precios por Ingrediente")
    st.info("🚧 Funcionalidad en desarrollo")
    
    st.write("**Próximamente podrás:**")
    st.write("• Ver qué proveedores tienen cada ingrediente")
    st.write("• Comparar precios entre proveedores")
    st.write("• Identificar el mejor precio por ingrediente")
    st.write("• Calcular ahorro potencial al cambiar de proveedor")

# ============================================================================
# MÓDULO: EMPRESA
# ============================================================================

def modulo_empresa():
    """Módulo de backoffice y empresa"""
    st.markdown('<h1 class="main-header">💼 Gestión Empresarial</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 KPIs", "💰 Facturación", "📉 Gastos"])
    
    with tab1:
        df_kpis = utils.leer_excel(config.ARCHIVO_EMPRESA, "KPIS_MENSUALES")
        
        if not df_kpis.empty:
            st.dataframe(df_kpis, use_container_width=True, hide_index=True)
        else:
            st.info("No hay KPIs registrados")
    
    with tab2:
        df_fact = utils.leer_excel(config.ARCHIVO_EMPRESA, "FACTURACION")
        
        if not df_fact.empty:
            st.dataframe(df_fact, use_container_width=True, hide_index=True)
        else:
            st.info("No hay facturas registradas")
    
    with tab3:
        df_gastos = utils.leer_excel(config.ARCHIVO_EMPRESA, "GASTOS")
        
        if not df_gastos.empty:
            st.dataframe(df_gastos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay gastos registrados")

# ============================================================================
# MÓDULO: CONFIGURACIÓN
# ============================================================================

def modulo_configuracion():
    """Configuración del sistema"""
    st.markdown('<h1 class="main-header">⚙️ Configuración</h1>', unsafe_allow_html=True)
    
    st.subheader("📁 Rutas del Sistema")
    st.code(f"OneDrive: {config.ONEDRIVE_BASE}")
    st.code(f"Datos: {config.RUTA_DATOS}")
    
    st.markdown("---")
    
    st.subheader("📊 Estado de los Archivos")
    archivos_faltantes = config.verificar_archivos_excel()
    
    if not archivos_faltantes:
        st.success("✅ Todos los archivos Excel están correctamente ubicados")
    else:
        st.error("❌ Archivos faltantes:")
        for archivo in archivos_faltantes:
            st.write(archivo)

# ============================================================================
# MAIN - PUNTO DE ENTRADA
# ============================================================================

def main():
    """Función principal"""
    
    # Verificar sistema
    verificar_sistema()
    
    # Mostrar sidebar y obtener módulo seleccionado
    modulo = mostrar_sidebar()
    
    # Renderizar módulo seleccionado
    if "Dashboard" in modulo:
        modulo_dashboard()
    elif "Clientes" in modulo:
        mod_clientes.modulo_clientes()
    elif "Escandallos" in modulo:
        modulo_escandallos()
    elif "Proveedores" in modulo:
        modulo_proveedores()
    elif "Empresa" in modulo:
        modulo_empresa()
    elif "Informes" in modulo:
        modulo_informes()
    elif "Configuración" in modulo:
        modulo_configuracion()

if __name__ == "__main__":
    main()
