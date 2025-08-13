@echo off
echo ===============================================
echo   ARCTIC MONITOR - GITHUB RELEASE CREATOR
echo   Replicando metodo del FPS Counter
echo ===============================================

:: Verificar GitHub CLI
gh --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: GitHub CLI no está instalado
    echo Instala desde: https://cli.github.com/
    echo O con: winget install GitHub.cli
    pause
    exit /b 1
)

:: Verificar que el ejecutable existe
if not exist "dist\Arctic-Monitor.exe" (
    echo ERROR: Ejecutable no encontrado
    echo Ejecuta build.bat primero
    pause
    exit /b 1
)

:: Verificar que estamos en un repo git
git status >nul 2>&1
if errorlevel 1 (
    echo ERROR: No estás en un repositorio Git
    echo Inicializa con: git init
    pause
    exit /b 1
)

:: Obtener información del release
set /p VERSION="Ingresa la version (ej: v1.0.0): "
set /p DESCRIPTION="Descripcion del release: "

:: Crear CHANGELOG.md si no existe
if not exist "CHANGELOG.md" (
    echo Creando CHANGELOG.md...
    echo # Changelog > CHANGELOG.md
    echo. >> CHANGELOG.md
    echo ## [%VERSION%] - %date% >> CHANGELOG.md
    echo. >> CHANGELOG.md
    echo ### Added >> CHANGELOG.md
    echo - Sistema de monitoreo para Arctic Nova Pro Wireless >> CHANGELOG.md
    echo - CPU, GPU, RAM y temperatura en tiempo real >> CHANGELOG.md
    echo - Control por keybinds: Ctrl+F9 y F10 hold >> CHANGELOG.md
    echo - Modo Hardware y Disco >> CHANGELOG.md
    echo. >> CHANGELOG.md
    echo ### Requirements >> CHANGELOG.md
    echo - Windows 10/11 >> CHANGELOG.md
    echo - SteelSeries GG running >> CHANGELOG.md
    echo - LibreHardwareMonitor as Administrator >> CHANGELOG.md
    echo - Arctic Nova Pro Wireless >> CHANGELOG.md
)

:: Commit cambios si hay alguno
git add . >nul 2>&1
git diff --staged --quiet || (
    echo Commiteando cambios...
    git commit -m "Release %VERSION%" >nul 2>&1
)

:: Crear release en GitHub (igual que FPS Counter)
echo Creando release %VERSION%...
gh release create %VERSION% ^
    "dist\Arctic-Monitor.exe" ^
    --title "Arctic Monitor %VERSION%" ^
    --notes "%DESCRIPTION%" ^
    -F CHANGELOG.md

set RELEASE_RESULT=%errorlevel%

if %RELEASE_RESULT% equ 0 (
    echo.
    echo ===============================================
    echo   RELEASE CREADO EXITOSAMENTE!
    echo ===============================================
    echo.
    echo Version: %VERSION%
    echo Archivo: Arctic-Monitor.exe
    echo.
    echo El release está disponible en:
    echo https://github.com/TU-USUARIO/TU-REPO/releases/tag/%VERSION%
    echo.
    echo Los usuarios pueden:
    echo 1. Descargar Arctic-Monitor.exe
    echo 2. Ejecutar como Administrador
    echo 3. Usar Ctrl+F9 y F10 para control
    echo.
) else (
    echo ERROR: Falló la creación del release
    echo Código de error: %RELEASE_RESULT%
    echo.
    echo Verifica:
    echo 1. Que tienes permisos en el repo
    echo 2. Que el token de GitHub es válido
    echo 3. Que el tag no existe ya
)

pause