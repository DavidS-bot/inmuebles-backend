#!/usr/bin/env python3
"""
Cliente API PSD2 de Bankinter
============================

Cliente para acceder a los datos de Bankinter usando la API PSD2 oficial
a través de la plataforma Redsys, evitando problemas de web scraping.

Basado en la documentación oficial:
https://market.apis-i.redsys.es/psd2/xs2a/nodos/bankinter
"""

import requests
import json
import base64
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import urllib.parse
import hashlib
import secrets

class BankinterAPIClient:
    """Cliente para la API PSD2 de Bankinter via Redsys"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, sandbox: bool = True):
        """
        Inicializar cliente API
        
        Args:
            client_id: ID de cliente PSD2 (se obtiene registrándose en Redsys)
            client_secret: Secret del cliente
            sandbox: Usar entorno sandbox (True) o producción (False)
        """
        self.client_id = client_id or "DEMO_CLIENT_ID"  # Placeholder para demo
        self.client_secret = client_secret or "DEMO_CLIENT_SECRET"
        self.sandbox = sandbox
        
        # URLs de la API según documentación oficial
        if sandbox:
            self.base_url = "https://apis-i.redsys.es:20443/psd2/xs2a/api-entrada-xs2a/services/bankinter/v1.1"
            self.oauth_url = "https://apis-i.redsys.es:20443/psd2/xs2a/api-oauth-xs2a/services/rest/bankinter"
        else:
            self.base_url = "https://apis-i.redsys.es:20443/psd2/xs2a/api-entrada-xs2a/services/bankinter/v1.1"
            self.oauth_url = "https://apis-i.redsys.es:20443/psd2/xs2a/api-oauth-xs2a/services/rest/bankinter"
        
        self.access_token = None
        self.consent_id = None
        self.session = requests.Session()
        
        # Headers estándar según documentación PSD2
        self.default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'InmueblesApp/1.0 PSD2Client',
            'X-Request-ID': self._generate_request_id()
        }
        
        self.session.headers.update(self.default_headers)
    
    def _generate_request_id(self) -> str:
        """Generar ID único para cada request"""
        return str(uuid.uuid4())
    
    def _get_auth_header(self) -> Dict[str, str]:
        """Obtener header de autorización"""
        if self.access_token:
            return {'Authorization': f'Bearer {self.access_token}'}
        return {}
    
    async def authenticate(self, username: str, password: str = None) -> Dict[str, Any]:
        """
        Autenticar usuario usando OAuth2 flow de Bankinter
        
        Returns:
            Dict con información de autenticación y siguiente paso
        """
        try:
            print(f"[INFO] Iniciando autenticación OAuth2 con Bankinter API...")
            
            # PASO 1: Solicitar autorización OAuth2
            auth_params = {
                'response_type': 'code',
                'client_id': self.client_id,
                'redirect_uri': 'https://localhost:8080/callback',  # URL de callback
                'scope': 'AIS',  # Account Information Service
                'state': secrets.token_urlsafe(32)
            }
            
            auth_url = f"{self.oauth_url}/authorize?" + urllib.parse.urlencode(auth_params)
            
            print(f"[INFO] URL de autorización generada")
            print(f"[IMPORTANTE] Para completar la autenticación necesitas:")
            print(f"1. Visitar esta URL en tu navegador:")
            print(f"   {auth_url}")
            print(f"2. Iniciar sesión con tus credenciales de Bankinter")
            print(f"3. Autorizar el acceso a tus cuentas")
            print(f"4. Copiar el código de autorización que aparece")
            
            return {
                'status': 'auth_required',
                'auth_url': auth_url,
                'message': 'Visita la URL de autorización para obtener el código',
                'next_step': 'exchange_code'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error en autenticación: {str(e)}'
            }
    
    async def exchange_auth_code(self, auth_code: str) -> Dict[str, Any]:
        """
        Intercambiar código de autorización por access token
        
        Args:
            auth_code: Código recibido después de autorizar
        """
        try:
            print(f"[INFO] Intercambiando código de autorización por access token...")
            
            # Datos para intercambio de token
            token_data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'https://localhost:8080/callback',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = self.session.post(
                f"{self.oauth_url}/token",
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info.get('access_token')
                
                print(f"[SUCCESS] Access token obtenido exitosamente")
                return {
                    'status': 'authenticated',
                    'access_token': self.access_token,
                    'expires_in': token_info.get('expires_in'),
                    'token_type': token_info.get('token_type')
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Error obteniendo token: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error intercambiando código: {str(e)}'
            }
    
    async def create_consent(self) -> Dict[str, Any]:
        """
        Crear consentimiento para acceso a cuentas
        """
        try:
            print(f"[INFO] Creando consentimiento para acceso a cuentas...")
            
            # Datos de consentimiento según spec PSD2
            consent_data = {
                'access': {
                    'accounts': [],  # Vacío para acceso a todas las cuentas
                    'balances': [],
                    'transactions': []
                },
                'recurringIndicator': True,
                'validUntil': (date.today() + timedelta(days=90)).isoformat(),
                'frequencyPerDay': 4,
                'combinedServiceIndicator': False
            }
            
            headers = {
                **self._get_auth_header(),
                'X-Request-ID': self._generate_request_id(),
                'TPP-Redirect-URI': 'https://localhost:8080/consent-callback'
            }
            
            response = self.session.post(
                f"{self.base_url}/consents",
                json=consent_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                consent_info = response.json()
                self.consent_id = consent_info.get('consentId')
                
                print(f"[SUCCESS] Consentimiento creado: {self.consent_id}")
                return {
                    'status': 'consent_created',
                    'consent_id': self.consent_id,
                    'consent_info': consent_info
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Error creando consentimiento: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error en consentimiento: {str(e)}'
            }
    
    async def get_accounts(self) -> Dict[str, Any]:
        """
        Obtener lista de cuentas del usuario
        """
        try:
            print(f"[INFO] Obteniendo lista de cuentas...")
            
            if not self.consent_id:
                return {'status': 'error', 'message': 'Consentimiento requerido'}
            
            headers = {
                **self._get_auth_header(),
                'X-Request-ID': self._generate_request_id(),
                'Consent-ID': self.consent_id
            }
            
            response = self.session.get(
                f"{self.base_url}/accounts",
                headers=headers
            )
            
            if response.status_code == 200:
                accounts_data = response.json()
                accounts = accounts_data.get('accounts', [])
                
                print(f"[SUCCESS] Obtenidas {len(accounts)} cuentas")
                return {
                    'status': 'success',
                    'accounts': accounts,
                    'count': len(accounts)
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Error obteniendo cuentas: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error en obtención de cuentas: {str(e)}'
            }
    
    async def get_account_transactions(self, account_id: str, date_from: date = None, date_to: date = None) -> Dict[str, Any]:
        """
        Obtener transacciones de una cuenta específica
        
        Args:
            account_id: ID de la cuenta
            date_from: Fecha inicio (por defecto: 90 días atrás)
            date_to: Fecha fin (por defecto: hoy)
        """
        try:
            if not date_from:
                date_from = date.today() - timedelta(days=90)
            if not date_to:
                date_to = date.today()
            
            print(f"[INFO] Obteniendo transacciones de cuenta {account_id} desde {date_from} hasta {date_to}")
            
            headers = {
                **self._get_auth_header(),
                'X-Request-ID': self._generate_request_id(),
                'Consent-ID': self.consent_id
            }
            
            params = {
                'dateFrom': date_from.isoformat(),
                'dateTo': date_to.isoformat()
            }
            
            response = self.session.get(
                f"{self.base_url}/accounts/{account_id}/transactions",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                transactions_data = response.json()
                transactions = transactions_data.get('transactions', {}).get('booked', [])
                
                print(f"[SUCCESS] Obtenidas {len(transactions)} transacciones")
                return {
                    'status': 'success',
                    'transactions': transactions,
                    'count': len(transactions),
                    'account_id': account_id
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Error obteniendo transacciones: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error en transacciones: {str(e)}'
            }
    
    async def get_account_balances(self, account_id: str) -> Dict[str, Any]:
        """Obtener saldos de una cuenta"""
        try:
            print(f"[INFO] Obteniendo saldos de cuenta {account_id}")
            
            headers = {
                **self._get_auth_header(),
                'X-Request-ID': self._generate_request_id(),
                'Consent-ID': self.consent_id
            }
            
            response = self.session.get(
                f"{self.base_url}/accounts/{account_id}/balances",
                headers=headers
            )
            
            if response.status_code == 200:
                balances_data = response.json()
                balances = balances_data.get('balances', [])
                
                print(f"[SUCCESS] Obtenidos saldos de cuenta")
                return {
                    'status': 'success',
                    'balances': balances,
                    'account_id': account_id
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Error obteniendo saldos: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error en saldos: {str(e)}'
            }


def create_demo_flow():
    """
    Crear flujo de demostración para registro en PSD2
    """
    print("=" * 60)
    print("ACCESO A BANKINTER VIA API PSD2 OFICIAL")
    print("=" * 60)
    print()
    print("Para usar la API PSD2 de Bankinter necesitas:")
    print()
    print("1. REGISTRO EN REDSYS:")
    print("   - Ve a: https://market.apis-i.redsys.es")
    print("   - Regístrate como Third Party Provider (TPP)")
    print("   - Solicita acceso a Bankinter PSD2 APIs")
    print("   - Obtén tu CLIENT_ID y CLIENT_SECRET")
    print()
    print("2. SOLICITAR ACCESO AL SANDBOX:")
    print("   - Envía email a: psd2.sandbox.soporte@redsys.es")
    print("   - Asunto: 'APP access request biometrics Sandbox'")
    print("   - Incluye tus datos de TPP")
    print()
    print("3. VENTAJAS DE LA API PSD2:")
    print("   ✓ Acceso oficial y legal a datos bancarios")
    print("   ✓ Sin problemas de web scraping o crashes")
    print("   ✓ Datos estructurados en formato JSON")
    print("   ✓ Soporte oficial de Bankinter")
    print("   ✓ Cumple normativa europea PSD2")
    print()
    print("4. SERVICIOS DISPONIBLES:")
    print("   ✓ Account Information Service (AIS)")
    print("   ✓ Payment Initiation Service (PIS)")
    print("   ✓ Confirmation of Funds Service")
    print()
    print("¿Quieres que te ayude a crear el proceso de registro?")


async def demo_api_flow():
    """Flujo de demostración de la API"""
    print("\n" + "="*50)
    print("DEMO: FLUJO API PSD2 BANKINTER")
    print("="*50)
    
    # Crear cliente (modo demo)
    client = BankinterAPIClient(sandbox=True)
    
    print("\n[PASO 1] Autenticación OAuth2...")
    auth_result = await client.authenticate("demo_user")
    
    if auth_result['status'] == 'auth_required':
        print(f"\n{auth_result['message']}")
        print(f"\nURL de autorización: {auth_result['auth_url']}")
        
        # En un flujo real, el usuario visitaría la URL y obtendría un código
        print("\n[DEMO] Simulando intercambio de código...")
        # Aquí normalmente esperarías el código del usuario
        
    print("\n[PASO 2] Crear consentimiento...")
    # En demo, esto fallaría sin credenciales reales
    print("[DEMO] En un entorno real, se crearía consentimiento para acceso a cuentas")
    
    print("\n[PASO 3] Obtener cuentas...")
    print("[DEMO] Se obtendrían todas las cuentas del usuario")
    
    print("\n[PASO 4] Obtener transacciones...")
    print("[DEMO] Se descargarían todas las transacciones en formato JSON")
    
    return True


if __name__ == "__main__":
    import asyncio
    
    print("Selecciona una opción:")
    print("1. Ver información de registro PSD2")
    print("2. Ejecutar demo del flujo API")
    
    choice = input("\nElige (1 o 2): ").strip()
    
    if choice == "1":
        create_demo_flow()
    elif choice == "2":
        asyncio.run(demo_api_flow())
    else:
        print("Opción no válida")