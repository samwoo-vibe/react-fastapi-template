$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env를 만들었습니다. 로컬 PostgreSQL 접속정보를 수정하세요."
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Push-Location frontend
npm install
Pop-Location

Write-Host "설치 완료"
Write-Host "Backend: .\\scripts\\start-backend.ps1"
Write-Host "Frontend: .\\scripts\\start-frontend.ps1"

