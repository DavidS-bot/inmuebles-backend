# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db, get_session
from .deps import get_current_user
from .routers import (
    properties, rules, movements, cashflow, auth,
    financial_movements, rental_contracts, mortgage_details, classification_rules, uploads, euribor_rates, analytics, mortgage_calculator, document_manager, notifications, tax_assistant, integrations, bank_integration, bankinter_v2, bankinter_simple, bankinter_real, payment_rules, bankinter_upload, bankinter_local, viability
)

app = FastAPI(title="Inmuebles API", version="0.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes para desarrollo local
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(properties.router)
app.include_router(rules.router)
app.include_router(movements.router)
app.include_router(cashflow.router)

# Financial Agent Routers
app.include_router(financial_movements.router)
app.include_router(rental_contracts.router)
app.include_router(mortgage_details.router)
app.include_router(classification_rules.router)
app.include_router(euribor_rates.router)
app.include_router(uploads.router)
app.include_router(analytics.router)
app.include_router(mortgage_calculator.router)
app.include_router(document_manager.router)
app.include_router(notifications.router)
app.include_router(tax_assistant.router)
app.include_router(integrations.router)
app.include_router(bank_integration.router)
app.include_router(bankinter_v2.router)
app.include_router(bankinter_simple.router)
app.include_router(bankinter_real.router)
app.include_router(bankinter_upload.router)
app.include_router(bankinter_local.router)
app.include_router(payment_rules.router)
app.include_router(viability.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    from sqlmodel import text
    try:
        with get_session() as session:
            # Check if viability tables exist
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'viability%';"))
            tables = [row[0] for row in result.fetchall()]
            return {
                "status": "ok", 
                "version": "0.1.2", 
                "viability_module": "enabled", 
                "timestamp": "2025-01-09",
                "viability_tables": tables
            }
    except Exception as e:
        return {"status": "ok", "version": "0.1.2", "viability_module": "enabled", "timestamp": "2025-01-09", "db_error": str(e)}

@app.get("/test-auth")
def test_auth(current_user = Depends(get_current_user)):
    return {"auth": "ok", "user_id": current_user.id, "user_email": current_user.email}

@app.get("/debug/routes")
def debug_routes():
    """Debug endpoint to check all available routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unnamed')
            })
    return {"routes": routes}

# Endpoint temporal removido para evitar errores
# Payment rules router incluido - forcing reload



