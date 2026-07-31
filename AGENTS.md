# Samwoo Vibe 개발 규칙

이 저장소에서 작업하는 AI 코딩 도구와 사람은 아래 규칙을 따른다.
요청이 불명확하거나 운영 데이터·보안·아키텍처에 영향을 주면 추측하지 말고 먼저
사용자에게 확인한다.
README는 사람을 위한 프로젝트 소개와 실행 안내다. 작업 규칙은 이 문서를 단일
기준으로 삼으며, 작업을 시작할 때 이 문서를 끝까지 먼저 읽는다.

## 고정 아키텍처

- 배포 경로: Coolify Traefik → frontend(Nginx/React) → backend(FastAPI) → PostgreSQL
- Traefik은 공개 도메인·HTTPS·라우팅을 담당한다.
- frontend Nginx는 React 정적 파일을 제공하고 `/api/`를 backend로 전달한다.
- 배포용 `compose.yaml`에 PostgreSQL 컨테이너나 호스트 포트를 추가하지 않는다.
- backend는 외부 Docker network `samwoo-postgres-prod`를 통해 중앙 PostgreSQL에
  접속하며 접속정보는 `DATABASE_URL`로만 받는다.
- Windows 개발 PC에는 Docker·WSL을 요구하지 않는다. 로컬 개발 DB는 Windows에
  설치한 PostgreSQL을 사용한다.
- 로컬 React는 Vite 개발 서버와 내장 `/api` proxy를 사용한다. Windows에 Nginx나
  Traefik을 설치하도록 안내하지 않는다.

## 기술 기준

- Frontend: React 19, Vite, TypeScript/TSX(strict), npm
- Backend: Python 3.13, FastAPI, SQLAlchemy 2, Alembic, psycopg 3, uv
- Database: PostgreSQL 17
- Deployment: Docker Compose, Coolify, Traefik
- Python 의존성은 `backend/pyproject.toml`과 `backend/uv.lock`으로 관리한다.
  `pip install`이나 `requirements.txt`를 새 표준으로 추가하지 않는다.

## 변경 규칙

- 기존 frontend/backend 서비스명, `/api/` 경로, `/health`, `/healthz`를 임의로
  바꾸지 않는다. 바꿔야 하면 Compose·Nginx·health check를 함께 수정한다.
- DB 스키마 변경은 SQLAlchemy 모델과 Alembic migration으로 함께 남긴다.
- 운영 또는 공유 DB에서 테이블을 직접 수정하거나 migration history를 삭제하지 않는다.
- destructive migration, 데이터 삭제, DB·role 삭제는 사전 승인을 받는다.
- `.env`, 비밀번호, API token, SSH key, 실제 `DATABASE_URL`을 코드·로그·문서·Git에
  넣지 않는다. 예시는 가짜 값만 사용한다.
- 커밋 전에 gitleaks 검사를 통과시킨다. 탐지 결과를 무시하거나 allowlist에 추가하려면
  담당자 승인을 받는다.
- frontend에 DB 접속정보를 넣거나 브라우저에서 PostgreSQL에 직접 접속하지 않는다.
- 외부 패키지는 꼭 필요한 경우에만 추가하고 lockfile을 함께 갱신한다.
- 서비스별 512MB 메모리 제한과 backend의 비특권 사용자를 유지한다.

## 작업 및 검증

- 시작 전 이 문서와 `compose.yaml`, 관련 코드를 읽고 기존 구조를 우선한다.
- 프로젝트 이름, 목적, 대상 사용자, 주요 기능과 성공 기준을 사용자와 먼저 확정한다.
- 구현 전에 변경 범위와 인수 조건을 제시하고 사용자 확인을 받는다.
- DB 스키마를 변경할 때는 다음과 같이 migration을 생성하고 적용한다.

```powershell
Push-Location backend
uv run alembic revision --autogenerate -m "변경 설명"
uv run alembic upgrade head
Pop-Location
```

- 로컬 Python 준비: `Push-Location backend; uv sync; Pop-Location`
- backend 실행·migration은 `uv run`으로 수행한다.
- frontend 의존성은 `npm ci`, 개발 실행은 `npm run dev`를 사용한다.
- frontend 변경은 `npm run typecheck`와 `npm run build`를 통과해야 한다.
- 변경 범위에 맞게 최소한 backend health, frontend build, migration을 검증한다.
- 실패한 검증을 숨기지 말고 원인과 미검증 항목을 보고한다.
- 관련 없는 파일을 정리하거나 사용자의 변경을 덮어쓰지 않는다.

## 프로젝트 README

- 프로젝트 이름과 목적이 확정되면 템플릿 `README.md`를 실제 프로젝트 README로
  교체한다.
- 최종 README는 현재 프로젝트의 이름, 목적, 주요 기능, 로컬 준비 사항과 사용자
  실행 방법을 설명해야 한다.
- Golden Template 자체를 소개하는 문구와 현재 프로젝트에 불필요한 범용 설명을
  그대로 남기지 않는다.
- AI 코딩 에이전트가 작업 전에 `AGENTS.md`를 반드시 읽어야 한다는 안내는 유지한다.
- 실제 프로젝트에 적용되는 보안·데이터 주의사항은 유지한다.

## Git 및 배포

- 원본 템플릿 저장소 `samwoo-vibe/golden-template`에는 commit하거나 push하지 않는다.
- 배포 대상 remote는 `samwoo-vibe` 조직에 만든 별도 앱 저장소여야 한다.
- 검증 결과와 변경사항을 사용자에게 보여주고 명시적 승인을 받은 뒤에만 앱 저장소의
  `main` 브랜치에 commit·push한다.
- push 전에 `compose.yaml`, `samwoo-service.yaml`, frontend/backend `Dockerfile`,
  `frontend/package-lock.json`, `backend/uv.lock`, `backend/migrations/`가 유지되는지
  확인한다.
- 기본 `main` 브랜치 push는 Coolify 개발 환경에 자동 배포된다.
- 운영 배포는 별도 환경과 담당자 승인 없이는 수행하지 않는다.
- 배포 시 backend가 `alembic upgrade head`에 성공한 뒤 시작되어야 한다.
- 자동 배포 설정, 중앙 DB network, 도메인 규칙을 임의로 우회하지 않는다.

## 완료 조건

- backend 의존성 동기화와 관련 테스트·health 검증 성공
- frontend `npm run typecheck`와 `npm run build` 성공
- migration 적용 성공
- gitleaks 검사 성공
- `.env`, 실제 자격증명과 `DATABASE_URL`이 Git 추적 대상이 아님
- `README.md`가 Golden Template 설명이 아니라 현재 프로젝트를 설명함
- Git remote가 원본 템플릿이 아닌 별도 앱 저장소를 가리킴
- 배포 작업이면 사용자 승인 후 `main` push 성공을 확인함
