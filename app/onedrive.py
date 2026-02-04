"""
ONEDRIVE.PY - Acceso a OneDrive via Microsoft Graph (Device Code)
"""

import os
import time
from io import BytesIO

import requests
import msal

import config

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


def _mostrar_mensaje(mensaje: str) -> None:
    if st:
        st.info(mensaje)
    else:
        print(mensaje)


def _cargar_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if config.ONEDRIVE_TOKEN_CACHE and os.path.exists(config.ONEDRIVE_TOKEN_CACHE):
        with open(config.ONEDRIVE_TOKEN_CACHE, "r", encoding="utf-8") as f:
            cache.deserialize(f.read())
    return cache


def _guardar_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed and config.ONEDRIVE_TOKEN_CACHE:
        with open(config.ONEDRIVE_TOKEN_CACHE, "w", encoding="utf-8") as f:
            f.write(cache.serialize())


def _get_app(cache: msal.SerializableTokenCache) -> msal.PublicClientApplication:
    if not config.ONEDRIVE_CLIENT_ID:
        raise ValueError("Falta ONEDRIVE_CLIENT_ID en variables de entorno.")

    authority = f"https://login.microsoftonline.com/{config.ONEDRIVE_TENANT_ID or 'common'}"
    return msal.PublicClientApplication(
        client_id=config.ONEDRIVE_CLIENT_ID,
        authority=authority,
        token_cache=cache,
    )


def obtener_token_acceso() -> str:
    cache = _cargar_cache()
    app = _get_app(cache)

    cuentas = app.get_accounts()
    resultado = None

    if cuentas:
        resultado = app.acquire_token_silent(config.ONEDRIVE_SCOPES, account=cuentas[0])

    if not resultado:
        flujo = app.initiate_device_flow(scopes=config.ONEDRIVE_SCOPES)
        if "user_code" not in flujo:
            raise RuntimeError("No se pudo iniciar el flujo de dispositivo.")

        _mostrar_mensaje(flujo.get("message", "Abre el enlace y autoriza la app."))
        resultado = app.acquire_token_by_device_flow(flujo)

    _guardar_cache(cache)

    if "access_token" not in resultado:
        raise RuntimeError(f"No se pudo obtener token: {resultado}")

    return resultado["access_token"]


def _headers() -> dict:
    token = obtener_token_acceso()
    return {"Authorization": f"Bearer {token}"}


def _url_contenido(ruta_remota: str) -> str:
    ruta = ruta_remota.lstrip("/")
    return f"https://graph.microsoft.com/v1.0/me/drive/root:/{ruta}:/content"


def descargar_archivo(ruta_remota: str) -> bytes:
    url = _url_contenido(ruta_remota)
    resp = requests.get(url, headers=_headers(), timeout=60)
    if resp.status_code == 404:
        raise FileNotFoundError(f"Archivo no encontrado en OneDrive: {ruta_remota}")
    if not resp.ok:
        raise RuntimeError(f"Error al descargar {ruta_remota}: {resp.status_code} {resp.text}")
    return resp.content


def subir_archivo(ruta_remota: str, contenido: bytes) -> None:
    url = _url_contenido(ruta_remota)
    resp = requests.put(url, headers=_headers(), data=contenido, timeout=120)
    if not resp.ok:
        raise RuntimeError(f"Error al subir {ruta_remota}: {resp.status_code} {resp.text}")
