setlocal
set PYTHONIOENCODING=utf-8
@echo off

echo ======================================================
echo   JobExtractor - Production Launch System
echo ======================================================

REM 1. Initialize Environment
if not exist .env copy .env.example .env

REM 2. Check for Python Virtual Environment
if not exist venv python -m venv venv
call venv\Scripts\activate

REM 3. Start Infrastructure
docker version >nul 2>&1
if errorlevel 1 (
    echo [!] Docker is NOT running.
    echo [!] Starting in local-only mode.
    pause
) else (
    echo [!] Starting databases...
    docker compose up -d postgres redis elasticsearch
)

REM 4. Install Dependencies
echo [!] Checking dependencies...
pip install -q --prefer-binary -r apps/worker/requirements.txt
pip install -q --prefer-binary -r apps/api/requirements.txt

if not exist apps\web\node_modules (
    echo [!] Installing web dependencies...
    cd apps\web && call npm install && cd ..\..
)

if not exist node_modules (
    echo [!] Installing root dependencies...
    call npm install
)

REM 5. Launch
echo Launching Platform...
echo Dashboard: http://localhost:3001
echo API Docs:  http://localhost:8000/docs
echo ======================================================

npm start
