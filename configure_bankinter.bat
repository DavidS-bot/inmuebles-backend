@echo off
echo === Configurador de Credenciales Bankinter ===
echo.

set /p USERNAME="Introduce tu DNI/NIE: "
set /p PASSWORD="Introduce tu password: "

echo.
echo Configurando variables de entorno...

set BANKINTER_USERNAME=%USERNAME%
set BANKINTER_PASSWORD=%PASSWORD%

echo [OK] Variables configuradas para esta sesion
echo.

echo Ejecutando test real...
echo IMPORTANTE: Se abrira Chrome, NO lo cierres manualmente
echo.
pause

python test_bankinter_auto.py