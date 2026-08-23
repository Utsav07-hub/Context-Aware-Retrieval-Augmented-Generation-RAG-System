@echo off
title YT-RAG Launcher

set "ROOT=%~dp0"
set "BACKEND=%ROOT%context_backend"
set "FRONTEND=%ROOT%context_frontend"

echo.
echo ========================================
echo           YT-RAG STARTING
echo ========================================
echo.

echo [1/2] Starting FastAPI backend...
start "YT-RAG Backend" cmd /k "cd /d "%BACKEND%" && python -m uvicorn api.main:app --reload"

echo [2/2] Starting Next.js frontend...
start "YT-RAG Frontend" cmd /k "cd /d "%FRONTEND%" && npm run dev"

echo.
echo Waiting for backend...

:WAIT_BACKEND
powershell -NoProfile -Command "try { $r=Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing -TimeoutSec 1; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto WAIT_BACKEND
)

echo Backend is ready.
echo.
echo Opening frontend...
start "" "http://localhost:3000"

echo.
echo ========================================
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo ========================================
echo.