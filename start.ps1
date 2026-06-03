# ============================================================
# start.ps1 — Chạy Backend + Frontend cùng lúc
# Cách dùng: .\start.ps1
# ============================================================

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Kiểm tra file .env
if (-not (Test-Path "$root\.env")) {
    Write-Host "[!] Chua co file .env — copy tu .env.example" -ForegroundColor Yellow
    Copy-Item "$root\.env.example" "$root\.env"
    Write-Host "[+] Da tao .env — mo file va dien API key truoc khi chay lai." -ForegroundColor Cyan
    exit
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Travel Chatbot — Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Backend ---
Write-Host "[1/2] Khoi dong Backend (port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    cd '$root\backend'
    if (-not (Test-Path 'venv')) {
        Write-Host 'Tao virtual environment...' -ForegroundColor Yellow
        python -m venv venv
    }
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt -q
    Write-Host ''
    Write-Host '>>> Backend chay tai http://localhost:8000' -ForegroundColor Cyan
    Write-Host ''
    uvicorn main:app --reload --port 8000
"@

# Doi backend khoi dong truoc
Start-Sleep -Seconds 3

# --- Frontend ---
Write-Host "[2/2] Khoi dong Frontend (port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    cd '$root\frontend'
    if (-not (Test-Path 'node_modules')) {
        Write-Host 'Cai npm packages...' -ForegroundColor Yellow
        npm install
    }
    Write-Host ''
    Write-Host '>>> Frontend chay tai http://localhost:3000' -ForegroundColor Cyan
    Write-Host ''
    npm run dev
"@

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Backend  : http://localhost:8000"
Write-Host " Frontend : http://localhost:3000"
Write-Host " API Docs  : http://localhost:8000/docs"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "2 terminal moi da duoc mo. Nhan Enter de dong cua so nay." -ForegroundColor Gray
Read-Host
