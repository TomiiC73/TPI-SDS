# 🔐 README - Desafío OAuth2 CSRF

## 🎯 Inicio Rápido

### Opción 1: Explotación Manual con Burp Suite (Recomendado)

**Sigue la documentación paso a paso:**
```
📖 docs/GUIA_PRACTICA_OAUTH.md - Guía completa con screenshots
📖 docs/DESAFIO_OAUTH.md - Referencia rápida del flujo de ataque
📖 docs/GUIA_COMPLETA_OAUTH - Guía original del desafío
```

**Pasos rápidos:**
1. Iniciar Burp Suite (127.0.0.1:8080)
2. Configurar proxy en el navegador
3. Ir a http://127.0.0.1:5001/desafio/oauth
4. Seguir las instrucciones en pantalla

### Opción 2: Script Automatizado de Testing

**Ejecutar el script de pruebas:**
```bash
cd tools
pip install requests colorama
python test_oauth_vulnerabilities.py
```

Este script prueba automáticamente las 3 vulnerabilidades principales.

---

## 📁 Estructura de Documentación

```
docs/
├── DESAFIO_OAUTH.md          # Referencia rápida del ataque CSRF
├── GUIA_PRACTICA_OAUTH.md    # Guía paso a paso con screenshots
├── GUIA_COMPLETA_OAUTH        # Guía original con todas las vulnerabilidades
└── OAUTH_VULNERABILITIES.md  # Listado técnico de vulnerabilidades

templates/
├── desafio_oauth.html         # Interfaz web del desafío
└── desafio_oauth_avanzado.html # Desafío con 5 vulnerabilidades

tools/
└── test_oauth_vulnerabilities.py # Script de testing automatizado
```

---

## 🎓 ¿Qué Aprenderás?

### Vulnerabilidad Principal: CSRF via State Parameter

**CWE-352 | CVSS 8.1 (High)**

- ✅ Identificar falta de validación del parámetro `state` en OAuth2
- ✅ Explotar Account Linking Hijacking
- ✅ Usar Burp Suite para interceptar y manipular tráfico HTTP
- ✅ Demostrar impacto con código de autorización capturado

### Otras Vulnerabilidades del Banco

1. **Client Secret Expuesto** (CVSS 9.8)
2. **Reutilización de Códigos OAuth** (CVSS 7.5)
3. **Redirect URI No Validado** (CVSS 8.2)
4. **Information Disclosure** (CVSS 5.3)

---

## 🛠️ Requisitos

### Software Necesario

- ✅ Python 3.7+
- ✅ Docker (opcional, si usas contenedores)
- ✅ Burp Suite Community Edition
- ✅ Navegador web (Chrome/Firefox)

### Dependencias Python

```bash
pip install flask requests colorama jwt sqlite3
```

---

## 🚀 Iniciar el Entorno

### Opción A: Sin Docker

```bash
# Terminal 1: Banco Nacional
python app_banco.py
# Escucha en: http://127.0.0.1:5000

# Terminal 2: Servidor de Enunciados (opcional)
python app_enunciados.py
# Escucha en: http://127.0.0.1:5001
```

### Opción B: Con Docker

```bash
cd docker
docker-compose up -d --build

# Verificar contenedores
docker ps
```

### Verificar que todo funcione

```bash
# Banco Nacional
curl http://127.0.0.1:5000

# Enunciados
curl http://127.0.0.1:5001
```

---

## 🎯 Flujo del Ataque (Resumen)

### Fase 1: Captura del State

```
1. Atacante → Login con test@google.com
2. Burp intercepta → Modificar state a "ATACANTE_12345"
3. Drop request (no completar el flujo)
```

### Fase 2: Ataque a la Víctima

```
4. Víctima (María) → Login con usuario@google.com
5. Burp intercepta → Reemplazar state de María con "ATACANTE_12345"
6. Forward → Banco vincula cuenta de María con Google del atacante
```

### Fase 3: Captura del Código

```
7. Observar redirect: /oauth/callback?code=CODIGO&state=ATACANTE_12345
8. Copiar el código de autorización
9. Verificar en: http://127.0.0.1:5001/desafio/oauth
```

---

## 📸 Evidencias Requeridas

Para completar el desafío, documenta:

1. **Screenshot 1:** Página /oauth/info con credenciales expuestas
2. **Screenshot 2:** Burp mostrando POST consent modificado (state=ATACANTE_12345)
3. **Screenshot 3:** Burp mostrando state de María siendo reemplazado
4. **Screenshot 4:** Callback con código de autorización capturado
5. **Screenshot 5:** Verificación exitosa en la interfaz web
6. **Screenshot 6:** Dashboard de María (opcional - demostración de impacto)

---

## 🔍 Credenciales de Prueba

### Atacante (Tu cuenta)
- Email: `test@google.com`
- Password: `test123`

### Víctima (María)
- Email: `usuario@google.com`
- Password: `google123`

### Banco Nacional (login directo - opcional)
- Usuario: `julian`
- Password: `juli123`

---

## 🛡️ Mitigación (Para Desarrolladores)

### Código Vulnerable

```python
# ❌ NO VALIDA EL STATE
@app.route('/oauth/google/consent', methods=['POST'])
def consent():
    state = request.form.get('state', '')
    # ... genera código sin validar state
```

### Código Seguro

```python
# ✅ VALIDA EL STATE CORRECTAMENTE
@app.route('/oauth/google/consent', methods=['POST'])
def consent():
    state = request.form.get('state', '')
    
    # Validación crítica
    if state != session.get('oauth_state'):
        abort(403, "Invalid state - CSRF detected!")
    
    # Verificar expiración
    if time.time() - session.get('oauth_state_timestamp', 0) > 300:
        abort(403, "State expired")
    
    # Marcar como usado
    session.pop('oauth_state', None)
    
    # ... genera código
```

---

## 📚 Referencias

### Especificaciones OAuth2
- RFC 6749: OAuth 2.0 Authorization Framework
- RFC 6819: OAuth 2.0 Threat Model
- OAuth 2.0 Security Best Current Practice

### Guías de Seguridad
- OWASP OAuth 2.0 Cheat Sheet
- OWASP Authentication Cheat Sheet

### Herramientas
- Burp Suite: https://portswigger.net/burp
- OAuth 2.0 Debugger: https://oauthdebugger.com/

---

## ❓ FAQ

### ¿Por qué necesito Burp Suite?

Burp Suite te permite interceptar y modificar peticiones HTTP en tiempo real, esencial para manipular el parámetro `state`.

### ¿Puedo usar otro proxy?

Sí, puedes usar OWASP ZAP, mitmproxy o cualquier proxy que permita modificar requests.

### ¿Funciona sin proxy?

No para el desafío CSRF. El ataque requiere modificar el `state` en vuelo, lo cual solo es posible con un proxy interceptor.

### ¿Qué hago si el código no es aceptado?

Verifica que:
- El código sea completo (sin espacios)
- Sea el valor del parámetro `code` del callback
- Hayas seguido el flujo correctamente (state modificado)

### ¿Cuánto tiempo es válido un código?

Los códigos de autorización expiran en 5 minutos (300 segundos) en este banco.

---

## 🚨 Disclaimer

**⚠️ SOLO PARA USO EDUCATIVO ⚠️**

Este desafío es para aprendizaje en un entorno controlado.

**NUNCA:**
- ❌ Uses estas técnicas en sistemas reales sin autorización
- ❌ Ataques aplicaciones de producción
- ❌ Accedas a cuentas de terceros sin permiso

**El acceso no autorizado a sistemas es un delito.**

**SIEMPRE:**
- ✅ Obtén autorización por escrito
- ✅ Respeta los Bug Bounty programs
- ✅ Reporta vulnerabilidades responsablemente

---

## 📞 Soporte

Si tienes problemas:

1. Revisa la documentación completa en `docs/GUIA_PRACTICA_OAUTH.md`
2. Verifica que el servidor esté corriendo
3. Confirma que Burp Suite esté interceptando
4. Revisa los logs del servidor para errores

---

## 🎉 ¡Éxito!

Una vez completado el desafío:

✅ Has demostrado conocimientos de OAuth2 Security
✅ Sabes usar Burp Suite para pentesting
✅ Puedes identificar y explotar CSRF en OAuth
✅ Entiendes cómo mitigar estas vulnerabilidades

**¡Continúa con las otras 4 vulnerabilidades OAuth del banco!**

---

**Creado por:** Equipo de Seguridad - Banco Nacional (Entorno de Pruebas)  
**Versión:** 2.0  
**Última actualización:** Noviembre 2025
