@echo off
echo ========================================
echo   SafeFind - Instant Deployment
echo ========================================
echo.
echo This will make your app accessible on the internet in 30 seconds!
echo.

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ngrok is not installed!
    echo.
    echo Please download ngrok from: https://ngrok.com/download
    echo Extract it and add to your PATH, or place ngrok.exe in this folder.
    echo.
    pause
    exit /b 1
)

echo [1/2] Starting SafeFind application...
start "SafeFind Server" cmd /k "python app_simple.py"

echo [2/2] Waiting for server to start...
timeout /t 5 /nobreak >nul

echo [3/3] Creating public URL with ngrok...
echo.
echo ========================================
echo   YOUR APP IS NOW LIVE!
echo ========================================
echo.
echo Copy the HTTPS URL from ngrok below and share it!
echo Press Ctrl+C to stop when done.
echo.

ngrok http 5000
