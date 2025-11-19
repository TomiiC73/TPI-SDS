from flask import Flask, render_template, request, jsonify
import hashlib

app = Flask(__name__)

# Hashes de verificación (MD5)
# Desafío RCE: MD5 de "RCE_COMPLETADO_2024"
HASH_RCE_CORRECTO = hashlib.md5("RCE_COMPLETADO_2024".encode()).hexdigest()  # 74b5ba78892e60262a87a80f3bb6440f

# Desafío OAuth: el estudiante debe obtener el CLIENT_SECRET
# Hash de verificación: MD5 del CLIENT_SECRET
HASH_OAUTH_CORRECTO = hashlib.md5("SECRET_SUPER_SECRETO_EXPUESTO_123".encode()).hexdigest()

@app.route('/')
def index():
    return render_template('enunciados_index.html')

@app.route('/desafio/rce')
def desafio_rce():
    return render_template('desafio_rce.html')

@app.route('/desafio/oauth')
def desafio_oauth():
    return render_template('desafio_oauth.html')

@app.route('/desafio/oauth/basico')
def desafio_oauth_basico():
    return render_template('desafio_oauth.html')

@app.route('/verificar/rce', methods=['POST'])
def verificar_rce():
    data = request.get_json()
    codigo = data.get('codigo', '').strip()
    
    # Verificar si el código es correcto
    # Aceptamos cualquier output de whoami en MD5
    if codigo.lower() == HASH_RCE_CORRECTO.lower() or codigo.lower() == hashlib.md5("whoami".encode()).hexdigest():
        return jsonify({
            'success': True,
            'mensaje': '¡Felicitaciones! Has completado el desafío RCE exitosamente.',
            'detalle': 'Lograste ejecutar comandos en el servidor del Banco Nacional. Has demostrado que la funcionalidad de transferencias es vulnerable a inyección de comandos (RCE).'
        })
    else:
        # Dar una pista si está cerca
        return jsonify({
            'success': False,
            'mensaje': 'Código incorrecto. Sigue intentando.',
            'pista': 'Debes ejecutar el comando "whoami" en el sistema y calcular el MD5 del resultado. Recuerda que la vulnerabilidad está en la sección de transferencias.'
        })

@app.route('/verificar/oauth', methods=['POST'])
def verificar_oauth():
    data = request.get_json()
    codigo = data.get('codigo', '').strip()
    tipo_vulnerabilidad = data.get('tipo', 'csrf')  # csrf, reuse, secret, redirect, disclosure
    
    # Verificaciones según el tipo de vulnerabilidad
    
    # OPCIÓN 1: CSRF - State parameter
    if tipo_vulnerabilidad == 'csrf':
        # Verificar si es un código de autorización válido (formato base64url)
        # Los códigos generados por secrets.token_urlsafe() tienen entre 16-32 caracteres
        if len(codigo) >= 16 and len(codigo) <= 50:
            # Verificar que no tenga caracteres inválidos
            import re
            if re.match(r'^[A-Za-z0-9_-]+$', codigo):
                return jsonify({
                    'success': True,
                    'mensaje': '🎉 ¡Felicitaciones! Has explotado la vulnerabilidad CSRF en OAuth2.',
                    'detalle': 'Demostraste que el parámetro state NO se valida correctamente, permitiendo ataques CSRF en el flujo OAuth2. Un atacante puede vincular cuentas ajenas manipulando el state.',
                    'codigo_capturado': codigo,
                    'vulnerabilidad': 'CWE-352: Cross-Site Request Forgery',
                    'cvss': '8.1 (High)',
                    'impacto': 'Account Linking Hijacking - Acceso no autorizado a información confidencial'
                })
    
    # OPCIÓN 2: Code Reuse
    elif tipo_vulnerabilidad == 'reuse':
        if len(codigo) > 30:  # Es un código de autorización
            return jsonify({
                'success': True,
                'mensaje': '¡Felicitaciones! Has explotado el Authorization Code Reuse.',
                'detalle': 'Demostraste que los códigos de autorización pueden reutilizarse múltiples veces para obtener nuevos tokens. Esto es una vulnerabilidad crítica según OAuth 2.0 Security Best Practices.'
            })
    
    # OPCIÓN 3: Client Secret (la más simple - para principiantes)
    elif tipo_vulnerabilidad == 'secret' or codigo == "SECRET_SUPER_SECRETO_EXPUESTO_123":
        if codigo == "SECRET_SUPER_SECRETO_EXPUESTO_123":
            return jsonify({
                'success': True,
                'mensaje': '¡Felicitaciones! Has encontrado el Client Secret expuesto.',
                'detalle': 'El CLIENT_SECRET estaba expuesto en endpoints públicos (/oauth/info). Esta credencial NUNCA debería ser accesible públicamente. Con ella, un atacante puede hacerse pasar por la aplicación legítima.'
            })
    
    # OPCIÓN 4: Redirect URI Manipulation
    elif tipo_vulnerabilidad == 'redirect':
        if len(codigo) > 30:  # Es un código capturado con redirect manipulado
            return jsonify({
                'success': True,
                'mensaje': '¡Felicitaciones! Has explotado Redirect URI Manipulation.',
                'detalle': 'Demostraste que el redirect_uri NO se valida contra una whitelist. Un atacante puede especificar su propia URL para recibir códigos de autorización.'
            })
    
    # OPCIÓN 5: Token Information Disclosure
    elif tipo_vulnerabilidad == 'disclosure':
        # Verificar si es un user_id válido (formato g_XXX)
        if codigo.startswith('g_'):
            return jsonify({
                'success': True,
                'mensaje': '¡Felicitaciones! Has identificado Information Disclosure.',
                'detalle': 'El endpoint /oauth/token expone información sensible del usuario (user_id, email) que NO debería incluirse en la respuesta. Solo debería retornar el access_token.'
            })
    
    # Fallback para verificación general
    if codigo == "SECRET_SUPER_SECRETO_EXPUESTO_123":
        return jsonify({
            'success': True,
            'mensaje': '¡Felicitaciones! Has completado el desafío OAuth2 básico.',
            'detalle': 'Encontraste el CLIENT_SECRET expuesto. Para desafíos avanzados, explora las vulnerabilidades del flujo OAuth2 con Burp Suite.'
        })
    
    # Si llegamos aquí, el código no es válido
    if len(codigo) == 0:
        return jsonify({
            'success': False,
            'mensaje': '❌ Por favor ingresa el código de autorización.',
            'pista': 'Debes completar el flujo OAuth con el state manipulado y capturar el código del callback.'
        })
    elif len(codigo) < 16:
        return jsonify({
            'success': False,
            'mensaje': '❌ El código parece ser muy corto.',
            'pista': 'El código de autorización debe ser el valor del parámetro "code" en la URL del callback. Ejemplo: /oauth/callback?code=CODIGO_AQUI&state=...'
        })
    else:
        return jsonify({
            'success': False,
            'mensaje': '❌ Código no válido. Verifica que sea un código de autorización real.',
            'pista': 'Sigue los pasos: 1) Interceptar tu flujo OAuth con Burp, 2) Modificar el state, 3) Hacer que María complete TU flujo, 4) Capturar el código del callback.',
            'ayuda_extra': 'Revisa la documentación completa en docs/GUIA_PRACTICA_OAUTH.md'
        })

@app.route('/ayuda/rce')
def ayuda_rce():
    return jsonify({
        'pistas': [
            'Paso 1: Inicia sesión en el Banco Nacional con las credenciales de Julián',
            'Paso 2: Explora la funcionalidad de "Transferencias"',
            'Paso 3: Intenta ingresar comandos del sistema en lugar de números de cuenta',
            'Paso 4: Ejecuta el comando "whoami" para obtener el usuario del sistema',
            'Paso 5: Calcula el MD5 del resultado y envíalo aquí para verificación'
        ]
    })

@app.route('/ayuda/oauth')
def ayuda_oauth():
    return jsonify({
        'pistas': [
            'Paso 1: Explora el sitio del Banco Nacional en busca de documentación',
            'Paso 2: Busca páginas relacionadas con OAuth, API o configuración',
            'Paso 3: La URL podría ser algo como /oauth/info o /oauth/docs',
            'Paso 4: Encuentra el CLIENT_SECRET expuesto',
            'Paso 5: Envía el CLIENT_SECRET aquí para verificación'
        ]
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🎯 SISTEMA DE DESAFÍOS - BANCO NACIONAL")
    print("=" * 70)
    print("")
    print("🌐 Página de Enunciados: http://127.0.0.1:5001")
    print("🏦 Banco Nacional (Target): http://127.0.0.1:5000")
    print("")
    print("📋 Desafíos disponibles:")
    print("   1. RCE (Remote Code Execution)")
    print("   2. OAuth2 (CSRF + Client Secret Exposed)")
    print("")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
