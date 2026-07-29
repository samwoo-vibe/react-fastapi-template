$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    throw ".env가 없습니다. 먼저 .\scripts\setup.ps1을 실행하세요."
}

Get-Content ".env" | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]*)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
    }
}

Push-Location backend
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Pop-Location
