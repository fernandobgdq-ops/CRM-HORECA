"""
MÓDULO DE SINCRONIZACIÓN EXCEL
Valida y sincroniza todos los datos entre hojas Excel
"""

import pandas as pd
import config
import utils
from datetime import datetime

# ============================================================================
# VALIDACIÓN DE ESTRUCTURA EXCEL
# ============================================================================

ESTRUCTURA_ESPERADA = {
    config.ARCHIVO_CRM: {
        "LEADS": [
            'ID', 'Nombre Comercial', 'Persona Contacto', 'Email', 'Teléfono',
            'Estado Lead', 'Temas Interés', 'Canal Preferido', 'Comercial Asignado',
            'Origen', 'CIF', 'Dirección', 'Notas', 'Fecha Registro'
        ],
        "CLIENTES_ACTIVOS": [
            'ID', 'Nombre Comercial', 'CIF', 'Tipo Local', 'Comercial Asignado',
            'Teléfono', 'Email', 'Dirección', 'Estado', 'Servicio Contratado', 
            'Precio Mensual', 'MRR', 'Fecha Alta', 'Satisfacción (1-5)', 'Notas'
        ],
        "INTERACCIONES": [
            'ID', 'ID Cliente', 'Nombre Cliente', 'Tipo', 'Descripción', 'Fecha',
            'Próxima Acción', 'Fecha Próxima Acción', 'Usuario', 'Notas'
        ],
        "SERVICIOS": [
            'ID', 'Nombre Servicio', 'Descripción', 'Precio', 'Activo'
        ],
        "CONTACTOS": [
            'ID', 'ID Cliente', 'Nombre Cliente', 'Nombre Contacto', 'Cargo',
            'Teléfono', 'Email', 'WhatsApp', 'Es Principal', 'Notas', 'Fecha Registro'
        ]
    },
    config.ARCHIVO_OPERACIONES: {
        "CARTA_CLIENTES": [
            'ID Plato', 'ID Cliente', 'Nombre Cliente', 'Nombre Plato',
            'Categoría', 'Precio Venta', 'Coste Total', 'Margen €', 'Margen %',
            'Food Cost %', 'Ventas/Mes', 'Clasificación', 'Precio Recomendado',
            'Activo', 'Notas'
        ],
        "ESCANDALLOS": [
            'ID Escandallo', 'ID Plato', 'Nombre Plato', 'ID Ingrediente',
            'Nombre Ingrediente', 'Cantidad', 'Unidad', 'Coste Unitario',
            'Coste Total', '% del Plato', 'ID Proveedor', 'Última Actualización'
        ],
        "INGREDIENTES_MAESTRO": [
            'ID Ingrediente', 'Nombre', 'Categoría', 'Unidad Compra',
            'Precio Mercado Medio', 'Var % Semana', 'Var % Mes',
            'Última Actualización', 'Estacionalidad', 'Marca', 'Notas'
        ],
        "PRECIOS_POR_CLIENTE": [
            'ID Precio', 'ID Cliente', 'Nombre Cliente', 'ID Ingrediente',
            'Nombre Ingrediente', 'Precio Cliente', 'Unidad',
            'Precio Mercado Referencia', 'Desviación %', 'Última Actualización',
            'ID Proveedor', 'Notas'
        ],
        "COMPRAS_CLIENTE": [
            'ID Compra', 'ID Cliente', 'Nombre Cliente', 'Fecha', 'Total',
            'Proveedor', 'Descripción', 'Número Factura'
        ],
        "INVENTARIO": [
            'ID', 'ID Cliente', 'Nombre Cliente', 'ID Ingrediente',
            'Nombre Ingrediente', 'Stock Actual', 'Consumo Semanal', 'Unidad',
            'Precio Unitario', 'Última Actualización', 'Notas'
        ],
        "SNAPSHOTS_PEDIDOS": [
            'ID', 'ID Cliente', 'Nombre Cliente', 'Fecha', 'ID Ingrediente',
            'Nombre Ingrediente', 'Stock', 'Consumo', 'Observaciones'
        ]
    },
    config.ARCHIVO_PROVEEDORES: {
        "PROVEEDORES": [
            'ID Proveedor', 'Nombre Comercial', 'CIF', 'Tipo', 'Especialidad',
            'Teléfono', 'Email', 'Contacto', 'Condiciones Pago', 'Pedido Mínimo',
            'Envío Gratis', 'Coste Envío', 'Días Entrega', 'Calidad (1-5)',
            'Servicio (1-5)', 'Precio (1-5)', 'Activo', 'Notas'
        ]
    },
    config.ARCHIVO_EMPRESA: {
        "KPIS_MENSUALES": [
            'Mes', 'Año', 'Ingresos', 'Gastos', 'Beneficio', 'ROI %'
        ],
        "FACTURACION": [
            'ID Factura', 'Fecha', 'ID Cliente', 'Concepto', 'Importe', 'Estado'
        ],
        "GASTOS": [
            'ID Gasto', 'Fecha', 'Categoría', 'Descripción', 'Importe', 'Proveedor'
        ]
    }
}

# ============================================================================
# FUNCIONES DE SINCRONIZACIÓN
# ============================================================================

def crear_hoja_vacia(archivo, nombre_hoja, columnas):
    """Crea una hoja vacía con la estructura correcta"""
    try:
        df_vacio = pd.DataFrame(columns=columnas)
        utils.escribir_excel(archivo, nombre_hoja, df_vacio)
        print(f"✅ Hoja '{nombre_hoja}' creada en {archivo}")
        return True
    except Exception as e:
        print(f"❌ Error al crear hoja: {str(e)}")
        return False

def agregar_columnas_faltantes(archivo, nombre_hoja, columnas_esperadas):
    """Agrega columnas faltantes a una hoja existente"""
    try:
        df = utils.leer_excel(archivo, nombre_hoja)
        
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]
        
        if columnas_faltantes:
            for col in columnas_faltantes:
                df[col] = None
            
            utils.escribir_excel(archivo, nombre_hoja, df)
            print(f"✅ Agregadas columnas a '{nombre_hoja}': {columnas_faltantes}")
            return True
        
        return False
    except Exception as e:
        print(f"❌ Error al agregar columnas: {str(e)}")
        return False

def validar_estructura_excel():
    """Verifica y actualiza la estructura de todas las hojas"""
    print("\n" + "="*70)
    print("🔍 VALIDANDO Y ACTUALIZANDO ESTRUCTURA DE EXCEL")
    print("="*70 + "\n")
    
    cambios_realizados = 0
    
    for archivo, hojas in ESTRUCTURA_ESPERADA.items():
        print(f"\n📄 Archivo: {archivo.split(chr(92))[-1]}")
        
        for nombre_hoja, columnas_esperadas in hojas.items():
            try:
                df = utils.leer_excel(archivo, nombre_hoja)
                
                if df.empty:
                    # Hoja existe pero está vacía - agregar estructura
                    print(f"  ⚠️  '{nombre_hoja}': Vacía, creando estructura...")
                    crear_hoja_vacia(archivo, nombre_hoja, columnas_esperadas)
                    cambios_realizados += 1
                else:
                    # Hoja existe con datos
                    columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]
                    
                    if columnas_faltantes:
                        print(f"  ⚠️  '{nombre_hoja}': Faltan columnas: {columnas_faltantes}")
                        agregar_columnas_faltantes(archivo, nombre_hoja, columnas_esperadas)
                        cambios_realizados += 1
                    else:
                        print(f"  ✅ '{nombre_hoja}': OK ({len(df)} filas)")
            
            except FileNotFoundError:
                # Hoja no existe
                print(f"  ⚠️  '{nombre_hoja}': NO EXISTE, creando...")
                crear_hoja_vacia(archivo, nombre_hoja, columnas_esperadas)
                cambios_realizados += 1
            
            except Exception as e:
                print(f"  ❌ '{nombre_hoja}': Error - {str(e)}")
    
    print("\n" + "="*70)
    print(f"✅ VALIDACIÓN COMPLETADA ({cambios_realizados} cambios realizados)")
    print("="*70 + "\n")

def sincronizar_referencias():
    """Sincroniza referencias entre hojas (IDs, nombres, etc)"""
    print("\n" + "="*70)
    print("🔄 SINCRONIZANDO REFERENCIAS")
    print("="*70 + "\n")
    
    actualizaciones = 0
    
    try:
        # Cargar datos
        df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
        df_leads = utils.leer_excel(config.ARCHIVO_CRM, "LEADS")
        df_carta = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
        df_precios = utils.leer_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
        df_escandallos = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
        df_ing = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
        df_int = utils.leer_excel(config.ARCHIVO_CRM, "INTERACCIONES")
        
        # 1. SINCRONIZAR NOMBRES EN INTERACCIONES
        if not df_int.empty and not df_clientes.empty:
            for idx, row in df_int.iterrows():
                if pd.notna(row.get('ID Cliente')):
                    cliente_info = df_clientes[df_clientes['ID'] == row['ID Cliente']]
                    if not cliente_info.empty:
                        nombre_correcto = cliente_info.iloc[0]['Nombre Comercial']
                        if row.get('Nombre Cliente') != nombre_correcto:
                            df_int.at[idx, 'Nombre Cliente'] = nombre_correcto
                            actualizaciones += 1
            
            if actualizaciones > 0:
                utils.escribir_excel(config.ARCHIVO_CRM, "INTERACCIONES", df_int)
                print(f"✅ INTERACCIONES: Actualizados {actualizaciones} nombres de cliente")
        
        # 2. SINCRONIZAR NOMBRES EN CARTA_CLIENTES
        actualizaciones = 0
        if not df_carta.empty and not df_clientes.empty:
            for idx, row in df_carta.iterrows():
                if pd.notna(row.get('ID Cliente')):
                    cliente_info = df_clientes[df_clientes['ID'] == row['ID Cliente']]
                    if not cliente_info.empty:
                        nombre_correcto = cliente_info.iloc[0]['Nombre Comercial']
                        if row.get('Nombre Cliente') != nombre_correcto:
                            df_carta.at[idx, 'Nombre Cliente'] = nombre_correcto
                            actualizaciones += 1
            
            if actualizaciones > 0:
                utils.escribir_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", df_carta)
                print(f"✅ CARTA_CLIENTES: Actualizados {actualizaciones} nombres de cliente")
        
        # 3. SINCRONIZAR NOMBRES EN PRECIOS_POR_CLIENTE
        actualizaciones = 0
        if not df_precios.empty and not df_clientes.empty and not df_ing.empty:
            for idx, row in df_precios.iterrows():
                # Actualizar nombre cliente
                if pd.notna(row.get('ID Cliente')):
                    cliente_info = df_clientes[df_clientes['ID'] == row['ID Cliente']]
                    if not cliente_info.empty:
                        nombre_correcto = cliente_info.iloc[0]['Nombre Comercial']
                        if row.get('Nombre Cliente') != nombre_correcto:
                            df_precios.at[idx, 'Nombre Cliente'] = nombre_correcto
                            actualizaciones += 1
                
                # Actualizar nombre ingrediente
                if pd.notna(row.get('ID Ingrediente')):
                    ing_info = df_ing[df_ing['ID Ingrediente'] == row['ID Ingrediente']]
                    if not ing_info.empty:
                        nombre_correcto = ing_info.iloc[0]['Nombre']
                        if row.get('Nombre Ingrediente') != nombre_correcto:
                            df_precios.at[idx, 'Nombre Ingrediente'] = nombre_correcto
                            actualizaciones += 1
            
            if actualizaciones > 0:
                utils.escribir_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE", df_precios)
                print(f"✅ PRECIOS_POR_CLIENTE: Actualizados {actualizaciones} nombres")
        
        # 4. SINCRONIZAR NOMBRES EN ESCANDALLOS
        actualizaciones = 0
        if not df_escandallos.empty and not df_ing.empty:
            for idx, row in df_escandallos.iterrows():
                if pd.notna(row.get('ID Ingrediente')):
                    ing_info = df_ing[df_ing['ID Ingrediente'] == row['ID Ingrediente']]
                    if not ing_info.empty:
                        nombre_correcto = ing_info.iloc[0]['Nombre']
                        if row.get('Nombre Ingrediente') != nombre_correcto:
                            df_escandallos.at[idx, 'Nombre Ingrediente'] = nombre_correcto
                            actualizaciones += 1
            
            if actualizaciones > 0:
                utils.escribir_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", df_escandallos)
                print(f"✅ ESCANDALLOS: Actualizados {actualizaciones} nombres de ingrediente")
        
        print("\n✅ Sincronización de referencias completada")
    
    except Exception as e:
        print(f"❌ Error en sincronización: {str(e)}")

def diagnostico_completo():
    """Ejecuta diagnóstico y sincronización completa"""
    
    # 1. Validar y actualizar estructura
    validar_estructura_excel()
    
    # 2. Sincronizar referencias
    sincronizar_referencias()
    
    # 3. Mostrar estadísticas
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS DEL SISTEMA")
    print("="*70 + "\n")
    
    try:
        df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
        df_leads = utils.leer_excel(config.ARCHIVO_CRM, "LEADS")
        df_int = utils.leer_excel(config.ARCHIVO_CRM, "INTERACCIONES")
        df_contactos = utils.leer_excel(config.ARCHIVO_CRM, "CONTACTOS")
        df_carta = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
        df_esc = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
        df_ing = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
        df_precios = utils.leer_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
        df_prov = utils.leer_excel(config.ARCHIVO_PROVEEDORES, "PROVEEDORES")
        
        print(f"📋 CRM:")
        print(f"  • Clientes Activos: {len(df_clientes)}")
        print(f"  • Leads: {len(df_leads)}")
        print(f"  • Interacciones: {len(df_int)}")
        print(f"  • Contactos: {len(df_contactos)}")
        
        print(f"\n🍽️  OPERACIONES:")
        print(f"  • Platos en Carta: {len(df_carta)}")
        print(f"  • Escandallos: {len(df_esc)}")
        print(f"  • Ingredientes Maestro: {len(df_ing)}")
        print(f"  • Precios por Cliente: {len(df_precios)}")
        
        print(f"\n🏪 PROVEEDORES:")
        print(f"  • Proveedores: {len(df_prov)}")
    
    except Exception as e:
        print(f"  ❌ Error al obtener estadísticas: {str(e)}")
    
    print("\n" + "="*70)
    print("✅ SINCRONIZACIÓN COMPLETADA")
    print("="*70 + "\n")

if __name__ == "__main__":
    diagnostico_completo()
