@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo No se encontro Python. Instala Python 3.10 o superior y vuelve a intentar.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 goto error
    echo Instalando dependencias...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto error
)

if not exist ".env" copy ".env.example" ".env" >nul
.venv\Scripts\python.exe main.py
if errorlevel 1 goto error
exit /b 0

:error
echo.
echo No fue posible iniciar MiMascota. Revisa el mensaje anterior.
pause
exit /b 1
