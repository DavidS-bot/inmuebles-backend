#!/usr/bin/env python3
"""
Procesador de Movimientos Bankinter Manual
==========================================

INSTRUCCIONES:
1. Ve a tu página de Bankinter
2. Haz clic en el saldo (2.123,98 €) junto a "Cc Euros No Resident"  
3. Copia TODO el texto de la página de movimientos (Ctrl+A, Ctrl+C)
4. Pega el texto en un archivo llamado 'movimientos.txt' en esta carpeta
5. Ejecuta: python procesar_movimientos.py
6. Se generará un nuevo CSV con todas tus transacciones reales

"""

import re
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any
import os

class MovimientosBankinterProcessor:
    """Procesador inteligente de movimientos de Bankinter desde texto copiado"""
    
    def __init__(self):
        self.transactions = []
        self.debug_lines = []
        
    def process_file(self, filename: str = "movimientos.txt") -> str:
        """Procesar archivo de texto con movimientos"""
        if not os.path.exists(filename):
            print(f"[ERROR] No se encontro el archivo '{filename}'")
            print("\n[INSTRUCCIONES]:")
            print("1. Ve a Bankinter online")
            print("2. Haz clic en el saldo 2.123,98 EUR junto a 'Cc Euros No Resident'")
            print("3. Copia TODO el texto de la pagina (Ctrl+A, Ctrl+C)")
            print("4. Pega en un archivo 'movimientos.txt' en esta carpeta")
            print("5. Ejecuta de nuevo: python procesar_movimientos.py")
            return ""
            
        print(f"[INFO] Leyendo archivo: {filename}")
        
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        print(f"[SUCCESS] Contenido leido: {len(content)} caracteres")
        return self.process_text(content)
    
    def process_text(self, text: str) -> str:
        """Procesar texto y extraer movimientos"""
        print("[INFO] Analizando texto para encontrar movimientos...")
        
        lines = text.split('\n')
        print(f"[INFO] Procesando {len(lines)} lineas de texto")
        
        # Patrones mejorados para detectar transacciones
        for i, line in enumerate(lines):
            line = line.strip()
            if len(line) < 6:
                continue
                
            # Buscar patrones de transacción
            transaction = self._extract_transaction_from_line(line, i)
            if transaction:
                self.transactions.append(transaction)
                print(f"[SUCCESS] Transaccion encontrada: {transaction['date']} - {transaction['description'][:40]}... - {transaction['amount']}EUR")
        
        # Generar CSV
        if self.transactions:
            csv_filename = self._generate_csv()
            print(f"\n[SUCCESS] EXITO! Generado: {csv_filename}")
            print(f"[INFO] Total transacciones: {len(self.transactions)}")
            print(f"[INFO] Suma total: {sum(t['amount'] for t in self.transactions):.2f}EUR")
            return csv_filename
        else:
            print("[ERROR] No se encontraron transacciones en el texto")
            self._show_debug_info(lines)
            return ""
    
    def _extract_transaction_from_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Extraer transacción de una línea de texto"""
        
        # PATRÓN 1: Fecha + Concepto + Importe
        # Ejemplo: "15/08/2025 TRANSFERENCIA RECIBIDA 850,00 €"
        pattern1 = r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})\s*€'
        match1 = re.search(pattern1, line)
        
        if match1:
            date_str, description, amount_str = match1.groups()
            return self._create_transaction(date_str, description.strip(), amount_str, f"PATTERN1_L{line_num}")
        
        # PATRÓN 2: Concepto con fecha integrada + importe al final
        # Ejemplo: "RECIBO COMUNIDAD 15/08/2025 -120,50 €"
        pattern2 = r'(.+?)(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})(.+?)(-?\d{1,3}(?:\.\d{3})*,\d{2})\s*€'
        match2 = re.search(pattern2, line)
        
        if match2:
            desc_part1, date_str, desc_part2, amount_str = match2.groups()
            description = f"{desc_part1.strip()} {desc_part2.strip()}".strip()
            return self._create_transaction(date_str, description, amount_str, f"PATTERN2_L{line_num}")
        
        # PATRÓN 3: Solo importe con concepto (usar fecha actual)
        # Ejemplo: "SALDO DISPONIBLE 2.123,98 €"
        pattern3 = r'(.+?)(-?\d{1,3}(?:\.\d{3})*,\d{2})\s*€'
        match3 = re.search(pattern3, line)
        
        if match3 and any(keyword in line.lower() for keyword in [
            'saldo', 'balance', 'disponible', 'ingreso', 'cargo', 'abono',
            'transferencia', 'bizum', 'recibo', 'nomina', 'pension'
        ]):
            description, amount_str = match3.groups()
            return self._create_transaction(None, description.strip(), amount_str, f"PATTERN3_L{line_num}")
        
        # PATRÓN 4: Líneas con palabras clave financieras + números
        financial_keywords = [
            'transferencia', 'bizum', 'recibo', 'domiciliacion', 'nomina', 'pension',
            'tarjeta', 'cajero', 'compra', 'venta', 'devolucion', 'comision',
            'ingreso', 'cargo', 'abono', 'pago', 'cobro'
        ]
        
        if any(keyword in line.lower() for keyword in financial_keywords):
            # Buscar cualquier importe en la línea
            amount_match = re.search(r'(-?\d{1,3}(?:\.\d{3})*,\d{2})', line)
            if amount_match:
                amount_str = amount_match.group(1)
                # Buscar fecha en la línea
                date_match = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', line)
                date_str = date_match.group(1) if date_match else None
                
                return self._create_transaction(date_str, line[:80], amount_str, f"PATTERN4_L{line_num}")
        
        # Si la línea parece interesante, guardarla para debug
        if any(char in line for char in ['€', ',']) and any(char.isdigit() for char in line):
            self.debug_lines.append(f"L{line_num}: {line[:100]}")
        
        return None
    
    def _create_transaction(self, date_str: str, description: str, amount_str: str, reference: str) -> Dict[str, Any]:
        """Crear diccionario de transacción"""
        
        # Procesar fecha
        transaction_date = date.today()  # Por defecto
        if date_str:
            try:
                # Intentar varios formatos de fecha
                for date_format in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y', '%d-%m-%y']:
                    try:
                        parsed_date = datetime.strptime(date_str, date_format)
                        # Si es año de 2 dígitos, ajustar
                        if parsed_date.year < 100:
                            if parsed_date.year < 50:
                                parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
                            else:
                                parsed_date = parsed_date.replace(year=parsed_date.year + 1900)
                        transaction_date = parsed_date.date()
                        break
                    except:
                        continue
            except:
                pass  # Usar fecha por defecto
        
        # Procesar importe
        try:
            # Convertir formato español a float (1.234,56 -> 1234.56)
            amount = float(amount_str.replace('.', '').replace(',', '.'))
        except:
            amount = 0.0
        
        # Limpiar descripción
        clean_description = description
        # Eliminar fecha y importe de la descripción
        clean_description = re.sub(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}', '', clean_description)
        clean_description = re.sub(r'-?\d{1,3}(?:\.\d{3})*,\d{2}\s*€?', '', clean_description)
        clean_description = re.sub(r'\s+', ' ', clean_description).strip()
        
        if not clean_description or len(clean_description) < 3:
            clean_description = f"Movimiento bancario {reference}"
        
        # Categorizar automáticamente
        category = self._categorize_transaction(clean_description.lower())
        
        return {
            'date': transaction_date,
            'description': clean_description[:100],  # Limitar longitud
            'amount': amount,
            'account': "ES02 0128 0730 9101 6000 0605",
            'category': category,
            'reference': reference
        }
    
    def _categorize_transaction(self, description_lower: str) -> str:
        """Categorizar transacción automáticamente"""
        
        categories = {
            'Transferencia': ['transferencia', 'bizum', 'envio', 'traspaso'],
            'Ingreso': ['nomina', 'pension', 'sueldo', 'salario', 'devolucion', 'ingreso'],
            'Recibo': ['recibo', 'domiciliacion', 'factura', 'suministro', 'gas', 'luz', 'agua'],
            'Tarjeta': ['tarjeta', 'cajero', 'compra', 'mastercard', 'visa'],
            'Servicios': ['comision', 'mantenimiento', 'cuota', 'servicio'],
            'Saldo': ['saldo', 'balance', 'disponible', 'total'],
            'Otros': ['otros', 'varios', 'miscela']
        }
        
        for category, keywords in categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'Sin Categoría'
    
    def _generate_csv(self) -> str:
        """Generar archivo CSV con las transacciones"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bankinter_movimientos_{timestamp}.csv"
        
        # Convertir a DataFrame
        df_data = []
        for trans in self.transactions:
            df_data.append({
                'Fecha': trans['date'].strftime('%d/%m/%Y'),
                'Concepto': trans['description'],
                'Importe': trans['amount'],
                'Cuenta': trans['account'],
                'Categoria': trans['category'],
                'Referencia': trans['reference']
            })
        
        df = pd.DataFrame(df_data)
        
        # Ordenar por fecha (más reciente primero)
        df['Fecha_Sort'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
        df = df.sort_values('Fecha_Sort', ascending=False)
        df = df.drop('Fecha_Sort', axis=1)
        
        # Guardar CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        
        return filename
    
    def _show_debug_info(self, lines: List[str]):
        """Mostrar información de debug si no se encontraron transacciones"""
        
        print("\n[DEBUG] INFORMACION DE DEBUG:")
        print(f"Total de lineas procesadas: {len(lines)}")
        print(f"Lineas con posible contenido financiero: {len(self.debug_lines)}")
        
        if self.debug_lines:
            print("\n[DEBUG] Lineas que parecian interesantes pero no se procesaron:")
            for debug_line in self.debug_lines[:10]:  # Mostrar solo las primeras 10
                print(f"  {debug_line}")
            
            if len(self.debug_lines) > 10:
                print(f"  ... y {len(self.debug_lines) - 10} lineas mas")
        
        print("\n[SUGERENCIAS]:")
        print("1. Asegúrate de copiar la página completa de movimientos")
        print("2. Verifica que el texto incluya fechas e importes")
        print("3. Si sigues teniendo problemas, pega una muestra del texto para analizarlo")


def main():
    """Función principal"""
    print("PROCESADOR DE MOVIMIENTOS BANKINTER")
    print("=" * 50)
    print(__doc__)
    
    processor = MovimientosBankinterProcessor()
    csv_file = processor.process_file()
    
    if csv_file:
        print(f"\n[SUCCESS] Proceso completado con exito!")
        print(f"[INFO] Archivo generado: {csv_file}")
        print(f"[INFO] Transacciones procesadas: {len(processor.transactions)}")
        
        # Mostrar resumen por categorías
        categories = {}
        for trans in processor.transactions:
            cat = trans['category']
            if cat not in categories:
                categories[cat] = {'count': 0, 'total': 0}
            categories[cat]['count'] += 1
            categories[cat]['total'] += trans['amount']
        
        print("\n[RESUMEN] POR CATEGORIAS:")
        for cat, data in categories.items():
            print(f"  {cat}: {data['count']} transacciones, {data['total']:.2f}EUR")
    
    else:
        print("\n[ERROR] No se pudo procesar el archivo")
        print("Revisa las instrucciones y vuelve a intentarlo")


if __name__ == "__main__":
    main()