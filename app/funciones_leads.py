
# ============================================================================
# FUNCIONES PARA NUEVA GESTIÓN DE LEADS
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import config
import utils

def crear_nuevo_lead_modal():
    """Modal para crear un nuevo lead"""
    st.markdown("### ➕ Nuevo Lead")
    
    with st.form(key="form_nuevo_lead"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre Comercial*", placeholder="Ej: Bar El Patio")
            persona = st.text_input("Persona de Contacto", placeholder="Ej: Juan Pérez")
            email = st.text_input("Email", placeholder="juan@ejemplo.com")
            telefono = st.text_input("Teléfono*", placeholder="+34 600 000 000")
        
        with col2:
            estado = st.selectbox("Estado*", ['Nuevo', 'En curso', 'Cliente', 'Baja'], index=0)
            
            temas = st.multiselect(
                "Temas Interés",
                ['Carta Nueva', 'Escandallo', 'Competencia', 'Digital'],
                default=['Carta Nueva']
            )
            temas_str = ', '.join(temas) if temas else ''
            
            canal = st.selectbox(
                "Canal Preferido",
                ['Correo', 'Llamada', 'WhatsApp', 'Reunión presencial']
            )
            
            comercial = st.text_input("Comercial Asignado", placeholder="Nombre del comercial")
        
        origen = st.selectbox(
            "Origen del Lead",
            ['Web', 'LinkedIn', 'Recomendación', 'Publicidad', 'Evento', 'Llamada en frío']
        )
        
        notas = st.text_area("Notas", height=80, placeholder="Información adicional...")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        with col_btn2:
            crear = st.form_submit_button("💾 Crear Lead", use_container_width=True, type="primary")
        
        if cancelar:
            st.session_state['crear_nuevo_lead'] = False
            st.rerun()
        
        if crear:
            if not nombre or not telefono:
                st.error("❌ Nombre y Teléfono son obligatorios")
            else:
                df_leads = utils.leer_excel(config.ARCHIVO_CRM, "LEADS")
                
                nuevo_lead = {
                    'ID': utils.generar_id(),
                    'Nombre Comercial': nombre,
                    'Persona Contacto': persona,
                    'Email': email,
                    'Teléfono': telefono,
                    'Estado Lead': estado,
                    'Temas Interés': temas_str,
                    'Canal Preferido': canal,
                    'Comercial Asignado': comercial,
                    'Origen': origen,
                    'CIF': '',
                    'Dirección': '',
                    'Notas': notas,
                    'Fecha Registro': datetime.now().date()
                }
                
                df_leads = pd.concat([df_leads, pd.DataFrame([nuevo_lead])], ignore_index=True)
                
                st.cache_data.clear()
                if utils.escribir_excel(config.ARCHIVO_CRM, "LEADS", df_leads):
                    st.success("✅ Lead creado correctamente")
                    st.session_state['crear_nuevo_lead'] = False
                    st.cache_data.clear()
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Error al crear lead")


def convertir_lead_a_cliente_modal():
    """Modal para convertir un lead a cliente activo"""
    st.markdown("### 🎉 Convertir Lead a Cliente")
    
    # Obtener el lead a convertir
    id_lead = st.session_state.get('id_lead_convertir')
    nombre_lead = st.session_state.get('nombre_lead_convertir')
    
    df_leads = utils.leer_excel(config.ARCHIVO_CRM, "LEADS")
    
    # Buscar el lead de forma más robusta
    if df_leads.empty:
        st.error("❌ No hay leads disponibles")
        return
    
    # Buscar por ID
    lead_mask = df_leads['ID'] == id_lead
    if not lead_mask.any():
        # Si no encuentra por ID, buscar por nombre
        lead_mask = df_leads['Nombre Comercial'] == nombre_lead
    
    if not lead_mask.any():
        st.error(f"❌ Lead no encontrado (ID: {id_lead}, Nombre: {nombre_lead})")
        st.session_state['convertir_a_cliente'] = False
        return
    
    lead_info = df_leads[lead_mask].iloc[0]
    
    st.success(f"🎉 ¡Enhorabuena! Estás convirtiendo a **{nombre_lead}** en Cliente.")
    st.info("Rellena todos los datos ahora para no tener que editarlos después.")
    
    with st.form(key=f"form_convertir_{id_lead}"):
        # ===== SECCIÓN 1: DATOS BÁSICOS Y GEOLOCALIZACIÓN =====
        st.markdown("### 📋 Datos Básicos y Ubicación")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Obtener lista de nombres de bares (sin duplicados)
            nombres_bares = sorted(df_leads['Nombre Comercial'].unique().tolist())
            
            bar_seleccionado = st.selectbox(
                "🏪 Nombre del Bar *",
                options=nombres_bares,
                index=nombres_bares.index(nombre_lead) if nombre_lead in nombres_bares else 0,
                help="Elige el bar al que se asignará este cliente"
            )
            
            cif = st.text_input(
                "CIF/NIF",
                value=lead_info.get('CIF', ''),
                placeholder="A12345678"
            )
            
            # Manejo seguro del índice de tipo de local
            tipo_local_actual = lead_info.get('Tipo Local', '')
            if tipo_local_actual and tipo_local_actual in config.TIPOS_LOCAL:
                index_tipo_local = config.TIPOS_LOCAL.index(tipo_local_actual)
            else:
                index_tipo_local = 0
            
            tipo_local = st.selectbox(
                "Tipo de Local",
                config.TIPOS_LOCAL,
                index=index_tipo_local
            )
        
        with col2:
            encargado = st.text_input(
                "👤 Encargado Asignado",
                value=lead_info.get('Comercial Asignado', ''),
                placeholder="Nombre del encargado"
            )
            
            # Manejo seguro del índice de fuente
            fuente_actual = lead_info.get('Fuente', '')
            if fuente_actual and fuente_actual in config.FUENTES_CAPTACION:
                index_fuente = config.FUENTES_CAPTACION.index(fuente_actual)
            else:
                index_fuente = 0
            
            fuente = st.selectbox(
                "Fuente de Captación",
                config.FUENTES_CAPTACION,
                index=index_fuente
            )
            
            telefono = st.text_input(
                "📱 Teléfono",
                value=lead_info.get('Teléfono', ''),
                placeholder="+34 600 000 000"
            )
        
        with col3:
            email = st.text_input(
                "📧 Email",
                value=lead_info.get('Email', ''),
                placeholder="contacto@ejemplo.com"
            )
            
            notas = st.text_area(
                "📝 Notas",
                value=lead_info.get('Notas', ''),
                placeholder="Información adicional...",
                height=100
            )
        
        # ===== SECCIÓN 2: DIRECCIÓN Y GEOLOCALIZACIÓN =====
        st.markdown("### 📍 Dirección y Geolocalización")
        
        direccion = st.text_input(
            "Dirección Completa *",
            value=lead_info.get('Dirección', ''),
            placeholder="C/ Principal, 123",
            help="Dirección para geocodificación automática"
        )
        
        col_cp, col_ciudad, col_provincia = st.columns(3)
        
        with col_cp:
            codigo_postal = st.text_input(
                "📬 Código Postal",
                value=lead_info.get('Código Postal', ''),
                placeholder="28001",
                max_chars=5
            )
        
        with col_ciudad:
            ciudad = st.text_input(
                "🏙️ Ciudad *",
                value=lead_info.get('Ciudad', 'Madrid'),
                placeholder="Madrid, Barcelona...",
                help="Ciudad para geocodificación correcta"
            )
        
        with col_provincia:
            provincia = st.text_input(
                "📍 Provincia",
                value=lead_info.get('Provincia', ''),
                placeholder="Madrid, Cataluña..."
            )
        
        # ===== SECCIÓN 3: SERVICIO INICIAL =====
        st.markdown("### 🛠️ Servicio Inicial")
        
        col_serv1, col_serv2 = st.columns(2)
        
        with col_serv1:
            servicio_inicial = st.selectbox(
                "Servicio Contratado *",
                options=list(config.SERVICIOS_DISPONIBLES.keys()),
                index=0
            )
            
            tipo_facturacion = st.selectbox(
                "Tipo Facturación",
                options=['Cuota', 'Puntual'],
                index=0
            )
        
        with col_serv2:
            if tipo_facturacion == 'Cuota':
                precio_inicial = st.number_input(
                    "💰 Precio Mensual (€) *",
                    value=float(config.SERVICIOS_DISPONIBLES[servicio_inicial].get('precio', 0)),
                    min_value=0.0,
                    step=1.0
                )
                precio_unico_inicial = 0.0
            else:
                precio_unico_inicial = st.number_input(
                    "💰 Precio Único (€) *",
                    value=float(config.SERVICIOS_DISPONIBLES[servicio_inicial].get('precio', 0)),
                    min_value=0.0,
                    step=1.0
                )
                precio_inicial = 0.0
            
            estado_servicio = st.selectbox(
                "Estado del Servicio",
                options=['Activo', 'Pausado', 'Cancelado'],
                index=0
            )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        with col_btn2:
            convertir = st.form_submit_button("✅ Convertir a Cliente", use_container_width=True, type="primary")
        
        if cancelar:
            st.session_state['convertir_a_cliente'] = False
            st.rerun()
        
        if convertir:
            # ===== VALIDACIÓN =====
            errores = []
            if not bar_seleccionado or not bar_seleccionado.strip():
                errores.append("🏪 **Nombre del Bar** es obligatorio")
            if not direccion or not direccion.strip():
                errores.append("📍 **Dirección** es obligatoria")
            if not ciudad or not ciudad.strip():
                errores.append("🏙️ **Ciudad** es obligatoria")
            if not servicio_inicial or not servicio_inicial.strip():
                errores.append("🛠️ **Servicio Contratado** es obligatorio")
            if precio_inicial == 0 and precio_unico_inicial == 0:
                errores.append("💰 **Precio** debe ser mayor a 0")
            
            if errores:
                st.error("❌ Faltan campos obligatorios:")
                for error in errores:
                    st.error(error)
            else:
                with st.spinner("Convirtiendo Lead a Cliente..."):
                    # Actualizar datos en el lead
                    df_leads.loc[df_leads['ID'] == id_lead, 'Nombre Comercial'] = bar_seleccionado
                    df_leads.loc[df_leads['ID'] == id_lead, 'CIF'] = cif
                    df_leads.loc[df_leads['ID'] == id_lead, 'Tipo Local'] = tipo_local
                    df_leads.loc[df_leads['ID'] == id_lead, 'Comercial Asignado'] = encargado
                    df_leads.loc[df_leads['ID'] == id_lead, 'Fuente'] = fuente
                    df_leads.loc[df_leads['ID'] == id_lead, 'Teléfono'] = telefono
                    df_leads.loc[df_leads['ID'] == id_lead, 'Email'] = email
                    df_leads.loc[df_leads['ID'] == id_lead, 'Dirección'] = direccion
                    df_leads.loc[df_leads['ID'] == id_lead, 'Ciudad'] = ciudad
                    df_leads.loc[df_leads['ID'] == id_lead, 'Código Postal'] = codigo_postal
                    df_leads.loc[df_leads['ID'] == id_lead, 'Provincia'] = provincia
                    df_leads.loc[df_leads['ID'] == id_lead, 'Notas'] = notas
                    df_leads.loc[df_leads['ID'] == id_lead, 'Estado'] = 'Cliente Activo'
                    
                    # Limpiar caché ANTES de escribir
                    st.cache_data.clear()
                    
                    # Guardar cambios en LEADS
                    if utils.escribir_excel(config.ARCHIVO_CRM, "LEADS", df_leads):
                        time.sleep(1)
                        
                        # ===== GEOCODIFICACIÓN AUTOMÁTICA =====
                        lat, lon = None, None
                        
                        try:
                            from geopy.geocoders import Nominatim
                            geolocator = Nominatim(user_agent="horeca_crm", timeout=5)
                            
                            direccion_completa = f"{direccion.strip()}, {ciudad.strip()}, España"
                            
                            try:
                                location = geolocator.geocode(direccion_completa, language='es')
                                if location:
                                    lat = location.latitude
                                    lon = location.longitude
                                else:
                                    # Fallback a caché de ciudades
                                    ciudades_cache = {
                                        'madrid': (40.4168, -3.7038),
                                        'barcelona': (41.3874, 2.1686),
                                        'valencia': (39.4699, -0.3763),
                                        'sevilla': (37.3891, -5.9845),
                                        'bilbao': (43.2630, -2.9350),
                                    }
                                    ciudad_lower = ciudad.lower().strip()
                                    lat, lon = ciudades_cache.get(ciudad_lower, (40.4168, -3.7038))
                            except Exception as e_nominatim:
                                # Fallback a caché si hay error
                                ciudades_cache = {
                                    'madrid': (40.4168, -3.7038),
                                    'barcelona': (41.3874, 2.1686),
                                    'valencia': (39.4699, -0.3763),
                                    'sevilla': (37.3891, -5.9845),
                                    'bilbao': (43.2630, -2.9350),
                                }
                                ciudad_lower = ciudad.lower().strip()
                                lat, lon = ciudades_cache.get(ciudad_lower, (40.4168, -3.7038))
                        except ImportError:
                            # Si no tiene geopy, usar caché
                            ciudades_cache = {
                                'madrid': (40.4168, -3.7038),
                                'barcelona': (41.3874, 2.1686),
                                'valencia': (39.4699, -0.3763),
                                'sevilla': (37.3891, -5.9845),
                                'bilbao': (43.2630, -2.9350),
                            }
                            ciudad_lower = ciudad.lower().strip()
                            lat, lon = ciudades_cache.get(ciudad_lower, (40.4168, -3.7038))
                        
                        # Crear registro en CLIENTES_ACTIVOS
                        df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
                        
                        nuevo_cliente = {
                            'ID': id_lead,  # Usar el mismo ID
                            'Nombre Comercial': bar_seleccionado,
                            'CIF': cif,
                            'Razón Social': bar_seleccionado,  # Copiar del nombre comercial
                            'Tipo Local': tipo_local,
                            'Dirección': direccion,
                            'Ciudad': ciudad,
                            'CP': codigo_postal,  # Alias para Código Postal
                            'Teléfono': telefono,
                            'Email': email,
                            'Nombre Contacto': '',  # Vacío por defecto
                            'Servicio Contratado': servicio_inicial,
                            'Precio Mensual': float(precio_inicial) if tipo_facturacion == 'Cuota' else 0.0,
                            'Fecha Inicio': datetime.now().date(),
                            'Fecha Fin': None,
                            'Estado': estado_servicio,
                            'MRR': float(precio_inicial) if tipo_facturacion == 'Cuota' else 0.0,
                            'Último Servicio': servicio_inicial,
                            'Satisfacción (1-5)': 3,
                            'Notas': notas,
                            'Encargado': encargado,
                            'Responsable': encargado,  # Copiar del encargado
                            'Precio Único': float(precio_unico_inicial) if tipo_facturacion == 'Puntual' else 0.0,
                            'Tipo Facturación': tipo_facturacion,
                            'Precio Servicio': float(precio_inicial) if tipo_facturacion == 'Cuota' else float(precio_unico_inicial),
                            'Tipo Servicio': tipo_facturacion,
                            'Fuente Captación': fuente,
                            'Comercial Asignado': encargado,
                            'Fecha Alta': datetime.now().date(),
                            'Última Actualización': datetime.now().date(),
                            'Código Postal': codigo_postal,
                            'Provincia': provincia,
                            'Latitud': float(lat) if lat is not None else None,
                            'Longitud': float(lon) if lon is not None else None
                        }
                        
                        df_clientes = pd.concat([df_clientes, pd.DataFrame([nuevo_cliente])], ignore_index=True)
                        
                        st.cache_data.clear()
                        
                        if utils.escribir_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS", df_clientes):
                            time.sleep(1)
                            
                            # ===== ACTUALIZAR ESTADO DEL LEAD EN LEADS =====
                            try:
                                df_leads = utils.leer_excel_forzado(config.ARCHIVO_CRM, "LEADS")
                                # Cambiar estado del lead a "Cliente" (para que sea consistente con otros clientes)
                                lead_mask = df_leads['ID'] == id_lead
                                if lead_mask.any():
                                    df_leads.loc[lead_mask, 'Estado Lead'] = 'Cliente'
                                    st.cache_data.clear()
                                    utils.escribir_excel(config.ARCHIVO_CRM, "LEADS", df_leads)
                                    time.sleep(0.5)
                            except Exception as e:
                                st.warning(f"⚠️ No se pudo actualizar estado en LEADS: {str(e)}")
                            
                            # ===== CREAR REGISTRO INICIAL EN HISTORIAL_CONTRATOS =====
                            try:
                                df_hist = utils.leer_excel_forzado(config.ARCHIVO_CRM, 'HISTORIAL_CONTRATOS')
                            except:
                                df_hist = pd.DataFrame(columns=['ID','ID Cliente','Servicio Anterior','Precio Anterior','Fecha Inicio','Fecha Fin','Tipo','Motivo Cambio'])
                            
                            # Crear registro inicial del servicio contratado
                            registro_inicial = {
                                'ID': utils.generar_id(),
                                'ID Cliente': id_lead,
                                'Servicio Anterior': servicio_inicial,
                                'Precio Anterior': float(precio_inicial) if tipo_facturacion == 'Cuota' else float(precio_unico_inicial),
                                'Fecha Inicio': datetime.now().date(),
                                'Fecha Fin': None,  # Aún activo
                                'Tipo': tipo_facturacion,
                                'Motivo Cambio': f'Conversión de Lead a Cliente - Servicio inicial: {servicio_inicial}'
                            }
                            
                            df_hist = pd.concat([df_hist, pd.DataFrame([registro_inicial])], ignore_index=True)
                            
                            if not utils.escribir_excel(config.ARCHIVO_CRM, 'HISTORIAL_CONTRATOS', df_hist):
                                st.warning("⚠️ Lead convertido pero no se pudo guardar historial inicial")
                            
                            time.sleep(0.5)
                            
                            st.success("✅ ¡Lead convertido a Cliente Activo correctamente!")
                            st.success(f"📍 Geocodificado en: ({lat:.4f}, {lon:.4f})")
                            st.success(f"📝 Servicio inicial '{servicio_inicial}' registrado en historial")
                            st.balloons()
                            st.session_state['convertir_a_cliente'] = False
                            st.cache_data.clear()
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Error al crear cliente")
                    else:
                        st.error("❌ Error al actualizar lead")
