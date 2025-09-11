"""
Servicio unificado para manejo de múltiples fuentes bancarias
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from abc import ABC, abstractmethod
import logging
from sqlmodel import Session, select

from ..models import User, FinancialMovement, BankConnection
from ..db import get_session

logger = logging.getLogger(__name__)

class BankingProvider(ABC):
    """Interfaz abstracta para proveedores bancarios"""
    
    @abstractmethod
    async def get_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene las cuentas del usuario"""
        pass
    
    @abstractmethod
    async def get_transactions(self, user_id: int, account_id: str = None, 
                              days_back: int = 30) -> List[Dict[str, Any]]:
        """Obtiene las transacciones del usuario"""
        pass
    
    @abstractmethod
    def format_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte transacción al formato estándar FinancialMovement"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nombre del proveedor"""
        pass

class BankinterProvider(BankingProvider):
    """Proveedor para Bankinter usando scraping existente"""
    
    def __init__(self):
        self.username = None
        self.password = None
    
    async def get_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene cuentas de Bankinter"""
        # Aquí se conectaría con tu sistema de scraping existente
        return [{
            "id": "bankinter_main",
            "name": "Cuenta Principal Bankinter",
            "type": "current",
            "balance": 0.0,
            "currency": "EUR",
            "iban": "ES21 0128 0000 0000 0000 0000"
        }]
    
    async def get_transactions(self, user_id: int, account_id: str = None, 
                              days_back: int = 30) -> List[Dict[str, Any]]:
        """Obtiene transacciones usando el scraper de Bankinter"""
        try:
            # Aquí llamarías a tu scraper existente de Bankinter
            # Por ahora devolvemos un ejemplo
            return [
                {
                    "id": f"bankinter_tx_{i}",
                    "date": "2025-01-09",
                    "description": f"Transacción de ejemplo {i}",
                    "amount": 100.0 * (-1 if i % 2 else 1),
                    "balance": 1000.0,
                    "account_id": account_id or "bankinter_main"
                }
                for i in range(5)
            ]
        except Exception as e:
            logger.error(f"Error getting Bankinter transactions: {e}")
            return []
    
    def format_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea transacción de Bankinter al formato estándar"""
        return {
            "date": transaction.get("date"),
            "concept": transaction.get("description", "Sin concepto"),
            "amount": float(transaction.get("amount", 0)),
            "category": self._classify_transaction(transaction),
            "subcategory": None,
            "is_classified": True,
            "bank_balance": transaction.get("balance"),
            "external_id": transaction.get("id"),
            "bank_account_id": transaction.get("account_id"),
            "source": "bankinter"
        }
    
    def _classify_transaction(self, transaction: Dict[str, Any]) -> str:
        """Clasificación básica de transacciones"""
        amount = float(transaction.get("amount", 0))
        description = transaction.get("description", "").lower()
        
        if amount > 0:
            if "nomina" in description or "salario" in description:
                return "Nómina"
            elif "transferencia" in description:
                return "Transferencia Recibida"
            else:
                return "Ingreso"
        else:
            if "hipoteca" in description or "prestamo" in description:
                return "Hipoteca"
            elif "alquiler" in description or "renta" in description:
                return "Gasto Vivienda"
            elif "super" in description or "mercado" in description:
                return "Alimentación"
            else:
                return "Gasto"
    
    @property
    def provider_name(self) -> str:
        return "bankinter"

class UnifiedBankingService:
    """Servicio unificado para manejar múltiples proveedores bancarios"""
    
    def __init__(self):
        self.providers: Dict[str, BankingProvider] = {
            "bankinter": BankinterProvider(),
            # Aquí puedes agregar más proveedores en el futuro
            # "bbva": BBVAProvider(),
            # "santander": SantanderProvider(),
        }
    
    def get_provider(self, provider_name: str) -> Optional[BankingProvider]:
        """Obtiene un proveedor específico"""
        return self.providers.get(provider_name)
    
    def list_providers(self) -> List[str]:
        """Lista todos los proveedores disponibles"""
        return list(self.providers.keys())
    
    async def sync_all_providers(self, user_id: int, days_back: int = 30) -> Dict[str, Any]:
        """Sincroniza transacciones de todos los proveedores del usuario"""
        results = {}
        
        with Session(get_session().__next__()) as session:
            # Obtener conexiones activas del usuario
            connections = session.exec(
                select(BankConnection).where(
                    BankConnection.user_id == user_id,
                    BankConnection.is_active == True
                )
            ).all()
            
            total_new_transactions = 0
            total_transactions = 0
            
            for connection in connections:
                provider_name = connection.institution_id.lower()
                provider = self.get_provider(provider_name)
                
                if not provider:
                    continue
                
                try:
                    # Obtener transacciones del proveedor
                    transactions = await provider.get_transactions(user_id, days_back=days_back)
                    total_transactions += len(transactions)
                    
                    new_count = 0
                    for transaction in transactions:
                        # Formatear transacción
                        formatted = provider.format_transaction(transaction)
                        
                        # Verificar si ya existe
                        existing = session.exec(
                            select(FinancialMovement).where(
                                FinancialMovement.external_id == formatted.get("external_id"),
                                FinancialMovement.user_id == user_id
                            )
                        ).first()
                        
                        if existing:
                            continue
                        
                        # Crear nuevo movimiento
                        movement = FinancialMovement(
                            user_id=user_id,
                            date=datetime.strptime(formatted["date"], "%Y-%m-%d").date(),
                            concept=formatted["concept"],
                            amount=formatted["amount"],
                            category=formatted["category"],
                            subcategory=formatted["subcategory"],
                            is_classified=formatted["is_classified"],
                            bank_balance=formatted["bank_balance"],
                            external_id=formatted["external_id"],
                            bank_account_id=formatted["bank_account_id"],
                            source=formatted["source"]
                        )
                        
                        session.add(movement)
                        new_count += 1
                    
                    # Actualizar estado de conexión
                    connection.last_sync = datetime.now()
                    connection.sync_status = "SUCCESS"
                    
                    results[provider_name] = {
                        "status": "success",
                        "total_transactions": len(transactions),
                        "new_transactions": new_count
                    }
                    
                    total_new_transactions += new_count
                    
                except Exception as e:
                    logger.error(f"Error syncing {provider_name}: {e}")
                    connection.sync_status = "ERROR"
                    connection.sync_error = str(e)
                    
                    results[provider_name] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            session.commit()
            
            return {
                "status": "completed",
                "total_transactions": total_transactions,
                "total_new_transactions": total_new_transactions,
                "provider_results": results
            }
    
    async def add_bank_connection(self, user_id: int, provider_name: str, 
                                 credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega una nueva conexión bancaria"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Proveedor {provider_name} no soportado")
        
        with Session(get_session().__next__()) as session:
            # Verificar si ya existe una conexión activa
            existing = session.exec(
                select(BankConnection).where(
                    BankConnection.user_id == user_id,
                    BankConnection.institution_id == provider_name,
                    BankConnection.is_active == True
                )
            ).first()
            
            if existing:
                return {
                    "status": "exists",
                    "connection_id": existing.id,
                    "message": f"Ya existe una conexión activa para {provider_name}"
                }
            
            # Crear nueva conexión
            connection = BankConnection(
                user_id=user_id,
                institution_id=provider_name,
                institution_name=provider_name.title(),
                requisition_id="local_" + provider_name,
                requisition_reference=f"local_{user_id}_{provider_name}",
                consent_status="ACTIVE",
                is_active=True,
                auto_sync_enabled=True,
                sync_frequency_hours=24
            )
            
            session.add(connection)
            session.commit()
            session.refresh(connection)
            
            return {
                "status": "created",
                "connection_id": connection.id,
                "provider_name": provider_name
            }

# Instancia global del servicio
banking_service = UnifiedBankingService()