@echo off
echo ===============================================
echo   ARCTIC MONITOR - GITHUB RELEASE CREATOR
echo   Automated Release Script
echo ===============================================

:: Verificar GitHub CLI
echo Checking GitHub CLI...
gh --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: GitHub CLI not installed
    echo.
    echo Install options:
    echo 1. Download from: https://cli.github.com/
    echo 2. Or with winget: winget install GitHub.cli
    echo 3. Or with chocolatey: choco install gh
    echo.
    pause
    exit /b 1
)

echo ✅ GitHub CLI detected

:: Verificar que estamos en un repo git
echo Checking Git repository...
git status >nul 2>&1
if errorlevel 1 (
    echo ERROR: Not in a Git repository
    echo Initialize with: git init
    pause
    exit /b 1
)

echo ✅ Git repository detected

:: Verificar que el ejecutable existe
echo Checking executable...
if not exist "dist\Arctic-Monitor.exe" (
    echo ERROR: Executable not found at dist\Arctic-Monitor.exe
    echo.
    echo Please run build.bat first to create the executable
    pause
    exit /b 1
)

echo ✅ Executable found: dist\Arctic-Monitor.exe

:: Mostrar información del ejecutable
for %%I in ("dist\Arctic-Monitor.exe") do (
    set /a size_mb=%%~zI/1024/1024
    echo    Size: !size_mb! MB
    echo    Date: %%~tI
)

:: Verificar autenticación con GitHub
echo Checking GitHub authentication...
gh auth status >nul 2>&1
if errorlevel 1 (
    echo ERROR: Not authenticated with GitHub
    echo.
    echo Please run: gh auth login
    echo Then try again
    pause
    exit /b 1
)

echo ✅ GitHub authentication verified

:: Obtener información del release
echo.
echo ===============================================
echo   RELEASE INFORMATION
echo ===============================================

set /p VERSION="Enter version (e.g., v1.0.0): "
if "%VERSION%"=="" (
    echo ERROR: Version cannot be empty
    pause
    exit /b 1
)

set /p TITLE="Enter release title (e.g., System Monitor with OLED Display): "
if "%TITLE%"=="" set TITLE=Arctic Monitor %VERSION%

set /p DESCRIPTION="Enter release description: "
if "%DESCRIPTION%"=="" set DESCRIPTION=New release of Arctic Monitor with system monitoring for SteelSeries OLED displays

:: Crear o actualizar CHANGELOG.md
echo.
echo Creating/updating CHANGELOG.md...
if not exist "CHANGELOG.md" (
    echo # Changelog > CHANGELOG.md
    echo. >> CHANGELOG.md
    echo All notable changes to Arctic Monitor will be documented in this file. >> CHANGELOG.md
    echo. >> CHANGELOG.md
)

:: Agregar entrada al changelog
echo ## [%VERSION%] - %date% >> CHANGELOG.temp
echo. >> CHANGELOG.temp
echo ### Added >> CHANGELOG.temp
echo - %DESCRIPTION% >> CHANGELOG.temp
echo. >> CHANGELOG.temp
echo ### Features >> CHANGELOG.temp
echo - Real-time CPU, GPU, RAM monitoring >> CHANGELOG.temp
echo - Temperature display from LibreHardwareMonitor >> CHANGELOG.temp
echo - Disk usage information >> CHANGELOG.temp
echo - Global hotkeys: Ctrl+F9 (toggle), F10 (mode switch) >> CHANGELOG.temp
echo - SteelSeries GameSense OLED integration >> CHANGELOG.temp
echo - Arctic Nova Pro Wireless support >> CHANGELOG.temp
echo. >> CHANGELOG.temp
echo ### Requirements >> CHANGELOG.temp
echo - Windows 10/11 >> CHANGELOG.temp
echo - SteelSeries GG running >> CHANGELOG.temp
echo - LibreHardwareMonitor as Administrator >> CHANGELOG.temp
echo - Arctic Nova Pro Wireless headset >> CHANGELOG.temp
echo. >> CHANGELOG.temp

:: Combinar con changelog existente
type CHANGELOG.md >> CHANGELOG.temp 2>nul
move CHANGELOG.temp CHANGELOG.md >nul

echo ✅ CHANGELOG.md updated

:: Commit cambios pendientes
echo.
echo Checking for uncommitted changes...
git add . >nul 2>&1
git diff --staged --quiet
if errorlevel 1 (
    echo Found uncommitted changes, committing...
    git commit -m "Release %VERSION% - %TITLE%" >nul 2>&1
    echo ✅ Changes committed
) else (
    echo ✅ No uncommitted changes
)

:: Push changes
echo Pushing changes to remote...
git push >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not push changes to remote
    echo This might be okay if you're working offline
) else (
    echo ✅ Changes pushed to remote
)

:: Crear el release en GitHub
echo.
echo ===============================================
echo   CREATING GITHUB RELEASE
echo ===============================================
echo.
echo Version: %VERSION%
echo Title: %TITLE%
echo Description: %DESCRIPTION%
echo File: dist\Arctic-Monitor.exe
echo.
echo Creating release...

:: Comando de release (igual que FPS Counter)
gh release create %VERSION% ^
    "dist\Arctic-Monitor.exe" ^
    --title "%TITLE%" ^
    --notes "%DESCRIPTION%" ^
    -F CHANGELOG.md

set RELEASE_RESULT=%errorlevel%

if %RELEASE_RESULT% equ 0 (
    echo.
    echo ===============================================
    echo   RELEASE CREATED SUCCESSFULLY! 🎉
    echo ===============================================
    echo.
    echo Version: %VERSION%
    echo Title: %TITLE%
    echo File: Arctic-Monitor.exe
    echo.
    echo 🌐 Release URL:
    for /f "tokens=*" %%i in ('gh repo view --json url -q .url') do set REPO_URL=%%i
    echo %REPO_URL%/releases/tag/%VERSION%
    echo.
    echo 📥 Users can now:
    echo 1. Go to your GitHub repository
    echo 2. Click "Releases"
    echo 3. Download Arctic-Monitor.exe
    echo 4. Run as Administrator
    echo 5. Enjoy system monitoring on OLED!
    echo.
    echo 🎮 Controls:
    echo - Ctrl+F9: Toggle monitor ON/OFF
    echo - F10 (hold 3s): Switch Hardware/Disk mode
    echo.
    
    :: Abrir release en navegador
    choice /c YN /m "Open release page in browser?"
    if errorlevel 2 goto :skip_browser
    if errorlevel 1 (
        echo Opening release page...
        start "" "%REPO_URL%/releases/tag/%VERSION%"
    )
    :skip_browser
    
) else (
    echo.
    echo ===============================================
    echo   ERROR CREATING RELEASE ❌
    echo ===============================================
    echo.
    echo Error code: %RELEASE_RESULT%
    echo.
    echo Common issues:
    if %RELEASE_RESULT% equ 1 echo - Release tag already exists
    if %RELEASE_RESULT% equ 2 echo - Authentication problem
    if %RELEASE_RESULT% equ 3 echo - Network connection issue
    if %RELEASE_RESULT% equ 4 echo - Repository not found or no permissions
    echo.
    echo Troubleshooting:
    echo 1. Check that tag "%VERSION%" doesn't already exist
    echo 2. Verify you have write access to the repository
    echo 3. Check your internet connection
    echo 4. Try: gh auth refresh
    echo.
    echo Manual alternative:
    echo 1. Go to your GitHub repository
    echo 2. Click "Releases" → "Create a new release"
    echo 3. Tag: %VERSION%
    echo 4. Upload: dist\Arctic-Monitor.exe
    echo 5. Add description and publish
)

echo.
echo ===============================================
echo   RELEASE PROCESS COMPLETED
echo ===============================================
pause