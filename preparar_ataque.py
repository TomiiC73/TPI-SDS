import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

# 1. Limpiar cuentas OAuth del hacker y maría
print("🧹 Limpiando cuentas OAuth existentes...")
cursor.execute("DELETE FROM cuentas WHERE usuario IN ('oauth_g_004', 'oauth_g_666')")

# 2. Dar credenciales a María González (ID 3) para login tradicional
print("🔐 Configurando credenciales para María González...")
password_hash = generate_password_hash('maria123')
cursor.execute("UPDATE cuentas SET usuario = ?, password = ? WHERE id = 3", 
               ('maria.gonzalez@banco.com', password_hash))

# 3. Dar credenciales al atacante (usar Julian)
print("🔐 Configurando credenciales para el atacante...")
password_hash_hacker = generate_password_hash('hacker123')
cursor.execute("UPDATE cuentas SET password = ? WHERE usuario = 'julian'", 
               (password_hash_hacker,))

conn.commit()

# Verificar
cursor.execute('SELECT id, nombre, usuario, tipo_cuenta, saldo FROM cuentas WHERE id IN (1, 3)')
print("\n✅ CUENTAS PREPARADAS PARA EL ATAQUE:\n")
for row in cursor.fetchall():
    print(f'ID: {row[0]} | Nombre: {row[1]} | Usuario: {row[2]} | Tipo: {row[3]} | Saldo: ${row[4]}')

conn.close()

print("\n🎯 CREDENCIALES PARA EL ATAQUE:")
print("👤 Atacante: julian / hacker123")
print("🎯 Víctima: maria.gonzalez@banco.com / maria123")
