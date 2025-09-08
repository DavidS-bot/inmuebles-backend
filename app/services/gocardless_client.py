import os
from nordigen import NordigenClient
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GoCardlessClient:
    def __init__(self):
        self.secret_id = os.getenv("GOCARDLESS_SECRET_ID")
        self.secret_key = os.getenv("GOCARDLESS_SECRET_KEY")
        self.client = NordigenClient(
            secret_id=self.secret_id,
            secret_key=self.secret_key
        )
        self.token = None

    def get_token(self):
        """Obtener token de acceso"""
        if not self.token:
            self.token = self.client.generate_token()
        return self.token

    def get_institutions(self, country_code: str = "ES") -> List[Dict]:
        """Obtener lista de bancos disponibles"""
        try:
            self.get_token()
            institutions = self.client.institution.get_institutions(country_code)
            return institutions
        except Exception as e:
            logger.error(f"Error obteniendo instituciones: {e}")
            return []

    def create_requisition(self, institution_id: str, redirect_uri: str, user_id: str) -> Dict:
        """Crear requisición para conectar banco"""
        try:
            self.get_token()
            requisition = self.client.initialize_session(
                redirect_uri=redirect_uri,
                institution_id=institution_id,
                reference_id=f"user_{user_id}",
                max_historical_days=365
            )
            return {
                "requisition_id": requisition.requisition_id,
                "link": requisition.link
            }
        except Exception as e:
            logger.error(f"Error creando requisición: {e}")
            return {}

    def get_accounts(self, requisition_id: str) -> List[str]:
        """Obtener cuentas asociadas a una requisición"""
        try:
            self.get_token()
            accounts = self.client.requisition.get_requisition_by_id(requisition_id)
            return accounts.get("accounts", [])
        except Exception as e:
            logger.error(f"Error obteniendo cuentas: {e}")
            return []

    def get_account_details(self, account_id: str) -> Dict:
        """Obtener detalles de una cuenta"""
        try:
            self.get_token()
            account = self.client.account.get_details(account_id)
            return account
        except Exception as e:
            logger.error(f"Error obteniendo detalles de cuenta: {e}")
            return {}

    def get_account_balances(self, account_id: str) -> Dict:
        """Obtener balances de una cuenta"""
        try:
            self.get_token()
            balances = self.client.account.get_balances(account_id)
            return balances
        except Exception as e:
            logger.error(f"Error obteniendo balances: {e}")
            return {}

    def get_transactions(self, account_id: str, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Obtener transacciones de una cuenta"""
        try:
            self.get_token()
            transactions = self.client.account.get_transactions(
                account_id=account_id,
                date_from=date_from,
                date_to=date_to
            )
            return transactions.get("transactions", {}).get("booked", [])
        except Exception as e:
            logger.error(f"Error obteniendo transacciones: {e}")
            return []