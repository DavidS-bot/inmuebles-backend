from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import uuid
import logging

from ..db import get_session
from ..models import User, BankConnection, BankAccount, FinancialMovement
from ..deps import get_current_user
from ..openbanking.clients.tink_client import tink_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openbanking-tink", tags=["Open Banking - Tink"])

@router.get("/providers")
async def get_providers(
    country_code: str = "ES",
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Obtiene la lista de proveedores bancarios disponibles en Tink"""
    try:
        providers = await tink_client.get_providers(country_code)
        return providers
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo proveedores: {str(e)}"
        )

@router.post("/connections")
async def create_bank_connection(
    provider_name: str,
    redirect_url: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Crea una nueva conexión bancaria con Tink"""
    try:
        # Generar referencia única
        reference = f"inmuebles_tink_{current_user.id}_{uuid.uuid4().hex[:8]}"
        
        # Crear enlace en Tink
        link_response = await tink_client.create_link(
            provider_name=provider_name,
            redirect_url=redirect_url,
            user_id=str(current_user.id)
        )
        
        # Guardar conexión en base de datos
        connection = BankConnection(
            user_id=current_user.id,
            institution_id=provider_name,  # En Tink es el provider name
            institution_name=provider_name,
            institution_logo=None,  # Tink maneja logos internamente
            requisition_id=link_response.get("linkId", ""),
            requisition_reference=reference,
            consent_url=link_response.get("url", ""),
            consent_expires_at=datetime.now() + timedelta(days=90),
            consent_status="CREATED"
        )
        
        session.add(connection)
        session.commit()
        session.refresh(connection)
        
        logger.info(f"Tink connection created for user {current_user.id}: {provider_name}")
        
        return {
            "connection_id": connection.id,
            "consent_url": link_response.get("url"),
            "provider_name": provider_name,
            "link_id": link_response.get("linkId")
        }
        
    except Exception as e:
        logger.error(f"Error creating Tink connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando conexión: {str(e)}"
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
            "consent_status": conn.consent_status,
            "is_active": conn.is_active,
            "created_at": conn.created_at,
            "last_sync": conn.last_sync,
            "sync_status": conn.sync_status,
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
                "currency": account.currency
            })
        
        result.append(connection_data)
    
    return result

@router.post("/connections/{connection_id}/sync")
async def sync_bank_transactions(
    connection_id: int,
    days_back: int = 30,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Sincroniza transacciones usando Tink"""
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
        session.commit()
        
        # Primero refrescar datos del usuario en Tink
        try:
            await tink_client.refresh_user_data(str(current_user.id))
        except Exception as e:
            logger.warning(f"Could not refresh user data: {e}")
        
        # Obtener cuentas de Tink
        tink_accounts = await tink_client.get_accounts(str(current_user.id))
        
        # Sincronizar cuentas primero
        for tink_account in tink_accounts:
            existing_account = session.exec(
                select(BankAccount).where(
                    BankAccount.connection_id == connection_id,
                    BankAccount.account_id == tink_account["id"]
                )
            ).first()
            
            if not existing_account:
                # Crear nueva cuenta
                bank_account = BankAccount(
                    connection_id=connection.id,
                    account_id=tink_account["id"],
                    iban=tink_account.get("identifiers", {}).get("iban", {}).get("iban"),
                    account_name=tink_account.get("name"),
                    account_type=tink_account.get("type"),
                    currency=tink_account.get("currencyCode", "EUR"),
                    current_balance=tink_account.get("balance", 0),
                    available_balance=tink_account.get("availableBalance", 0)
                )
                session.add(bank_account)
        
        session.commit()
        
        # Obtener transacciones
        date_from = date.today() - timedelta(days=days_back)
        date_to = date.today()
        
        total_transactions = 0
        new_transactions = 0
        
        # Obtener transacciones de Tink
        tink_transactions = await tink_client.get_transactions(
            str(current_user.id), 
            date_from=date_from, 
            date_to=date_to
        )
        
        for transaction in tink_transactions:
            total_transactions += 1
            
            # Convertir a formato FinancialMovement
            movement_data = tink_client.format_transaction_to_financial_movement(
                transaction, transaction.get("accountId", "")
            )
            
            # Verificar si ya existe
            existing = session.exec(
                select(FinancialMovement).where(
                    FinancialMovement.external_id == movement_data.get("external_id"),
                    FinancialMovement.user_id == current_user.id
                )
            ).first()
            
            if existing:
                continue
            
            # Crear nuevo movimiento
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
                source="tink"
            )
            
            session.add(financial_movement)
            new_transactions += 1
        
        # Actualizar estado de la conexión
        connection.sync_status = "SUCCESS"
        connection.last_sync = datetime.now()
        session.commit()
        
        logger.info(f"Tink sync completed for connection {connection_id}: {new_transactions}/{total_transactions}")
        
        return {
            "status": "success",
            "total_transactions": total_transactions,
            "new_transactions": new_transactions,
            "accounts_synced": len(tink_accounts)
        }
        
    except Exception as e:
        logger.error(f"Error syncing Tink transactions: {e}")
        
        # Marcar error
        connection = session.get(BankConnection, connection_id)
        if connection:
            connection.sync_status = "ERROR"
            connection.sync_error = str(e)
            session.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sincronizando: {str(e)}"
        )

@router.delete("/connections/{connection_id}")
async def delete_bank_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """Elimina una conexión bancaria"""
    connection = session.exec(
        select(BankConnection).where(
            BankConnection.id == connection_id,
            BankConnection.user_id == current_user.id
        )
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Conexión no encontrada")
    
    # Marcar como inactiva
    connection.is_active = False
    session.commit()
    
    return {"status": "success"}