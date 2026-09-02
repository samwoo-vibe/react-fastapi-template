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

## 사내 배포 규약

배포 규약 전문은 사내 문서 **`마이그레이션 규칙.md`** 에 있다(관리자 보관). 이 템플릿은
그 규약을 이미 만족한 상태로 배포된다. 아래는 **깨뜨리면 배포가 실패하거나 조용히
잘못 동작하는 항목**이므로 임의로 바꾸지 않는다.

- `samwoo-service.yaml`의 `public_service: frontend` / `public_port: 8080` 조합은
  프로비저너 허용 목록에 등록된 값이다. 바꾸면 배포가 거부된다. 매니페스트가 잘못되면
  GitHub에는 성공으로 보이고 배포만 조용히 안 되므로, push 후 도메인을 눈으로 확인한다.
- 각 컨테이너가 노출하는 포트는 정확히 하나여야 한다(`EXPOSE 8080`, `EXPOSE 8000`).
  관리·메트릭 포트를 추가로 열면 Traefik이 대상 포트를 정하지 못해 라우팅이 실패한다.
- Dockerfile의 공식 base image와 외부 `COPY --from` 이미지는 태그와 OCI digest를 함께
  고정한다. digest를 지우거나 임의 이미지로 바꾸면 동일 커밋 재빌드가 달라질 수 있고
  자동 배포 gate에서 거부된다.
- `compose.yaml`에 `ports:`를 쓰지 않는다(`expose:`만). 자체 `db:` 서비스를 추가하지
  않는다 - DB는 프로비저너가 중앙 PostgreSQL에 만들어 주고 `DATABASE_URL`로 주입한다.
- `container_name`을 지정하지 않는다. 무중단 교체 배포가 깨진다.
- backend는 `--proxy-headers`로 기동한다. HTTPS 종단은 Traefik이고 컨테이너에는 평문이
  도달한다(R6-2). 쿠키를 쓰면 `Secure`를 켠다(R6-3).
- 설정이 없을 때 조용히 다른 저장소로 넘어가는 코드를 만들지 않는다(R4-4).
  `DATABASE_URL`은 값이 없으면 즉시 실패해야 한다(`os.environ[...]`).
- 브라우저에 노출되는 값(`VITE_*`)은 **빌드 시점**에 주입해야 한다. 런타임에만 넣으면
  브라우저에서 `undefined`가 된다(R5-2). 비밀에는 공개 접두어를 붙이지 않는다(R5-3).
- 앱의 기준 URL은 프로비저너가 모든 서비스에 주입하는 `APP_BASE_URL`을 읽는다.
  공개 서비스에만 채워질 수 있는 `COOLIFY_URL`이나 도메인 하드코딩에 의존하지 않는다(R5-1).
- `APP_ENV`는 운영에서도 항상 `dev`다. 이 값으로 환경을 분기하지 않는다(R5-1).
- 시간은 시간대 인식 타입으로 저장하고 표시할 때만 변환한다(R9-1).
- 앱 볼륨은 자동 백업 대상이 아니다. 소실되면 안 되는 파일은 관리자에게 백업 등록을
  신청한다(R4-5).
- PostgreSQL role의 20 connection 제한과 rolling 배포 여유를 위해 backend pool의
  `pool_size=5`, `max_overflow=3`, `pool_timeout=5`를 유지한다. replica나 worker 수를
  늘릴 때는 전체 동시 연결 수를 먼저 계산한다.

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
- Coolify는 앱 환경 파일을 모든 Compose 서비스에 붙인다. backend 전용 비밀 키마다
  frontend `environment`에 비어 있지 않은 invalid sentinel을 둔다. `null`은 실제 값을
  상속하고 빈 문자열은 Coolify가 저장값으로 치환하므로 비밀 차단에 사용하지 않는다.
- 신규 자동 배포 앱은 기본 공개이며 회사 공용 HTTP Basic Auth가 없다. 개인정보나
  업무상 민감정보를 다루기 전에 앱 자체 인증·인가를 구현하고 API에서 권한을 검사한다.
- 프록시 뒤의 `request.client`나 `X-Forwarded-For`를 사용자 신원·권한의 근거로 쓰지
  않는다. 현재 Nginx는 외부에서 들어온 전달 체인을 덮어써 위조를 막기 때문에 실제 사용자
  IP를 보존하지 않는다.
- 외부 패키지는 꼭 필요한 경우에만 추가하고 lockfile을 함께 갱신한다.
- 서비스별 512MB·1 CPU·256 PID 제한과 모든 서비스의 명시적 비특권 사용자,
  `cap_drop: [ALL]`, `no-new-privileges`를 유지한다.

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
- backend 테스트는 `Push-Location backend; uv run pytest; Pop-Location`로 실행한다.
- backend Python 변경은 같은 디렉터리에서 `uv run ruff check .`와
  `uv run ruff format --check .`도 통과해야 한다.
- 변경 범위에 맞게 최소한 backend health, frontend build, migration을 검증한다.
- 실패한 검증을 숨기지 말고 원인과 미검증 항목을 보고한다.
- 관련 없는 파일을 정리하거나 사용자의 변경을 덮어쓰지 않는다.

## 프로젝트 README

- 프로젝트 이름과 목적이 확정되면 템플릿 `README.md`를 실제 프로젝트 README로
  교체한다.
- 최종 README는 현재 프로젝트의 이름, 목적, 주요 기능, 로컬 준비 사항과 사용자
  실행 방법을 설명해야 한다.
- React/FastAPI Template 자체를 소개하는 문구와 현재 프로젝트에 불필요한 범용 설명을
  그대로 남기지 않는다.
- AI 코딩 에이전트가 작업 전에 `AGENTS.md`를 반드시 읽어야 한다는 안내는 유지한다.
- 실제 프로젝트에 적용되는 보안·데이터 주의사항은 유지한다.

## Git 및 배포

- 원본 템플릿 저장소 `samwoo-vibe/react-fastapi-template`에는 commit하거나 push하지 않는다.
- 신규 작업은 공개 템플릿을 내려받은 로컬 작업 폴더에서 수행한다. 신규 앱 GitHub
  저장소 URL을 작업자에게 요구하지 않는다.
- 검증 결과와 변경사항을 사용자에게 보여준 뒤, 사용자가 결과물을 Nextcloud의
  `공유 자료/VibeCoding/<프로젝트명>/` 폴더에 직접 올려 관리자 검토를 받는다.
- 바이브코딩 작업 중에는 원본 템플릿이나 어떤 GitHub 저장소에도 commit·push하지
  않는다. 관리자가 검토 후 별도 private 앱 저장소를 만들고 승인본을 push한다.
- push 전에 `compose.yaml`, `samwoo-service.yaml`, frontend/backend `Dockerfile`,
  `frontend/package-lock.json`, `backend/uv.lock`, `backend/migrations/`가 유지되는지
  확인한다.
- 기본 `main` 브랜치 push는 Coolify 개발 환경에 자동 배포된다.
- 운영 배포는 별도 환경과 담당자 승인 없이는 수행하지 않는다.
- 배포 시 backend가 `alembic upgrade head`에 성공한 뒤 시작되어야 한다.
- 자동 배포 설정, 중앙 DB network, 도메인 규칙을 임의로 우회하지 않는다.

## Nextcloud 인계 ZIP

개발과 검증이 끝나면 관리자가 압축을 풀고 파일을 보충하지 않아도 새 저장소에
바로 Push할 수 있는 배포용 인계 ZIP을 만든다.

```bash
uv run --frozen --project backend python scripts/export_handoff.py --project-name 프로젝트명
```

스크립트는 `_handoff/<프로젝트명>-source.zip`을 만든다. ZIP 내부에는
`frontend/`, `backend/`, `compose.yaml`, `samwoo-service.yaml` 등 저장소에 필요한
파일이 최상위에 바로 들어가며, `<프로젝트명>-source/` 같은 래퍼 폴더를 만들지
않는다. 관리자는 이 ZIP을 새 private GitHub 저장소의 루트에 압축 해제한 뒤 파일을
이동하거나 추가하지 않고 `main`에 최초 Push한다.

`.git`, `.env`, 토큰·비밀번호·키, `node_modules`, `.venv`, 빌드 결과, 캐시, 로그,
로컬 DB와 실제 데이터는 ZIP에 포함하지 않는다. 스크립트가 실패하거나 필수 파일이
누락되면 인계 완료로 보고하지 않는다.

## 완료 조건

- backend 의존성 동기화와 관련 테스트·health 검증 성공
- frontend `npm run typecheck`와 `npm run build` 성공
- migration 적용 성공
- gitleaks 검사 성공
- `.env`, 실제 자격증명과 `DATABASE_URL`이 Git 추적 대상이 아님
- `README.md`가 React/FastAPI Template 설명이 아니라 현재 프로젝트를 설명함
- 원본 템플릿의 공개 remote에 push하지 않음
- Nextcloud 수동 인계를 위한 소스·테스트 보고서·변경 요약을 준비함
- `uv run --frozen --project backend python scripts/export_handoff.py --project-name 프로젝트명` 성공
- 인계 ZIP을 새 저장소 루트에 풀었을 때 `compose.yaml`과
  `samwoo-service.yaml`이 최상위에 존재함
- 관리자가 별도 앱 저장소에 승인본을 push한 경우에만 Coolify 자동 배포를 확인함
