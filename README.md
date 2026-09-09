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
8. 배포가 필요하면 AI 코딩 도구에 배포용 인계 ZIP 생성을 요청합니다. 생성된 ZIP은
   배포 담당자에게 전달합니다. 배포하지 않을 때는 ZIP을 만들 필요가 없습니다.

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

## 실제 데이터 사용 금지

엑셀·CSV·문서·기존 시스템 추출본 등 실제 회사 데이터를 소스코드, 테스트 데이터,
정적 파일, migration 또는 Git 저장소에 넣지 마세요. 코드에 값으로 직접 적는 것도
금지합니다. 예제와 테스트에는 실제 대상과 연결되지 않는 합성 데이터만 사용합니다.

기능상 실제 데이터가 필요하면 PostgreSQL이나 실행 시 업로드 방식으로 처리하고,
로컬 파일은 저장소 밖 또는 `local-data/`에 둡니다. `local-data/`와 실제 데이터는
배포용 ZIP에도 포함되지 않습니다.

## 기본 로그인

별도의 로그인 방식을 요청하지 않으면, 이 템플릿으로 만드는 앱은 회사 메일 계정으로
로그인하도록 구현합니다. 별도 회원가입은 없으며 backend가 아래 IMAP 서버에 로그인을
시도해 계정을 인증합니다.

- IMAP 서버: `play.samwooeleco.com`
- 포트: `993`
- 연결: SSL/TLS
- 용도: 사이트 로그인 인증만 사용

메일함 조회나 메일 발송 기능은 만들지 않습니다. 입력한 메일 비밀번호는 인증 시도에만
사용하고 저장하거나 로그에 남기지 않습니다. 인증 성공 후에는 비밀번호가 포함되지 않은
보안 session 또는 token으로 로그인 상태를 유지합니다.

자체 로그인, SSO, OAuth 등 다른 로그인 방식을 요청한 프로젝트에는 위 IMAP 방식을
추가하지 않고 요청한 인증 방식만 적용합니다.

## 배포

배포를 원할 때만 다음 명령으로 필요한 소스코드와 배포 설정을 압축합니다.

```powershell
uv run --frozen --project backend python scripts/export_handoff.py --project-name 프로젝트명
```

생성된 `_handoff/<프로젝트명>-source.zip`을 배포 담당자에게 전달하세요. ZIP에 `.env`,
비밀번호·토큰, 로컬 DB, 업로드 파일 또는 실제 업무 데이터가 들어가면 안 됩니다.
배포 담당자가 승인본을 별도 private 저장소의 `main`에 push하면 Coolify 개발 환경에
자동 배포됩니다. 운영 배포는 별도 승인 후 진행합니다.

Coolify 배포용 `compose.yaml`에는 PostgreSQL 컨테이너가 없습니다. 중앙
PostgreSQL의 앱 전용 database·role과 `DATABASE_URL`을 프로비저너가
생성·주입합니다.

이 템플릿의 `compose.yaml`, `samwoo-service.yaml`, Dockerfile과 Nginx 설정은 사내
Coolify 자동 배포 규약에 맞춰져 있습니다. 임의로 바꾸지 말고 자세한 기술 규칙은
`AGENTS.md`를 따르세요.

배포 주소 자체에는 회사 공용 HTTP Basic Auth가 적용되지 않습니다. 따라서 위 기본
IMAP 로그인 또는 사용자가 지정한 다른 인증 방식을 앱 안에 구현하고, backend API에서
권한을 검사해야 합니다. 인증 구현 전에는 실제 민감 데이터를 입력하지 마세요.
