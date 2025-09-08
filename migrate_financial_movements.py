#!/usr/bin/env python3
"""
Migration script to update FinancialMovement table:
1. Add user_id column
2. Make property_id nullable
3. Populate user_id for existing records
"""

from app.db import get_session
from app.models import FinancialMovement, Property
from sqlmodel import text
from sqlalchemy import text as sql_text
import sys

def migrate_financial_movements():
    with next(get_session()) as session:
        try:
            print("Starting FinancialMovement table migration...")
            
            # Step 1: Add user_id column if it doesn't exist
            print("Step 1: Adding user_id column...")
            try:
                session.exec(text("ALTER TABLE financialmovement ADD COLUMN user_id INTEGER"))
                print("OK - Added user_id column")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("WARNING - user_id column already exists")
                else:
                    raise e
            
            # Step 2: Create a new table with correct schema
            print("Step 2: Creating new table with correct schema...")
            session.exec(text("""
                CREATE TABLE IF NOT EXISTS financialmovement_new (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    property_id INTEGER NULL,
                    date DATE NOT NULL,
                    concept VARCHAR NOT NULL,
                    amount FLOAT NOT NULL,
                    category VARCHAR NOT NULL,
                    subcategory VARCHAR NULL,
                    tenant_name VARCHAR NULL,
                    is_classified BOOLEAN NOT NULL,
                    bank_balance FLOAT NULL,
                    FOREIGN KEY(user_id) REFERENCES user(id),
                    FOREIGN KEY(property_id) REFERENCES property(id)
                )
            """))
            
            # Step 3: Populate user_id for existing records and copy to new table
            print("Step 3: Migrating existing data...")
            
            # Get all existing movements with their property owner
            existing_movements = session.exec(text("""
                SELECT fm.*, p.owner_id as user_id_from_property
                FROM financialmovement fm
                JOIN property p ON fm.property_id = p.id
            """)).fetchall()
            
            # Insert into new table with user_id populated
            for movement in existing_movements:
                insert_sql = sql_text("""
                    INSERT INTO financialmovement_new 
                    (id, user_id, property_id, date, concept, amount, category, subcategory, tenant_name, is_classified, bank_balance)
                    VALUES (:id, :user_id, :property_id, :date, :concept, :amount, :category, :subcategory, :tenant_name, :is_classified, :bank_balance)
                """)
                session.connection().execute(insert_sql, {
                    "id": movement.id,
                    "user_id": movement.user_id_from_property,  # Use property owner as user_id
                    "property_id": movement.property_id,
                    "date": movement.date,
                    "concept": movement.concept,
                    "amount": movement.amount,
                    "category": movement.category,
                    "subcategory": movement.subcategory,
                    "tenant_name": movement.tenant_name,
                    "is_classified": movement.is_classified,
                    "bank_balance": movement.bank_balance
                })
            
            # Step 4: Replace old table with new one
            print("Step 4: Replacing old table...")
            session.exec(text("DROP TABLE financialmovement"))
            session.exec(text("ALTER TABLE financialmovement_new RENAME TO financialmovement"))
            
            session.commit()
            print("OK - Migration completed successfully!")
            print(f"   Migrated {len(existing_movements)} existing movements")
            
        except Exception as e:
            session.rollback()
            print(f"ERROR - Migration failed: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    migrate_financial_movements()