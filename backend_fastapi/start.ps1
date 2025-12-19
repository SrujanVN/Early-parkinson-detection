# Quick Start Script for FastAPI Backend
# Run this script to start the server

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "="*59 -ForegroundColor Cyan
Write-Host "Parkinson's Disease Detection - FastAPI Backend" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "="*59 -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "[WARNING] .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "[ACTION REQUIRED] Please edit .env and add your GEMINI_API_KEY" -ForegroundColor Red
    Write-Host "Get your API key from: https://makersuite.google.com/app/apikey" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter after adding your API key to continue"
}

# Check if models directory exists
if (-not (Test-Path "models")) {
    Write-Host "[ERROR] Models directory not found!" -ForegroundColor Red
    Write-Host "Please copy models from ../backend/models" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Checking Python version..." -ForegroundColor Cyan
python --version

Write-Host ""
Write-Host "[INFO] Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "="*59 -ForegroundColor Cyan
Write-Host "Starting FastAPI Server..." -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "="*59 -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

# Start server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
