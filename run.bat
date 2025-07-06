@echo off
echo Iniciando GesClinica...

REM Navega al directorio donde se encuentra este script
cd /d "%~dp0"

REM Ejecuta el programa de Python
python main.py

echo La aplicacion se ha cerrado.
pause