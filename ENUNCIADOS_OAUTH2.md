# 🔐 ENUNCIADOS: VULNERABILIDADES OAUTH2

## 📋 Contexto del Desafío

El Banco Nacional implementó OAuth2 para permitir que los usuarios inicien sesión usando sus cuentas de Google. Sin embargo, la implementación tiene múltiples vulnerabilidades críticas que pueden ser explotadas mediante el análisis de peticiones HTTP con herramientas como Burp Suite.

---

## 🎯 **OPCIÓN 1: CSRF mediante State Parameter**

### Historia:
"El Atacante Silencioso"

María López, empleada de RR HH del Banco Nacional, tiene acceso privilegiado a información confidencial. Un atacante descubrió que el flujo OAuth2 del banco NO valida correctamente el parámetro `state`, lo que permite realizar ataques CSRF (Cross-Site Request Forgery).

### Objetivo:
Explotar la falta de validación del parámetro `state` para vincular la cuenta bancaria de María con TU cuenta de Google, obteniendo así acceso a su información privilegiada.

### Tarea:
1. Inicia el flujo OAuth2 normalmente con tu cuenta de Google
2. Intercepta las peticiones con Burp Suite
3. Identifica el parámetro `state` en las peticiones
4. Manipula el flujo para:
   - Iniciar una autorización con TU cuenta de Google
   - Capturar el código de autorización
   - Modificar el `state` parameter o reutilizarlo
   - Vincular la autorización a la sesión de otra víctima

### Verificación:
Obtén el código de autorización de otra cuenta y úsalo para vincular una sesión diferente. Calcula el MD5 del código de autorización exitoso.

---

## 🎯 **OPCIÓN 2: Authorization Code Reuse**

### Historia:
"El Código Reutilizable"

Durante una auditoría de seguridad, descubriste que el banco NO invalida los códigos de autorización después de su uso. Esto significa que un código puede ser reutilizado múltiples veces para obtener nuevos access tokens.

### Objetivo:
Demostrar que los códigos de autorización (authorization codes) pueden ser reutilizados para obtener múltiples access tokens.

### Tarea:
1. Completa un flujo OAuth2 normal y obtén un código de autorización
2. Intercambia el código por un access token usando `/oauth/token`
3. Intercepta la respuesta y guarda el access token
4. **Reutiliza el MISMO código** para obtener un segundo access token
5. Verifica que ambos tokens sean válidos

### Pistas:
- El código de autorización tiene formato: `xxxxxxxxxxxxxxxxxxxxx`
- La petición a `/oauth/token` debe incluir: `code`, `client_id`, `client_secret`, `grant_type`
- Burp Suite te permite reenviar peticiones HTTP
- El endpoint NO valida si el código ya fue usado

### Verificación:
Envía el código de autorización que pudiste reutilizar (el mismo código usado 2+ veces).

---

## 🎯 **OPCIÓN 3: Client Secret Leakage**

### Historia:
"El Secreto Expuesto"

Los desarrolladores del banco dejaron endpoints de debugging activos en producción que exponen información sensible de la configuración OAuth2.

### Objetivo:
Encontrar el `client_secret` expuesto en algún endpoint público del banco.

### Tarea:
1. Explora el sitio del banco en busca de endpoints relacionados con OAuth
2. Busca páginas de debugging, información, o documentación
3. Encuentra el `client_secret` que NO debería estar expuesto
4. Con el secret, podrías hacerte pasar por la aplicación legítima

### Pistas:
- Explora rutas como: `/oauth/*`, `/debug/*`, `/api/*`
- Los desarrolladores suelen dejar endpoints de información
- Busca endpoints que retornen JSON con configuración
- El client secret es una credencial crítica

### Verificación:
Envía el `client_secret` encontrado.

---

## 🎯 **OPCIÓN 4: Redirect URI Manipulation**

### Historia:
"La Redirección Maliciosa"

El banco NO valida correctamente el parámetro `redirect_uri` en las peticiones OAuth. Esto permite que un atacante especifique SU PROPIA URL para recibir los códigos de autorización.

### Objetivo:
Demostrar que puedes cambiar el `redirect_uri` a una URL controlada por ti para interceptar códigos de autorización.

### Tarea:
1. Inicia un flujo OAuth2 normal
2. Intercepta la petición de autorización con Burp Suite
3. Modifica el parámetro `redirect_uri` a una URL que controles (ej: `http://attacker.com/callback`)
4. Completa el flujo y observa que el código es enviado a TU URL
5. Captura el código de autorización

### Pistas:
- El `redirect_uri` aparece en múltiples etapas del flujo
- Debe modificarse ANTES de la autorización del usuario
- El banco NO verifica que el URI esté en una whitelist
- Puedes usar `http://127.0.0.1:8080/callback` para pruebas locales

### Verificación:
Envía un código de autorización que fue redirigido a una URL manipulada.

---

## 🎯 **OPCIÓN 5: Token Information Disclosure**

### Historia:
"El Token Parlanchín"

La respuesta del endpoint `/oauth/token` incluye información sensible del usuario que NO debería exponerse, incluyendo `user_id`, `email` y datos internos.

### Objetivo:
Obtener información sensible de un usuario a través de la respuesta del token endpoint.

### Tarea:
1. Completa un flujo OAuth2 y obtén un código de autorización
2. Envía una petición POST a `/oauth/token` con el código
3. Analiza la respuesta JSON
4. Identifica qué información sensible se está exponiendo
5. Documenta los datos que NO deberían estar en la respuesta

### Pistas:
- La respuesta debería contener SOLO: `access_token`, `token_type`, `expires_in`
- Cualquier dato adicional del usuario es una filtración
- Usa Burp Suite para inspeccionar la respuesta completa
- Busca campos como `user_info`, `user_id`, `email`, etc.

### Verificación:
Envía el `user_id` extraído de la respuesta del token endpoint.

---

## 🔍 **Cómo Usar Burp Suite**

### Configuración Básica:
1. Abre Burp Suite
2. Ve a `Proxy` > `Intercept`
3. Configura tu navegador para usar el proxy: `127.0.0.1:8080`
4. Activa intercepción: `Intercept is on`

### Análisis de Peticiones:
1. Haz clic en "Iniciar sesión con Google" en el banco
2. Burp interceptará cada petición HTTP
3. Inspecciona los parámetros en la URL y en el body
4. Busca: `state`, `code`, `redirect_uri`, `client_id`, `client_secret`

### Modificación:
1. En Burp, edita los parámetros que quieras modificar
2. Click en "Forward" para enviar la petición modificada
3. Observa la respuesta

### Repetición:
1. Click derecho en una petición > "Send to Repeater"
2. Ve a la pestaña "Repeater"
3. Modifica y reenvía la petición múltiples veces

---

## 📊 **Flujo OAuth2 Completo del Banco**

```
1. Cliente → App: GET /oauth/init
   ↓ Respuesta: { "authorization_url": "...", "state": "xxx" }

2. Cliente → Google: GET /oauth/google/authorize?client_id=xxx&redirect_uri=xxx&state=xxx
   ↓ Muestra pantalla de login

3. Usuario → Google: POST /oauth/google/login
   ↓ Con email + password

4. Google → Cliente: Pantalla de consentimiento /oauth/google/authorize

5. Usuario → Google: POST /oauth/google/consent
   ↓ Acepta permisos

6. Google → App: Redirect a /oauth/callback?code=xxxxx&state=xxx

7. App → Google: POST /oauth/token
   Body: { code, client_id, client_secret, grant_type }
   ↓ Respuesta: { access_token, user_info, ... }

8. App crea sesión bancaria con el token
```

---

## 🏆 **Recomendaciones para el Estudiante**

✅ **Usa Burp Suite** para interceptar TODAS las peticiones  
✅ **Documenta cada paso** del flujo OAuth2  
✅ **Identifica parámetros sensibles**: state, code, redirect_uri  
✅ **Prueba manipular cada parámetro** y observa el comportamiento  
✅ **Busca endpoints de debugging** que puedan exponer información  
✅ **Reutiliza peticiones** usando Burp Repeater  
✅ **Analiza las respuestas JSON** en detalle  

---

## 📚 **Recursos Adicionales**

- **OAuth 2.0 Security Best Practices:** https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics
- **Common OAuth Vulnerabilities:** OWASP OAuth Cheat Sheet
- **Burp Suite Documentation:** https://portswigger.net/burp/documentation

---

**¡Buena suerte encontrando las vulnerabilidades!** 🔓🎯
