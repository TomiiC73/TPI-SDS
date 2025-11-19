import sqlite3

conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

# Ver tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('\n=== TABLAS EN banco.db ===')
for table in cursor.fetchall():
    print(f'- {table[0]}')

# Ver contenido de cuentas
cursor.execute('SELECT id, nombre, usuario, tipo_cuenta, saldo FROM cuentas')
print('\n=== CONTENIDO DE LA TABLA "cuentas" ===\n')
for row in cursor.fetchall():
    print(f'ID: {row[0]:2} | Nombre: {row[1]:25} | Usuario: {str(row[2]):30} | Tipo: {row[3]:20} | Saldo: ${row[4]}')

conn.close()
