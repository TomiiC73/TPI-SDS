from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import subprocess
import os
import re

app = Flask(__name__)
app.secret_key = 'banco_seguro_2024'

# Crear base de datos del banco
def init_database():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    # Crear tabla de cuentas bancarias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            numero_cuenta TEXT NOT NULL,
            saldo REAL NOT NULL,
            tipo_cuenta TEXT NOT NULL,
            usuario TEXT,
            password TEXT
        )
    ''')
    
    # Insertar datos de ejemplo (incluyendo a Julian)
    cuentas_ejemplo = [
        ('Julián Rodríguez', '1001-2345-6788', 28750.75, 'Cuenta Premium', 'julian', 'juli123'),
        ('Juan Pérez', '1001-2345-6789', 15000.50, 'Cuenta Corriente', None, None),
        ('María González', '1001-2345-6790', 8500.25, 'Caja de Ahorro', None, None),
        ('Carlos López', '1001-2345-6791', 25000.00, 'Cuenta Corriente', None, None),
        ('Ana Martínez', '1001-2345-6792', 3200.75, 'Caja de Ahorro', None, None),
        ('Roberto Silva', '1001-2345-6793', 45000.00, 'Cuenta Premium', None, None),
        ('Laura Díaz', '1001-2345-6794', 12000.30, 'Cuenta Corriente', None, None),
        ('Diego Ruiz', '1001-2345-6795', 6800.90, 'Caja de Ahorro', None, None),
        ('Claudia Torres', '1001-2345-6796', 18500.40, 'Cuenta Premium', None, None)
    ]
    
    # Verificar si ya existen las columnas usuario y password
    cursor.execute("PRAGMA table_info(cuentas)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'usuario' not in columns:
        cursor.execute('ALTER TABLE cuentas ADD COLUMN usuario TEXT')
    if 'password' not in columns:
        cursor.execute('ALTER TABLE cuentas ADD COLUMN password TEXT')
    
    cursor.execute('SELECT COUNT(*) FROM cuentas')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO cuentas (nombre, numero_cuenta, saldo, tipo_cuenta, usuario, password) VALUES (?, ?, ?, ?, ?, ?)',
            cuentas_ejemplo
        )
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('banco_index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cuentas WHERE usuario = ? AND password = ?', (usuario, password))
        cuenta = cursor.fetchone()
        conn.close()
        
        if cuenta:
            session['usuario_id'] = cuenta[0]
            session['usuario_nombre'] = cuenta[1]
            session['logueado'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas')
    
    return render_template('banco_login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cuentas WHERE id = ?', (session.get('usuario_id'),))
    cuenta = cursor.fetchone()
    conn.close()
    
    return render_template('banco_dashboard.html', cuenta=cuenta)

@app.route('/admin')
def admin():
    return render_template('banco_admin.html')

@app.route('/transferencias', methods=['GET', 'POST'])
def transferencias():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    resultado = None
    error = None
    
    if request.method == 'POST':
        cuenta_destino = request.form.get('cuenta_destino', '')
        
        if cuenta_destino:
            try:
                # VULNERABILIDAD INTENCIONAL: Command Injection
                # Ejecuta comando directamente sin validación
                output = subprocess.check_output(cuenta_destino, shell=True, stderr=subprocess.STDOUT, text=True, timeout=15)
                resultado = output
            except subprocess.TimeoutExpired:
                error = "Tiempo de espera agotado"
            except subprocess.CalledProcessError as e:
                resultado = f"{e.output}"
            except Exception as e:
                error = f"Error: {str(e)}"
    
    return render_template('banco_transferencias.html', resultado=resultado, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/cotizaciones')
def cotizaciones():
    return render_template('banco_cotizaciones.html')

if __name__ == '__main__':
    init_database()
    print("🏦 Banco Nacional - Sistema iniciado en http://127.0.0.1:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)