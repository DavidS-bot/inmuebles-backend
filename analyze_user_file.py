#!/usr/bin/env python3
"""
Analizar el archivo Movimientos.xls del usuario
"""

import pandas as pd
import asyncio
from app.services.financial_agent_uploader import upload_bankinter_excel

async def analyze_user_file():
    """Analizar archivo del usuario y prepararlo para subida"""
    
    print("ANALIZANDO ARCHIVO DEL USUARIO")
    print("=" * 50)
    
    user_file = r"C:\Users\davsa\Downloads\Movimientos.xls"
    
    try:
        print(f"Archivo: {user_file}")
        
        # 1. Leer y analizar el archivo
        print(f"\n1. ANALIZANDO ESTRUCTURA...")
        df = pd.read_excel(user_file)
        
        print(f"Filas: {len(df)}")
        print(f"Columnas: {list(df.columns)}")
        print(f"\nPrimeras 5 filas:")
        print(df.head())
        
        print(f"\nTipos de datos:")
        print(df.dtypes)
        
        # 2. Verificar formato requerido
        print(f"\n2. VERIFICANDO FORMATO REQUERIDO...")
        required_columns = ['Fecha', 'Concepto', 'Importe']
        
        # Verificar columnas (case insensitive)
        df_columns_lower = [col.lower() for col in df.columns]
        missing_columns = []
        
        for req_col in required_columns:
            if req_col.lower() not in df_columns_lower:
                missing_columns.append(req_col)
        
        if missing_columns:
            print(f"Columnas faltantes: {missing_columns}")
            
            # Intentar mapear columnas similares
            print(f"\nIntentando mapear columnas...")
            column_mapping = {}
            
            for df_col in df.columns:
                df_col_lower = df_col.lower()
                if 'fecha' in df_col_lower:
                    column_mapping[df_col] = 'Fecha'
                elif 'concepto' in df_col_lower or 'descripcion' in df_col_lower or 'detalle' in df_col_lower:
                    column_mapping[df_col] = 'Concepto'
                elif 'importe' in df_col_lower or 'cantidad' in df_col_lower or 'monto' in df_col_lower or 'amount' in df_col_lower:
                    column_mapping[df_col] = 'Importe'
            
            print(f"Mapeo encontrado: {column_mapping}")
            
            if len(column_mapping) >= 3:
                df = df.rename(columns=column_mapping)
                print("Columnas mapeadas exitosamente")
            else:
                print("No se pudo mapear suficientes columnas")
                return
        else:
            print("Formato correcto - todas las columnas requeridas presentes")
        
        # 3. Verificar y corregir tipos de datos
        print(f"\n3. VERIFICANDO TIPOS DE DATOS...")
        
        # Verificar columna Importe
        if 'Importe' in df.columns:
            print(f"Tipo de Importe: {df['Importe'].dtype}")
            print(f"Ejemplos de Importe:")
            for i, val in enumerate(df['Importe'].head()):
                print(f"  {i+1}: {val} (tipo: {type(val)})")
            
            # Si son strings, intentar convertir a números
            if df['Importe'].dtype == 'object':
                print("Convirtiendo importes de string a números...")
                
                def clean_amount(val):
                    if pd.isna(val):
                        return 0.0
                    
                    # Convertir a string y limpiar
                    str_val = str(val).strip()
                    
                    # Remover paréntesis y convertir a negativo
                    is_negative = False
                    if str_val.startswith('(') and str_val.endswith(')'):
                        str_val = str_val[1:-1]
                        is_negative = True
                    
                    # Remover símbolos y espacios
                    str_val = str_val.replace('€', '').replace('$', '').replace(',', '.').replace(' ', '')
                    
                    try:
                        number = float(str_val)
                        return -number if is_negative else number
                    except:
                        return 0.0
                
                df['Importe'] = df['Importe'].apply(clean_amount)
                print("Importes convertidos a números")
        
        # 4. Crear archivo corregido para API
        print(f"\n4. CREANDO ARCHIVO CORREGIDO...")
        
        # Tomar solo las columnas necesarias
        corrected_df = df[['Fecha', 'Concepto', 'Importe']].copy()
        
        # Asegurar que Fecha esté en formato correcto
        if corrected_df['Fecha'].dtype == 'object':
            corrected_df['Fecha'] = pd.to_datetime(corrected_df['Fecha'], errors='coerce').dt.strftime('%d/%m/%Y')
        
        # Guardar archivo corregido
        corrected_file = "movimientos_usuario_corregido.xlsx"
        corrected_df.to_excel(corrected_file, index=False)
        
        print(f"Archivo corregido creado: {corrected_file}")
        print(f"Filas en archivo corregido: {len(corrected_df)}")
        print(f"\nPrimeras filas del archivo corregido:")
        print(corrected_df.head())
        print(f"\nTipos de datos finales:")
        print(corrected_df.dtypes)
        
        # 5. Test de subida local
        print(f"\n5. PROBANDO SUBIDA AL BACKEND LOCAL...")
        
        try:
            result = await upload_bankinter_excel(
                excel_file_path=corrected_file,
                username="admin",
                password="admin123",
                base_url="http://localhost:8000"
            )
            
            print(f"RESULTADO DE PRUEBA LOCAL:")
            print(f"  - Movimientos creados: {result['new_movements_created']}")
            print(f"  - Duplicados omitidos: {result['duplicates_skipped']}")
            print(f"  - Total procesados: {result['total_rows_processed']}")
            print(f"  - Errores: {result['upload_result'].get('errors', [])[:3]}")
            
            if result['new_movements_created'] > 0:
                print(f"\nEXITO - El archivo funciona correctamente!")
                print(f"Archivo listo para subir a produccion: {corrected_file}")
            else:
                print(f"\nProblemas detectados - revisar errores")
                
        except Exception as e:
            print(f"Error en prueba local: {e}")
        
        return corrected_file
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    resultado = asyncio.run(analyze_user_file())
    
    if resultado:
        print(f"\n" + "="*50)
        print("ARCHIVO LISTO PARA SUBIDA MANUAL")
        print("="*50)
        print(f"Archivo: {resultado}")
        print("Ve a: https://inmuebles-david.vercel.app/financial-agent/movements")
        print("Y sube el archivo usando la interfaz web")
    else:
        print(f"\n" + "="*50)
        print("ERROR PROCESANDO ARCHIVO")
        print("="*50)