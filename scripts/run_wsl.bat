@echo off
echo ======================================
echo   TPI-SDS en WSL Ubuntu (LINUX)
echo ======================================
echo.
echo [*] Servidor Flask corriendo en LINUX
echo [*] Ahora puedes usar comandos de Linux!
echo.
echo Acceso:
echo   - http://127.0.0.1:5000
echo   - http://localhost:5000
echo.
echo Credenciales:
echo   Usuario: julian
echo   Password: juli123
echo.
echo Comandos Linux para RCE:
echo   ls, pwd, whoami, cat, ps, env
echo.
echo Presiona Ctrl+C para detener
echo ======================================
echo.

wsl -d Ubuntu-24.04 -e bash -c "cd ~/TPI-SDS && source venv/bin/activate && python app_banco.py"
