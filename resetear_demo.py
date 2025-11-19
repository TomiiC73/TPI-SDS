import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

print("🔄 RESETEANDO BASE DE DATOS PARA NUEVA DEMOSTRACIÓN...\n")

# 1. Eliminar todas las cuentas OAuth
print("🧹 Eliminando cuentas OAuth...")
cursor.execute("DELETE FROM cuentas WHERE tipo_cuenta LIKE '%OAuth%'")
deleted = cursor.rowcount
print(f"   ✅ {deleted} cuentas OAuth eliminadas")

# 2. Restaurar cuenta de María González a estado original
print("\n🔧 Restaurando cuenta de María González...")
cursor.execute("""
    UPDATE cuentas 
    SET usuario = ?, 
        tipo_cuenta = ?,
        password = ?
    WHERE id = 3
""", ('maria.gonzalez@banco.com', 'Caja de Ahorro', generate_password_hash('maria123')))
print("   ✅ María restaurada (Caja de Ahorro)")

# 3. Asegurar credenciales de Julian
print("\n🔧 Verificando credenciales de Julian...")
cursor.execute("UPDATE cuentas SET password = ? WHERE usuario = 'julian'", 
               (generate_password_hash('hacker123'),))
print("   ✅ Julian configurado")

conn.commit()

# Verificar estado final
print("\n" + "="*60)
print("✅ ESTADO FINAL - LISTO PARA NUEVA DEMOSTRACIÓN")
print("="*60)

cursor.execute("""
    SELECT id, nombre, usuario, tipo_cuenta, saldo 
    FROM cuentas 
    WHERE id IN (1, 3) OR usuario LIKE '%oauth%'
    ORDER BY id
""")

for row in cursor.fetchall():
    print(f"ID: {row[0]:2} | {row[1]:25} | {str(row[2]):30} | {row[3]:20} | ${row[4]}")

conn.close()

print("\n🎯 CREDENCIALES PARA EL ATAQUE:")
print("   👤 Atacante: julian / hacker123")
print("   🎯 Víctima: maria.gonzalez@banco.com / maria123")
print("\n✅ Todo listo para repetir el ataque!")
