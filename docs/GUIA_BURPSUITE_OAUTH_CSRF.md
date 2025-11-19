# 🔥 Guía Paso a Paso: Explotación OAuth2 CSRF con Burp Suite

## 📋 Tabla de Contenidos
1. [Preparación del Entorno](#preparación)
2. [Configuración de Burp Suite](#configuración-burp)
3. [Fase 1: Atacante Inicia el Flujo OAuth](#fase-1)
4. [Fase 2: Captura del State con Burp](#fase-2)
5. [Fase 3: La Víctima Completa el Ataque](#fase-3)
6. [Resultado Final](#resultado)
7. [Análisis Técnico de la Vulnerabilidad](#análisis-técnico)
8. [Mitigación](#mitigación)

---

## 🛠️ Preparación del Entorno {#preparación}

### Requisitos Previos

✅ **Servidor corriendo:**
```bash
# Verificar que el servidor está activo
# En tu terminal PowerShell:
cd C:\Users\shado\OneDrive\Escritorio\TPI-SDS\TPI-SDS
.\INICIAR.bat
```

✅ **Burp Suite instalado y configurado**

✅ **Dos navegadores/ventanas:**
- **Navegador 1:** Con proxy de Burp (será el atacante)
- **Navegador 2:** Modo Incógnito SIN proxy (será la víctima)

✅ **Credenciales de prueba:**

| Rol | Email Google | Password | Descripción |
|-----|-------------|----------|-------------|
| **ATACANTE** | `test@google.com` | `test123` | Tu cuenta (controlada por ti) |
| **VÍCTIMA** | `maria.lopez@google.com` | `maria123` | Cuenta objetivo (alta privilegios) |

---

## ⚙️ Configuración de Burp Suite {#configuración-burp}

### Paso 1: Iniciar Burp Suite

1. **Abre Burp Suite Community Edition**
2. Crea un proyecto temporal: `New temporary project` → `Next`
3. Usa configuración por defecto: `Use Burp defaults` → `Start Burp`

### Paso 2: Configurar el Proxy

1. Ve a la pestaña **Proxy** → **Options** (o **Proxy Settings**)
2. Verifica que el proxy esté escuchando en:
   - **IP:** `127.0.0.1`
   - **Puerto:** `5500` (o el que prefieras, por defecto es 8080)
   - **Running:** ✅ Activado

📝 **NOTA:** Puedes usar cualquier puerto disponible. En este ejemplo usaremos `5500`.

### Paso 3: Configurar el Navegador (Atacante)

**Opción A: Usar Burp Browser (Recomendado)**
1. En Burp, ve a **Proxy** → **Intercept**
2. Click en `Open Browser`
3. Burp abrirá Chromium pre-configurado

**Opción B: Configurar tu navegador manualmente**
1. Abre **Firefox** o **Chrome**
2. Configuración de Proxy:
   - **HTTP Proxy:** `127.0.0.1`
   - **Puerto:** `5500`
   - **SSL Proxy:** `127.0.0.1`
   - **Puerto:** `5500`
3. Guarda la configuración

### Paso 4: Instalar Certificado de Burp (Solo primera vez)

1. Con el proxy configurado, visita: `http://burpsuite`
2. Click en `CA Certificate` (arriba a la derecha)
3. Guarda el certificado como `cacert.der`
4. Instálalo en tu navegador:
   - **Firefox:** Configuración → Privacidad → Certificados → Ver Certificados → Importar
   - **Chrome:** Configuración → Privacidad → Seguridad → Administrar certificados → Importar

### Paso 5: Verificar que Funciona

1. En Burp: **Proxy** → **Intercept** → `Intercept is on`
2. En el navegador con proxy: visita `http://127.0.0.1:5000`
3. **DEBERÍAS VER** la petición interceptada en Burp
4. Click en `Forward` para dejar pasar la petición
5. La página del banco debería cargar

---

## 🎯 Fase 1: Atacante Inicia el Flujo OAuth {#fase-1}

### Objetivo
Como atacante, vas a iniciar un flujo OAuth con **TU cuenta Google** (`test@google.com`) y capturar el parámetro `state` que se genera.

### Paso 1.1: Activar Intercept en Burp

1. En Burp Suite: **Proxy** → **Intercept** → Click en `Intercept is off` para activarlo
2. Debería decir: `Intercept is on` (fondo naranja)

### Paso 1.2: Iniciar el Flujo OAuth

🚨 **IMPORTANTE:** NO uses `/oauth/init`. El flujo correcto es diferente.

1. En el **navegador con proxy de Burp** (navegador del atacante)
2. Ve a la página de login del banco: `http://127.0.0.1:5000/login`
3. Haz scroll hacia abajo hasta encontrar el botón **"Iniciar sesión con Google"**
4. **NO HAGAS CLICK AÚN** - Primero activa el intercept en Burp

### Paso 1.3: Hacer Click en "Iniciar sesión con Google"

Con el intercept activado en Burp:

1. Haz click en el botón **"Iniciar sesión con Google"**
2. Burp interceptará un redirect

**DEBERÍAS VER** en Burp:

```http
GET /oauth/google/login?redirect_uri=http://127.0.0.1:5000/oauth/google/callback&client_id=banco-app-123456 HTTP/1.1
Host: 127.0.0.1:5000
...
```

**Acción:** Click en `Forward`

### Paso 1.4: Interceptar la Petición de Autorización

Burp interceptará la siguiente petición que es la MÁS IMPORTANTE:

```http
GET /oauth/google/authorize?client_id=banco-app-123456&redirect_uri=http://127.0.0.1:5000/oauth/google/callback&state=&scope=&response_type=code HTTP/1.1
Host: 127.0.0.1:5000
Cache-Control: max-age=0
Accept-Language: es-419,es;q=0.9
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...
Accept: text/html,application/xhtml+xml,application/xml;q=0.9...
Referer: http://127.0.0.1:5000/oauth/google/login?redirect_uri=http://127.0.0.1:5000/oauth/google/callback&client_id=banco-app-123456
Cookie: session=.eJyrVkrPz0_PSY1PLC3JSM0ryUxOLElNUbIqKSpN1YHJlRanFsWn5iZm5ihZKZWkFpc4QCT0kvNzlVBVZQL1KqXHGxgYK9UCAE9qIV4...
Connection: keep-alive
```

🚨 **MOMENTO CRÍTICO - MODIFICAR EL STATE**

📝 **OBSERVA:** El parámetro `state=` está **VACÍO** en la URL. Esto es PERFECTO para el ataque.

### Paso 1.5: Generar tu Propio State

Necesitas generar un `state` personalizado que identificará TU sesión de atacante.

**Opción 1: State Simple (para pruebas)**
```
state=ATACANTE123
```

**Opción 2: State Realista (más convincente)**
```
state=abc123XYZ789_atacante
```

### Paso 1.6: 🔧 MODIFICAR LA PETICIÓN EN BURP

En Burp Suite, **EDITA** la petición interceptada:

**ANTES (como la capturaste):**
```http
GET /oauth/google/authorize?client_id=banco-app-123456&redirect_uri=http://127.0.0.1:5000/oauth/google/callback&state=&scope=&response_type=code HTTP/1.1
```

**DESPUÉS (modificado por ti):**
```http
GET /oauth/google/authorize?client_id=banco-app-123456&redirect_uri=http://127.0.0.1:5000/oauth/callback&state=ATACANTE123&scope=email+profile&response_type=code HTTP/1.1
```

📝 **Cambios realizados:**
1. `redirect_uri=...oauth/google/callback` → `redirect_uri=...oauth/callback` ⚠️ **CRÍTICO: quitar "/google"**
2. `state=` → `state=ATACANTE123` (tu token único)
3. `scope=` → `scope=email+profile` (permisos necesarios)

🚨 **MUY IMPORTANTE:** El `redirect_uri` debe ser `/oauth/callback` (SIN "/google"), de lo contrario obtendrás un error 404.

### Paso 1.7: Enviar la Petición Modificada

1. Después de modificar la URL en Burp
2. Click derecho en la petición
3. Selecciona `Forward` o presiona el botón `Forward`
4. La petición modificada se enviará al servidor

**IMPORTANTE:** Burp seguirá interceptando. Haz `Forward` a todas las siguientes peticiones hasta llegar al login

⚠️ **NOTA:** Después de hacer login, Burp te mostrará la pantalla de autorización, pero **NO sigas haciendo Forward**. Ve directo al Paso 2.3.

---

## 🔍 Fase 2: Captura del State con Burp {#fase-2}

### Paso 2.1: Login como Atacante

1. Después de hacer `Forward` a varias peticiones, llegarás a la **pantalla de login de FakeGoogle**
2. Ingresa TUS credenciales de atacante:
   - **Email:** `test@google.com`
   - **Contraseña:** `test123`
   - Click en `Iniciar Sesión`

3. Burp interceptará la petición POST:

```http
POST /oauth/google/login HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded

email=test%40google.com&password=test123&client_id=banco-app-123456&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Foauth%2Fcallback&state=ATACANTE123&scope=email+profile
```

📝 **CONFIRMA QUE EL STATE ESTÁ AHÍ:** Deberías ver `state=ATACANTE123` (o el que pusiste) en el POST

**Acción:** Click en `Forward` varias veces **SOLO hasta que veas la pantalla de autorización**

⚠️ **DETENTE AQUÍ:** 
- Cuando veas la pantalla con botones "Permitir" y "Cancelar"
- **DESACTIVA Burp Intercept** (click en "Intercept is on" → debe quedar "Intercept is off")
- Si sigues haciendo Forward después de esto, completarás el OAuth y te loguearás
- **Eso NO es el ataque CSRF** - el ataque requiere que la VÍCTIMA complete el flujo, no tú

### Paso 2.2: Pantalla de Autorización/Consentimiento

Deberías ver una pantalla que dice:

```
Banco Nacional quiere acceder a:
✓ Tu información de perfil
✓ Tu email

Usuario: Test User (test@google.com)

[Permitir] [Cancelar]
```

### Paso 2.3: 🚨 MOMENTO CRÍTICO - NO PRESIONES PERMITIR AÚN

**IMPORTANTE:** 
- ❌ **NO presiones "Permitir" todavía**
- ❌ **NO completes el flujo OAuth**
- ⚠️ **DESACTIVA Burp Intercept AHORA** (click en "Intercept is on" para apagarlo)

🔴 **PROBLEMA COMÚN:** Si seguiste haciendo `Forward` en Burp después del login, probablemente:
1. Burp interceptó automáticamente cuando presionaste "Permitir" sin que te dieras cuenta
2. Hiciste `Forward` y completó el flujo OAuth
3. Te logueaste al dashboard del banco

Si esto pasó, significa que completaste el flujo como ATACANTE. **Esto NO es el ataque CSRF**. Necesitas empezar de nuevo.

### 🔄 Si te logueaste al dashboard - REINICIAR

Si llegaste al dashboard (`http://127.0.0.1:5000/dashboard`):

1. **Cierra sesión:** Ve a `http://127.0.0.1:5000/logout`
2. **Cierra el navegador completamente**
3. **Vuelve al Paso 1.1** y esta vez:
   - En el Paso 2.2 (pantalla de autorización)
   - **DESACTIVA Burp Intercept** (botón que dice "Intercept is on" → click → "Intercept is off")
   - **NO presiones "Permitir"**
   - **Solo copia la URL** de la barra de direcciones

### Paso 2.4: Copiar la URL de Autorización Completa

⚠️ **ANTES DE ESTE PASO:** Asegúrate que:
- ✅ Estás en la pantalla de autorización (con botones "Permitir" y "Cancelar")
- ✅ Burp Intercept está **DESACTIVADO** ("Intercept is off")
- ✅ **NO has presionado "Permitir"**
- ✅ **NO estás en el dashboard del banco**

Si ya estás en el dashboard, ve al paso "🔄 Si te logueaste al dashboard - REINICIAR" arriba.

1. En la barra de direcciones del navegador, copia la **URL COMPLETA** actual
2. Debería ser algo como:

```
http://127.0.0.1:5000/oauth/google/authorize?client_id=banco-app-123456&redirect_uri=http://127.0.0.1:5000/oauth/callback&state=ATACANTE123&scope=email+profile&response_type=code
```

3. **VERIFICA:** 
   - ✅ `state=ATACANTE123` (tu state personalizado)
   - ✅ `redirect_uri=...oauth/callback` (SIN "/google")
   - ✅ `scope=email+profile` (con permisos)
4. **GUARDA ESTA URL** en un bloc de notas - La usarás en la Fase 3

**Ejemplo de URL que debes guardar:**
```
http://127.0.0.1:5000/oauth/google/authorize?client_id=banco-app-123456&redirect_uri=http://127.0.0.1:5000/oauth/callback&state=ATACANTE123&scope=email+profile&response_type=code
```

⚠️ **NOTA:** Si tu URL tiene `redirect_uri=...oauth/google/callback`, bórrala y vuelve a empezar desde el Paso 1.6, modificando correctamente el redirect_uri en Burp.

### Paso 2.5: Analizar el State en Burp

1. En Burp, ve a **Proxy** → **HTTP history**
2. Busca las peticiones a `/oauth/google/authorize`
3. Click en una de ellas
4. En la pestaña **Request** → **Params**, deberías ver:

| Type | Name | Value |
|------|------|-------|
| URL | client_id | banco-app-123456 |
| URL | redirect_uri | http://127.0.0.1:5000/oauth/callback |
| URL | response_type | code |
| URL | state | ATACANTE123 |
| URL | scope | email profile |

📝 **CONFIRMA:** 
- El `state=ATACANTE123` es el que TÚ pusiste manualmente en Burp
- El `redirect_uri` es `/oauth/callback` (SIN "/google")

---

## 🎭 Fase 3: La Víctima Completa el Ataque {#fase-3}

### Objetivo
Ahora simularás a la víctima (María) que recibirá la URL maliciosa y completará el flujo OAuth **sin saber que está usando el `state` del atacante**.

### Paso 3.1: Preparar el Navegador de la Víctima

1. **Abre un navegador en MODO INCÓGNITO** (o un navegador diferente)
2. **NO configures el proxy** en este navegador
3. Este navegador representa a **María López** (la víctima)

### Paso 3.2: La Víctima Visita la URL Maliciosa

1. En el navegador de la víctima (sin proxy, modo incógnito)
2. **Pega la URL** que guardaste en el Paso 2.4:

```
http://127.0.0.1:5000/oauth/google/authorize?client_id=banco-app-123456&redirect_uri=http://127.0.0.1:5000/oauth/callback&state=ATACANTE123&scope=email+profile&response_type=code
```

3. **VERIFICA:** 
   - ✅ `state=ATACANTE123` (el state del atacante)
   - ✅ `redirect_uri=...oauth/callback` (SIN "/google")
4. Presiona `Enter`

⚠️ **ERROR COMÚN:** Si obtienes un error 404 después de hacer "Permitir", es porque la URL tiene `redirect_uri=...oauth/google/callback`. Debe ser solo `/oauth/callback`.

📧 **Contexto del ataque real:** 
En un escenario real, enviarías esta URL a la víctima por:
- Email de phishing
- Mensaje de WhatsApp
- Post en redes sociales
- Inyección en sitio web comprometido

### Paso 3.3: Login como Víctima

Deberías ver la pantalla de login de FakeGoogle.

**Ingresa las credenciales de la VÍCTIMA:**
- **Email:** `maria.lopez@google.com`
- **Contraseña:** `maria123`
- Click en `Iniciar Sesión`

### Paso 3.4: Pantalla de Autorización

Ahora verás:

```
Banco Nacional quiere acceder a:
✓ Tu información de perfil
✓ Tu email

Usuario: María López (maria.lopez@google.com)

[Permitir] [Cancelar]
```

⚠️ **NOTA:** La víctima ve SU nombre, no sabe que el `state` es del atacante

### Paso 3.5: 🎯 Completar la Autorización

**Acción:** Click en `Permitir`

### Paso 3.6: Capturar el Redirect en Burp (Opcional)

Si quieres ver qué pasa internamente:

1. **Vuelve al navegador del atacante** (el que tiene proxy de Burp)
2. Asegúrate que `Intercept is on` en Burp
3. Luego de que la víctima presiona "Permitir", Burp podría capturar el redirect

### Paso 3.7: Analizar la Petición POST en Burp

En el navegador de la víctima, después de presionar "Permitir", se hará un POST.

Si vuelves a Burp y revisas el **HTTP history**, verás:

```http
POST /oauth/google/consent HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded

client_id=banco-app-123456&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Foauth%2Fcallback&state=ATACANTE123
```

🔴 **VULNERABILIDAD EXPLOTADA:** 
- El `state=ATACANTE123` fue **generado por el ATACANTE** (test@google.com)
- Pero está siendo **usado por la VÍCTIMA** (maria.lopez@google.com)
- El servidor **NO valida** que el state pertenezca a la sesión de María
- **RESULTADO:** La cuenta bancaria de María se vinculará a la sesión del atacante

### Paso 3.8: Redirect al Callback

El servidor responderá con un redirect:

```http
HTTP/1.1 302 Found
Location: http://127.0.0.1:5000/oauth/callback?code=z_Kq7nesCnPw9DI43yc6Gg&state=ATACANTE123
```

### Paso 3.9: Capturar el Código de Autorización

1. Observa la URL final en el navegador de la víctima
2. Debería ser algo como:

```
http://127.0.0.1:5000/dashboard
```

3. **PERO** antes de llegar ahí, pasó por `/oauth/callback?code=XXXXXX&state=XXXXXX`

### Paso 3.10: Obtener el Código de Burp

Para ver el código de autorización:

**Método 1: HTTP History en Burp (Navegador del Atacante)**

Si activaste el proxy en el navegador del atacante durante la Fase 3:

1. En Burp: **Proxy** → **HTTP history**
2. Busca la petición GET a `/oauth/callback`
3. En la URL verás:

```
GET /oauth/callback?code=z_Kq7nesCnPw9DI43yc6Gg&state=ATACANTE123 HTTP/1.1
```

4. **Copia el valor de `code`** (ej: `z_Kq7nesCnPw9DI43yc6Gg`)

📝 **NOTA:** El state sigue siendo `ATACANTE123` confirmando el CSRF

**Método 2: Usar el navegador**
1. En el navegador de la víctima, presiona F12 (DevTools)
2. Ve a la pestaña **Network**
3. Busca la petición a `callback`
4. En la URL verás el `code`

**Método 3: Inspeccionar el Error 404 (Si olvidaste modificar redirect_uri)**

Si obtuviste un error 404 con la URL:
```
http://127.0.0.1:5000/oauth/google/callback?code=z_Kq7nesCnPw9DI43yc6Gg&state=ATACANTE123
```

**¡NO TE PREOCUPES!** Aunque es un 404, el **código sigue siendo válido**. Solo copia el `code` de la URL:
- `code=z_Kq7nesCnPw9DI43yc6Gg`

Luego puedes usarlo manualmente construyendo la URL correcta:
```
http://127.0.0.1:5000/oauth/callback?code=z_Kq7nesCnPw9DI43yc6Gg&state=ATACANTE123
```

O simplemente **reinicia el ataque** desde el Paso 1.6, modificando correctamente el `redirect_uri` en Burp.

---

## 🎉 Resultado Final {#resultado}

### ¿Qué Pasó?

1. ✅ El **atacante** inició un flujo OAuth desde la página de login del banco
2. ✅ El atacante **modificó manualmente** el parámetro `state=` vacío en Burp, añadiendo `state=ATACANTE123`
3. ✅ El atacante hizo login con su cuenta (`test@google.com`) usando ese state modificado
4. ✅ El atacante capturó la URL completa con `state=ATACANTE123` desde la pantalla de autorización
5. ✅ La **víctima** (`maria.lopez@google.com`) abrió esa URL maliciosa en su navegador
6. ✅ La víctima hizo login con **su cuenta de Google** (no la del atacante)
7. ✅ La víctima autorizó la aplicación, pensando que era legítimo
8. ✅ El servidor **NO validó** que el `state=ATACANTE123` perteneciera a la sesión de María
9. ✅ La cuenta bancaria de **María** quedó vinculada al `state` controlado por el **atacante**
10. ✅ El atacante puede ahora acceder a la cuenta bancaria de María

### Comprobación del Ataque

1. **En el navegador del atacante** (con proxy):
   - Ve a: `http://127.0.0.1:5000/dashboard`
   - Deberías ver el dashboard del banco con la cuenta de María López

2. **Verificar la vinculación:**
   - En la sesión del atacante, ahora tienes acceso a la cuenta bancaria que se creó/vinculó con la cuenta Google de María
   - El atacante puede realizar operaciones en nombre de María

---

## 🔬 Análisis Técnico de la Vulnerabilidad {#análisis-técnico}

### ¿Por Qué Funciona Este Ataque?

El ataque funciona porque:

1. **El parámetro `state` viene VACÍO** del servidor: `state=&scope=`
2. **Burp Suite permite modificar** la petición antes de enviarla
3. **El atacante inyecta su propio state:** `state=ATACANTE123`
4. **El servidor NO valida** que ese state le pertenezca a nadie
5. **La víctima usa el state del atacante** sin saberlo
6. **El servidor acepta cualquier state** y vincula la cuenta

### ¿Dónde Está el Bug?

**Archivo:** `app_banco.py`

**Línea ~450-480:** En la función `oauth_callback()`

```python
@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state', '')
    
    # ❌ VULNERABILIDAD: NO SE VALIDA EL STATE
    # El código debería validar:
    # 1. Que el state existe en oauth_states
    # 2. Que el state pertenece a la MISMA SESIÓN del usuario actual
    # 3. Que el state no ha expirado
    # 4. Que el state no ha sido usado antes
    
    # ❌ CÓDIGO VULNERABLE (actual):
    # No hay validación de state
    
    # ✅ CÓDIGO SEGURO (debería ser):
    # if state not in oauth_states:
    #     return "Invalid state - CSRF detected", 403
    # 
    # state_data = oauth_states[state]
    # if state_data['session_id'] != session.get('_id'):
    #     return "State from different session - CSRF ATTACK", 403
    # 
    # if time.time() - state_data['timestamp'] > 300:
    #     return "State expired", 403
    # 
    # if state_data['used']:
    #     return "State already used", 403
    # 
    # oauth_states[state]['used'] = True
    
    # El código continúa sin validar el state...
```

### Flujo del Ataque - Diagrama

```
┌──────────────┐                    ┌──────────────┐                    ┌──────────────┐
│  ATACANTE    │                    │  SERVIDOR    │                    │   VÍCTIMA    │
│(test@google) │                    │    BANCO     │                    │(maria.lopez) │
└──────┬───────┘                    └──────┬───────┘                    └──────┬───────┘
       │                                   │                                   │
       │ 1. Click "Login con Google"       │                                   │
       │ ────────────────────────────────> │                                   │
       │                                   │                                   │
       │ 2. Redirect a /oauth/authorize    │                                   │
       │    ?state=&scope= (VACÍO!)        │                                   │
       │ <──────────────────────────────── │                                   │
       │                                   │                                   │
       │ 3. BURP INTERCEPTA petición       │                                   │
       │    🔧 MODIFICA: state=ATACANTE123 │                                   │
       │ ────────────────────────────────> │                                   │
       │                                   │                                   │
       │ 4. Login: test@google.com         │                                   │
       │ ────────────────────────────────> │                                   │
       │                                   │                                   │
       │ 5. Pantalla autorización          │                                   │
       │ <──────────────────────────────── │                                   │
       │    (URL tiene state=ATACANTE123)  │                                   │
       │                                   │                                   │
       │ ❌ NO PRESIONA "Permitir"         │                                   │
       │ 📋 COPIA URL COMPLETA             │                                   │
       │                                   │                                   │
       │ 6. Envía URL a víctima            │                                   │
       │    (state=ATACANTE123 incluido)   │                                   │
       │ ────────────────────────────────────────────────────────────────────> │
       │    (Por email/WhatsApp/phishing)  │                                   │
       │                                   │                                   │
       │                                   │ 7. Víctima abre URL maliciosa     │
       │                                   │    ?state=ATACANTE123             │
       │                                   │ <──────────────────────────────── │
       │                                   │                                   │
       │                                   │ 8. Login: maria.lopez@google.com  │
       │                                   │ <──────────────────────────────── │
       │                                   │                                   │
       │                                   │ 9. Presiona "Permitir"            │
       │                                   │ <──────────────────────────────── │
       │                                   │                                   │
       │                                   │ ❌ VULNERABILIDAD CRÍTICA:        │
       │                                   │    NO valida que ATACANTE123      │
       │                                   │    pertenezca a María             │
       │                                   │    ✅ Acepta CUALQUIER state      │
       │                                   │                                   │
       │                                   │ 10. Genera código con             │
       │                                   │     state=ATACANTE123             │
       │                                   │ ────────────────────────────────> │
       │                                   │                                   │
       │                                   │ 11. Callback ejecutado            │
       │                                   │     Cuenta de María vinculada     │
       │                                   │     a state del atacante          │
       │                                   │                                   │
       │ 12. Atacante accede a /dashboard  │                                   │
       │     Ve la cuenta de María         │                                   │
       │ <──────────────────────────────── │                                   │
       └───────────────────────────────────┴───────────────────────────────────┘
```

### ¿Por Qué es Crítico?

| Aspecto | Detalle |
|---------|---------|
| **Severidad** | 🔴 Crítica (CVSS 9.1) |
| **Tipo de Ataque** | CSRF (Cross-Site Request Forgery) via OAuth |
| **Impacto** | Secuestro de cuenta, acceso no autorizado |
| **Explotabilidad** | Alta - Solo requiere que la víctima haga clic en un link |
| **Visibilidad** | Baja - La víctima no se da cuenta del ataque |
| **Persistencia** | Alta - El vínculo queda permanente |

### Escenarios de Ataque Real

**Escenario 1: Phishing Dirigido**
```
De: admin@banco-nacional.com (spoofed)
Para: maria.lopez@empresa.com
Asunto: Actualización de Seguridad Requerida

Estimada María,

Por motivos de seguridad, necesitamos que revincules tu cuenta de Google.
Por favor haz clic aquí: http://127.0.0.1:5000/oauth/google/authorize?state=ABC123...

Gracias,
Departamento de Seguridad
```

**Escenario 2: Inyección en Sitio Confiable**
- Atacante compromete un foro/blog donde la víctima participa
- Inyecta un iframe invisible con la URL maliciosa
- Si la víctima ya tiene sesión en Google, el ataque es automático

**Escenario 3: Ataque de Ingeniería Social**
- Atacante se hace pasar por soporte técnico
- "Necesito que abras este link para verificar tu cuenta"
- La víctima confía porque el link es del dominio oficial del banco

---

## 🛡️ Mitigación {#mitigación}

### Implementación Correcta del State

```python
import secrets
import time

# Al generar el state
@app.route('/oauth/init')
def oauth_init():
    # 1. Generar state criptográficamente seguro
    state = secrets.token_urlsafe(32)
    
    # 2. Guardar con metadatos de la sesión
    oauth_states[state] = {
        'timestamp': time.time(),
        'session_id': session.get('_id'),  # ID único de la sesión
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'used': False,
        'expires': time.time() + 300  # 5 minutos
    }
    
    return jsonify({'authorization_url': auth_url, 'state': state})

# Al validar en el callback
@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    # 1. Verificar que el state existe
    if not state or state not in oauth_states:
        abort(403, "Invalid state parameter - CSRF attack detected")
    
    state_data = oauth_states[state]
    
    # 2. Verificar que pertenece a la MISMA sesión
    if state_data['session_id'] != session.get('_id'):
        abort(403, "State belongs to different session - CSRF ATTACK")
    
    # 3. Verificar que no ha expirado (5 minutos)
    if time.time() > state_data['expires']:
        abort(403, "State expired")
    
    # 4. Verificar que no ha sido usado
    if state_data['used']:
        abort(403, "State already used")
    
    # 5. Marcar como usado y eliminar
    oauth_states[state]['used'] = True
    del oauth_states[state]  # Limpiar después de usar
    
    # Continuar con el flujo OAuth...
```

### Checklist de Seguridad OAuth2

| ✅ | Control de Seguridad |
|----|---------------------|
| ✅ | Generar `state` criptográficamente seguro (mínimo 128 bits) |
| ✅ | Vincular `state` a la sesión del usuario específico |
| ✅ | Validar `state` en el callback contra la sesión actual |
| ✅ | Expirar `state` después de 5-10 minutos |
| ✅ | Invalidar `state` después del primer uso |
| ✅ | Validar `redirect_uri` contra whitelist estricta |
| ✅ | Usar HTTPS en producción (previene MITM) |
| ✅ | Implementar rate limiting en endpoints OAuth |
| ✅ | Loguear intentos sospechosos de CSRF |
| ✅ | Implementar PKCE para clientes públicos |

### Defensas Adicionales

**1. PKCE (Proof Key for Code Exchange)**
```python
# Cliente genera code_verifier y code_challenge
code_verifier = secrets.token_urlsafe(64)
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode().rstrip('=')

# En authorize: envía code_challenge
# En callback: valida code_verifier contra code_challenge
```

**2. Nonce (Number Used Once)**
```python
# Adicional al state, incluir un nonce en el token JWT
nonce = secrets.token_urlsafe(16)
session['oauth_nonce'] = nonce

# Al recibir el token, validar que el nonce coincida
```

**3. Timeouts Agresivos**
```python
# State expira en 5 minutos (no 30 minutos)
STATE_EXPIRATION = 300  # 5 minutos

# Códigos de autorización expiran en 1 minuto (no 5)
CODE_EXPIRATION = 60  # 1 minuto
```

---

## 📸 Evidencias para tu Informe

### Captura 1: Generación del State
- Burp HTTP History: GET /oauth/init
- Mostrar JSON con `state` generado

### Captura 2: State en URL del Atacante
- Pantalla de autorización con `state=ABC123` en la URL
- Usuario: test@google.com (atacante)

### Captura 3: Víctima Usando el State del Atacante
- Misma URL con `state=ABC123`
- Pero ahora Usuario: maria.lopez@google.com (víctima)

### Captura 4: Código de Autorización en Callback
- Burp HTTP History: GET /oauth/callback?code=XXX&state=ABC123
- Mostrar que el state es el mismo

### Captura 5: Dashboard Comprometido
- Atacante logueado en el banco
- Mostrando datos de la víctima (María López)

---

## 🎓 Conceptos Clave

### ¿Qué es el State Parameter?

El parámetro `state` es un **token anti-CSRF** en OAuth2:

```
┌─────────────────────────────────────────────────────────┐
│ FLUJO OAUTH2 SEGURO (con state validado)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. Cliente genera: state = random_token()              │
│    - Guarda en sesión: session['state'] = state        │
│                                                         │
│ 2. Redirige a OAuth Provider con ?state=random_token   │
│                                                         │
│ 3. Usuario autoriza                                    │
│                                                         │
│ 4. Provider redirige a callback con ?code=X&state=Y    │
│                                                         │
│ 5. Cliente valida:                                     │
│    if state != session['state']:                       │
│        raise CSRFError("State mismatch!")              │
│                                                         │
│ 6. Solo si el state coincide, procesa el código        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### CSRF vs OAuth CSRF

| CSRF Tradicional | OAuth CSRF |
|-----------------|------------|
| Ejecuta acción no autorizada | Vincula cuenta no autorizada |
| Token CSRF en formularios | State parameter en OAuth |
| Víctima autenticada en sitio | Víctima autenticada en Google |
| Ej: Transferir dinero | Ej: Vincular cuenta bancaria |

### ¿Por Qué es Diferente de CSRF Normal?

En CSRF normal:
- Atacante fuerza una acción (transferir dinero, cambiar email)
- Víctima debe estar logueada en el sitio vulnerable

En OAuth CSRF:
- Atacante fuerza una **vinculación de cuenta**
- Víctima NO necesita estar logueada en el banco
- Víctima solo necesita estar logueada en Google
- **Más peligroso:** El atacante obtiene acceso persistente

---

## 🚀 Pruebas Adicionales

### Variante 1: Reutilización de State

```bash
# Captura el state en Burp
state=ABC123

# Intenta usar el mismo state en DOS navegadores diferentes
# Navegador 1: usa state=ABC123
# Navegador 2: usa state=ABC123 (mismo)

# ¿Funciona en ambos? ❌ No debería (pero probablemente sí)
```

### Variante 2: State Expirado

```bash
# 1. Genera un state
# 2. Espera 10 minutos
# 3. Intenta completar el flujo OAuth

# ¿Todavía funciona? ❌ No debería (debería expirar en 5min)
```

### Variante 3: State de Otro Usuario

```bash
# 1. Usuario A genera state=XXX
# 2. Usuario B captura ese state
# 3. Usuario B lo usa en SU flujo

# ¿B puede usar el state de A? ❌ No debería
```

---

## 📚 Referencias

- [OAuth 2.0 RFC 6749 - Section 10.12](https://tools.ietf.org/html/rfc6749#section-10.12)
- [OAuth 2.0 Threat Model (RFC 6819)](https://tools.ietf.org/html/rfc6819)
- [OWASP OAuth 2.0 Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html)
- [Burp Suite Documentation](https://portswigger.net/burp/documentation)

---

## ✅ Resumen Final

Has aprendido a:

1. ✅ Configurar Burp Suite para interceptar tráfico OAuth
2. ✅ Identificar el parámetro `state` en peticiones OAuth
3. ✅ Explotar la falta de validación del `state` (CSRF)
4. ✅ Vincular cuentas ajenas usando state hijacking
5. ✅ Entender el impacto real de esta vulnerabilidad
6. ✅ Implementar mitigaciones correctas

**Nivel de Dificultad:** 🔴🔴🔴⚪⚪ (Medio-Alto)
**Tiempo Estimado:** 30-45 minutos
**Herramientas:** Burp Suite, 2 navegadores

---

**⚠️ ADVERTENCIA LEGAL**

Esta guía es para **PROPÓSITOS EDUCATIVOS** únicamente en un entorno de laboratorio controlado.

❌ **NUNCA uses estas técnicas en:**
- Aplicaciones en producción
- Sistemas de terceros sin autorización
- Entornos que no controlas

✅ **SOLO usa en:**
- Este laboratorio local
- Tu propio entorno de pruebas
- Con autorización explícita por escrito

El uso no autorizado de estas técnicas puede ser **ILEGAL** y tener consecuencias legales graves.

---

**Desarrollado para fines educativos** | TPI-SDS 2024
