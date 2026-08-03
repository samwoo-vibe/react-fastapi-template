# Samwoo Vibe React/FastAPI Template

삼우에레코 시민 개발자를 위한 React + FastAPI + PostgreSQL 표준 템플릿입니다.

> AI 코딩 도구는 작업을 시작하기 전에 반드시 루트의 [`AGENTS.md`](AGENTS.md)를
> 먼저 읽고 따라야 합니다. 에이전트용 아키텍처·보안·DB migration·검증·배포
> 규칙은 README가 아니라 `AGENTS.md`를 기준으로 합니다.

## 기술스택

- Frontend: React 19 + Vite + TypeScript/TSX, npm
- Backend: Python 3.13 + FastAPI + SQLAlchemy 2 + Alembic + psycopg 3
- Python 패키지·가상환경: uv (`pyproject.toml` + `uv.lock`)
- Database: 로컬/중앙 PostgreSQL 17
- 배포: Docker Compose + Coolify Traefik
- React 파일·API 연결: frontend Nginx

## 새 서비스 만들기

1. GitHub의 `Use this template`으로 `samwoo-vibe` 조직에 private 저장소를 만듭니다.
2. 저장소를 Windows PC에 clone합니다.
3. Node.js 22, PostgreSQL 17, uv를 준비합니다.
4. PostgreSQL에 프로젝트 전용 로컬 DB와 role을 만듭니다.
5. PowerShell에서 `.\scripts\setup.ps1`을 실행합니다.
6. 생성된 `.env`의 `DATABASE_URL`을 로컬 DB 정보로 수정합니다.
7. 백엔드와 프런트엔드를 실행하고 기능을 개발합니다.

uv가 없다면 PowerShell에서 다음 명령으로 설치합니다.

```powershell
winget install --id=astral-sh.uv -e
```

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

프런트엔드는 `http://127.0.0.1:5173`, API는
`http://127.0.0.1:8000`에서 실행됩니다.
로컬에서는 Vite가 React를 제공하고 `/api` 요청을 FastAPI로 전달하므로 Nginx를
설치할 필요가 없습니다. Nginx는 서버 배포용 frontend 이미지 안에서만 실행됩니다.

## 배포

- feature 브랜치: 자동 배포하지 않음
- 기본 `main` 브랜치: Coolify 개발 환경 자동 배포
- 운영 배포: 별도 운영 환경에서 담당자 승인 후 진행

Coolify 배포용 `compose.yaml`에는 PostgreSQL 컨테이너가 없습니다. 중앙
PostgreSQL의 앱 전용 database·role과 `DATABASE_URL`을 프로비저너가
생성·주입합니다.

배포 시 backend가 `alembic upgrade head`를 실행한 뒤 FastAPI를 시작합니다.
frontend와 backend는 각각 512MB 메모리 제한과 health check를 사용합니다.
