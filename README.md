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

1. 공개 템플릿을 내려받아 Windows PC의 새 로컬 작업 폴더에 풉니다.
2. 원본 템플릿의 Git 이력이나 remote를 작업 폴더에 가져오지 않습니다.
3. Node.js 22, PostgreSQL 17, uv를 준비합니다.
4. PostgreSQL에 프로젝트 전용 로컬 DB와 role을 만듭니다.
5. PowerShell에서 `.\scripts\setup.ps1`을 실행합니다.
6. 생성된 `.env`의 `DATABASE_URL`을 로컬 DB 정보로 수정합니다.
7. 백엔드와 프런트엔드를 실행하고 기능을 개발합니다.
8. 검증 후
   `uv run --frozen --project backend python scripts/export_handoff.py --project-name 프로젝트명`
   으로 인계본을 만들고 Nextcloud에 올립니다. 관리자가 검토한 뒤 별도 private 앱
   저장소를 만들고 승인된 소스만 `main`에 push합니다.

uv가 없다면 PowerShell에서 다음 명령으로 설치합니다.

```powershell
winget install --id=astral-sh.uv -e
```

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

프런트엔드는 `http://127.0.0.1:5173`, 프런트엔드를 통해 접근하는 API는
`http://127.0.0.1:5173/api`에서 실행됩니다. FastAPI 문서는
`http://127.0.0.1:5173/api/docs`에서 확인합니다.
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
frontend와 backend는 각각 512MB·1 CPU·256 PID 제한과 health check를 사용하며,
비특권 사용자·capability 제거·`no-new-privileges`로 실행됩니다. frontend의 비특권
Nginx는 컨테이너 내부 8080 포트를 사용하고 외부 HTTPS 주소는 그대로 Traefik이 제공합니다.
backend는 동시에 처리할 연결·작업을 100개로 제한해 과부하 시 무제한으로 메모리를
늘리는 대신 503으로 backpressure를 적용합니다.
Traefik에서 종료된 HTTPS 정보는 frontend Nginx가 보존하며, FastAPI는 외부 API
경로인 `/api`를 기준으로 리다이렉트와 OpenAPI 문서 URL을 생성합니다.
외부에서 주입한 `X-Forwarded-For`는 Nginx가 덮어쓰므로 backend의 client IP를
사용자 인증이나 권한 판단에 사용하면 안 됩니다.
API 요청 본문은 최대 50MiB이며 WebSocket은 로컬 Vite와 배포 Nginx에서 모두
전달됩니다. 앱의 기준 URL은 프로비저너가 `APP_BASE_URL`로 주입합니다.

자동 배포된 신규 앱은 기본 공개이며 회사 공용 HTTP Basic Auth가 적용되지 않습니다.
개인정보나 업무상 민감정보를 다루기 전에는 앱 안에 인증·인가를 구현하고 서버 API에서
권한을 검사해야 합니다. 인증 구현 전에는 실제 민감 데이터를 입력하지 마세요.
