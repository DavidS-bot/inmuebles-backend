@echo off
echo.
echo === 📦 Preparando proyecto para Vercel ===
echo.

cd inmuebles-web

echo [INFO] Limpiando archivos innecesarios...
if exist .next rmdir /s /q .next
if exist node_modules rmdir /s /q node_modules

echo [INFO] Creando archivo comprimido para Vercel...
powershell -Command "Compress-Archive -Path '.' -DestinationPath '../inmuebles-web-for-vercel.zip' -Force"

echo.
echo ✅ Archivo creado: inmuebles-web-for-vercel.zip
echo.
echo INSTRUCCIONES:
echo 1. Ve a tu dashboard de Vercel
echo 2. Click "Import Project"  
echo 3. Sube el archivo: inmuebles-web-for-vercel.zip
echo 4. Configura las variables de entorno
echo 5. Click Deploy!
echo.
echo El archivo esta en: %cd%\..\inmuebles-web-for-vercel.zip
echo.

cd ..
start .

pause