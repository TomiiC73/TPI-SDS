import sqlite3

conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

cursor.execute('SELECT id, nombre, usuario, tipo_cuenta, saldo FROM cuentas')
rows = cursor.fetchall()

print('\n=== CUENTAS EN LA BASE DE DATOS ===\n')
for row in rows:
    print(f'ID: {row[0]} | Nombre: {row[1]} | Usuario: {row[2]} | Tipo: {row[3]} | Saldo: ${row[4]}')

conn.close()
