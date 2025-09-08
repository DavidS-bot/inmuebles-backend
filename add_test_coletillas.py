#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('./data/dev.db')
cursor = conn.cursor()

# Add coletillas to 3 most recent movements for testing
cursor.execute("""
    UPDATE financialmovement 
    SET concept = concept || ' Pulsa para ver detalle del movimiento'
    WHERE id IN (
        SELECT id FROM financialmovement 
        ORDER BY id DESC 
        LIMIT 3
    )
""")

affected = cursor.rowcount
conn.commit()
conn.close()

print(f"Added test coletillas to {affected} movements")