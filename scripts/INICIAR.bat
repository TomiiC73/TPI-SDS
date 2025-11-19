@echo off
REM ========================================
REM   TPI-SDS - Script de Inicio Automatico
REM ========================================

echo.
echo ========================================
echo    Banco Nacional - TPI SDS
echo    Iniciando Sistema Completo
echo ========================================
echo.

REM Verificar que Docker este instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta instalado
    echo.
    echo Por favor instala Docker Desktop desde:
    echo https://docs.docker.com/desktop/install/windows-install/
    echo.
    pause
    exit /b 1
)

echo [1/3] Docker detectado correctamente
echo.

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose no esta instalado
    pause
    exit /b 1
)

echo [2/3] Docker Compose detectado correctamente
echo.

REM Detener contenedores previos si existen
echo [INFO] Deteniendo contenedores previos (si existen)...
docker-compose down 2>nul

echo.
echo [3/3] Construyendo e iniciando contenedores...
echo.
echo Este proceso puede tardar algunos minutos la primera vez.
echo Por favor espera...
echo.

REM Construir e iniciar
docker-compose up -d --build

if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un error al iniciar los contenedores
    echo.
    echo Revisa los logs con: docker-compose logs
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SISTEMA INICIADO CORRECTAMENTE
echo ========================================
echo.
echo URLs de Acceso:
echo.
echo   [+] Banco:      http://localhost:5000
echo   [+] Enunciados: http://localhost:5001
echo   [+] DB Admin:   http://localhost:8080
echo.
echo ========================================
echo   CREDENCIALES
echo ========================================
echo.
echo Login Bancario:
echo   Usuario:  julian
echo   Password: juli123
echo.
echo OAuth FakeGoogle:
echo   usuario@fakegoogle.com / fakegoogle123
echo   admin@fakegoogle.com / admin123
echo   hacker@fakegoogle.com / hacker123
echo.
echo ========================================
echo   COMANDOS UTILES
echo ========================================
echo.
echo Ver logs:        docker-compose logs -f
echo Detener:         docker-compose down
echo Reiniciar:       docker-compose restart
echo Estado:          docker-compose ps
echo.
echo ========================================
echo.

REM Esperar 3 segundos antes de abrir el navegador
timeout /t 3 /nobreak >nul

REM Abrir el navegador automaticamente
echo Abriendo navegador...
start http://localhost:5000

echo.
echo Presiona cualquier tecla para salir...
pause >nul
