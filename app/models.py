# app/models.py
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from typing import ForwardRef

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    is_active: bool = True

    properties: List["Property"] = Relationship(back_populates="owner")
    payment_rules: List["PaymentRule"] = Relationship(back_populates="user")
    viability_studies: List["ViabilityStudy"] = Relationship(back_populates="user")

class Property(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    address: str
    rooms: Optional[int] = None
    m2: Optional[int] = None
    photo: Optional[str] = None
    
    # Campos financieros adicionales
    property_type: Optional[str] = None  # "Piso", "Unifamiliar", etc.
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    appraisal_value: Optional[float] = None
    down_payment: Optional[float] = None  # Entrada/enganche pagado
    acquisition_costs: Optional[float] = None  # Gastos de compra (notaría, impuestos, etc.)
    renovation_costs: Optional[float] = None  # Costos de renovación

    owner: Optional[User] = Relationship(back_populates="properties")
    rules: List["Rule"] = Relationship(back_populates="property")
    movements: List["Movement"] = Relationship(back_populates="property")
    
    # Nuevas relaciones financieras
    mortgage_details: Optional["MortgageDetails"] = Relationship(back_populates="property")
    rental_contracts: List["RentalContract"] = Relationship(back_populates="property")
    financial_movements: List["FinancialMovement"] = Relationship(back_populates="property")
    classification_rules: List["ClassificationRule"] = Relationship(back_populates="property")
    payment_rules: List["PaymentRule"] = Relationship(back_populates="property")
    viability_studies: List["ViabilityStudy"] = Relationship(back_populates="property")

class Rule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id")
    name: str
    match_text: str
    category: str  # "mortgage", "rent", "tax", "insurance", "hoa", "maintenance", "management", "utilities", "other"

    property: Optional[Property] = Relationship(back_populates="rules")

class Movement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id")
    date: date
    concept: str
    amount: float            # + ingreso, - gasto
    category: Optional[str] = None  # si ya viene categorizado

    property: Optional[Property] = Relationship(back_populates="movements")

class FinancialMovement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")  # Owner of the movement
    property_id: Optional[int] = Field(default=None, foreign_key="property.id")  # Can be null initially
    date: date
    concept: str
    amount: float
    category: str  # "Renta", "Hipoteca", "Gasto"
    subcategory: Optional[str] = None  # Para gastos: "Comunidad", "IBI", etc.
    tenant_name: Optional[str] = None  # Para rentas
    is_classified: bool = True  # Si fue clasificado automáticamente
    bank_balance: Optional[float] = None  # Saldo después del movimiento
    
    # Campos para integración bancaria
    external_id: Optional[str] = None  # ID de la transacción en el banco (para evitar duplicados)
    bank_account_id: Optional[str] = None  # ID de la cuenta bancaria origen
    source: str = "manual"  # "manual", "nordigen", "bankinter", etc.
    
    user: Optional[User] = Relationship()
    property: Optional[Property] = Relationship(back_populates="financial_movements")

class RentalContract(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id")
    tenant_name: str
    start_date: date
    end_date: Optional[date] = None
    monthly_rent: float
    deposit: Optional[float] = None
    contract_pdf_path: Optional[str] = None
    contract_file_name: Optional[str] = None
    is_active: bool = True
    
    # Información adicional del inquilino
    tenant_email: Optional[str] = None
    tenant_phone: Optional[str] = None
    tenant_dni: Optional[str] = None
    tenant_address: Optional[str] = None
    monthly_income: Optional[float] = None
    job_position: Optional[str] = None
    employer_name: Optional[str] = None
    
    property: Optional[Property] = Relationship(back_populates="rental_contracts")
    tenant_documents: List["TenantDocument"] = Relationship(back_populates="rental_contract")

class TenantDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rental_contract_id: int = Field(foreign_key="rentalcontract.id")
    document_type: str  # "dni", "payslip", "employment_contract", "bank_statement", "other"
    document_name: str  # Nombre del archivo
    file_path: str  # Ruta donde se almacena el archivo
    file_size: Optional[int] = None  # Tamaño en bytes
    upload_date: date = Field(default_factory=lambda: date.today())
    description: Optional[str] = None  # Descripción opcional del documento
    
    rental_contract: Optional[RentalContract] = Relationship(back_populates="tenant_documents")

class MortgageDetails(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id", unique=True)
    loan_id: Optional[str] = None
    bank_entity: Optional[str] = None
    mortgage_type: str = "Variable"  # "Variable" o "Fija"
    initial_amount: float
    outstanding_balance: float
    margin_percentage: float
    start_date: date
    end_date: date
    review_period_months: int = 12
    
    property: Optional[Property] = Relationship(back_populates="mortgage_details")
    revisions: List["MortgageRevision"] = Relationship(back_populates="mortgage")
    prepayments: List["MortgagePrepayment"] = Relationship(back_populates="mortgage")

class MortgageRevision(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mortgage_id: int = Field(foreign_key="mortgagedetails.id")
    effective_date: date
    euribor_rate: Optional[float] = None
    margin_rate: float
    period_months: int
    
    mortgage: Optional[MortgageDetails] = Relationship(back_populates="revisions")

class MortgagePrepayment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mortgage_id: int = Field(foreign_key="mortgagedetails.id")
    payment_date: date
    amount: float
    
    mortgage: Optional[MortgageDetails] = Relationship(back_populates="prepayments")

class ClassificationRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id")
    keyword: str  # Palabra clave a buscar en el concepto
    category: str  # "Renta", "Hipoteca", "Gasto"
    subcategory: Optional[str] = None  # Para gastos específicos
    tenant_name: Optional[str] = None  # Para asociar rentas a inquilinos
    is_active: bool = True
    
    property: Optional[Property] = Relationship(back_populates="classification_rules")

class EuriborRate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date  # Fecha de la tasa (normalmente primer día del mes)
    rate_12m: Optional[float] = None  # Tasa Euribor a 12 meses
    rate_6m: Optional[float] = None   # Tasa Euribor a 6 meses
    rate_3m: Optional[float] = None   # Tasa Euribor a 3 meses
    rate_1m: Optional[float] = None   # Tasa Euribor a 1 mes
    source: Optional[str] = None      # Fuente de los datos
    created_at: Optional[date] = None # Fecha de creación del registro

class BankConnection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    institution_id: str  # ID del banco en Nordigen/GoCardless
    institution_name: str  # Nombre del banco
    institution_logo: Optional[str] = None  # URL del logo del banco
    institution_bic: Optional[str] = None  # BIC del banco
    requisition_id: str  # ID de la requisición de Nordigen
    requisition_reference: str  # Referencia única de la requisición
    consent_status: str = "CR"  # CR, GC, UA, RJ, EX, GA, SA
    consent_url: Optional[str] = None  # URL de consentimiento
    consent_expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync: Optional[datetime] = None
    sync_status: str = "PENDING"  # PENDING, SYNCING, SUCCESS, ERROR
    sync_error: Optional[str] = None
    
    # Configuración de sincronización
    auto_sync_enabled: bool = True
    sync_frequency_hours: int = 24  # Frecuencia de sincronización en horas
    
    # Relaciones
    user: Optional[User] = Relationship()
    bank_accounts: List["BankAccount"] = Relationship(back_populates="connection")

class BankAccount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    connection_id: int = Field(foreign_key="bankconnection.id")
    account_id: str  # ID de la cuenta en Nordigen/GoCardless
    iban: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None  # "current", "savings", etc.
    currency: str = "EUR"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Saldos actuales
    available_balance: Optional[float] = None
    current_balance: Optional[float] = None
    credit_limit: Optional[float] = None
    
    # Información adicional
    bic: Optional[str] = None
    owner_name: Optional[str] = None
    product_name: Optional[str] = None
    
    # Control de sincronización
    last_transaction_sync: Optional[datetime] = None
    sync_from_date: Optional[date] = None  # Desde qué fecha sincronizar
    
    connection: Optional[BankConnection] = Relationship(back_populates="bank_accounts")

class PaymentRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    property_id: Optional[int] = Field(default=None, foreign_key="property.id")  # null = applies to all properties
    tenant_name: Optional[str] = None  # null = applies to all tenants
    
    # Payment window configuration
    payment_start_day: int = 1  # Day of month when payment window starts (1-31)
    payment_end_day: int = 5    # Day of month when payment window ends (1-31)
    
    # Support for previous month end days
    allow_previous_month_end: bool = False  # Allow payments from end of previous month
    previous_month_end_days: int = 0  # Number of days from end of previous month (0-10)
    
    # Overdue configuration
    overdue_grace_days: int = 15  # Days after payment window before considering overdue
    warning_days: int = 30       # Days before showing warning notifications
    critical_days: int = 60      # Days before marking as critical
    
    # Rule configuration
    rule_name: str = "Default Payment Rule"
    is_active: bool = True
    created_at: Optional[date] = Field(default_factory=date.today)
    
    # Relationships
    user: Optional[User] = Relationship()
    property: Optional[Property] = Relationship()

class ViabilityStudy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    property_id: Optional[int] = Field(default=None, foreign_key="property.id")
    study_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # DATOS DE COMPRA
    purchase_price: float
    property_valuation: Optional[float] = None
    purchase_taxes_percentage: float = 0.11  # ITP + Notario + Registro
    purchase_costs: float = 0  # Calculado automáticamente
    total_purchase_price: float = 0  # Precio + Costes
    renovation_costs: Optional[float] = 0
    real_estate_commission: Optional[float] = 0
    
    # FINANCIACIÓN
    loan_amount: float
    down_payment: float = 0  # Equity/Depósito - calculado
    loan_type: str = "fixed"  # "fixed" o "variable"
    interest_rate: float
    loan_term_years: int = 25
    euribor_spread: Optional[float] = 0.015  # Diferencial sobre Euribor para préstamos variables
    euribor_reset_vector: Optional[str] = None  # JSON string con vector de Euribor proyectado
    monthly_mortgage_payment: float = 0  # Calculado
    loan_to_value: float = 0  # LTV calculado
    
    # INGRESOS
    monthly_rent: float
    annual_rent_increase: float = 0.02  # 2% anual
    
    # GASTOS FIJOS ANUALES
    community_fees: Optional[float] = 0
    property_tax_ibi: float
    life_insurance: Optional[float] = 0
    home_insurance: float
    maintenance_percentage: float = 0.01  # 1% valor propiedad
    property_management_fee: Optional[float] = 0  # Si se gestiona por terceros
    
    # RESULTADOS CALCULADOS
    monthly_net_cashflow: float = 0
    annual_net_cashflow: float = 0
    net_annual_return: float = 0  # Rentabilidad neta anual
    total_annual_return: float = 0  # Rentabilidad + equity
    monthly_equity_increase: float = 0  # Amortización del préstamo
    annual_equity_increase: float = 0
    
    # ANÁLISIS DE RIESGO
    break_even_rent: float = 0  # Renta mínima para cubrir gastos
    vacancy_risk_percentage: float = 0.05  # 5% riesgo vacancia
    stress_test_rent_decrease: float = 0.10  # Test con 10% menos renta
    
    # ESTADO DEL ESTUDIO
    is_favorable: bool = Field(default=False)
    risk_level: str = Field(default="MEDIUM")  # LOW, MEDIUM, HIGH
    notes: Optional[str] = None
    
    # Relaciones
    user: Optional[User] = Relationship()
    property: Optional["Property"] = Relationship()
    projections: List["ViabilityProjection"] = Relationship(back_populates="viability_study")

class ViabilityProjection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    viability_study_id: int = Field(foreign_key="viabilitystudy.id")
    year: int
    month: int
    
    # SALDOS
    outstanding_loan_balance: float
    accumulated_equity: float
    property_value: float  # Con revalorización
    
    # FLUJOS DEL MES
    monthly_rent: float
    monthly_mortgage_payment: float
    monthly_interest: float
    monthly_principal: float
    monthly_expenses: float
    monthly_net_cashflow: float
    accumulated_cashflow: float
    
    # MÉTRICAS
    annual_return: float
    total_return_with_equity: float
    current_ltv: float
    
    # Relación
    viability_study: Optional[ViabilityStudy] = Relationship(back_populates="projections")

