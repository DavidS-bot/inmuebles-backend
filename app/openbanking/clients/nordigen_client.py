import os
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

class NordigenClient:
    """Cliente para la API de Nordigen (GoCardless Bank Account Data)"""
    
    def __init__(self):
        self.secret_id = os.getenv("NORDIGEN_SECRET_ID")
        self.secret_key = os.getenv("NORDIGEN_SECRET_KEY")
        self.base_url = "https://ob.nordigen.com/api/v2"
        self._access_token = None
        self._token_expires_at = None
        
        if not self.secret_id or not self.secret_key:
            raise ValueError("Nordigen credentials not found in environment variables")

    async def _get_access_token(self) -> str:
        """Obtiene o renueva el token de acceso"""
        if self._access_token and self._token_expires_at and datetime.now() < self._token_expires_at:
            return self._access_token
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/token/new/",
                json={
                    "secret_id": self.secret_id,
                    "secret_key": self.secret_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            self._access_token = data["access"]
            # El token expira en 24 horas
            self._token_expires_at = datetime.now() + timedelta(seconds=data.get("access_expires", 86400))
            
            logger.info("Nordigen access token obtained successfully")
            return self._access_token

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Realiza una petición autenticada a la API de Nordigen"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def get_institutions(self, country_code: str = "ES") -> List[Dict[str, Any]]:
        """Obtiene la lista de instituciones bancarias disponibles"""
        return await self._make_request("GET", f"/institutions/?country={country_code}")

    async def create_requisition(self, institution_id: str, redirect_url: str, 
                               reference: str, user_language: str = "ES") -> Dict[str, Any]:
        """Crea una requisición para conectar con un banco"""
        data = {
            "redirect": redirect_url,
            "institution_id": institution_id,
            "reference": reference,
            "agreement": "",
            "user_language": user_language
        }
        return await self._make_request("POST", "/requisitions/", json=data)

    async def get_requisition(self, requisition_id: str) -> Dict[str, Any]:
        """Obtiene el estado de una requisición"""
        return await self._make_request("GET", f"/requisitions/{requisition_id}/")

    async def delete_requisition(self, requisition_id: str) -> Dict[str, Any]:
        """Elimina una requisición"""
        return await self._make_request("DELETE", f"/requisitions/{requisition_id}/")

    async def get_account_details(self, account_id: str) -> Dict[str, Any]:
        """Obtiene los detalles de una cuenta bancaria"""
        return await self._make_request("GET", f"/accounts/{account_id}/details/")

    async def get_account_balances(self, account_id: str) -> Dict[str, Any]:
        """Obtiene los saldos de una cuenta bancaria"""
        return await self._make_request("GET", f"/accounts/{account_id}/balances/")

    async def get_account_transactions(self, account_id: str, 
                                     date_from: Optional[date] = None,
                                     date_to: Optional[date] = None) -> Dict[str, Any]:
        """Obtiene las transacciones de una cuenta bancaria"""
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
            
        endpoint = f"/accounts/{account_id}/transactions/"
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint += f"?{query_string}"
            
        return await self._make_request("GET", endpoint)

    async def get_account_metadata(self, account_id: str) -> Dict[str, Any]:
        """Obtiene metadatos de una cuenta bancaria"""
        return await self._make_request("GET", f"/accounts/{account_id}/")

    def format_transaction_to_financial_movement(self, transaction: Dict[str, Any], 
                                               account_id: str) -> Dict[str, Any]:
        """Convierte una transacción de Nordigen al formato FinancialMovement"""
        booked = transaction.get("transactionDetails", {})
        if not booked:
            booked = transaction
            
        # Intentar obtener la fecha de diferentes campos posibles
        transaction_date = (
            booked.get("bookingDate") or 
            booked.get("valueDate") or 
            booked.get("transactionDate")
        )
        
        # Convertir el monto - puede estar en diferentes estructuras
        amount_data = booked.get("transactionAmount", {})
        amount = float(amount_data.get("amount", 0))
        
        # Si el monto es negativo en débitos, Nordigen a veces lo marca como positivo
        # pero indica la dirección en el campo debitCreditIndicator
        if booked.get("debitCreditIndicator") == "DBIT" and amount > 0:
            amount = -amount
            
        concept = (
            booked.get("remittanceInformationUnstructured") or
            booked.get("additionalInformation") or
            booked.get("transactionDetails", {}).get("remittanceInformation") or
            "Sin concepto"
        )
        
        return {
            "date": transaction_date,
            "concept": concept,
            "amount": amount,
            "category": "Sin clasificar",
            "subcategory": None,
            "is_classified": False,
            "bank_balance": booked.get("balanceAfterTransaction", {}).get("amount"),
            "external_id": booked.get("transactionId") or booked.get("entryReference"),
            "account_id": account_id
        }

# Instancia global del cliente
nordigen_client = NordigenClient()