Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  Ministry of Tribal Affairs (MoTA) Scholarship System" -ForegroundColor Yellow
Write-Host "  SIH Problem Statement 26239 - Starting Local Servers" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Backend in new window
Write-Host "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$baseDir\backend'; .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload"

# Start Frontend in new window
Write-Host "[2/2] Starting React (Vite) Frontend on http://127.0.0.1:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$baseDir\frontend'; npm run dev -- --host 127.0.0.1 --port 5173"

Write-Host "`nAll servers initiated!" -ForegroundColor Cyan
Write-Host "Open your browser at: http://127.0.0.1:5173" -ForegroundColor Yellow
Write-Host "API Documentation available at: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
