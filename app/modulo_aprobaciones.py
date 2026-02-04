"""
MODULO_APROBACIONES.PY - Panel de aprobación de cambios
Permite revisar y aprobar/rechazar solicitudes de cambios antes de aplicarlos
"""

import streamlit as st
import pandas as pd
import config
import utils
import solicitudes_cambios
import time

# ============================================================================
# MÓDULO PRINCIPAL
# ============================================================================

def modulo_aprobaciones():
	"""Panel de aprobación de cambios"""
	
	st.markdown('<h1 class="main-header">📋 Aprobaciones Pendientes</h1>', unsafe_allow_html=True)
	
	# Obtener solicitudes pendientes
	df_pendientes = solicitudes_cambios.obtener_solicitudes_pendientes()
	
	if df_pendientes.empty:
		st.success("✅ No hay solicitudes pendientes de aprobación")
		return
	
	# Mostrar estadísticas
	col1, col2, col3 = st.columns(3)
	with col1:
		st.metric("Total Pendiente", len(df_pendientes))
	with col2:
		precios = len(df_pendientes[df_pendientes["Tipo"] == "precio"])
		st.metric("Cambios de Precio", precios)
	with col3:
		datos = len(df_pendientes[df_pendientes["Tipo"] == "datos"])
		st.metric("Cambios de Datos", datos)
	
	st.markdown("---")
	
	# Mostrar cada solicitud pendiente
	st.markdown("### 🔍 Solicitudes para Revisar")
	
	for idx, (_, solicitud) in enumerate(df_pendientes.iterrows()):
		# Contenedor expandible para cada solicitud
		with st.expander(
			f"📝 {solicitud['Tipo'].upper()} - {solicitud['Nombre Cliente']} - {solicitud['Campo']}",
			expanded=(idx == 0)
		):
			# Información de la solicitud
			col1, col2 = st.columns(2)
			
			with col1:
				st.markdown("**Información General**")
				st.write(f"ID Solicitud: `{solicitud['ID Solicitud']}`")
				st.write(f"Fecha: {solicitud['Fecha Creación']}")
				st.write(f"Cliente: **{solicitud['Nombre Cliente']}**")
				st.write(f"Tipo: **{solicitud['Tipo'].upper()}**")
			
			with col2:
				st.markdown("**Cambio Propuesto**")
				st.write(f"Campo: **{solicitud['Campo']}**")
				try:
					ant = float(solicitud['Valor Anterior'])
					nue = float(solicitud['Valor Nuevo'])
					dif = nue - ant
					dif_pct = (dif / ant * 100) if ant != 0 else 0
					
					st.write(f"Valor Anterior: `{ant:.2f}`")
					st.write(f"Valor Nuevo: `{nue:.2f}`")
					st.write(f"Diferencia: `{dif:+.2f}` ({dif_pct:+.1f}%)")
				except:
					st.write(f"Valor Anterior: `{solicitud['Valor Anterior']}`")
					st.write(f"Valor Nuevo: `{solicitud['Valor Nuevo']}`")
			
			# Detalle
			if pd.notna(solicitud['Detalle']) and solicitud['Detalle'] != "":
				st.markdown("**Detalle:**")
				st.info(solicitud['Detalle'])
			
			# Botones de aprobación/rechazo
			st.markdown("---")
			col1, col2, col3 = st.columns([2, 2, 2])
			
			with col1:
				if st.button(
					"✅ APROBAR",
					key=f"aprobar_{solicitud['ID Solicitud']}",
					help="Aplica este cambio",
					use_container_width=True,
					type="primary"
				):
					# Aprobar solicitud
					if solicitudes_cambios.aprobar_solicitud(solicitud['ID Solicitud'], aprobado_por="Admin"):
						st.success(f"✅ Solicitud aprobada e implementada")
						st.cache_data.clear()
						time.sleep(1)
						st.rerun()
					else:
						st.error("❌ Error al aprobar solicitud")
			
			with col2:
				motivo = st.text_input("Motivo (opcional):", key=f"motivo_{solicitud['ID Solicitud']}")
				if st.button(
					"❌ RECHAZAR",
					key=f"rechazar_{solicitud['ID Solicitud']}",
					help="Descarta este cambio",
					use_container_width=True,
					type="secondary"
				):
					# Rechazar solicitud
					if solicitudes_cambios.rechazar_solicitud(solicitud['ID Solicitud'], motivo=motivo):
						st.warning(f"❌ Solicitud rechazada")
						st.cache_data.clear()
						time.sleep(1)
						st.rerun()
					else:
						st.error("❌ Error al rechazar solicitud")
			
			with col3:
				st.empty()  # Espacio vacío para balance visual
	
	# Histórico de solicitudes
	st.markdown("---")
	st.markdown("### 📊 Histórico de Solicitudes")
	
	# Obtener todas las solicitudes (no solo pendientes)
	try:
		import os
		archivo = os.path.join(config.RUTA_DATOS, "SOLICITUDES_CAMBIOS.csv")
		if os.path.exists(archivo):
			df_todas = pd.read_csv(archivo)
			
			# Filtrar por estado
			estado_filtro = st.selectbox(
				"Filtrar por estado:",
				["Pendiente", "Aprobado", "Rechazado", "Todos"],
				key="historico_estado"
			)
			
			if estado_filtro != "Todos":
				df_mostrar = df_todas[df_todas["Estado"] == estado_filtro]
			else:
				df_mostrar = df_todas
			
			if not df_mostrar.empty:
				# Mostrar tabla
				st.dataframe(
					df_mostrar[[
						"Fecha Creación", "Nombre Cliente", "Campo", 
						"Valor Anterior", "Valor Nuevo", "Estado", "Fecha Aprobación"
					]].sort_values("Fecha Creación", ascending=False),
					use_container_width=True,
					hide_index=True
				)
			else:
				st.info(f"Sin solicitudes {estado_filtro.lower()}")
	except:
		st.info("No hay historico de solicitudes aún")
