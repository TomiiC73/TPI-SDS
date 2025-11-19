# 📋 RESUMEN DE MODIFICACIONES - DESAFÍO OAUTH2

## 📊 Estado Actual del Proyecto

### ✅ Archivos Creados

1. **`docs/DESAFIO_OAUTH.md`**
   - Guía completa de explotación OAuth2 CSRF
   - Flujo detallado del ataque con el tráfico HTTP real capturado
   - Análisis técnico del código vulnerable
   - Mitigaciones y mejores prácticas
   - **Incluye las credenciales correctas:** `usuario@google.com` / `google123`

2. **`docs/GUIA_PRACTICA_OAUTH.md`**
   - Tutorial paso a paso para ejecutar el desafío
   - Configuración de Burp Suite desde cero
   - Screenshots sugeridos para documentación
   - Checklist de completitud
   - Análisis de las 5 vulnerabilidades OAuth del banco
   - Código vulnerable vs código seguro con explicaciones

3. **`docs/README_OAUTH.md`**
   - Inicio rápido para estudiantes
   - FAQ y troubleshooting
   - Requisitos y setup
   - Referencias a la documentación completa

4. **`tools/test_oauth_vulnerabilities.py`**
   - Script automatizado de testing
   - Prueba las 3 vulnerabilidades principales
   - Reporte visual con colores
   - Útil para validación rápida

### ✅ Archivos Modificados

1. **`templates/desafio_oauth.html`**
   - ✅ Credenciales actualizadas: `usuario@google.com` (víctima)
   - ✅ Sección de pasos rápidos del ataque
   - ✅ Referencias a la documentación completa
   - ✅ Mejores hints y explicaciones

2. **`app_enunciados.py`**
   - ✅ Validación mejorada de códigos de autorización
   - ✅ Mejor regex para detectar códigos válidos
   - ✅ Mensajes de error más informativos
   - ✅ Pistas específicas según el tipo de error

---

## 🎯 Características del Desafío

### Vulnerabilidades Implementadas

#### 1. CSRF via State Parameter (Principal)
- **CWE-352** | **CVSS 8.1 (High)**
- **Ubicación:** `/oauth/google/consent`, `/oauth/callback`
- **Explotación:** Manipular el parámetro `state` con Burp Suite
- **Evidencia:** Código de autorización capturado

#### 2. Client Secret Expuesto
- **CVSS 9.8 (Critical)**
- **Ubicación:** `/oauth/info`
- **Explotación:** Acceso directo vía GET
- **Evidencia:** CLIENT_SECRET visible

#### 3. Reutilización de Códigos OAuth
- **CVSS 7.5 (High)**
- **Ubicación:** `/oauth/callback`
- **Explotación:** Usar mismo código múltiples veces
- **Evidencia:** Múltiples tokens del mismo código

#### 4. Redirect URI No Validado
- **CVSS 8.2 (High)**
- **Explotación:** Modificar `redirect_uri` a dominio del atacante

#### 5. Information Disclosure
- **CVSS 5.3 (Medium)**
- **Ubicación:** `/oauth/google/token`
- **Explotación:** Endpoint expone información sensible

---

## 📖 Documentación Disponible

### Para Estudiantes

```
📖 docs/README_OAUTH.md
   ├─ Inicio rápido
   ├─ Configuración del entorno
   ├─ Credenciales de prueba
   └─ FAQ

📖 docs/GUIA_PRACTICA_OAUTH.md
   ├─ Tutorial completo con screenshots
   ├─ 9 secciones detalladas
   ├─ Código vulnerable vs seguro
   └─ Checklist de completitud

📖 docs/DESAFIO_OAUTH.md
   ├─ Flujo del ataque con tráfico HTTP real
   ├─ Análisis técnico profundo
   ├─ Todas las fases del ataque
   └─ Verificación y evidencias
```

### Para Instructores

```
📖 docs/GUIA_COMPLETA_OAUTH (original)
   ├─ Las 5 vulnerabilidades
   ├─ Mitigaciones detalladas
   └─ Referencias RFC

🔧 tools/test_oauth_vulnerabilities.py
   ├─ Validación automatizada
   ├─ Reporte de vulnerabilidades
   └─ Testing sin intervención manual
```

---

## 🚀 Cómo Ejecutar el Desafío

### Método 1: Manual con Burp Suite (Recomendado para aprendizaje)

```bash
# 1. Iniciar el banco
python app_banco.py

# 2. Iniciar servidor de enunciados (opcional)
python app_enunciados.py

# 3. Configurar Burp Suite (127.0.0.1:8080)

# 4. Seguir la guía
# docs/GUIA_PRACTICA_OAUTH.md - Paso a paso
# docs/DESAFIO_OAUTH.md - Referencia rápida

# 5. Verificar en:
http://127.0.0.1:5001/desafio/oauth
```

### Método 2: Script Automatizado (Para validación)

```bash
# Instalar dependencias
pip install requests colorama

# Ejecutar tests
cd tools
python test_oauth_vulnerabilities.py

# El script probará:
# ✓ Vulnerabilidad #1: CSRF State
# ✓ Vulnerabilidad #2: Secret Expuesto
# ✓ Vulnerabilidad #3: Code Reuse
```

---

## 🎓 Flujo de Aprendizaje Sugerido

### Nivel 1: Reconocimiento (15 min)
1. Leer `docs/README_OAUTH.md`
2. Iniciar el banco y explorar
3. Encontrar `/oauth/info` (Vulnerabilidad #2 - fácil)
4. Familiarizarse con el flujo OAuth normal

### Nivel 2: Setup de Herramientas (30 min)
1. Instalar Burp Suite
2. Configurar proxy en navegador
3. Interceptar tráfico HTTP
4. Practicar Forward/Drop en Burp

### Nivel 3: Explotación CSRF (60 min)
1. Seguir `docs/GUIA_PRACTICA_OAUTH.md` paso a paso
2. Capturar el `state` del atacante
3. Manipular el consent de la víctima
4. Obtener el código de autorización
5. Verificar en la interfaz web

### Nivel 4: Documentación (30 min)
1. Tomar screenshots de evidencias
2. Documentar el proceso
3. Explicar el impacto
4. Proponer mitigaciones

### Nivel 5: Exploración Adicional (opcional)
1. Probar Vulnerabilidad #3 (Code Reuse)
2. Explorar Vulnerabilidad #4 (Redirect URI)
3. Analizar el código fuente (`app_banco.py`)
4. Ejecutar el script de testing automatizado

---

## 📸 Evidencias Requeridas (para informe)

### Screenshots Obligatorios

1. **Burp Suite - Intercepción inicial**
   - POST /oauth/google/consent
   - State original vacío o del atacante

2. **Burp Suite - State modificado**
   - State = "ATACANTE_12345"
   - Cookie de María presente

3. **Callback con código**
   - GET /oauth/callback?code=...&state=ATACANTE_12345
   - Código de autorización visible

4. **Verificación exitosa**
   - Interfaz web mostrando "¡Desafío completado!"
   - Mensaje de éxito con detalles

5. **Página /oauth/info (Vulnerabilidad #2)**
   - CLIENT_SECRET expuesto

### Documentación Requerida

```markdown
# Informe de Vulnerabilidad OAuth2 CSRF

## 1. Resumen Ejecutivo
- Vulnerabilidad encontrada: CSRF via State Parameter
- Severidad: CRÍTICA (CVSS 8.1)
- Impacto: Account Linking Hijacking

## 2. Descripción Técnica
- CWE-352: Cross-Site Request Forgery
- Falta de validación del parámetro `state`
- Código vulnerable en app_banco.py líneas 434-505

## 3. Prueba de Concepto (PoC)
- Pasos de reproducción
- Screenshots de Burp Suite
- Código de autorización obtenido: [CODIGO]

## 4. Impacto
- Acceso no autorizado a cuentas bancarias
- Robo de información confidencial de RR.HH.
- Bypass de autenticación

## 5. Mitigación
- Validar state: if state != session['oauth_state']: abort(403)
- Implementar expiración (5 min)
- Usar secrets.token_urlsafe(32)
```

---

## 🔧 Configuración del Entorno

### Variables del Sistema

```python
# app_banco.py
GOOGLE_CLIENT_ID = "banco-app-123456"
GOOGLE_CLIENT_SECRET = "SECRET_SUPER_SECRETO_EXPUESTO_123"  # ⚠️ Vulnerable
GOOGLE_REDIRECT_URI = "http://127.0.0.1:5000/oauth/callback"
```

### Usuarios de Prueba

```python
GOOGLE_USERS = {
    'test@google.com': {        # Atacante
        'password': 'test123',
        'name': 'Test User'
    },
    'usuario@google.com': {     # Víctima (María)
        'password': 'google123',
        'name': 'Usuario Google'
    }
}
```

---

## 🛡️ Código Vulnerable vs Seguro

### Vulnerable (Actual)

```python
@app.route('/oauth/google/consent', methods=['POST'])
def oauth_google_consent():
    state = request.form.get('state', '')
    
    # ❌ NO VALIDA EL STATE
    # Acepta cualquier state sin verificar
    
    code = secrets.token_urlsafe(16)
    # ... genera código sin validación
    
    return redirect(f"{redirect_uri}?code={code}&state={state}")
```

### Seguro (Mitigado)

```python
@app.route('/oauth/google/consent', methods=['POST'])
def oauth_google_consent():
    state = request.form.get('state', '')
    
    # ✅ VALIDACIONES CRÍTICAS
    if not state or state != session.get('oauth_state'):
        abort(403, "Invalid state - CSRF detected!")
    
    if time.time() - session.get('oauth_state_timestamp', 0) > 300:
        abort(403, "State expired")
    
    # ✅ Marcar como usado (one-time use)
    session.pop('oauth_state', None)
    
    code = secrets.token_urlsafe(16)
    # ... genera código
    
    return redirect(f"{redirect_uri}?code={code}&state={state}")
```

---

## 📚 Referencias Implementadas

### Estándares OAuth2
- ✅ RFC 6749 (Authorization Framework)
- ✅ RFC 6819 (Threat Model)
- ✅ OAuth 2.0 Security Best Practices

### OWASP
- ✅ OAuth 2.0 Cheat Sheet
- ✅ Authentication Cheat Sheet
- ✅ A01:2021 – Broken Access Control

### CWE
- ✅ CWE-352: CSRF
- ✅ CWE-522: Insufficiently Protected Credentials
- ✅ CWE-294: Authentication Bypass

---

## ✅ Checklist de Implementación

### Documentación
- [x] README_OAUTH.md (inicio rápido)
- [x] GUIA_PRACTICA_OAUTH.md (tutorial completo)
- [x] DESAFIO_OAUTH.md (referencia técnica)
- [x] GUIA_COMPLETA_OAUTH (original preservado)

### Código
- [x] Vulnerabilidad #1 CSRF implementada
- [x] Vulnerabilidad #2 Secret expuesto
- [x] Vulnerabilidad #3 Code reuse
- [x] Validación mejorada en app_enunciados.py
- [x] Template HTML actualizado con mejores hints

### Herramientas
- [x] Script de testing automatizado
- [x] Reporte visual de vulnerabilidades
- [x] Credenciales de prueba configuradas

### Testing
- [x] Flujo OAuth completo funcional
- [x] Intercepción con Burp Suite probada
- [x] Verificación de códigos implementada
- [x] Mensajes de error informativos

---

## 🎯 Próximos Pasos para Estudiantes

### Completar el Desafío Principal
1. ✅ Leer documentación
2. ✅ Configurar Burp Suite
3. ✅ Explotar CSRF OAuth
4. ✅ Capturar código de autorización
5. ✅ Verificar en interfaz web

### Exploración Adicional
1. ⬜ Probar las otras 4 vulnerabilidades
2. ⬜ Analizar el código fuente
3. ⬜ Proponer mitigaciones
4. ⬜ Escribir informe completo
5. ⬜ Ejecutar script de testing

### Profundización
1. ⬜ Estudiar RFC 6749 y RFC 6819
2. ⬜ Investigar CVEs relacionados
3. ⬜ Practicar con OAuth Debugger
4. ⬜ Explorar PKCE (Proof Key for Code Exchange)

---

## 📞 Soporte y Troubleshooting

### Problemas Comunes

**1. "No se puede conectar al servidor"**
```bash
# Solución:
python app_banco.py
# Verificar: http://127.0.0.1:5000
```

**2. "Burp no intercepta tráfico"**
```bash
# Verificar:
- Proxy configurado en navegador: 127.0.0.1:8080
- Intercept is ON en Burp
- Certificado CA instalado
```

**3. "Código no es aceptado"**
```bash
# Verificar:
- Código completo (sin espacios)
- Formato correcto (16-50 caracteres alfanuméricos)
- Flujo ejecutado correctamente (state modificado)
```

**4. "No veo el state en Burp"**
```bash
# El state puede estar vacío inicialmente
# Debes AGREGARLO manualmente: state=ATACANTE_12345
```

---

## 🎉 Conclusión

### Logros Completados

✅ **3 documentos completos** con guías paso a paso  
✅ **Script automatizado** para testing de vulnerabilidades  
✅ **Interfaz web mejorada** con mejores instrucciones  
✅ **Validación robusta** de códigos de autorización  
✅ **Credenciales corregidas** (usuario@google.com para María)  

### Valor Educativo

Este desafío proporciona:
- **Experiencia práctica** con vulnerabilidades OAuth2 reales
- **Habilidades de pentesting** con Burp Suite
- **Comprensión profunda** de CSRF y Account Linking Hijacking
- **Conocimiento aplicable** a auditorías de seguridad reales

---

**⚠️ DISCLAIMER FINAL**

Este material es **exclusivamente educativo** para un entorno controlado.

**NUNCA usar estas técnicas en sistemas reales sin autorización.**

El acceso no autorizado a sistemas informáticos es un **delito** en la mayoría de jurisdicciones.

---

**Creado por:** Equipo de Desarrollo - TPI SDS  
**Versión:** 2.0  
**Fecha:** Noviembre 2025  
**Licencia:** Uso Educativo Únicamente
