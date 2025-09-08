@echo off
echo ================================================
echo PROCESADOR DE MOVIMIENTOS BANKINTER
echo ================================================
echo.
echo INSTRUCCIONES:
echo 1. Ve a tu pagina de Bankinter online
echo 2. Haz clic en el saldo 2.123,98 EUR junto a "Cc Euros No Resident"
echo 3. Copia TODO el texto de la pagina (Ctrl+A, Ctrl+C)
echo 4. Pega el texto en un archivo "movimientos.txt" en esta carpeta
echo 5. Presiona cualquier tecla para continuar...
echo.
pause

python procesar_movimientos.py

echo.
echo Presiona cualquier tecla para salir...
pause