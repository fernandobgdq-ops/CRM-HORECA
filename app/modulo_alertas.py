"""
MODULO_ALERTAS.PY - Sistema de Alertas Inteligentes
Detecta cambios y genera alertas relevantes para cada cliente
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import config
import utils
import tracking_cambios

# ============================================================================
# CONSTRUCCIÓN DE ALERTAS
# ============================================================================

def construir_alertas_cliente(id_cliente, nombre_cliente):
	"""
	Construye alertas para un cliente específico.
	Lee de CLIENTES_ACTIVOS y genera alertas básicas.
	"""
	alertas = []

	try:
		# Leer datos del cliente desde CLIENTES_ACTIVOS
		df_clientes = utils.leer_excel_forzado(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
		
		if df_clientes.empty:
			return alertas
		
		# Filtrar por cliente
		cliente = df_clientes[df_clientes["ID"] == id_cliente]
		
		if cliente.empty:
			return alertas
		
		cliente = cliente.iloc[0]
		
		# ----- ALERTA: DATOS INCOMPLETOS -----
		campos_obligatorios = ["Dirección", "Ciudad", "Teléfono", "Email"]
		campos_vacios = [c for c in campos_obligatorios if pd.isna(cliente.get(c)) or str(cliente.get(c)).strip() == ""]
		
		if campos_vacios:
			alertas.append({
				"nivel": "advertencia",
				"categoria": "Cliente",
				"titulo": "Datos incompletos",
				"detalle": f"Faltan: {', '.join(campos_vacios)}",
				"impacto": "Completa los datos para mejorar comunicación",
				"origen": "CLIENTES_ACTIVOS"
			})
		
		# ----- ALERTA: SERVICIO PRÓXIMO A VENCER -----
		fecha_fin = cliente.get("Fecha Fin")
		if pd.notna(fecha_fin):
			fecha_fin = pd.to_datetime(fecha_fin)
			dias_restantes = (fecha_fin - datetime.now()).days
			
			if 0 <= dias_restantes <= 30:
				alertas.append({
					"nivel": "critica",
					"categoria": "Cliente",
					"titulo": "Servicio próximo a vencer",
					"detalle": f"Vence en {dias_restantes} días ({fecha_fin.strftime('%d/%m/%Y')})",
					"impacto": "Contacta cliente para renovación",
					"origen": "CLIENTES_ACTIVOS"
				})
			elif dias_restantes < 0:
				alertas.append({
					"nivel": "critica",
					"categoria": "Cliente",
					"titulo": "Servicio vencido",
					"detalle": f"Vencido hace {abs(dias_restantes)} días",
					"impacto": "Contacta inmediatamente para renovación",
					"origen": "CLIENTES_ACTIVOS"
				})
		
		# ----- ALERTA: BAJA SATISFACCIÓN -----
		satisfaccion = cliente.get("Satisfacción (1-5)")
		if pd.notna(satisfaccion):
			try:
				satisfaccion = float(satisfaccion)
				if satisfaccion < 3:
					alertas.append({
						"nivel": "critica",
						"categoria": "Cliente",
						"titulo": "Baja satisfacción del cliente",
						"detalle": f"Puntuación: {satisfaccion:.1f}/5",
						"impacto": "Realiza seguimiento urgente para mejorar relación",
						"origen": "CLIENTES_ACTIVOS"
					})
			except:
				pass
		
		# ----- ALERTA: SIN ACTUALIZACIONES RECIENTES -----
		ultima_act = cliente.get("Última Actualización")
		if pd.notna(ultima_act):
			ultima_act = pd.to_datetime(ultima_act)
			dias_sin_actualizar = (datetime.now() - ultima_act).days
			
			if dias_sin_actualizar > 30:
				alertas.append({
					"nivel": "advertencia",
					"categoria": "Cliente",
					"titulo": "Sin actualizaciones recientes",
					"detalle": f"Última actualización hace {dias_sin_actualizar} días",
					"impacto": "Realiza seguimiento y actualiza información",
					"origen": "CLIENTES_ACTIVOS"
				})
		
	except Exception as e:
		print(f"Error en construir_alertas_cliente: {e}")
	
	return alertas


def construir_alertas_cambios(id_cliente, nombre_cliente):
	"""
	Construye alertas basadas en cambios recientes
	"""
	alertas = []
	
	try:
		# Obtener cambios de últimos 7 días
		df_cambios = tracking_cambios.obtener_cambios_cliente(id_cliente, dias=7)
		
		if df_cambios.empty:
			return alertas
		
		# Por cada cambio, crear una alerta
		for _, row in df_cambios.iterrows():
			tipo = row.get("Tipo", "")
			campo = row.get("Campo", "")
			valor_anterior = row.get("Valor Anterior", "")
			valor_nuevo = row.get("Valor Nuevo", "")
			fecha = row.get("Fecha", "")
			
			# Cambios de precio
			if tipo == "precio":
				try:
					ant = float(valor_anterior)
					nue = float(valor_nuevo)
					dif = nue - ant
					dif_pct = (dif / ant * 100) if ant > 0 else 0
					
					alertas.append({
						"nivel": "advertencia",
						"categoria": "Cambios",
						"titulo": f"Cambio de precio en {campo}",
						"detalle": f"{ant:.2f}€ → {nue:.2f}€ ({dif_pct:+.1f}%)",
						"impacto": f"Cambio registrado el {fecha}",
						"origen": "CAMBIOS_REGISTRO"
					})
				except:
					pass
			
			# Cambios de datos
			elif tipo == "datos":
				alertas.append({
					"nivel": "advertencia",
					"categoria": "Cambios",
					"titulo": f"Actualización en {campo}",
					"detalle": f"'{valor_anterior}' → '{valor_nuevo}'",
					"impacto": f"Cambio registrado el {fecha}",
					"origen": "CAMBIOS_REGISTRO"
				})
	
	except Exception as e:
		print(f"Error en construir_alertas_cambios: {e}")
	
	return alertas

# ============================================================================
# RENDERIZADO
# ============================================================================

def _render_alerta(alerta, id_cliente=None):
	"""Renderiza una alerta individual"""
	nivel = alerta.get("nivel", "advertencia")
	clase = "warning-box"
	icono = "⚠️"

	if nivel == "critica":
		clase = "danger-box"
		icono = "🚨"
	elif nivel == "oportunidad":
		clase = "success-box"
		icono = "✅"

	titulo = alerta.get("titulo", "Alerta")
	detalle = alerta.get("detalle", "")
	impacto = alerta.get("impacto", "")
	categoria = alerta.get("categoria", "")

	st.markdown(
		f"""
		<div class="{clase}">
			<strong>{icono} {titulo}</strong><br/>
			<span>{detalle}</span><br/>
			<em>{impacto}</em>
			{f"<br/><small>Área: {categoria}</small>" if categoria else ""}
		</div>
		""",
		unsafe_allow_html=True
	)


# ============================================================================
# BANNERS CONTEXTUALES
# ============================================================================

def mostrar_banners_alertas(id_cliente, nombre_cliente, contexto=None, max_items=3):
	"""Muestra alertas en contexto (usado en diferentes pantallas)"""
	try:
		alertas = construir_alertas_cliente(id_cliente, nombre_cliente)

		if contexto:
			alertas = [a for a in alertas if a.get("categoria") == contexto]

		if not alertas:
			return

		st.markdown("### 🚨 Alertas relevantes")
		for alerta in alertas[:max_items]:
			_render_alerta(alerta, id_cliente)
	except Exception as e:
		# Sin mostrar error, simplemente no mostrar alertas si hay problema
		pass


# ============================================================================
# MÓDULO PRINCIPAL
# ============================================================================

def modulo_alertas():
	"""Pantalla principal de alertas"""
	st.markdown('<h1 class="main-header">🚨 Alertas Inteligentes</h1>', unsafe_allow_html=True)

	# Selector de cliente
	df_clientes = utils.leer_excel_forzado(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
	if df_clientes.empty:
		st.info("No hay clientes activos registrados")
		return

	opciones = [f"{int(row['ID'])} - {row['Nombre Comercial']}" for _, row in df_clientes.iterrows()]
	cliente_sel = st.selectbox("Selecciona Cliente", opciones, key="alertas_cliente_sel")

	try:
		id_cliente = int(cliente_sel.split(" - ")[0])
		nombre_cliente = cliente_sel.split(" - ")[1]
	except:
		st.error("Error al procesar selección de cliente")
		return

	# Combinar alertas de estado + cambios
	alertas_estado = construir_alertas_cliente(id_cliente, nombre_cliente)
	alertas_cambios = construir_alertas_cambios(id_cliente, nombre_cliente)
	alertas = alertas_estado + alertas_cambios

	# Métricas
	total = len(alertas)
	criticas = len([a for a in alertas if a["nivel"] == "critica"])
	advertencias = len([a for a in alertas if a["nivel"] == "advertencia"])
	cambios_recientes = len(alertas_cambios)

	col1, col2, col3, col4 = st.columns(4)
	with col1:
		st.metric("Total", total)
	with col2:
		st.metric("🚨 Críticas", criticas)
	with col3:
		st.metric("⚠️ Advertencias", advertencias)
	with col4:
		st.metric("📝 Cambios Recientes", cambios_recientes)

	st.markdown("---")

	if total == 0:
		st.success("✅ No hay alertas. Cliente en buen estado.")
		return

	tab1, tab2, tab3, tab4 = st.tabs(["🚨 Críticas", "⚠️ Advertencias", "📝 Cambios Recientes", "📌 Resumen"])

	with tab1:
		criticas_list = [a for a in alertas if a["nivel"] == "critica"]
		if not criticas_list:
			st.success("Sin alertas críticas")
		else:
			for a in criticas_list:
				_render_alerta(a, id_cliente)

	with tab2:
		advert_list = [a for a in alertas if a["nivel"] == "advertencia" and a["categoria"] != "Cambios"]
		if not advert_list:
			st.success("Sin advertencias")
		else:
			for a in advert_list:
				_render_alerta(a, id_cliente)

	with tab3:
		cambios_list = [a for a in alertas if a["categoria"] == "Cambios"]
		if not cambios_list:
			st.info("Sin cambios recientes (últimos 7 días)")
		else:
			for a in cambios_list:
				_render_alerta(a, id_cliente)

	with tab4:
		st.markdown("### 📋 Resumen Completo")
		
		# Tabla de alertas
		df_alertas = pd.DataFrame([
			{
				"Nivel": a["nivel"].upper(),
				"Categoría": a["categoria"],
				"Título": a["titulo"],
				"Detalle": a["detalle"]
			}
			for a in alertas
		])
		
		if not df_alertas.empty:
			st.dataframe(df_alertas, use_container_width=True, hide_index=True)
		else:
			st.info("Sin alertas")
		
		# Recomendaciones
		st.markdown("### 💡 Recomendaciones")
		for alerta in alertas:
			st.markdown(f"- **{alerta['titulo']}**: {alerta['impacto']}")

