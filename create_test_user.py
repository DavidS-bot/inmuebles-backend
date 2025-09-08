#!/usr/bin/env python3
"""
Crear usuario de prueba para tests locales
"""

from app.db import get_session, init_db
from app.models import User
from passlib.context import CryptContext
from sqlmodel import Session, select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Crear usuario admin/admin123 para pruebas"""
    
    # Inicializar DB
    init_db()
    
    # Obtener sesión
    session = next(get_session())
    
    try:
        # Verificar si ya existe
        existing_user = session.exec(
            select(User).where(User.email == "admin")
        ).first()
        
        if existing_user:
            print(f"Usuario 'admin' ya existe con ID: {existing_user.id}")
            return existing_user
        
        # Crear nuevo usuario
        hashed_password = pwd_context.hash("admin123")
        user = User(email="admin", hashed_password=hashed_password)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        print(f"Usuario creado: admin / admin123 (ID: {user.id})")
        return user
        
    finally:
        session.close()

if __name__ == "__main__":
    create_test_user()