#!/usr/bin/env python3
"""Script para crear el usuario por defecto en producción"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select, create_engine
from app.models import User
from app.auth import hash_password

# Usar la base de datos de producción si está configurada
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_wR5UbmeYV2zL@ep-weathered-scene-a2i7fqn3-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def create_default_user():
    """Crear usuario por defecto para producción"""
    
    email = "davsanchez21277@gmail.com"
    password = "123456"
    
    with Session(engine) as session:
        # Verificar si el usuario ya existe
        existing_user = session.exec(select(User).where(User.email == email)).first()
        
        if existing_user:
            print(f"Usuario {email} ya existe")
            return
        
        # Crear nuevo usuario
        hashed_password = hash_password(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        print(f"Usuario creado exitosamente:")
        print(f"   Email: {email}")
        print(f"   ID: {user.id}")
        print(f"   Activo: {user.is_active}")

if __name__ == "__main__":
    print("Creando usuario por defecto...")
    print(f"Base de datos: {DATABASE_URL[:50]}...")
    try:
        create_default_user()
        print("Usuario por defecto creado exitosamente")
    except Exception as e:
        print(f"Error creando usuario: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)