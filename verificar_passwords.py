import sqlite3
from werkzeug.security import check_password_hash

conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

# Verificar Julian
cursor.execute("SELECT id, nombre, usuario, password FROM cuentas WHERE usuario = 'julian'")
row = cursor.fetchone()

if row:
    print(f"✅ Usuario encontrado:")
    print(f"   ID: {row[0]}")
    print(f"   Nombre: {row[1]}")
    print(f"   Usuario: {row[2]}")
    print(f"   Password hash existe: {row[3] is not None}")
    
    if row[3]:
        is_valid = check_password_hash(row[3], 'hacker123')
        print(f"   Password 'hacker123' válido: {is_valid}")
else:
    print("❌ Usuario 'julian' no encontrado")

# Verificar María
cursor.execute("SELECT id, nombre, usuario, password FROM cuentas WHERE id = 3")
row = cursor.fetchone()

if row:
    print(f"\n✅ María encontrada:")
    print(f"   ID: {row[0]}")
    print(f"   Nombre: {row[1]}")
    print(f"   Usuario: {row[2]}")
    print(f"   Password hash existe: {row[3] is not None}")
    
    if row[3]:
        is_valid = check_password_hash(row[3], 'maria123')
        print(f"   Password 'maria123' válido: {is_valid}")

conn.close()
