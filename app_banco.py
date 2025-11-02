from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import subprocess
import os
import re
import jwt
import secrets
import time
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'banco_seguro_2024'

# ============================================
# CONFIGURACIÓN OAUTH2 GOOGLE
# ============================================
GOOGLE_CLIENT_ID = "banco-app-123456"
GOOGLE_CLIENT_SECRET = "SECRET_SUPER_SECRETO_EXPUESTO_123"
GOOGLE_JWT_SECRET = "jwt_secret_debil"
GOOGLE_REDIRECT_URI = "http://127.0.0.1:5000/oauth/callback"
GOOGLE_AUTH_URL = "http://127.0.0.1:5000/oauth/google/authorize"
GOOGLE_TOKEN_URL = "http://127.0.0.1:5000/oauth/google/token"

# Base de datos de usuarios de Google (simulación)
GOOGLE_USERS = {
    'usuario@google.com': {
        'password': 'google123',
        'name': 'Usuario Google',
        'email': 'usuario@google.com',
        'user_id': 'g_001'
    },
    'admin@google.com': {
        'password': 'admin123',
        'name': 'Admin Google',
        'email': 'admin@google.com',
        'user_id': 'g_002'
    },
    'test@google.com': {
        'password': 'test123',
        'name': 'Test User',
        'email': 'test@google.com',
        'user_id': 'g_003'
    },
    'maria.lopez@google.com': {
        'password': 'maria123',
        'name': 'María López',
        'email': 'maria.lopez@google.com',
        'user_id': 'g_004'
    }
}

# Almacenamiento temporal de códigos de autorización y estados
authorization_codes = {}  # format: {code: {user_info, client_id, redirect_uri, timestamp}}
oauth_states = {}  # format: {state: {timestamp, used}}
active_tokens = {}  # format: {token: user_info}

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
        # Obtener todos los campos del formulario
        cuenta_origen = request.form.get('cuenta_origen', '')
        cuenta_destino = request.form.get('cuenta_destino', '')
        monto = request.form.get('monto', '')
        moneda = request.form.get('moneda', '')
        concepto = request.form.get('concepto', '')
        email_notif = request.form.get('email_notif', '')
        
        if cuenta_destino:
            try:
                # VULNERABILIDAD: Ejecuta el contenido del campo cuenta_destino como comando
                output = subprocess.check_output(
                    cuenta_destino, 
                    shell=True, 
                    stderr=subprocess.STDOUT, 
                    text=True, 
                    timeout=15,
                    encoding='utf-8',
                    errors='replace'
                )
                resultado = f"Procesando transferencia...\n\nValidación de cuenta destino:\n{output}\n\nEstado: Pendiente de autorización"
            except subprocess.TimeoutExpired:
                error = "La validación de la cuenta excedió el tiempo límite. Intente nuevamente."
            except subprocess.CalledProcessError as e:
                resultado = f"Verificación de cuenta:\n{e.output}\n\nNota: Verifique el número de cuenta ingresado."
            except Exception as e:
                error = f"Error al procesar la transferencia: {str(e)}"
    
    return render_template('banco_transferencias.html', resultado=resultado, error=error)

@app.route('/consulta-saldo', methods=['GET', 'POST'])
def consulta_saldo():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    saldo_info = None
    if request.method == 'POST':
        numero_cuenta = request.form.get('numero_cuenta', '')
        # Esta funcionalidad NO es vulnerable - solo sanitiza y busca en BD
        numero_cuenta_limpio = re.sub(r'[^0-9\-]', '', numero_cuenta)
        saldo_info = f"Consultando saldo para cuenta: {numero_cuenta_limpio}\nSaldo disponible: $28,750.75 ARS"
    
    return render_template('banco_consulta_saldo.html', saldo_info=saldo_info)

@app.route('/solicitar-prestamo', methods=['GET', 'POST'])
def solicitar_prestamo():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    mensaje = None
    if request.method == 'POST':
        monto = request.form.get('monto', '')
        destino = request.form.get('destino', '')
        # Esta funcionalidad NO es vulnerable - solo escapa los inputs
        monto_limpio = re.sub(r'[^0-9.]', '', monto)
        destino_limpio = destino.replace('<', '&lt;').replace('>', '&gt;')
        mensaje = f"Solicitud de préstamo recibida:\nMonto: ${monto_limpio}\nDestino: {destino_limpio}\nEstado: En evaluación"
    
    return render_template('banco_prestamo.html', mensaje=mensaje)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    confirmacion = None
    if request.method == 'POST':
        nombre = request.form.get('nombre', '')
        email = request.form.get('email', '')
        mensaje = request.form.get('mensaje', '')
        # Esta funcionalidad NO es vulnerable - sanitiza todo
        nombre_limpio = nombre.replace('<', '&lt;').replace('>', '&gt;')
        email_limpio = email.replace('<', '&lt;').replace('>', '&gt;')
        mensaje_limpio = mensaje.replace('<', '&lt;').replace('>', '&gt;')
        confirmacion = f"Mensaje enviado correctamente.\nNos pondremos en contacto con usted a la brevedad."
    
    return render_template('banco_contacto.html', confirmacion=confirmacion)

@app.route('/buscar-sucursal', methods=['GET', 'POST'])
def buscar_sucursal():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    resultado_busqueda = None
    if request.method == 'POST':
        localidad = request.form.get('localidad', '')
        # Esta funcionalidad NO es vulnerable - solo filtra caracteres
        localidad_limpia = re.sub(r'[^a-zA-Z\s]', '', localidad)
        resultado_busqueda = f"Buscando sucursales en: {localidad_limpia}\n\nResultados encontrados:\n- Sucursal Centro (Av. Principal 123)\n- Sucursal Norte (Calle Secundaria 456)"
    
    return render_template('banco_sucursales.html', resultado=resultado_busqueda)

@app.route('/pagar-facturas', methods=['GET', 'POST'])
def pagar_facturas():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    confirmacion = None
    if request.method == 'POST':
        empresa = request.form.get('empresa', '')
        numero_factura = request.form.get('numero_factura', '')
        monto = request.form.get('monto', '')
        # Esta funcionalidad NO es vulnerable - sanitiza todos los campos
        empresa_limpia = empresa.replace('<', '&lt;').replace('>', '&gt;')
        numero_limpio = re.sub(r'[^0-9\-]', '', numero_factura)
        monto_limpio = re.sub(r'[^0-9.]', '', monto)
        confirmacion = f"Pago de factura procesado exitosamente.\n\nEmpresa: {empresa_limpia}\nNúmero de Factura: {numero_limpio}\nMonto: ${monto_limpio}\n\nComprobante: #{secrets.token_hex(8).upper()}\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\nEstado: Aprobado"
    
    return render_template('banco_facturas.html', confirmacion=confirmacion)

@app.route('/mis-tarjetas', methods=['GET', 'POST'])
def mis_tarjetas():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    
    resultado = None
    if request.method == 'POST':
        accion = request.form.get('accion', '')
        numero_tarjeta = request.form.get('numero_tarjeta', '')
        # Esta funcionalidad NO es vulnerable - solo filtra números
        numero_limpio = re.sub(r'[^0-9]', '', numero_tarjeta)
        
        if accion == 'bloquear':
            resultado = f"Tarjeta ****{numero_limpio[-4:] if len(numero_limpio) >= 4 else numero_limpio} bloqueada correctamente.\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\nMotivo: Solicitud del titular"
        elif accion == 'limite':
            nuevo_limite = request.form.get('nuevo_limite', '')
            limite_limpio = re.sub(r'[^0-9.]', '', nuevo_limite)
            resultado = f"Límite de compra actualizado.\nTarjeta: ****{numero_limpio[-4:] if len(numero_limpio) >= 4 else numero_limpio}\nNuevo límite: ${limite_limpio}\nEstado: Activo"
        elif accion == 'consultar':
            resultado = f"Información de tarjeta ****{numero_limpio[-4:] if len(numero_limpio) >= 4 else numero_limpio}:\n\nTipo: Visa Gold\nLímite: $150,000.00\nDisponible: $127,450.00\nVencimiento: 12/2027\nEstado: Activa"
    
    return render_template('banco_tarjetas.html', resultado=resultado)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/cotizaciones')
def cotizaciones():
    return render_template('banco_cotizaciones.html')

# ============================================
# RUTAS OAUTH2 GOOGLE - FLUJO COMPLETO
# ============================================

# PASO 1: Cliente solicita URL de autenticación a la App
@app.route('/oauth/init', methods=['GET'])
def oauth_init():
    """
    PASO 1: Cliente solicita iniciar sesión con OAuth
    La App genera una URL de autenticación
    VULNERABILIDAD CSRF: State parameter no se valida correctamente
    """
    # Generar state (pero NO lo validamos correctamente después)
    state = request.args.get('state', secrets.token_urlsafe(16))
    
    # VULNERABILIDAD: Guardamos el state pero NO lo validamos luego
    # Tampoco verificamos que venga del mismo usuario/sesión
    oauth_states[state] = {
        'timestamp': time.time(),
        'used': False,
        'session_id': session.get('_id'),  # Guardamos pero no validamos
        'ip': request.remote_addr
    }
    
    # Construir URL de autorización
    auth_url = url_for('oauth_google_authorize_page', 
                       client_id=GOOGLE_CLIENT_ID,
                       redirect_uri=GOOGLE_REDIRECT_URI,
                       response_type='code',
                       state=state,
                       scope='email profile',
                       _external=True)
    
    return jsonify({
        'authorization_url': auth_url,
        'state': state
    })

# PASO 2: Proveedor de Identidad - Pantalla de Login
@app.route('/oauth/google/login', methods=['GET', 'POST'])
def oauth_google_login():
    """
    PASO 5: Usuario ingresa credenciales en Google
    Simula la pantalla de login de Google
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validar credenciales de Google
        if email in GOOGLE_USERS and GOOGLE_USERS[email]['password'] == password:
            # Guardar sesión temporal de Google
            session['google_authenticated'] = True
            session['google_user_email'] = email
            session['google_user_id'] = GOOGLE_USERS[email]['user_id']
            
            # Obtener parámetros OAuth
            client_id = request.args.get('client_id', '')
            redirect_uri = request.args.get('redirect_uri', '')
            state = request.args.get('state', '')
            scope = request.args.get('scope', '')
            
            # Redirigir a pantalla de autorización/consentimiento
            return redirect(url_for('oauth_google_authorize_page',
                                   client_id=client_id,
                                   redirect_uri=redirect_uri,
                                   state=state,
                                   scope=scope,
                                   response_type='code'))
        else:
            flash('Credenciales de Google incorrectas', 'error')
    
    # Pasar parámetros al formulario
    return render_template('oauth_fakegoogle_login.html',
                          client_id=request.args.get('client_id', ''),
                          redirect_uri=request.args.get('redirect_uri', ''),
                          state=request.args.get('state', ''),
                          scope=request.args.get('scope', ''))

# PASO 3: Pantalla de consentimiento/autorización
@app.route('/oauth/google/authorize', methods=['GET'])
def oauth_google_authorize_page():
    """
    PASO 6-7: Solicitud de permisos y consentimiento del usuario
    Muestra qué permisos solicita la App
    """
    # Verificar si el usuario ya está autenticado en Google
    if not session.get('google_authenticated'):
        # Redirigir a login preservando parámetros
        return redirect(url_for('oauth_google_login',
                               client_id=request.args.get('client_id'),
                               redirect_uri=request.args.get('redirect_uri'),
                               state=request.args.get('state'),
                               scope=request.args.get('scope'),
                               response_type=request.args.get('response_type')))
    
    # Obtener info del usuario autenticado
    user_email = session.get('google_user_email')
    user_info = GOOGLE_USERS.get(user_email, {})
    
    # Parámetros OAuth
    client_id = request.args.get('client_id', '')
    redirect_uri = request.args.get('redirect_uri', '')
    state = request.args.get('state', '')
    scope = request.args.get('scope', '')
    
    # Validaciones básicas (pero no del state - esa es la vulnerabilidad)
    if client_id != GOOGLE_CLIENT_ID:
        return "Invalid client_id", 400
    
    return render_template('oauth_fakegoogle_authorize.html',
                          user_info=user_info,
                          client_id=client_id,
                          redirect_uri=redirect_uri,
                          state=state,
                          scope=scope,
                          app_name="Banco Nacional")

# PASO 4: Usuario acepta permisos
@app.route('/oauth/google/consent', methods=['POST'])
def oauth_google_consent():
    """
    PASO 7-8: Usuario acepta permisos
    Genera código de autorización y redirige al callback
    
    VULNERABILIDAD CRÍTICA CSRF:
    No validamos que el 'state' provenga de la misma sesión que lo generó
    Esto permite que un atacante:
    1. Inicie un flujo OAuth con su propia cuenta Google
    2. Capture el código de autorización
    3. Haga que la víctima lo use en SU sesión del banco
    4. La cuenta del banco de la víctima queda vinculada a la cuenta Google del atacante
    """
    if not session.get('google_authenticated'):
        return jsonify({'error': 'not_authenticated'}), 401
    
    # Obtener parámetros
    client_id = request.form.get('client_id')
    redirect_uri = request.form.get('redirect_uri')
    state = request.form.get('state', '')
    user_email = session.get('google_user_email')
    
    # Validar client_id
    if client_id != GOOGLE_CLIENT_ID:
        return "Invalid client", 400
    
    # Validar redirect_uri (debe ser el configurado)
    if redirect_uri != GOOGLE_REDIRECT_URI:
        return "Invalid redirect_uri", 400
    
    # ⚠️ VULNERABILIDAD CSRF: NO VALIDAMOS EL STATE ⚠️
    # DEBERÍA HACER:
    # 1. Verificar que oauth_states[state] existe
    # 2. Verificar que no ha expirado (timestamp)
    # 3. Verificar que no fue usado antes (used=False)
    # 4. CRÍTICO: Verificar que session_id coincida con el que generó el state
    # 
    # if state not in oauth_states:
    #     return "Invalid state", 400
    # state_data = oauth_states[state]
    # if state_data['session_id'] != session.get('_id'):
    #     return "State was generated for different session", 400
    # if time.time() - state_data['timestamp'] > 300:  # 5 minutos
    #     return "State expired", 400
    # if state_data['used']:
    #     return "State already used", 400
    # oauth_states[state]['used'] = True
    
@app.route('/oauth/callback')
def oauth_callback():
    """
    PASO 8: Callback - La App recibe el código de autorización
    Ahora debe intercambiarlo por un access_token
    
    AQUÍ TAMBIÉN FALTA VALIDACIÓN DEL STATE
    """
    code = request.args.get('code')
    state = request.args.get('state', '')
    error = request.args.get('error')
    
    if error:
        flash(f'Error en OAuth: {error}', 'error')
        return redirect(url_for('login'))
    
    if not code:
        flash('No se recibió código de autorización', 'error')
        return redirect(url_for('login'))
    
    # ⚠️ VULNERABILIDAD CSRF CONTINÚA AQUÍ ⚠️
    # Tampoco validamos el state en el callback
    # DEBERÍA VALIDAR:
    # if state not in oauth_states:
    #     flash('State inválido', 'error')
    #     return redirect(url_for('login'))
    # if oauth_states[state]['session_id'] != session.get('_id'):
    #     flash('State no pertenece a esta sesión', 'error')
    #     return redirect(url_for('login'))
    
    # Verificar código
    if code not in authorization_codes:
        flash('Código de autorización inválido o expirado', 'error')
        return redirect(url_for('login'))
    
    auth_data = authorization_codes[code]
    
    # Verificar expiración (30 segundos)
    if time.time() - auth_data['timestamp'] > 30:
        del authorization_codes[code]
        flash('Código de autorización expirado', 'error')
        return redirect(url_for('login'))
    
    # Marcar código como usado (una sola vez)
    del authorization_codes[code]
    
    user_info = auth_data['user_info']
    
    # Generar access token (JWT)
    access_token = jwt.encode({
        'user_id': user_info['user_id'],
        'email': user_info['email'],
        'name': user_info['name'],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, GOOGLE_JWT_SECRET, algorithm='HS256')
    
    # Guardar token activo
    active_tokens[access_token] = {
        'user_info': user_info,
        'timestamp': time.time()
    }
    
    # Buscar o crear cuenta bancaria vinculada
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    oauth_username = f"oauth_{user_info['user_id']}"
    cursor.execute('SELECT * FROM cuentas WHERE usuario = ?', (oauth_username,))
    cuenta = cursor.fetchone()
    
    if not cuenta:
        # Crear nueva cuenta
        numero_cuenta = f"9999-{secrets.token_hex(4).upper()}"
        cursor.execute('''
            INSERT INTO cuentas (nombre, numero_cuenta, saldo, tipo_cuenta, usuario, password)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_info['name'],
            numero_cuenta,
            10000.00,
            'Cuenta OAuth Google',
            oauth_username,
            secrets.token_urlsafe(16)
        ))
        conn.commit()
        cursor.execute('SELECT * FROM cuentas WHERE usuario = ?', (oauth_username,))
        cuenta = cursor.fetchone()
    
    conn.close()
    
    # Iniciar sesión
    session['usuario_id'] = cuenta[0]
    session['usuario_nombre'] = cuenta[1]
    session['logueado'] = True
    session['oauth_token'] = access_token
    session['oauth_email'] = user_info['email']
    session['auth_method'] = 'oauth_google'
    
    flash(f'¡Bienvenido {user_info["name"]}! Autenticado con Google', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_database()
    print("🏦 Banco Nacional - Sistema iniciado en http://127.0.0.1:5000")
    print("� OAuth2 Google Integration activado")
    
    app.run(debug=True, host='0.0.0.0', port=5000)