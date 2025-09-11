from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import uuid
import logging

from ..db import get_session
from ..models import User, BankConnection, BankAccount, FinancialMovement
from ..deps import get_current_user
from ..openbanking.clients.nordigen_client import nordigen_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openbanking", tags=["Open Banking"])

@router.get("/institutions")
async def get_institutions(
    country_code: str = "ES",
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Obtiene la lista de instituciones bancarias disponibles"""
    try:
        institutions = await nordigen_client.get_institutions(country_code)
        return institutions
    except Exception as e:
        logger.error(f"Error getting institutions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo instituciones: {str(e)}"
        )

@router.post("/connections")
async def create_bank_connection(
    institution_id: str,
    redirect_url: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Crea una nueva conexión bancaria"""
    try:
        # Generar referencia única
        reference = f"inmuebles_{current_user.id}_{uuid.uuid4().hex[:8]}"
        
        # Crear requisición en Nordigen
        requisition = await nordigen_client.create_requisition(
            institution_id=institution_id,
            redirect_url=redirect_url,
            reference=reference
        )
        
        # Obtener información de la institución
        institutions = await nordigen_client.get_institutions()
        institution = next((inst for inst in institutions if inst["id"] == institution_id), None)
        
        if not institution:
            raise HTTPException(status_code=404, detail="Institución no encontrada")
        
        # Guardar conexión en base de datos
        connection = BankConnection(
            user_id=current_user.id,
            institution_id=institution_id,
            institution_name=institution["name"],
            institution_logo=institution.get("logo"),
            institution_bic=institution.get("bic"),
            requisition_id=requisition["id"],
            requisition_reference=reference,
            consent_url=requisition["link"],
            consent_expires_at=datetime.now() + timedelta(days=90),  # 90 días típicos
            consent_status="CR"  # Created
        )
        
        session.add(connection)
        session.commit()
        session.refresh(connection)
        
        logger.info(f"Bank connection created for user {current_user.id}: {institution['name']}")
        
        return {
            "connection_id": connection.id,
            "consent_url": requisition["link"],
            "institution_name": institution["name"],
            "requisition_id": requisition["id"]
        }
        
    except Exception as e:
        logger.error(f"Error creating bank connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando conexión bancaria: {str(e)}"
        )

@router.get("/connections")
async def get_bank_connections(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[Dict[str, Any]]:
    """Obtiene las conexiones bancarias del usuario"""
    connections = session.exec(
        select(BankConnection).where(BankConnection.user_id == current_user.id)
    ).all()
    
    result = []
    for conn in connections:
        connection_data = {
            "id": conn.id,
            "institution_name": conn.institution_name,
            "institution_logo": conn.institution_logo,
            "consent_status": conn.consent_status,
            "is_active": conn.is_active,
            "created_at": conn.created_at,
            "last_sync": conn.last_sync,
            "sync_status": conn.sync_status,
            "sync_error": conn.sync_error,
            "auto_sync_enabled": conn.auto_sync_enabled,
            "accounts": []
        }
        
        # Obtener cuentas asociadas
        accounts = session.exec(
            select(BankAccount).where(BankAccount.connection_id == conn.id)
        ).all()
        
        for account in accounts:
            connection_data["accounts"].append({
                "id": account.id,
                "account_id": account.account_id,
                "iban": account.iban,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "available_balance": account.available_balance,
                "current_balance": account.current_balance,
                "currency": account.currency,
                "last_transaction_sync": account.last_transaction_sync
            })
        
        result.append(connection_data)
    
    return result

@router.post("/connections/{connection_id}/callback")
async def bank_connection_callback(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Procesa el callback después del consentimiento bancario"""
    try:
        # Obtener conexión
        connection = session.exec(
            select(BankConnection).where(
                BankConnection.id == connection_id,
                BankConnection.user_id == current_user.id
            )
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Conexión no encontrada")
        
        # Verificar estado de la requisición
        requisition = await nordigen_client.get_requisition(connection.requisition_id)
        
        if requisition["status"] not in ["LN", "GA"]:  # Linked or Granting Access
            connection.consent_status = requisition["status"]
            session.commit()
            raise HTTPException(
                status_code=400, 
                detail=f"Consentimiento no completado. Estado: {requisition['status']}"
            )
        
        # Actualizar estado de la conexión
        connection.consent_status = requisition["status"]
        session.commit()
        
        # Obtener y guardar cuentas
        accounts_created = 0
        for account_id in requisition.get("accounts", []):
            existing_account = session.exec(
                select(BankAccount).where(BankAccount.account_id == account_id)
            ).first()
            
            if existing_account:
                continue
                
            try:
                # Obtener detalles de la cuenta
                account_details = await nordigen_client.get_account_details(account_id)
                account_balances = await nordigen_client.get_account_balances(account_id)
                
                # Crear cuenta en base de datos
                bank_account = BankAccount(
                    connection_id=connection.id,
                    account_id=account_id,
                    iban=account_details.get("iban"),
                    account_name=account_details.get("name"),
                    account_type=account_details.get("usage"),
                    currency=account_details.get("currency", "EUR"),
                    bic=account_details.get("bic"),
                    owner_name=account_details.get("ownerName"),
                    product_name=account_details.get("product"),
                    sync_from_date=date.today() - timedelta(days=90)  # Sincronizar últimos 90 días
                )
                
                # Obtener saldos
                if account_balances.get("balances"):
                    for balance in account_balances["balances"]:
                        if balance.get("balanceType") == "closingBooked":
                            bank_account.current_balance = float(balance["balanceAmount"]["amount"])
                        elif balance.get("balanceType") == "interimAvailable":
                            bank_account.available_balance = float(balance["balanceAmount"]["amount"])
                
                session.add(bank_account)
                accounts_created += 1
                
            except Exception as e:
                logger.error(f"Error creating account {account_id}: {e}")
                continue
        
        session.commit()
        
        logger.info(f"Bank connection callback processed: {accounts_created} accounts created")
        
        return {
            "status": "success",
            "accounts_created": accounts_created,
            "connection_status": connection.consent_status
        }
        
    except Exception as e:
        logger.error(f"Error in bank connection callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando callback: {str(e)}"
        )

@router.post("/connections/{connection_id}/sync")
async def sync_bank_transactions(
    connection_id: int,
    days_back: int = 30,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Sincroniza transacciones de todas las cuentas de una conexión"""
    try:
        # Obtener conexión
        connection = session.exec(
            select(BankConnection).where(
                BankConnection.id == connection_id,
                BankConnection.user_id == current_user.id
            )
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Conexión no encontrada")
        
        # Marcar como sincronizando
        connection.sync_status = "SYNCING"
        connection.sync_error = None
        session.commit()
        
        # Obtener cuentas de la conexión
        accounts = session.exec(
            select(BankAccount).where(BankAccount.connection_id == connection_id)
        ).all()
        
        total_transactions = 0
        new_transactions = 0
        
        date_from = date.today() - timedelta(days=days_back)
        date_to = date.today()
        
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
                            FinancialMovement.user_id == current_user.id
                        )
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Crear nuevo movimiento financiero
                    financial_movement = FinancialMovement(
                        user_id=current_user.id,
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
                
            except Exception as e:
                logger.error(f"Error syncing account {account.account_id}: {e}")
                continue
        
        # Actualizar estado de la conexión
        connection.sync_status = "SUCCESS"
        connection.last_sync = datetime.now()
        session.commit()
        
        logger.info(f"Sync completed for connection {connection_id}: {new_transactions}/{total_transactions} new transactions")
        
        return {
            "status": "success",
            "total_transactions": total_transactions,
            "new_transactions": new_transactions,
            "accounts_synced": len(accounts)
        }
        
    except Exception as e:
        logger.error(f"Error syncing transactions: {e}")
        
        # Marcar error en la conexión
        connection = session.get(BankConnection, connection_id)
        if connection:
            connection.sync_status = "ERROR"
            connection.sync_error = str(e)
            session.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sincronizando transacciones: {str(e)}"
        )

@router.delete("/connections/{connection_id}")
async def delete_bank_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """Elimina una conexión bancaria"""
    try:
        # Obtener conexión
        connection = session.exec(
            select(BankConnection).where(
                BankConnection.id == connection_id,
                BankConnection.user_id == current_user.id
            )
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Conexión no encontrada")
        
        # Eliminar requisición en Nordigen
        try:
            await nordigen_client.delete_requisition(connection.requisition_id)
        except Exception as e:
            logger.warning(f"Error deleting Nordigen requisition: {e}")
        
        # Marcar como inactiva (no eliminar para preservar historial)
        connection.is_active = False
        session.commit()
        
        logger.info(f"Bank connection {connection_id} deactivated for user {current_user.id}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error deleting bank connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando conexión: {str(e)}"
        )

@router.post("/connections/{connection_id}/toggle-auto-sync")
async def toggle_auto_sync(
    connection_id: int,
    enabled: bool,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Activa/desactiva la sincronización automática"""
    connection = session.exec(
        select(BankConnection).where(
            BankConnection.id == connection_id,
            BankConnection.user_id == current_user.id
        )
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Conexión no encontrada")
    
    connection.auto_sync_enabled = enabled
    session.commit()
    
    return {
        "status": "success",
        "auto_sync_enabled": enabled
    }