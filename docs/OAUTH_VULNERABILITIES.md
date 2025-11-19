# 🔓 Vulnerabilidades OAuth2 - FakeGoogle

## 📋 Resumen

Este proyecto implementa un sistema OAuth2 **intencionalmente vulnerable** para fines educativos. Simula la autenticación con Google pero contiene múltiples vulnerabilidades de seguridad para práctica ética.

---

## 🎯 Vulnerabilidades Implementadas

### 1. **State Parameter Missing/Manipulation (CSRF)** ⚠️

**Descripción:**
El parámetro `state` en OAuth2 es un token aleatorio que debe generarse por el cliente y validarse al recibir el callback. Esta aplicación NO valida correctamente el parámetro state, lo que permite ataques CSRF (Cross-Site Request Forgery).

**Ubicación en el código:**
- `app_banco.py` - Ruta `/oauth/fakegoogle/authorize` (línea ~175)
- `app_banco.py` - Ruta `/oauth/fakegoogle/callback` (línea ~215)

**Cómo funciona el ataque:**

1. El atacante inicia sesión con su propia cuenta FakeGoogle
2. El atacante inicia el flujo OAuth pero NO completa la autorización
3. El atacante obtiene la URL de autorización con SU state
4. El atacante engaña a la víctima para que visite esa URL
5. La víctima completa la autorización
6. La cuenta bancaria de la VÍCTIMA queda vinculada a la sesión del ATACANTE

**Ejemplo de explotación:**

```bash
# Paso 1: Atacante obtiene URL de autorización
http://127.0.0.1:5000/oauth/fakegoogle/authorize?
  redirect_uri=http://127.0.0.1:5000/oauth/fakegoogle/callback
  &state=ATACANTE_STATE_123
  &client_id=banco-app-123456

# Paso 2: Atacante envía esta URL a la víctima
# Paso 3: Víctima hace clic, inicia sesión con SU cuenta FakeGoogle
# Paso 4: Víctima autoriza la aplicación
# Paso 5: La cuenta bancaria de la víctima se vincula a la sesión del atacante
```

**Impacto:**
- El atacante puede acceder a la cuenta bancaria de la víctima
- El atacante puede realizar transacciones en nombre de la víctima
- La víctima no se da cuenta de que su cuenta fue comprometida

**Mitigación correcta:**
```python
# En la ruta de callback, SIEMPRE validar:
stored_state = session.get('oauth_state')
received_state = request.args.get('state')

if not stored_state or stored_state != received_state:
    abort(403, "Invalid state parameter - CSRF attack detected")
```

---

### 2. **Client Secret Expuesto en Frontend** 🔑

**Descripción:**
El `CLIENT_SECRET` de OAuth2 debe ser secreto y NUNCA exponerse públicamente. Esta aplicación expone el secret de múltiples formas:

1. **Hardcodeado en el código Python** (visible en GitHub)
2. **Expuesto en una página web pública** (`/oauth/info`)
3. **Incluido en JavaScript del frontend**

**Ubicación en el código:**
- `app_banco.py` - Variables globales (línea ~18-20)
- `templates/oauth_info.html` - Todo el archivo
- `templates/banco_login.html` - client_id en la URL

**Cómo funciona el ataque:**

Con el CLIENT_SECRET expuesto, un atacante puede:

1. **Hacer peticiones OAuth como si fuera la aplicación legítima**
2. **Obtener tokens de acceso sin autorización**
3. **Crear aplicaciones maliciosas que se hacen pasar por el Banco**

**Ejemplo de explotación:**

```bash
# Atacante hace petición directa al endpoint de tokens
curl -X POST http://127.0.0.1:5000/oauth/fakegoogle/token \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CODIGO_INTERCEPTADO",
    "client_id": "banco-app-123456",
    "client_secret": "SECRET_SUPER_SECRETO_EXPUESTO_123"
  }'

# Respuesta: Token válido que permite acceso a cuentas
```

**Dónde está expuesto:**

1. **En el código fuente:**
```python
FAKEGOOGLE_CLIENT_SECRET = "SECRET_SUPER_SECRETO_EXPUESTO_123"
```

2. **En la página web `/oauth/info`:**
```html
<div class="credential-value">SECRET_SUPER_SECRETO_EXPUESTO_123</div>
```

3. **En JavaScript del frontend:**
```javascript
const OAUTH_CONFIG = {
    client_id: 'banco-app-123456',
    client_secret: 'SECRET_SUPER_SECRETO_EXPUESTO_123',  // ¡VULNERABLE!
};
```

**Impacto:**
- Cualquiera puede obtener tokens de acceso
- Bypass completo del flujo OAuth
- Suplantación de identidad de la aplicación

**Mitigación correcta:**
```python
# CLIENT_SECRET debe:
# 1. Estar en variables de entorno
import os
CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET')

# 2. NUNCA enviarse al frontend
# 3. NUNCA estar en el código fuente
# 4. NUNCA exponerse públicamente
```

---

## 🛠️ Cómo Probar las Vulnerabilidades

### Prueba 1: CSRF en OAuth (State Missing)

**Escenario:** Atacante vincula cuenta de víctima

```bash
# Terminal 1 (Atacante)
# 1. Inicia flujo OAuth como atacante
http://127.0.0.1:5000/oauth/fakegoogle/login?redirect_uri=http://127.0.0.1:5000/oauth/fakegoogle/callback&client_id=banco-app-123456&state=ATACANTE123

# 2. Login con: hacker@fakegoogle.com / hacker123
# 3. NO completes la autorización
# 4. Copia la URL de la pantalla de autorización

# Terminal 2 (Víctima - otra navegador/incógnito)
# 1. Pega la URL que el atacante te envió
# 2. Login con: usuario@fakegoogle.com / fakegoogle123
# 3. Completa la autorización

# Resultado: La cuenta bancaria del usuario se vincula a la sesión del hacker
```

### Prueba 2: Client Secret Expuesto

**Escenario:** Obtener token sin autorización del usuario

```bash
# 1. Visita http://127.0.0.1:5000/oauth/info
# 2. Copia el CLIENT_SECRET expuesto
# 3. Obtén un código de autorización (completa flujo OAuth normal)
# 4. Usa curl para obtener token:

curl -X POST http://127.0.0.1:5000/oauth/fakegoogle/token \
  -H "Content-Type: application/json" \
  -d '{
    "code": "TU_CODIGO_AQUI",
    "client_id": "banco-app-123456",
    "client_secret": "SECRET_SUPER_SECRETO_EXPUESTO_123"
  }'
```

---

## 📊 Flujo OAuth2 Vulnerable

```
┌─────────┐                                      ┌──────────────┐
│ Usuario │                                      │ FakeGoogle   │
│ (Banco) │                                      │ OAuth Server │
└────┬────┘                                      └──────┬───────┘
     │                                                   │
     │ 1. Click "Login con FakeGoogle"                  │
     │ ─────────────────────────────────────────────>   │
     │                                                   │
     │ 2. Redirect a /oauth/fakegoogle/login            │
     │   (state NO validado ❌)                         │
     │ <─────────────────────────────────────────────   │
     │                                                   │
     │ 3. Usuario ingresa credenciales                  │
     │ ─────────────────────────────────────────────>   │
     │                                                   │
     │ 4. Pantalla de consentimiento                    │
     │   (state NO validado ❌)                         │
     │ <─────────────────────────────────────────────   │
     │                                                   │
     │ 5. Usuario acepta permisos                       │
     │ ─────────────────────────────────────────────>   │
     │                                                   │
     │ 6. Código de autorización generado               │
     │ <─────────────────────────────────────────────   │
     │                                                   │
     │ 7. Exchange code por token                       │
     │   (usando CLIENT_SECRET expuesto ❌)             │
     │ ─────────────────────────────────────────────>   │
     │                                                   │
     │ 8. Token JWT (firma no validada ❌)              │
     │ <─────────────────────────────────────────────   │
     │                                                   │
     │ 9. Acceso a cuenta bancaria                      │
     └──────────────────────────────────────────────────┘
```

---

## 🔐 Credenciales de Prueba

### Usuarios FakeGoogle:

| Email | Password | Rol | User ID |
|-------|----------|-----|---------|
| usuario@fakegoogle.com | fakegoogle123 | Usuario Normal | fg_001 |
| admin@fakegoogle.com | admin123 | Administrador | fg_002 |
| hacker@fakegoogle.com | hacker123 | Atacante | fg_666 |

### OAuth Credentials (EXPUESTOS):

```
CLIENT_ID:     banco-app-123456
CLIENT_SECRET: SECRET_SUPER_SECRETO_EXPUESTO_123
JWT_SECRET:    jwt_secret_debil
```

---

## 🌐 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/oauth/fakegoogle/login` | Pantalla de login de FakeGoogle |
| GET | `/oauth/fakegoogle/authorize` | Pantalla de autorización (consentimiento) |
| POST | `/oauth/fakegoogle/grant` | Otorgar permisos y generar código |
| GET | `/oauth/fakegoogle/callback` | Callback OAuth (vulnerable CSRF) |
| POST | `/oauth/fakegoogle/token` | Intercambiar código por token (API) |
| GET | `/oauth/info` | Información de credenciales EXPUESTAS |

---

## 🎓 Conceptos Clave de OAuth2

### ¿Qué es OAuth2?

OAuth2 es un protocolo de autorización que permite a aplicaciones de terceros obtener acceso limitado a un servicio HTTP, ya sea en nombre del propietario del recurso o permitiendo que la aplicación de terceros obtenga acceso en su propio nombre.

### Flujo Authorization Code (Usado aquí):

1. **Authorization Request:** Cliente redirige al usuario al servidor de autorización
2. **Authorization Grant:** Usuario autoriza y servidor devuelve código
3. **Access Token Request:** Cliente intercambia código por token
4. **Access Token Response:** Servidor devuelve token de acceso
5. **Protected Resource Access:** Cliente usa token para acceder a recursos

### Parámetros Importantes:

- **client_id:** Identificador público de la aplicación
- **client_secret:** Secreto que NO debe exponerse (vulnerable aquí)
- **redirect_uri:** URL a donde redirigir después de autorización
- **state:** Token aleatorio para prevenir CSRF (NO validado aquí)
- **code:** Código de autorización temporal
- **access_token:** Token para acceder a recursos protegidos

---

## ⚠️ ADVERTENCIA

Este código es **INTENCIONALMENTE VULNERABLE** y solo debe usarse en:

✅ Entornos de práctica local  
✅ Laboratorios de seguridad  
✅ Formación en ciberseguridad  
✅ Demostraciones educativas  

❌ **NUNCA usar en producción**  
❌ **NUNCA exponer a internet**  
❌ **NUNCA usar con datos reales**  

---

## 📚 Recursos Adicionales

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [OWASP OAuth 2.0 Security](https://owasp.org/www-community/vulnerabilities/OAuth_2.0)
- [OAuth 2.0 Threat Model](https://tools.ietf.org/html/rfc6819)

---

**Desarrollado para fines educativos** | Proyecto de Práctica de Vulnerabilidades
