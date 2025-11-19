import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

print("🔄 RECREANDO CUENTA DE MARÍA GONZÁLEZ...\n")

# Verificar si existe
cursor.execute("SELECT id FROM cuentas WHERE id = 3")
if cursor.fetchone():
    print("❌ María ya existe, actualizando...")
    cursor.execute("""
        UPDATE cuentas 
        SET nombre = ?, usuario = ?, tipo_cuenta = ?, saldo = ?, password = ?
        WHERE id = 3
    """, ('María González', 'maria.gonzalez@banco.com', 'Caja de Ahorro', 8500.25, 
          generate_password_hash('maria123')))
else:
    print("✅ Creando nueva cuenta para María...")
    cursor.execute("""
        INSERT INTO cuentas (id, nombre, numero_cuenta, saldo, tipo_cuenta, usuario, password)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (3, 'María González', '1234-5678-90AB', 8500.25, 'Caja de Ahorro', 
          'maria.gonzalez@banco.com', generate_password_hash('maria123')))

conn.commit()

# Verificar cuentas finales
print("\n✅ CUENTAS PREPARADAS:\n")
cursor.execute("SELECT id, nombre, usuario, tipo_cuenta, saldo FROM cuentas WHERE id IN (1, 3)")
for row in cursor.fetchall():
    print(f"ID: {row[0]} | {row[1]:25} | {str(row[2]):30} | {row[3]:20} | ${row[4]}")

conn.close()

print("\n🎯 CREDENCIALES:")
print("   👤 Atacante: julian / hacker123")
print("   🎯 Víctima: maria.gonzalez@banco.com / maria123")
