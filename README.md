# Samwoo Vibe Golden Template

삼우에레코 시민 개발자를 위한 React + FastAPI + PostgreSQL 표준 템플릿입니다.

## 새 서비스 만들기

1. GitHub의 `Use this template`으로 `samwoo-vibe` 조직에 private 저장소를 만듭니다.
2. 기능을 개발하고 로컬 PostgreSQL로 테스트합니다.
3. 저장소를 Windows PC에 clone합니다.
4. PostgreSQL 17에 프로젝트 전용 로컬 DB와 role을 만듭니다.
5. PowerShell에서 `.\scripts\setup.ps1`을 실행합니다.
6. 생성된 `.env`의 `DATABASE_URL`을 로컬 DB 정보로 수정합니다.
7. 백엔드와 프런트엔드를 각각 실행합니다.

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

프런트엔드는 `http://127.0.0.1:5173`, API는
`http://127.0.0.1:8000`에서 실행됩니다.

## 데이터베이스 변경

테이블을 직접 수동 변경하지 않고 SQLAlchemy 모델과 Alembic migration으로
관리합니다.

```powershell
Push-Location backend
..\.venv\Scripts\alembic.exe revision --autogenerate -m "변경 설명"
..\.venv\Scripts\alembic.exe upgrade head
Pop-Location
```

DB 비밀번호와 `.env`는 Git에 올리지 않습니다.

## 배포

- feature 브랜치: 자동 배포하지 않음
- 기본 `main` 브랜치: Coolify 개발 환경 자동 배포
- 운영 배포: 별도 운영 환경에서 담당자 승인 후 진행

Coolify 배포용 `compose.yaml`에는 PostgreSQL 컨테이너가 없습니다. 중앙
PostgreSQL의 앱 전용 database·role과 `DATABASE_URL`을 프로비저너가
생성·주입합니다.

배포 시 backend가 `alembic upgrade head`를 실행한 뒤 FastAPI를 시작합니다.
frontend와 backend는 각각 512MB 메모리 제한과 health check를 사용합니다.
