"""
Script de diagnóstico para probar escritura en Excel
"""

import pandas as pd
import os
from datetime import datetime

# Ruta del archivo
RUTA_EXCEL = r"C:\Users\ferna\OneDrive\CONSULTORIA GASTRONOMICA\SISTEMA OPERATIVO\datos\CRM_CLIENTES.xlsx"

print("="*60)
print("DIAGNÓSTICO DE EXCEL")
print("="*60)

# 1. Verificar que el archivo existe
print(f"\n1. Verificando existencia del archivo...")
print(f"   Ruta: {RUTA_EXCEL}")
if os.path.exists(RUTA_EXCEL):
    print("   ✅ El archivo existe")
else:
    print("   ❌ El archivo NO existe")
    exit()

# 2. Verificar permisos de lectura
print(f"\n2. Probando lectura...")
try:
    df_leads = pd.read_excel(RUTA_EXCEL, sheet_name="LEADS")
    print(f"   ✅ LEADS leído correctamente ({len(df_leads)} filas)")
except Exception as e:
    print(f"   ❌ Error al leer LEADS: {e}")
    exit()

try:
    df_clientes = pd.read_excel(RUTA_EXCEL, sheet_name="CLIENTES_ACTIVOS")
    print(f"   ✅ CLIENTES_ACTIVOS leído correctamente ({len(df_clientes)} filas)")
    print(f"\n   Columnas en CLIENTES_ACTIVOS:")
    for i, col in enumerate(df_clientes.columns, 1):
        print(f"      {i}. {col}")
except Exception as e:
    print(f"   ❌ Error al leer CLIENTES_ACTIVOS: {e}")
    exit()

# 3. Probar escritura
print(f"\n3. Probando escritura en CLIENTES_ACTIVOS...")

# Crear un cliente de prueba
nuevo_cliente = {
    'ID': 999,
    'Nombre Comercial': 'TEST DIAGNOSTICO',
    'CIF': 'B99999999',
    'Razón Social': 'TEST DIAGNOSTICO SL',
    'Tipo Local': 'Bar',
    'Dirección': 'Calle Test',
    'Ciudad': 'Pamplona',
    'CP': '31001',
    'Teléfono': '948999999',
    'Email': 'test@test.com',
    'Nombre Contacto': 'Test User',
    'Servicio Contratado': 'Por definir',
    'Precio Mensual': 0,
    'Fecha Inicio': datetime.now().date(),
    'Fecha Fin': None,
    'Estado': 'Activo',
    'MRR': 0,
    'Último Servicio': None,
    'Satisfacción (1-5)': 5,
    'Notas': 'Cliente de prueba para diagnóstico'
}

print(f"   Agregando cliente: {nuevo_cliente['Nombre Comercial']}")

# Agregar la fila
df_nuevo = pd.concat([df_clientes, pd.DataFrame([nuevo_cliente])], ignore_index=True)

print(f"   Filas antes: {len(df_clientes)}, después: {len(df_nuevo)}")

# Intentar guardar
try:
    # Leer todas las hojas primero
    excel_file = pd.ExcelFile(RUTA_EXCEL)
    todas_hojas = {}
    for nombre_hoja in excel_file.sheet_names:
        todas_hojas[nombre_hoja] = pd.read_excel(RUTA_EXCEL, sheet_name=nombre_hoja)
    
    # Actualizar la hoja de clientes
    todas_hojas['CLIENTES_ACTIVOS'] = df_nuevo
    
    # Escribir de vuelta
    with pd.ExcelWriter(RUTA_EXCEL, engine='openpyxl', mode='w') as writer:
        for nombre_hoja, datos in todas_hojas.items():
            datos.to_excel(writer, sheet_name=nombre_hoja, index=False)
    
    print("   ✅ Escritura exitosa!")
    
    # Verificar que se guardó
    df_verificar = pd.read_excel(RUTA_EXCEL, sheet_name="CLIENTES_ACTIVOS")
    
    # Buscar el registro de prueba
    test_encontrado = df_verificar[df_verificar['ID'] == 999]
    
    if not test_encontrado.empty:
        print(f"   ✅ VERIFICADO: Cliente de prueba encontrado en el Excel")
        print(f"      ID: {test_encontrado.iloc[0]['ID']}")
        print(f"      Nombre: {test_encontrado.iloc[0]['Nombre Comercial']}")
        print(f"\n   Total clientes ahora: {len(df_verificar)}")
    else:
        print(f"   ❌ El cliente de prueba NO se encontró después de guardar")
        
except PermissionError as e:
    print(f"   ❌ Error de permisos: {e}")
    print(f"\n   💡 SOLUCIÓN:")
    print(f"      1. Cierra Excel completamente")
    print(f"      2. Verifica que OneDrive no esté sincronizando")
    print(f"      3. Cierra cualquier programa que use el archivo")
    
except Exception as e:
    print(f"   ❌ Error inesperado: {e}")
    import traceback
    print(traceback.format_exc())

print("\n" + "="*60)
print("DIAGNÓSTICO COMPLETADO")
print("="*60)
