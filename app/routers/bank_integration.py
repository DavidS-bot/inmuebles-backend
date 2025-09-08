from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict
from datetime import date

from ..deps import get_current_user
from ..db import get_session
from ..models import User, BankConnection, BankAccount
from ..services.gocardless_client import GoCardlessClient

router = APIRouter(prefix="/bank-integration", tags=["Bank Integration"])

@router.get("/institutions")
async def get_institutions(
    country_code: str = "ES",
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """Obtener lista de bancos disponibles"""
    client = GoCardlessClient()
    institutions = client.get_institutions(country_code)
    return institutions

@router.post("/connect")
async def connect_bank(
    institution_id: str,
    redirect_uri: str = "http://localhost:3000/financial-agent/integrations/bankinter",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Dict:
    """Iniciar proceso de conexión con un banco"""
    client = GoCardlessClient()
    
    # Crear requisición
    requisition = client.create_requisition(
        institution_id=institution_id,
        redirect_uri=redirect_uri,
        user_id=str(current_user.id)
    )
    
    if not requisition:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creando conexión bancaria"
        )
    
    # Obtener nombre del banco
    institutions = client.get_institutions()
    institution_name = next(
        (inst["name"] for inst in institutions if inst["id"] == institution_id),
        "Banco desconocido"
    )
    
    # Guardar conexión en BD
    connection = BankConnection(
        user_id=current_user.id,
        institution_id=institution_id,
        institution_name=institution_name,
        requisition_id=requisition["requisition_id"],
        created_at=date.today()
    )
    
    db.add(connection)
    db.commit()
    db.refresh(connection)
    
    return {
        "connection_id": connection.id,
        "link": requisition["link"],
        "requisition_id": requisition["requisition_id"]
    }

@router.post("/callback/{connection_id}")
async def connection_callback(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Dict:
    """Callback después de autorizar conexión bancaria"""
    # Obtener conexión
    connection = db.get(BankConnection, connection_id)
    if not connection or connection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conexión no encontrada"
        )
    
    client = GoCardlessClient()
    
    # Obtener cuentas
    account_ids = client.get_accounts(connection.requisition_id)
    
    if not account_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudieron obtener las cuentas"
        )
    
    # Guardar cuentas en BD
    accounts_created = []
    for account_id in account_ids:
        # Obtener detalles de la cuenta
        details = client.get_account_details(account_id)
        balances = client.get_account_balances(account_id)
        
        account = BankAccount(
            connection_id=connection.id,
            account_id=account_id,
            iban=details.get("iban"),
            account_name=details.get("name", "Cuenta principal"),
            account_type=details.get("cashAccountType", "current"),
            balance=float(balances.get("balances", [{}])[0].get("balanceAmount", {}).get("amount", 0)),
            currency=balances.get("balances", [{}])[0].get("balanceAmount", {}).get("currency", "EUR")
        )
        
        db.add(account)
        accounts_created.append(account)
    
    # Actualizar conexión
    connection.is_active = True
    connection.last_sync = date.today()
    
    db.commit()
    
    return {
        "message": "Conexión establecida exitosamente",
        "accounts_count": len(accounts_created)
    }

@router.get("/connections")
async def get_user_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> List[Dict]:
    """Obtener conexiones bancarias del usuario"""
    statement = select(BankConnection).where(
        BankConnection.user_id == current_user.id,
        BankConnection.is_active == True
    )
    connections = db.exec(statement).all()
    
    result = []
    for conn in connections:
        result.append({
            "id": conn.id,
            "institution_name": conn.institution_name,
            "created_at": conn.created_at,
            "last_sync": conn.last_sync,
            "accounts_count": len(conn.bank_accounts)
        })
    
    return result

@router.get("/accounts/{connection_id}")
async def get_connection_accounts(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> List[Dict]:
    """Obtener cuentas de una conexión bancaria"""
    connection = db.get(BankConnection, connection_id)
    if not connection or connection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conexión no encontrada"
        )
    
    accounts = []
    for account in connection.bank_accounts:
        accounts.append({
            "id": account.id,
            "account_id": account.account_id,
            "iban": account.iban,
            "account_name": account.account_name,
            "balance": account.balance,
            "currency": account.currency
        })
    
    return accounts

@router.post("/sync/{connection_id}")
async def sync_transactions(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Dict:
    """Sincronizar transacciones de una conexión"""
    connection = db.get(BankConnection, connection_id)
    if not connection or connection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conexión no encontrada"
        )
    
    client = GoCardlessClient()
    total_transactions = 0
    
    # Sincronizar cada cuenta
    for account in connection.bank_accounts:
        transactions = client.get_transactions(account.account_id)
        
        # Aquí puedes procesar y guardar las transacciones
        # Similar a como lo haces con Bankinter
        total_transactions += len(transactions)
    
    # Actualizar fecha de sincronización
    connection.last_sync = date.today()
    db.commit()
    
    return {
        "message": f"Sincronización completada: {total_transactions} transacciones",
        "transactions_count": total_transactions
    }

@router.delete("/connections/{connection_id}")
async def disconnect_bank(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Dict:
    """Desconectar banco"""
    connection = db.get(BankConnection, connection_id)
    if not connection or connection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conexión no encontrada"
        )
    
    # Marcar como inactiva
    connection.is_active = False
    for account in connection.bank_accounts:
        account.is_active = False
    
    db.commit()
    
    return {"message": "Banco desconectado exitosamente"}