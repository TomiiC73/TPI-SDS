# 📦 Instalación de Dependencias - Desafío OAuth2

## 🐍 Dependencias Python

### requirements.txt actualizado

```txt
# Framework Web
Flask==2.3.0
Werkzeug==2.3.0

# Base de Datos
sqlite3  # Incluido en Python standard library

# OAuth y JWT
PyJWT==2.8.0
cryptography==41.0.0

# HTTP y Testing
requests==2.31.0
urllib3==2.0.0

# CLI y Output
colorama==0.4.6
click==8.1.0

# Opcional - para desarrollo
pytest==7.4.0
pytest-flask==1.2.0
```

### Instalación Rápida

```bash
# Opción 1: Usar requirements.txt (recomendado)
pip install -r requirements.txt

# Opción 2: Instalación manual
pip install Flask PyJWT requests colorama

# Opción 3: Instalación individual para el desafío OAuth
pip install Flask==2.3.0
pip install PyJWT==2.8.0
pip install requests==2.31.0
pip install colorama==0.4.6
```

---

## 🔧 Burp Suite Community Edition

### Windows

```powershell
# Descargar desde:
https://portswigger.net/burp/communitydownload

# Ejecutar instalador
# Burp-Suite-Community-Installer-windows-x64.exe

# Ubicación por defecto:
C:\Program Files\BurpSuiteCommunity\BurpSuiteCommunity.exe
```

### macOS

```bash
# Descargar desde:
https://portswigger.net/burp/communitydownload

# Montar DMG y arrastrar a Applications
# O usar Homebrew:
brew install --cask burp-suite
```

### Linux

```bash
# Descargar desde:
https://portswigger.net/burp/communitydownload

# Dar permisos de ejecución
chmod +x burpsuite_community_linux_*.sh

# Ejecutar instalador
./burpsuite_community_linux_*.sh

# O usar script de instalación:
wget -O burp.sh https://portswigger.net/burp/releases/download?product=community&type=Linux
chmod +x burp.sh
./burp.sh
```

---

## 🐋 Docker (Opcional)

### Windows

```powershell
# Descargar Docker Desktop:
https://www.docker.com/products/docker-desktop

# Instalar y reiniciar

# Verificar instalación:
docker --version
docker-compose --version
```

### macOS

```bash
# Descargar Docker Desktop:
https://www.docker.com/products/docker-desktop

# O usar Homebrew:
brew install --cask docker

# Verificar:
docker --version
```

### Linux (Ubuntu/Debian)

```bash
# Actualizar repositorios
sudo apt-get update

# Instalar dependencias
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common

# Agregar clave GPG de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Agregar repositorio
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Instalar Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar
docker --version
docker-compose --version
```

---

## 🌐 Configuración de Navegador

### Google Chrome

**Método 1: Manual**
```
1. Settings → Advanced → System → Open proxy settings
2. LAN Settings → Proxy server
3. Address: 127.0.0.1, Port: 8080
4. OK
```

**Método 2: Extensión SwitchyOmega**
```
1. Instalar: chrome.google.com/webstore → SwitchyOmega
2. Opciones → New Profile → "Burp"
3. Protocol: HTTP, Server: 127.0.0.1, Port: 8080
4. Apply changes
5. Click ícono SwitchyOmega → Burp
```

### Mozilla Firefox

**Método 1: Manual**
```
1. Settings → General → Network Settings
2. Settings button
3. Manual proxy configuration
4. HTTP Proxy: 127.0.0.1, Port: 8080
5. Check: "Use this proxy server for all protocols"
6. OK
```

**Método 2: Extensión FoxyProxy**
```
1. Instalar: addons.mozilla.org → FoxyProxy
2. Opciones → Add → Proxy Details
3. Title: Burp Suite
4. Proxy Type: HTTP
5. Proxy IP: 127.0.0.1
6. Port: 8080
7. Save
```

---

## 🔐 Certificado CA de Burp

### Todos los navegadores

```
1. Configurar proxy apuntando a Burp (127.0.0.1:8080)
2. Iniciar Burp Suite
3. En el navegador, ir a: http://burpsuite
4. Click en "CA Certificate"
5. Guardar archivo: cacert.der
```

### Chrome (Windows)

```
1. Settings → Privacy and Security → Security
2. Manage certificates
3. Trusted Root Certification Authorities → Import
4. Seleccionar cacert.der
5. Siguiente → Finalizar
```

### Firefox

```
1. Settings → Privacy & Security
2. Certificates → View Certificates
3. Authorities → Import
4. Seleccionar cacert.der
5. Marcar: "Trust this CA to identify websites"
6. OK
```

### macOS

```bash
# Doble click en cacert.der
# O usar terminal:
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain cacert.der
```

### Linux

```bash
# Ubuntu/Debian
sudo cp cacert.der /usr/local/share/ca-certificates/burp.crt
sudo update-ca-certificates

# Fedora/RHEL
sudo cp cacert.der /etc/pki/ca-trust/source/anchors/burp.crt
sudo update-ca-trust
```

---

## ✅ Verificación de Instalación

### Script de Verificación

```bash
# Crear archivo: check_setup.py

#!/usr/bin/env python3
import sys

def check_python():
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Error: Se requiere Python 3.7+")
        return False
    return True

def check_module(module_name):
    try:
        __import__(module_name)
        print(f"✓ {module_name} instalado")
        return True
    except ImportError:
        print(f"✗ {module_name} NO instalado")
        return False

def check_all():
    print("=" * 50)
    print("Verificación de Dependencias - Desafío OAuth2")
    print("=" * 50)
    print()
    
    checks = []
    
    # Python
    checks.append(check_python())
    
    # Módulos requeridos
    modules = ['flask', 'jwt', 'requests', 'colorama']
    for module in modules:
        checks.append(check_module(module))
    
    # SQLite (incluido en Python)
    checks.append(check_module('sqlite3'))
    
    print()
    print("=" * 50)
    
    if all(checks):
        print("✓ Todas las dependencias están instaladas")
        return 0
    else:
        print("✗ Faltan dependencias. Ejecuta:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(check_all())
```

### Ejecutar Verificación

```bash
python check_setup.py
```

### Verificación Manual

```python
# En terminal Python:
python

>>> import flask
>>> import jwt
>>> import requests
>>> import colorama
>>> print("✅ Todas las dependencias OK")
```

---

## 🚀 Inicio Rápido Post-Instalación

### 1. Verificar Dependencias

```bash
python check_setup.py
```

### 2. Iniciar el Banco

```bash
python app_banco.py
```

**Salida esperada:**
```
🏦 Banco Nacional - Sistema iniciado en http://127.0.0.1:5000
🔓 OAuth2 Google Integration activado
⚠️  VULNERABILIDADES ACTIVAS:
   1. RCE en /transferencias
   2. OAuth CSRF (state no validado)
   3. Client Secret expuesto en /oauth/info
   4. Reutilización de códigos OAuth
```

### 3. Verificar Acceso

```bash
# En otro terminal:
curl http://127.0.0.1:5000

# Debería retornar HTML del banco
```

### 4. Configurar Burp Suite

```
1. Iniciar Burp Suite
2. Create temporary project → Next
3. Use Burp defaults → Start Burp
4. Proxy → Intercept → Intercept is on
```

### 5. Ejecutar Test Automatizado (Opcional)

```bash
cd tools
python test_oauth_vulnerabilities.py
```

---

## 🐛 Troubleshooting

### Error: "Module not found: flask"

```bash
# Solución:
pip install flask

# O reinstalar todas las dependencias:
pip install -r requirements.txt
```

### Error: "Address already in use: 127.0.0.1:5000"

```bash
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -ti:5000 | xargs kill -9
```

### Error: "sqlite3.OperationalError"

```bash
# Eliminar y recrear base de datos:
rm banco.db
python app_banco.py
```

### Burp no intercepta tráfico

```
1. Verificar que el proxy esté configurado en el navegador
2. Verificar que "Intercept is on" en Burp
3. Intentar acceder a: http://burpsuite (debería ver página de Burp)
4. Si falla, reinstalar certificado CA
```

### Error: "Connection refused" al acceder al banco

```bash
# Verificar que el servidor esté corriendo:
ps aux | grep python
# O en Windows:
tasklist | findstr python

# Si no está corriendo:
python app_banco.py
```

---

## 📋 Checklist Pre-Desafío

Antes de comenzar el desafío, verifica:

- [ ] Python 3.7+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Burp Suite Community Edition instalado
- [ ] Certificado CA de Burp instalado en el navegador
- [ ] Proxy configurado en el navegador (127.0.0.1:8080)
- [ ] `app_banco.py` corriendo y accesible
- [ ] Test de conexión exitoso (`curl http://127.0.0.1:5000`)
- [ ] Burp Suite interceptando tráfico correctamente
- [ ] Documentación descargada (`docs/GUIA_PRACTICA_OAUTH.md`)

---

## 🆘 Soporte Adicional

Si después de seguir esta guía sigues teniendo problemas:

1. **Revisar documentación completa:**
   - `docs/README_OAUTH.md` - FAQ
   - `docs/GUIA_PRACTICA_OAUTH.md` - Troubleshooting

2. **Verificar logs del servidor:**
   ```bash
   python app_banco.py
   # Observar mensajes de error
   ```

3. **Reiniciar todo:**
   ```bash
   # Matar procesos
   pkill -f app_banco.py
   
   # Limpiar base de datos
   rm banco.db
   
   # Reiniciar
   python app_banco.py
   ```

---

**Última actualización:** Noviembre 2025  
**Versión:** 1.0
