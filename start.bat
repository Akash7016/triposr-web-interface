@echo off
title TripoSR Web Interface
cd /d "%~dp0src"
echo.
echo ===============================================
echo    TripoSR Web Interface
echo ===============================================
echo.
echo Starting web server...
echo Open your browser to: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.
python app.py
pause