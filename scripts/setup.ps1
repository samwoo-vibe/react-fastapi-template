$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env를 만들었습니다. 로컬 PostgreSQL 접속정보를 수정하세요."
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv가 없습니다. 먼저 'winget install --id=astral-sh.uv -e'를 실행하세요."
}

Push-Location backend
uv sync
Pop-Location
Push-Location frontend
npm ci
Pop-Location

Write-Host "설치 완료"
Write-Host "Backend: .\\scripts\\start-backend.ps1"
Write-Host "Frontend: .\\scripts\\start-frontend.ps1"
