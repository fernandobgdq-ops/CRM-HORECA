"""
TRACKING_CAMBIOS.PY - Sistema para registrar cambios de precio y datos de clientes
Mantiene un registro de qué cambios se han hecho y cuándo
"""

import pandas as pd
from datetime import datetime
import config
import utils
import os

# ============================================================================
# ARCHIVO DE CAMBIOS
# ============================================================================

ARCHIVO_CAMBIOS = os.path.join(config.RUTA_DATOS, "CAMBIOS_REGISTRO.csv")


def registrar_cambio(tipo_cambio, id_cliente, nombre_cliente, campo, valor_anterior, valor_nuevo, detalle=""):
    """
    Registra un cambio en el archivo de cambios.
    
    Parámetros:
    - tipo_cambio: "precio", "datos", "servicio", etc.
    - id_cliente: ID del cliente
    - nombre_cliente: Nombre del cliente
    - campo: El campo que se modificó (ej: "Precio Mensual", "Cachopo")
    - valor_anterior: Valor antes del cambio
    - valor_nuevo: Valor después del cambio
    - detalle: Información adicional
    """
    
    try:
        # Leer cambios existentes
        if os.path.exists(ARCHIVO_CAMBIOS):
            df_cambios = pd.read_csv(ARCHIVO_CAMBIOS)
        else:
            df_cambios = pd.DataFrame()
        
        # Crear nuevo registro
        nuevo_cambio = {
            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Tipo": tipo_cambio,
            "ID Cliente": id_cliente,
            "Nombre Cliente": nombre_cliente,
            "Campo": campo,
            "Valor Anterior": str(valor_anterior),
            "Valor Nuevo": str(valor_nuevo),
            "Detalle": detalle
        }
        
        # Agregar a dataframe
        df_cambios = pd.concat([df_cambios, pd.DataFrame([nuevo_cambio])], ignore_index=True)
        
        # Guardar
        df_cambios.to_csv(ARCHIVO_CAMBIOS, index=False, encoding='utf-8')
        
        return True
        
    except Exception as e:
        print(f"Error registrando cambio: {e}")
        return False


def obtener_cambios_cliente(id_cliente, dias=30):
    """
    Obtiene los cambios de un cliente en los últimos X días
    """
    try:
        if not os.path.exists(ARCHIVO_CAMBIOS):
            return pd.DataFrame()
        
        df_cambios = pd.read_csv(ARCHIVO_CAMBIOS)
        
        if df_cambios.empty:
            return pd.DataFrame()
        
        # Filtrar por cliente
        df_cliente = df_cambios[df_cambios["ID Cliente"] == id_cliente]
        
        # Filtrar por fecha
        df_cliente["Fecha"] = pd.to_datetime(df_cliente["Fecha"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
        fecha_limite = datetime.now() - pd.Timedelta(days=dias)
        df_cliente = df_cliente[df_cliente["Fecha"] >= fecha_limite]
        
        return df_cliente.sort_values("Fecha", ascending=False)
        
    except Exception as e:
        print(f"Error obteniendo cambios: {e}")
        return pd.DataFrame()


def obtener_cambios_ultimos(dias=7):
    """
    Obtiene los cambios de los últimos X días (todos los clientes)
    """
    try:
        if not os.path.exists(ARCHIVO_CAMBIOS):
            return pd.DataFrame()
        
        df_cambios = pd.read_csv(ARCHIVO_CAMBIOS)
        
        if df_cambios.empty:
            return pd.DataFrame()
        
        # Filtrar por fecha
        df_cambios["Fecha"] = pd.to_datetime(df_cambios["Fecha"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
        fecha_limite = datetime.now() - pd.Timedelta(days=dias)
        df_cambios = df_cambios[df_cambios["Fecha"] >= fecha_limite]
        
        return df_cambios.sort_values("Fecha", ascending=False)
        
    except Exception as e:
        print(f"Error obteniendo cambios recientes: {e}")
        return pd.DataFrame()
