# Samwoo Vibe 개발 규칙

이 저장소에서 작업하는 AI 코딩 도구와 사람은 아래 규칙을 따른다.
요청이 불명확하거나 운영 데이터·보안·아키텍처에 영향을 주면 추측하지 말고 먼저
사용자에게 확인한다.
README는 사람을 위한 프로젝트 소개와 실행 안내다. 작업 규칙은 이 문서를 단일
기준으로 삼으며, 작업을 시작할 때 이 문서를 끝까지 먼저 읽는다.

## 로컬 프로젝트에 규칙 파일 정착

- 이 템플릿을 clone하지 않고 참고 자료로만 사용해 별도 로컬 프로젝트에서 개발을
  시작하는 경우에도, 실제 작업을 시작하기 전에 그 프로젝트 루트에 `AGENTS.md`가
  있는지 확인한다.
- 로컬 프로젝트 루트에 `AGENTS.md`가 없다면 이 템플릿의 최신 `AGENTS.md`를 파일명과
  내용을 유지해 복사한 뒤 작업한다. 링크만 남기거나 현재 대화에 규칙을 임시로 붙여
  넣는 것으로 대신하지 않는다.
- 이미 로컬 `AGENTS.md`가 있다면 무조건 덮어쓰지 않는다. 기존 프로젝트 고유 규칙과
  이 템플릿의 필수 배포·보안·데이터·인증 규칙을 비교하고, 충돌하거나 누락된 내용은
  사용자에게 알린 뒤 안전하게 병합한다.
- 복사된 `AGENTS.md`는 프로젝트 소스와 함께 유지한다. 새 세션이나 다른 AI 코딩
  도구가 작업을 이어 갈 때도 가장 먼저 이 파일을 끝까지 읽어야 하며, 프로젝트 구조나
  정책이 달라졌다면 같은 변경에서 문서도 갱신한다.

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

## 기본 UI 디자인

- 사용자가 별도의 디자인, 브랜드 또는 기존 화면 유지를 요청하지 않았다면
  [`samwoo-vibe/samwoo-ui-standard`](https://github.com/samwoo-vibe/samwoo-ui-standard)의
  최신 기본 브랜치를 **기본 UI 디자인 기준**으로 적용한다.
- 사용자가 다른 디자인, 디자인 시스템, 참고 화면 또는 기존 UI 유지를 명시했다면
  SAMWOO UI Standard를 강제로 섞지 않고 사용자의 요청을 우선한다.
- UI 작업을 시작하기 전에 표준 저장소의 `AGENTS.md`, `docs/DESIGN_SYSTEM.md`,
  `docs/UI_CHECKLIST.md`, `docs/DEPLOYMENT_CACHE.md`, `src/styles/tokens.css`와
  `src/components/`를 확인한다. 출처 저장소에 접근할 수 없으면 임의로 비슷하게 만들지
  말고 사용자에게 알려야 한다.
- 표준 저장소의 디자인 토큰, 공통 컴포넌트, 로고·파비콘과 반응형·접근성 패턴을 현재
  프로젝트의 `frontend/` 안으로 가져와 제품 기능에 맞게 구성한다. 표준 저장소를 런타임
  CDN이나 외부 Git 저장소에 의존하게 만들지 말고 배포 소스가 자체 완결적이어야 한다.
- 표준 저장소의 갤러리용 화면, 문구, 서비스 목록과 예시 수치는 복사하지 않는다.
  프로젝트의 실제 기능과 정보 구조로 교체하며, 화면 검증용 콘텐츠가 필요하면 실제 회사
  데이터가 아닌 합성 한국어 데이터를 사용한다.
- UI를 적용하면서 이 템플릿의 `/api` 호출 경로, Vite proxy, Nginx 설정, Dockerfile,
  health check와 Coolify 배포 계약을 덮어쓰지 않는다. UI 파일과 배포 파일의 책임을
  구분하고 필요한 부분만 병합한다.
- 기본 적용 완료 후 라이트·다크 테마, loading·empty·error·disabled 상태, 키보드
  포커스, reduced motion과 320px 이상 반응형 화면을 확인하고 `npm run typecheck`와
  `npm run build`를 통과시킨다.

## 사내 배포 규약

배포 규약 전문은 사내 문서 **`마이그레이션 규칙.md`** 에 있다(관리자 보관). 이 템플릿은
그 규약을 이미 만족한 상태로 배포된다. 아래는 **깨뜨리면 배포가 실패하거나 조용히
잘못 동작하는 항목**이므로 임의로 바꾸지 않는다.

- `samwoo-service.yaml`의 `public_service: frontend` / `public_port: 8080` 조합은
  프로비저너 허용 목록에 등록된 값이다. 바꾸면 배포가 거부된다. 매니페스트가 잘못되면
  GitHub에는 성공으로 보이고 배포만 조용히 안 되므로, 배포 담당자가 push한 경우
  도메인을 직접 확인한다.
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
- 엑셀·CSV·문서·기존 시스템 추출본을 포함한 **실제 회사 데이터는 어떤 형태로도
  소스코드에 하드코딩하거나 저장소에 넣지 않는다.** frontend 정적 자산, backend
  상수, 테스트 fixture, seed, migration, 주석과 문서도 예외가 아니다.
- 실제 데이터가 필요한 기능은 PostgreSQL, 사용자가 실행 시 업로드하는 파일 또는
  담당자가 승인한 외부 저장소에서 읽도록 구현한다. 로컬에서 쓰는 실제 데이터 파일은
  저장소 밖이나 Git에서 제외된 `local-data/`에 두며 배포 인계본에는 포함하지 않는다.
- 예제와 테스트에는 실제 데이터의 일부를 복사하거나 단순히 이름만 가린 값을 쓰지
  않는다. 현실의 사람·거래·설비와 연결되지 않는 최소한의 합성 데이터만 사용한다.
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

## 기본 로그인 인증

- 사용자가 별도의 로그인 방식이나 인증 체계를 명시하지 않았다면, 완성되는 앱에는
  **회사 메일 계정을 이용한 IMAP 로그인**을 기본으로 구현한다. 회원가입, 별도 비밀번호
  생성과 자체 비밀번호 저장 기능은 만들지 않는다.
- 사용자가 자체 로그인, SSO, OAuth 등 다른 인증 방식을 명시했다면 이 기본 IMAP 규칙은
  적용하지 않고 사용자가 요청한 인증 방식을 구현한다. 두 로그인 체계를 임의로 함께
  만들지 않는다.
- 로그인 화면에서 회사 이메일 주소와 비밀번호를 입력받고, backend가
  `play.samwooeleco.com:993`에 SSL/TLS로 IMAP 로그인을 실제 시도해 성공 여부를
  확인한다. frontend가 IMAP 서버에 직접 접속하면 안 된다.
- IMAP은 로그인 인증에만 사용한다. 메일함 목록·본문·첨부파일을 읽거나 메일을 검색,
  변경, 삭제 또는 발송하는 기능은 구현하지 않는다. SMTP 연결도 만들지 않는다.
- 메일 비밀번호는 IMAP 인증 요청 동안에만 메모리에서 사용하고 즉시 버린다. DB, 파일,
  캐시, session, token, 로그, 오류 메시지, 모니터링 도구 또는 브라우저 저장소에
  저장하지 않는다. 요청 body나 IMAP 명령 전체를 로깅하지 않는다.
- TLS 인증서 검증을 끄지 않고 연결·인증 timeout을 둔다. IMAP 연결은 성공·실패와
  관계없이 종료하고, blocking IMAP 호출로 async event loop를 막지 않도록 threadpool
  등으로 격리한다.
- 인증 성공 후에는 비밀번호가 들어 있지 않은 서버측 session 또는 안전한 token으로
  로그인 상태를 유지한다. 쿠키를 사용하면 `HttpOnly`, `Secure`, 적절한 `SameSite`,
  만료시간을 설정하고 로그아웃 시 무효화한다. 상태 변경 요청에는 CSRF 방어를 적용한다.
- 로그인 endpoint에는 사용자·IP 기준 rate limit과 반복 실패 지연을 적용한다. 계정 존재
  여부, 비밀번호 오류, IMAP 장애를 구분해 노출하지 않는 일반화된 오류 메시지를 사용한다.
  인증 실패 응답이나 로그에 이메일 주소 전체와 비밀번호를 남기지 않는다.
- 로그인하지 않은 사용자는 health check와 로그인에 필요한 endpoint·정적 자산 외의
  화면과 API를 사용할 수 없어야 한다. frontend 표시만 숨기지 말고 backend의 모든 보호
  API에서 session 또는 token을 검증한다.

## 작업 및 검증

- 시작 전 이 문서와 `compose.yaml`, 관련 코드를 읽고 기존 구조를 우선한다.
- 프로젝트 이름, 목적, 대상 사용자와 주요 기능을 요청에서 파악한다. 보안·데이터·배포
  방식에 영향을 주는 중요한 내용만 불명확할 때 사용자에게 확인한다.
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
- 바이브코딩 작업 중에는 원본 템플릿이나 어떤 GitHub 저장소에도 commit·push하지
  않는다. 관리자가 검토 후 별도 private 앱 저장소를 만들고 승인본을 push한다.
- 사용자가 배포 의사를 명확히 밝히기 전에는 인계 ZIP을 만들거나 배포 절차를 진행하지
  않는다. 로컬 실행과 기능 검증까지만 완료한다.
- 사용자가 배포를 원하면 검증을 마친 뒤 필요한 소스코드와 배포 설정만 담은 인계 ZIP을
  만들고, 그 압축파일을 배포 담당자에게 전달하라고 안내한다. 전달 경로나 특정 파일
  공유 서비스는 지정하지 않는다.
- push 전에 `compose.yaml`, `samwoo-service.yaml`, frontend/backend `Dockerfile`,
  `frontend/package-lock.json`, `backend/uv.lock`, `backend/migrations/`가 유지되는지
  확인한다.
- 기본 `main` 브랜치 push는 Coolify 개발 환경에 자동 배포된다.
- 운영 배포는 별도 환경과 담당자 승인 없이는 수행하지 않는다.
- 배포 시 backend가 `alembic upgrade head`에 성공한 뒤 시작되어야 한다.
- 자동 배포 설정, 중앙 DB network, 도메인 규칙을 임의로 우회하지 않는다.

## 배포 인계 ZIP (사용자가 배포를 원할 때만)

사용자가 배포를 요청한 경우에만, 개발과 검증을 마친 뒤 배포 담당자가 새 저장소에
바로 반영할 수 있는 소스 전용 ZIP을 만든다.

```bash
uv run --frozen --project backend python scripts/export_handoff.py --project-name 프로젝트명
```

스크립트는 `_handoff/<프로젝트명>-source.zip`을 만든다. ZIP 내부에는
`frontend/`, `backend/`, `compose.yaml`, `samwoo-service.yaml`, lockfile, migration 등
빌드·검증·배포에 필요한 파일이 최상위에 바로 들어가며, `<프로젝트명>-source/` 같은
래퍼 폴더를 만들지 않는다. 사용자에게 이 ZIP을 배포 담당자에게 전달하라고 안내한다.

`.git`, `.env`, 토큰·비밀번호·키, `node_modules`, `.venv`, 빌드 결과, 캐시, 로그,
로컬 DB, 업로드 파일, 엑셀·CSV 등의 실제 데이터는 ZIP에 포함하지 않는다. 실제 값을
코드에 하드코딩해 파일 확장자 검사를 우회해서도 안 된다. 스크립트가 실패하거나 필수
파일이 누락되면 인계 완료로 보고하지 않는다.

## 완료 조건

- 변경한 범위의 backend 의존성 동기화와 관련 테스트·health 검증 성공
- frontend를 변경했다면 `npm run typecheck`와 `npm run build` 성공
- DB 스키마를 변경했다면 migration 생성·적용 성공
- gitleaks 검사 성공
- `.env`, 실제 자격증명과 `DATABASE_URL`이 Git 추적 대상이 아님
- 실제 회사 데이터가 코드·문서·테스트·정적 자산·migration과 Git 추적 대상에 없음
- 별도 인증 요구가 없다면 회사 메일 IMAP 로그인과 backend API 인증 검증이 동작하고,
  비밀번호 비저장·로그 마스킹·rate limit·session 보안 테스트가 통과함
- 사용자가 다른 인증 방식을 명시했다면 IMAP 로그인을 추가하지 않고 요청한 방식의
  로그인·인가 테스트가 통과함
- 별도 디자인 요구가 없다면 SAMWOO UI Standard의 토큰·브랜드 자산·공통 컴포넌트와
  접근성·반응형 기준이 적용되고, 갤러리용 예시 콘텐츠는 남아 있지 않음
- 사용자가 다른 디자인이나 기존 UI 유지를 명시했다면 SAMWOO UI Standard를 강제로
  혼합하지 않고 요청한 디자인 기준을 따름
- `README.md`가 React/FastAPI Template 설명이 아니라 현재 프로젝트를 설명함
- 원본 템플릿의 공개 remote에 push하지 않음
- 사용자가 배포를 요청한 경우에만 인계 ZIP 생성 명령이 성공하고, ZIP 최상위에
  `compose.yaml`과 `samwoo-service.yaml`이 존재하며, 배포 담당자에게 전달하도록 안내함
- 배포 담당자가 별도 앱 저장소에 승인본을 push한 경우에만 Coolify 자동 배포를 확인함
- frontend Nginx가 SPA 진입 문서는 재검증하고 `/api/`는 `no-store`, 해시된
  `/assets/`만 `immutable`로 제공하는 캐시 계약을 유지함
