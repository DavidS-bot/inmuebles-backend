#!/usr/bin/env python3
"""
Bankinter Excel Formatter - Transforma datos de Bankinter al formato del agente financiero
"""

import re
from datetime import date
from typing import List, Dict
import pandas as pd
from dataclasses import dataclass

@dataclass
class BankinterMovement:
    """Movimiento de Bankinter con formato original"""
    fecha: date
    concepto: str
    importe: float
    saldo: float

@dataclass 
class FinancialAgentMovement:
    """Movimiento en formato del agente financiero"""
    fecha: str
    concepto: str
    importe: str

class BankinterExcelFormatter:
    """Formateador de datos de Bankinter para Excel"""
    
    def __init__(self):
        pass
    
    def clean_concept(self, raw_concept: str) -> str:
        """Limpiar y formatear el concepto"""
        if not raw_concept:
            return "MOVIMIENTO BANCARIO"
        
        # Handle Unicode characters and encoding issues
        try:
            # Normalize Unicode characters
            import unicodedata
            concept = unicodedata.normalize('NFKD', raw_concept)
            # Remove non-ASCII characters that cause encoding issues
            concept = ''.join(c for c in concept if ord(c) < 128 or c in 'ñÑáéíóúÁÉÍÓÚüÜ')
        except:
            concept = raw_concept
        
        # Remover texto "Pulsa para ver detalle del movimiento" y variaciones
        concept = re.sub(r'Pulsa para ver detalle.*$', '', concept, flags=re.IGNORECASE | re.MULTILINE)
        concept = re.sub(r'\n.*Pulsa para ver.*$', '', concept, flags=re.IGNORECASE | re.MULTILINE)
        concept = re.sub(r'.*Pulsa para ver.*', '', concept, flags=re.IGNORECASE)
        
        # Remover días de la semana en español
        concept = re.sub(r'\b(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)\b\s*', '', concept, flags=re.IGNORECASE)
        
        # Limpiar caracteres especiales comunes de Bankinter
        concept = concept.replace('#$', ' ')  # Carmen#$ramos -> Carmen ramos
        concept = concept.replace('/', ' ')   # Trans Inm/ -> Trans Inm 
        concept = concept.replace('Recib /', 'RECIBO ')  # Recib / -> RECIBO
        concept = concept.replace('Trans /', 'TRANSFERENCIA ')  # Trans / -> TRANSFERENCIA
        concept = concept.replace('Pago Bizum A ', 'BIZUM ')  # Pago Bizum A -> BIZUM
        concept = concept.replace('Trans Inm/', 'TRANSFERENCIA ')  # Trans Inm/ -> TRANSFERENCIA
        
        # Fix common problematic characters
        concept = concept.replace('ñ', 'n').replace('Ñ', 'N')  # ñ -> n
        concept = concept.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        concept = concept.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        
        # Normalizar espacios múltiples
        concept = re.sub(r'\s+', ' ', concept).strip()
        
        # Convertir a mayúsculas para consistencia
        concept = concept.upper()
        
        # Limitar longitud
        if len(concept) > 50:
            concept = concept[:47] + "..."
        
        return concept or "MOVIMIENTO BANCARIO"
    
    def format_amount(self, amount: float, api_format: bool = False) -> str:
        """
        Formatear importe según el estilo del agente financiero
        
        Args:
            amount: Importe a formatear
            api_format: Si True, usa formato americano (puntos) para API. 
                       Si False, usa formato español (comas) para visualización
        """
        if api_format:
            # Formato americano para API (750.00)
            formatted_number = f"{abs(amount):.2f}"
        else:
            # Formato español para visualización (750,00)
            formatted_number = f"{abs(amount):.2f}".replace('.', ',')
        
        # Si es negativo (gasto), ponerlo entre paréntesis
        if amount < 0:
            return f"({formatted_number})"
        else:
            # Si es positivo (ingreso), sin paréntesis
            return formatted_number
    
    def format_date(self, movement_date: date) -> str:
        """Formatear fecha al estilo dd/mm/yyyy"""
        return movement_date.strftime('%d/%m/%Y')
    
    def transform_movements(self, bankinter_movements: List[BankinterMovement], api_format: bool = False) -> List[FinancialAgentMovement]:
        """
        Transformar lista de movimientos de Bankinter al formato del agente financiero
        
        Args:
            bankinter_movements: Lista de movimientos de Bankinter
            api_format: Si True, formatea importes para API (750.00). Si False, para visualización (750,00)
        """
        transformed_movements = []
        
        for movement in bankinter_movements:
            try:
                # Transformar cada campo
                formatted_date = self.format_date(movement.fecha)
                formatted_concept = self.clean_concept(movement.concepto)
                formatted_amount = self.format_amount(movement.importe, api_format=api_format)
                
                # Crear movimiento transformado
                financial_movement = FinancialAgentMovement(
                    fecha=formatted_date,
                    concepto=formatted_concept,
                    importe=formatted_amount
                )
                
                transformed_movements.append(financial_movement)
                
            except Exception as e:
                print(f"Error transformando movimiento: {movement} - {e}")
                continue
        
        return transformed_movements
    
    def export_to_excel(self, movements: List[FinancialAgentMovement], filename: str = None) -> str:
        """Exportar movimientos a Excel en formato del agente financiero"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"movimientos_bankinter_excel_{timestamp}.xlsx"
        
        # Crear DataFrame
        data = []
        for movement in movements:
            data.append({
                'Fecha': movement.fecha,
                'Concepto': movement.concepto,
                'Importe': movement.importe
            })
        
        df = pd.DataFrame(data)
        
        # Exportar a Excel con encoding seguro
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Movimientos', index=False)
                
                # Ajustar ancho de columnas
                worksheet = writer.sheets['Movimientos']
                worksheet.column_dimensions['A'].width = 12  # Fecha
                worksheet.column_dimensions['B'].width = 50  # Concepto
                worksheet.column_dimensions['C'].width = 15  # Importe
        except Exception as e:
            print(f"Error exporting Excel: {e}")
            # Fallback: save as CSV instead
            csv_filename = filename.replace('.xlsx', '.csv')
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            return csv_filename
        
        return filename
    
    def export_to_excel_for_api(self, bankinter_movements: List[BankinterMovement], filename: str = None) -> str:
        """Exportar movimientos a Excel específicamente para subida a API (números puros)"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"movimientos_api_{timestamp}.xlsx"
        
        # Crear DataFrame directamente con números puros (NO usar transform_movements)
        data = []
        for movement in bankinter_movements:
            # Limpiar concepto
            clean_concept = self.clean_concept(movement.concepto)
            
            data.append({
                'Fecha': self.format_date(movement.fecha),
                'Concepto': clean_concept,
                'Importe': movement.importe  # NÚMERO PURO - NO STRING!
            })
        
        df = pd.DataFrame(data)
        
        # Exportar a Excel con encoding seguro
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Movimientos', index=False)
                
                # Ajustar ancho de columnas
                worksheet = writer.sheets['Movimientos']
                worksheet.column_dimensions['A'].width = 12  # Fecha
                worksheet.column_dimensions['B'].width = 50  # Concepto
                worksheet.column_dimensions['C'].width = 15  # Importe
        except Exception as e:
            print(f"Error exporting Excel: {e}")
            # Fallback: save as CSV instead
            csv_filename = filename.replace('.xlsx', '.csv')
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            return csv_filename
        
        print(f"Excel para API generado: {filename} (numeros puros)")
        return filename
    
    def export_to_csv_formatted(self, movements: List[FinancialAgentMovement], filename: str = None) -> str:
        """Exportar movimientos a CSV en formato del agente financiero"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"movimientos_bankinter_formatted_{timestamp}.csv"
        
        # Crear DataFrame
        data = []
        for movement in movements:
            data.append({
                'Fecha': movement.fecha,
                'Concepto': movement.concepto,
                'Importe': movement.importe
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig', sep='\t')  # Tab-separated para mejor compatibilidad con Excel
        
        return filename
    
    def preview_transformation(self, bankinter_movements: List[BankinterMovement], num_examples: int = 5) -> None:
        """Mostrar preview de la transformación"""
        print("PREVIEW DE TRANSFORMACION DE DATOS")
        print("=" * 80)
        
        # Mostrar formato original
        print("FORMATO ORIGINAL BANKINTER:")
        print("-" * 40)
        for i, movement in enumerate(bankinter_movements[:num_examples], 1):
            fecha_original = movement.fecha.strftime('%A %d/%m/%Y')  # Con día de semana
            print(f"{i}. {fecha_original}")
            print(f"   Concepto: {movement.concepto}")
            print(f"   Importe: {movement.importe:+.2f}€")
            print(f"   Saldo: {movement.saldo:.2f}€")
            print()
        
        # Transformar
        transformed = self.transform_movements(bankinter_movements[:num_examples])
        
        # Mostrar formato transformado
        print("FORMATO AGENTE FINANCIERO:")
        print("-" * 40)
        print(f"{'Fecha':<12} {'Concepto':<40} {'Importe':<15}")
        print("-" * 67)
        
        for movement in transformed:
            print(f"{movement.fecha:<12} {movement.concepto:<40} {movement.importe:<15}")
        
        print("\n" + "=" * 80)

# Función helper para convertir datos del scraper
def convert_scraper_to_bankinter_movements(scraper_transactions) -> List[BankinterMovement]:
    """Convertir transacciones del scraper a formato BankinterMovement"""
    movements = []
    
    for transaction in scraper_transactions:
        try:
            movement = BankinterMovement(
                fecha=transaction.date,
                concepto=transaction.description,
                importe=transaction.amount,
                saldo=transaction.balance or 0.0  # Si no hay saldo, usar 0
            )
            movements.append(movement)
        except Exception as e:
            print(f"Error convirtiendo transacción: {transaction} - {e}")
            continue
    
    return movements