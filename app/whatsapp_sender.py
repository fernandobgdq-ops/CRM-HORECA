# filepath: whatsapp_sender.py

import streamlit as st
from datetime import datetime
import urllib.parse
import pandas as pd
import time

def registrar_envio_whatsapp(id_cliente, nombre_cliente, cantidad_platos):
    """
    Registra el envío de WhatsApp en el Timeline de Actividad
    
    Args:
        id_cliente: ID del cliente
        nombre_cliente: Nombre del cliente
        cantidad_platos: Cantidad de platos alertados
    """
    
    try:
        from config import ARCHIVO_CRM
        import utils
        
        # Crear registro
        registro = {
            'ID Cliente': id_cliente,
            'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Tipo': 'WhatsApp',
            'Descripción': f'Alerta de precios enviada - {cantidad_platos} plato(s) con Food Cost > 35%'
        }
        
        # Cargar interacciones
        df_int = utils.leer_excel_forzado(ARCHIVO_CRM, "INTERACCIONES")
        
        if df_int.empty:
            df_int = pd.DataFrame([registro])
        else:
            df_int = pd.concat([df_int, pd.DataFrame([registro])], ignore_index=True)
        
        # Guardar
        if utils.escribir_excel(ARCHIVO_CRM, "INTERACCIONES", df_int):
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error registrando WhatsApp: {str(e)}")
        return False


def generar_mensaje_alerta(nombre_contacto, platos_alerta):
    """
    Genera mensaje de alerta de precios para WhatsApp
    
    Args:
        nombre_contacto: Nombre del contacto principal (no del cliente)
        platos_alerta: Lista de dicts con {nombre, food_cost, precio_actual, precio_recomendado}
    
    Returns:
        String con el mensaje formateado
    """
    
    mensaje = f"📊 *ALERTA DE PRECIOS*\n\n"
    mensaje += f"Hola {nombre_contacto}, 👋\n\n"
    mensaje += "Se ha detectado que algunos platos de tu carta tienen precios incorrectos.\n\n"
    mensaje += "*🔴 PLATOS A REVISAR:*\n"
    
    for idx, plato in enumerate(platos_alerta, 1):
        nombre = plato['nombre']
        precio_actual = plato['precio_actual']
        precio_recomendado = plato['precio_recomendado']
        incremento = precio_recomendado - precio_actual
        
        mensaje += f"\n{idx}. *{nombre}*\n"
        mensaje += f"   💰 Actual: {precio_actual:.2f}€\n"
        mensaje += f"   📈 Recomendado: {precio_recomendado:.2f}€\n"
        mensaje += f"   ➕ Incremento: +{incremento:.2f}€\n"
    
    mensaje += f"\n\n💡 *RECOMENDACIÓN:*\n"
    mensaje += "Subir estos precios genera:\n"
    mensaje += "• Mayor margen unitario\n"
    mensaje += "• Mejor posicionamiento de marca\n"
    mensaje += "• Impacto mínimo en demanda\n\n"
    mensaje += "Si tienes alguna duda llamame!"
    
    return mensaje


def enviar_whatsapp_automatico(numero_telefono, mensaje):
    """
    Genera URL para WhatsApp Web (sin abrir nueva pestaña)
    
    Args:
        numero_telefono: Número del cliente
        mensaje: Texto del mensaje
    
    Returns:
        tuple: (éxito: bool, resultado: str, url: str)
    """
    
    try:
        # Limpiar número
        numero_limpio = numero_telefono.replace(" ", "").replace("-", "").replace("+", "")
        
        # Agregar código de país si no lo tiene
        if not numero_limpio.startswith("34"):
            numero_limpio = "34" + numero_limpio
        
        # Agregar +
        numero_final = "+" + numero_limpio
        
        # Codificar mensaje para URL
        mensaje_encoded = urllib.parse.quote(mensaje)
        
        # URL de WhatsApp Web
        url_whatsapp = f"https://web.whatsapp.com/send?phone={numero_final}&text={mensaje_encoded}"
        
        return True, "URL generada", url_whatsapp
        
    except Exception as e:
        return False, f"❌ Error: {str(e)}", ""


def mostrar_boton_enviar_whatsapp(nombre_cliente, numero_telefono, platos_alerta, id_cliente, key_suffix=""):
    """
    Muestra botón para enviar alerta a WhatsApp usando contacto principal
    
    Args:
        nombre_cliente: Nombre del cliente
        numero_telefono: Número del cliente
        platos_alerta: Lista de platos con precios incorrectos
        id_cliente: ID del cliente (para obtener contacto principal)
        key_suffix: Sufijo para la clave única del botón
    """
    
    from config import ARCHIVO_CRM
    import utils
    
    if not numero_telefono or numero_telefono == "":
        st.warning("⚠️ Cliente sin teléfono registrado")
        return
    
    # Buscar contacto principal
    df_contactos = utils.leer_excel_forzado(ARCHIVO_CRM, "CONTACTOS")
    contacto_principal = None
    nombre_contacto = nombre_cliente  # Default al nombre del cliente
    
    if not df_contactos.empty:
        contactos_cliente = df_contactos[df_contactos['ID Cliente'] == id_cliente]
        if not contactos_cliente.empty:
            # Convertir 'Es Principal' a bool si es necesario
            contactos_cliente = contactos_cliente.copy()
            contactos_cliente['Es Principal'] = contactos_cliente['Es Principal'].astype(bool)
            principal = contactos_cliente[contactos_cliente['Es Principal'] == True]
            if not principal.empty:
                contacto_principal = principal.iloc[0]
                nombre_contacto = contacto_principal.get('Nombre Contacto', nombre_cliente)
                # Usar teléfono del contacto si existe, sino usar el del cliente
                tel_contacto = contacto_principal.get('Teléfono', '')
                if tel_contacto and str(tel_contacto).strip() != '':
                    numero_telefono = str(tel_contacto)
    
    if st.button(
        "📱 Enviar a WhatsApp",
        key=f"btn_whatsapp_{key_suffix}",
        use_container_width=True,
        type="primary"
    ):
        # Generar mensaje con nombre del contacto principal
        mensaje = generar_mensaje_alerta(nombre_contacto, platos_alerta)
        exito, resultado, url = enviar_whatsapp_automatico(numero_telefono, mensaje)
        
        if exito:
            # Registrar en Timeline
            registrar_envio_whatsapp(id_cliente, nombre_cliente, len(platos_alerta))
            
            # Abrir WhatsApp Web
            import webbrowser
            webbrowser.open(url)
            
            st.success(f"✅ WhatsApp abierto - El mensaje a {nombre_contacto} está listo, solo presiona Enter")
            st.balloons()
        else:
            st.error(resultado)
