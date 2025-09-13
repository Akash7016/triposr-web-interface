@echo off
title TripoSR Web Interface Installer
echo.
echo ===============================================
echo    TripoSR Web Interface Installer
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
)

echo [✓] Python and Git found
echo.

REM Create directory structure
echo [1/5] Creating directory structure...
if not exist "C:\ai3d" mkdir "C:\ai3d"
cd /d "C:\ai3d"

REM Install TripoSR
echo [2/5] Installing TripoSR (this may take several minutes)...
if exist "TripoSR" (
    echo     TripoSR directory already exists, skipping clone...
) else (
    git clone https://github.com/VAST-AI-Research/TripoSR.git
    if errorlevel 1 (
        echo [ERROR] Failed to clone TripoSR
        pause
        exit /b 1
    )
)

cd TripoSR

REM Create virtual environment
echo [3/5] Setting up Python environment...
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
call .venv\Scripts\activate.bat
echo     Installing PyTorch and dependencies...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
if errorlevel 1 (
    echo [WARNING] CUDA version failed, installing CPU version...
    pip install torch torchvision
)

pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install TripoSR dependencies
    pause
    exit /b 1
)

REM Install Web Interface
echo [4/5] Installing Web Interface...
cd /d "C:\ai3d"
if exist "triposr-web-interface" (
    echo     Web interface directory already exists, updating...
    cd triposr-web-interface
    git pull
) else (
    git clone https://github.com/Akash7016/triposr-web-interface.git
    if errorlevel 1 (
        echo [ERROR] Failed to clone web interface
        echo Please check the GitHub URL
        pause
        exit /b 1
    )
    cd triposr-web-interface
)

pip install flask werkzeug
if errorlevel 1 (
    echo [ERROR] Failed to install Flask dependencies
    pause
    exit /b 1
)

REM Create PowerShell scripts
echo [5/5] Setting up PowerShell scripts...
cd /d "C:\ai3d\TripoSR"

REM Create run_fast.ps1
echo Creating run_fast.ps1...
(
echo param^(
echo   [Parameter^(Mandatory=$true^)][string]$img,
echo   [string]$out = ""
echo ^)
echo.
echo $ErrorActionPreference = "Stop"
echo $repo = "C:\ai3d\TripoSR"
echo.
echo # Basic checks + nice window title
echo if ^(-not ^(Test-Path $img^)^) { throw "Image not found: $img" }
echo $Host.UI.RawUI.WindowTitle = "TripoSR - " + ^(Split-Path $img -Leaf^)
echo.
echo # Activate venv
echo . "$repo\.venv\Scripts\Activate.ps1"
echo.
echo # Pick output folder
echo if ^(-not $out^) {
echo   $imgDir = Split-Path $img -Parent
echo   $out = Join-Path $imgDir "output"
echo }
echo New-Item -ItemType Directory -Force -Path $out ^| Out-Null
echo.
echo # Show progress messages
echo Write-Host "[*] Image: $img"
echo Write-Host "[*] Output: $out"
echo Write-Host "[*] Forcing CPU ^(stable on your setup^)..."
echo $env:CUDA_VISIBLE_DEVICES = ""
echo.
echo # Run with unbuffered Python
echo Write-Host "[*] Running TripoSR... this may take a few minutes."
echo Set-Location $repo
echo try {
echo   ^& python -u run.py "$img" --output-dir "$out" --bake-texture --texture-resolution 512
echo   if ^($LASTEXITCODE -ne 0^) { throw "python exited with code $LASTEXITCODE" }
echo   Write-Host "`n✅ Done: $img" -ForegroundColor Green
echo   Write-Host "   Output: $out ^(mesh.obj + textures^)" -ForegroundColor Green
echo }
echo catch {
echo   Write-Host "`n❌ Failed: $img" -ForegroundColor Red
echo   Write-Host $_.Exception.Message -ForegroundColor Red
echo   exit 1
echo }
) > run_fast.ps1

REM Set PowerShell execution policy
echo Setting PowerShell execution policy...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"

echo.
echo ===============================================
echo    Installation Complete! 🎉
echo ===============================================
echo.
echo Your TripoSR Web Interface is ready to use:
echo.
echo 📁 Installation Directory: C:\ai3d\
echo 🌐 Web Interface: C:\ai3d\triposr-web-interface\
echo 🤖 TripoSR Engine: C:\ai3d\TripoSR\
echo.
echo 🚀 To start the web interface:
echo    1. cd C:\ai3d\triposr-web-interface\src
echo    2. python app.py
echo    3. Open: http://127.0.0.1:5000
echo.
echo 📋 Test TripoSR directly:
echo    cd C:\ai3d\TripoSR
echo    .venv\Scripts\activate
echo    python run.py path\to\image.jpg
echo.

REM Create start script
echo Creating start.bat for easy launching...
cd /d "C:\ai3d\triposr-web-interface"
(
echo @echo off
echo title TripoSR Web Interface
echo cd /d "C:\ai3d\triposr-web-interface\src"
echo echo Starting TripoSR Web Interface...
echo echo Open your browser to: http://127.0.0.1:5000
echo echo.
echo python app.py
echo pause
) > start.bat

echo 💡 Quick Start: Double-click start.bat to launch the web interface
echo.
pause