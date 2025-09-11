import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from sqlmodel import Session, select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .db import engine
from .models import BankConnection, BankAccount, FinancialMovement, User
from .openbanking.clients.nordigen_client import nordigen_client

logger = logging.getLogger(__name__)

class OpenBankingScheduler:
    """Scheduler para sincronización automática de Open Banking"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Inicia el scheduler"""
        if not self.is_running:
            # Agregar job de sincronización cada hora
            self.scheduler.add_job(
                func=self.sync_all_connections,
                trigger=IntervalTrigger(hours=1),
                id='sync_all_connections',
                name='Sync All Bank Connections',
                replace_existing=True
            )
            
            # Agregar job de limpieza de conexiones expiradas cada día
            self.scheduler.add_job(
                func=self.cleanup_expired_connections,
                trigger=IntervalTrigger(days=1),
                id='cleanup_expired_connections',
                name='Cleanup Expired Connections',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("OpenBanking Scheduler started")
    
    def stop(self):
        """Detiene el scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("OpenBanking Scheduler stopped")
    
    async def sync_all_connections(self):
        """Sincroniza todas las conexiones bancarias activas"""
        logger.info("Starting scheduled sync of all bank connections")
        
        try:
            with Session(engine) as session:
                # Obtener conexiones que necesitan sincronización
                now = datetime.now()
                connections = session.exec(
                    select(BankConnection).where(
                        BankConnection.is_active == True,
                        BankConnection.auto_sync_enabled == True,
                        BankConnection.consent_status.in_(["LN", "GA"])  # Linked or Granting Access
                    )
                ).all()
                
                synced_count = 0
                error_count = 0
                
                for connection in connections:
                    try:
                        # Verificar si es tiempo de sincronizar
                        if connection.last_sync:
                            time_since_sync = now - connection.last_sync
                            hours_since_sync = time_since_sync.total_seconds() / 3600
                            
                            if hours_since_sync < connection.sync_frequency_hours:
                                continue  # No es tiempo de sincronizar todavía
                        
                        # Sincronizar conexión
                        await self.sync_connection(connection, session)
                        synced_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error syncing connection {connection.id}: {e}")
                        
                        # Marcar error en la conexión
                        connection.sync_status = "ERROR"
                        connection.sync_error = str(e)
                        session.add(connection)
                        error_count += 1
                
                session.commit()
                logger.info(f"Scheduled sync completed: {synced_count} synced, {error_count} errors")
                
        except Exception as e:
            logger.error(f"Error in scheduled sync: {e}")
    
    async def sync_connection(self, connection: BankConnection, session: Session):
        """Sincroniza una conexión bancaria específica"""
        logger.info(f"Syncing connection {connection.id} for user {connection.user_id}")
        
        # Marcar como sincronizando
        connection.sync_status = "SYNCING"
        connection.sync_error = None
        session.add(connection)
        session.commit()
        
        # Obtener cuentas de la conexión
        accounts = session.exec(
            select(BankAccount).where(BankAccount.connection_id == connection.id)
        ).all()
        
        total_transactions = 0
        new_transactions = 0
        
        # Sincronizar últimos 7 días por defecto
        date_from = datetime.now().date() - timedelta(days=7)
        date_to = datetime.now().date()
        
        for account in accounts:
            try:
                # Obtener transacciones de Nordigen
                transactions_data = await nordigen_client.get_account_transactions(
                    account.account_id, date_from, date_to
                )
                
                # Procesar transacciones bookadas
                booked_transactions = transactions_data.get("transactions", {}).get("booked", [])
                
                for transaction in booked_transactions:
                    total_transactions += 1
                    
                    # Convertir a formato FinancialMovement
                    movement_data = nordigen_client.format_transaction_to_financial_movement(
                        transaction, account.account_id
                    )
                    
                    # Verificar si ya existe (idempotencia)
                    existing = session.exec(
                        select(FinancialMovement).where(
                            FinancialMovement.external_id == movement_data.get("external_id"),
                            FinancialMovement.user_id == connection.user_id
                        )
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Crear nuevo movimiento financiero
                    financial_movement = FinancialMovement(
                        user_id=connection.user_id,
                        date=datetime.strptime(movement_data["date"], "%Y-%m-%d").date(),
                        concept=movement_data["concept"],
                        amount=movement_data["amount"],
                        category=movement_data["category"],
                        subcategory=movement_data["subcategory"],
                        is_classified=movement_data["is_classified"],
                        bank_balance=movement_data["bank_balance"],
                        external_id=movement_data["external_id"],
                        bank_account_id=movement_data["account_id"],
                        source="nordigen"
                    )
                    
                    session.add(financial_movement)
                    new_transactions += 1
                
                # Actualizar fecha de última sincronización de la cuenta
                account.last_transaction_sync = datetime.now()
                session.add(account)
                
            except Exception as e:
                logger.error(f"Error syncing account {account.account_id}: {e}")
                continue
        
        # Actualizar estado de la conexión
        connection.sync_status = "SUCCESS"
        connection.last_sync = datetime.now()
        session.add(connection)
        
        logger.info(f"Connection {connection.id} synced: {new_transactions}/{total_transactions} new transactions")
    
    async def cleanup_expired_connections(self):
        """Limpia conexiones expiradas"""
        logger.info("Starting cleanup of expired connections")
        
        try:
            with Session(engine) as session:
                now = datetime.now()
                
                # Buscar conexiones expiradas
                expired_connections = session.exec(
                    select(BankConnection).where(
                        BankConnection.is_active == True,
                        BankConnection.consent_expires_at < now
                    )
                ).all()
                
                cleaned_count = 0
                
                for connection in expired_connections:
                    try:
                        # Verificar estado en Nordigen
                        requisition = await nordigen_client.get_requisition(connection.requisition_id)
                        
                        if requisition["status"] in ["EX", "RJ", "SA"]:  # Expired, Rejected, Suspended
                            connection.is_active = False
                            connection.consent_status = requisition["status"]
                            session.add(connection)
                            cleaned_count += 1
                            
                    except Exception as e:
                        logger.warning(f"Error checking connection {connection.id}: {e}")
                        # En caso de error, marcar como inactiva si está muy expirada
                        if connection.consent_expires_at < now - timedelta(days=7):
                            connection.is_active = False
                            session.add(connection)
                            cleaned_count += 1
                
                session.commit()
                logger.info(f"Cleanup completed: {cleaned_count} connections deactivated")
                
        except Exception as e:
            logger.error(f"Error in cleanup: {e}")

# Instancia global del scheduler
openbanking_scheduler = OpenBankingScheduler()

def start_scheduler():
    """Función para iniciar el scheduler desde la aplicación"""
    openbanking_scheduler.start()

def stop_scheduler():
    """Función para detener el scheduler"""
    openbanking_scheduler.stop()