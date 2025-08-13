@echo off
echo ===============================================
echo   ARCTIC MONITOR - Build Script
echo   Replicando metodo del FPS Counter
echo ===============================================

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed or not in PATH
    pause
    exit /b 1
)

:: Verificar archivo principal
if not exist "main.py" (
    echo ERROR: main.py not found
    echo Make sure you're in the project root directory
    pause
    exit /b 1
)

:: Instalar dependencias
echo Installing dependencies...
pip install -r requirements.txt

:: Limpiar builds anteriores
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del *.spec

:: Verificar/crear icono
if not exist "assets\icon.ico" (
    echo Creating assets directory...
    if not exist "assets" mkdir assets
    echo WARNING: Icon not found at assets\icon.ico
    echo Using default Windows icon
    set ICON_PARAM=
) else (
    echo Using custom icon: assets\icon.ico
    set ICON_PARAM=--icon "assets\icon.ico" --add-data "assets;assets"
)

:: Construir ejecutable (mismo estilo que FPS counter)
echo Building executable...
pyinstaller ^
    --clean ^
    -F ^
    --onefile ^
    %ICON_PARAM% ^
    --uac-admin ^
    --noconsole ^
    --hidden-import wmi ^
    --hidden-import pythoncom ^
    --hidden-import win32com.client ^
    --hidden-import psutil ^
    --hidden-import keyboard ^
    --hidden-import requests ^
    --add-data "src;src" ^
    -n "Arctic-Monitor" ^
    main.py

if errorlevel 0 (
    echo.
    echo ===============================================
    echo   BUILD SUCCESSFUL!
    echo   Location: dist\Arctic-Monitor.exe
    echo ===============================================
    
    :: Mostrar tamaño
    for %%I in ("dist\Arctic-Monitor.exe") do (
        set /a size_mb=%%~zI/1024/1024
        echo   Size: !size_mb! MB
    )
    
    echo.
    echo Next steps:
    echo 1. Test the executable: dist\Arctic-Monitor.exe
    echo 2. Create GitHub release: release.bat
    
) else (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above.
)

pause