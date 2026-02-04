"""
SOLICITUDES_CAMBIOS.PY - Sistema de solicitudes de cambio con aprobación manual
Permite solicitar cambios pero requiere aprobación antes de aplicarlos
"""

import pandas as pd
from datetime import datetime
import config
import utils
import os

# ============================================================================
# ARCHIVOS
# ============================================================================

ARCHIVO_SOLICITUDES = os.path.join(config.RUTA_DATOS, "SOLICITUDES_CAMBIOS.csv")


def crear_solicitud_cambio(tipo_cambio, id_cliente, nombre_cliente, campo, valor_anterior, valor_nuevo, detalle=""):
    """
    Crea una solicitud de cambio PENDIENTE DE APROBACIÓN
    No aplica el cambio automáticamente
    """
    
    try:
        # Leer solicitudes existentes
        if os.path.exists(ARCHIVO_SOLICITUDES):
            df_solicitudes = pd.read_csv(ARCHIVO_SOLICITUDES)
        else:
            df_solicitudes = pd.DataFrame()
        
        # Crear nueva solicitud
        nueva_solicitud = {
            "ID Solicitud": utils.generar_id(),
            "Fecha Creación": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Tipo": tipo_cambio,
            "ID Cliente": id_cliente,
            "Nombre Cliente": nombre_cliente,
            "Campo": campo,
            "Valor Anterior": str(valor_anterior),
            "Valor Nuevo": str(valor_nuevo),
            "Detalle": detalle,
            "Estado": "Pendiente",
            "Fecha Aprobación": "",
            "Aprobado Por": ""
        }
        
        # Agregar a dataframe
        df_solicitudes = pd.concat([df_solicitudes, pd.DataFrame([nueva_solicitud])], ignore_index=True)
        
        # Guardar
        df_solicitudes.to_csv(ARCHIVO_SOLICITUDES, index=False, encoding='utf-8')
        
        return nueva_solicitud["ID Solicitud"]
        
    except Exception as e:
        print(f"Error creando solicitud: {e}")
        return None


def obtener_solicitudes_pendientes():
    """
    Obtiene todas las solicitudes PENDIENTES de aprobación
    """
    try:
        if not os.path.exists(ARCHIVO_SOLICITUDES):
            return pd.DataFrame()
        
        df = pd.read_csv(ARCHIVO_SOLICITUDES)
        
        if df.empty:
            return pd.DataFrame()
        
        # Filtrar pendientes
        return df[df["Estado"] == "Pendiente"].sort_values("Fecha Creación", ascending=False)
        
    except Exception as e:
        print(f"Error obteniendo solicitudes: {e}")
        return pd.DataFrame()


def obtener_solicitudes_cliente(id_cliente):
    """
    Obtiene todas las solicitudes (aprobadas, rechazadas, pendientes) de un cliente
    """
    try:
        if not os.path.exists(ARCHIVO_SOLICITUDES):
            return pd.DataFrame()
        
        df = pd.read_csv(ARCHIVO_SOLICITUDES)
        
        if df.empty:
            return pd.DataFrame()
        
        # Filtrar por cliente
        return df[df["ID Cliente"] == id_cliente].sort_values("Fecha Creación", ascending=False)
        
    except Exception as e:
        print(f"Error obteniendo solicitudes del cliente: {e}")
        return pd.DataFrame()


def aprobar_solicitud(id_solicitud, aprobado_por="Administrador"):
    """
    Aprueba una solicitud y aplica el cambio
    Retorna True si se aplicó correctamente
    """
    try:
        if not os.path.exists(ARCHIVO_SOLICITUDES):
            return False
        
        df = pd.read_csv(ARCHIVO_SOLICITUDES)
        
        # Encontrar solicitud
        mask = df["ID Solicitud"] == id_solicitud
        if not mask.any():
            return False
        
        solicitud = df[mask].iloc[0]
        
        # Aplicar el cambio en Excel (depende del tipo)
        if solicitud["Tipo"] == "precio":
            # Actualizar precio en CLIENTES_ACTIVOS
            df_clientes = utils.leer_excel_forzado(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
            mask_cliente = df_clientes["ID"] == solicitud["ID Cliente"]
            
            if mask_cliente.any():
                df_clientes.loc[mask_cliente, solicitud["Campo"]] = float(solicitud["Valor Nuevo"])
                
                # Guardar cambio en Excel
                utils.cache_data.clear() if hasattr(utils, 'cache_data') else None
                if not utils.escribir_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS", df_clientes):
                    return False
        
        # Marcar solicitud como aprobada
        df.loc[mask, "Estado"] = "Aprobado"
        df.loc[mask, "Fecha Aprobación"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        df.loc[mask, "Aprobado Por"] = aprobado_por
        
        df.to_csv(ARCHIVO_SOLICITUDES, index=False, encoding='utf-8')
        
        return True
        
    except Exception as e:
        print(f"Error aprobando solicitud: {e}")
        return False


def rechazar_solicitud(id_solicitud, motivo=""):
    """
    Rechaza una solicitud (no aplica el cambio)
    """
    try:
        if not os.path.exists(ARCHIVO_SOLICITUDES):
            return False
        
        df = pd.read_csv(ARCHIVO_SOLICITUDES)
        
        # Encontrar solicitud
        mask = df["ID Solicitud"] == id_solicitud
        if not mask.any():
            return False
        
        # Marcar como rechazada
        df.loc[mask, "Estado"] = "Rechazado"
        df.loc[mask, "Fecha Aprobación"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        df.loc[mask, "Aprobado Por"] = f"Rechazado - {motivo}"
        
        df.to_csv(ARCHIVO_SOLICITUDES, index=False, encoding='utf-8')
        
        return True
        
    except Exception as e:
        print(f"Error rechazando solicitud: {e}")
        return False
