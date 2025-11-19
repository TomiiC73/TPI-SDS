@echo off
REM Script para construir y ejecutar la aplicacion con Docker en Windows

echo ======================================
echo   Docker Builder - Banco Nacional
echo ======================================
echo.

REM Verificar que Docker este instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta instalado
    echo Instala Docker Desktop desde: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose no esta instalado
    pause
    exit /b 1
)

echo [OK] Docker y Docker Compose instalados
echo.

echo Selecciona una opcion:
echo.
echo 1. Construir imagenes Docker
echo 2. Iniciar contenedores
echo 3. Construir e iniciar (todo en uno)
echo 4. Detener contenedores
echo 5. Ver logs
echo 6. Eliminar todo (contenedores + imagenes)
echo 7. Reconstruir desde cero
echo.

set /p opcion="Opcion: "

if "%opcion%"=="1" goto build
if "%opcion%"=="2" goto start
if "%opcion%"=="3" goto all
if "%opcion%"=="4" goto stop
if "%opcion%"=="5" goto logs
if "%opcion%"=="6" goto clean
if "%opcion%"=="7" goto rebuild
goto invalid

:build
echo.
echo [INFO] Construyendo imagenes Docker...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Error al construir las imagenes
    pause
    exit /b 1
)
echo [OK] Imagenes construidas exitosamente
goto end

:start
echo.
echo [INFO] Iniciando contenedores...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Error al iniciar contenedores
    pause
    exit /b 1
)
echo.
echo [OK] Contenedores iniciados
echo.
echo Acceso a la aplicacion:
echo   - Banco: http://localhost:5000
echo   - Enunciados: http://localhost:5001
echo   - DB Admin: http://localhost:8080
goto end

:all
echo.
echo [INFO] Construyendo imagenes...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Error al construir
    pause
    exit /b 1
)
echo [OK] Imagenes construidas
echo.
echo [INFO] Iniciando contenedores...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Error al iniciar
    pause
    exit /b 1
)
echo.
echo [OK] Aplicacion iniciada exitosamente
echo.
echo ======================================
echo   URLs de Acceso:
echo ======================================
echo   Banco:      http://localhost:5000
echo   Enunciados: http://localhost:5001
echo   DB Admin:   http://localhost:8080
echo ======================================
echo.
echo Credenciales:
echo   Usuario: julian
echo   Password: juli123
echo.
echo Ver logs: docker-compose logs -f
goto end

:stop
echo.
echo [INFO] Deteniendo contenedores...
docker-compose down
echo [OK] Contenedores detenidos
goto end

:logs
echo.
echo [INFO] Mostrando logs (Ctrl+C para salir)...
docker-compose logs -f
goto end

:clean
echo.
echo [WARNING] Esto eliminara TODOS los contenedores e imagenes
set /p confirm="Estas seguro? (s/N): "
if /i not "%confirm%"=="s" (
    echo [INFO] Operacion cancelada
    goto end
)
echo.
echo [INFO] Deteniendo contenedores...
docker-compose down
echo [INFO] Eliminando imagenes...
docker rmi banco-nacional:latest banco-enunciados:latest 2>nul
echo [OK] Todo eliminado
goto end

:rebuild
echo.
echo [INFO] Reconstruyendo desde cero (sin cache)...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo.
echo [OK] Aplicacion reconstruida e iniciada
echo.
echo Acceso a la aplicacion:
echo   - Banco: http://localhost:5000
echo   - Enunciados: http://localhost:5001
echo   - DB Admin: http://localhost:8080
goto end

:invalid
echo.
echo [ERROR] Opcion invalida
pause
exit /b 1

:end
echo.
echo [OK] Operacion completada
echo.
pause
