"""Create a source-only React/FastAPI Template handoff package."""

from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

ROOT_FILES = (
    "README.md",
    "AGENTS.md",
    ".gitignore",
    "compose.yaml",
    "samwoo-service.yaml",
    ".env.example",
)
SOURCE_DIRECTORIES = (
    "frontend/src",
    "frontend/public",
    "backend/app",
    "backend/migrations",
    "backend/tests",
    "scripts",
)
SOURCE_FILES = (
    "frontend/.dockerignore",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/tsconfig.json",
    "frontend/tsconfig.app.json",
    "frontend/vite.config.ts",
    "frontend/index.html",
    "frontend/Dockerfile",
    "frontend/nginx.conf",
    "backend/.dockerignore",
    "backend/pyproject.toml",
    "backend/uv.lock",
    "backend/alembic.ini",
    "backend/Dockerfile",
)
REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    ".gitignore",
    ".env.example",
    "compose.yaml",
    "samwoo-service.yaml",
    "frontend/.dockerignore",
    "frontend/Dockerfile",
    "frontend/nginx.conf",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/vite.config.ts",
    "backend/.dockerignore",
    "backend/Dockerfile",
    "backend/pyproject.toml",
    "backend/uv.lock",
    "backend/alembic.ini",
    "backend/migrations/env.py",
    "backend/tests/test_deployment_contract.py",
    "backend/tests/test_proxy_contract.py",
    "scripts/export_handoff.py",
    "scripts/setup.ps1",
    "scripts/start-backend.ps1",
    "scripts/start-frontend.ps1",
)
EXCLUDED_PARTS = {
    ".git",
    ".ssh",
    ".venv",
    "node_modules",
    "dist",
    "_handoff",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "data",
}
SECRET_NAME = re.compile(
    r"(^|[._-])(secrets?|token|password|passwd|credentials?|private[-_]?key|"
    r"api[-_]?key|access[-_]?key|client[-_]?secret)([._-]|$)",
    re.IGNORECASE,
)
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"}
SECRET_FILENAMES = {
    ".netrc",
    ".npmrc",
    ".pypirc",
    "credentials",
    "credentials.json",
    "credentials.toml",
    "credentials.yaml",
    "credentials.yml",
    "id_ed25519",
    "id_ed25519_sk",
    "id_ecdsa",
    "id_ecdsa_sk",
    "id_ed448",
    "id_dsa",
    "id_rsa",
    "id_xmss",
    "secrets",
    "secrets.json",
    "secrets.toml",
    "secrets.yaml",
    "secrets.yml",
}


def project_name(raw: str) -> str:
    value = re.sub(r"[^A-Za-z0-9가-힣._-]+", "-", raw.strip()).strip(".-")
    if not value:
        raise ValueError("프로젝트 이름에 사용할 수 있는 문자가 없습니다.")
    return value


def sensitive(path: Path) -> bool:
    name = path.name.lower()
    return bool(
        name.startswith(".env")
        and name != ".env.example"
        or name in SECRET_FILENAMES
        or path.suffix.lower() in SECRET_SUFFIXES
        or SECRET_NAME.search(path.name)
    )


def excluded(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return True
    if sensitive(path):
        return True
    name = path.name.lower()
    # Treat backup/copy variants (for example ``prod.db.bak`` and
    # ``cache.sqlite.copy``) as database artifacts too. Checking only the final
    # suffix would otherwise package a full local database under a second
    # extension.
    if ".db" in name or ".sqlite" in name:
        return True
    return path.suffix.lower() in {
        ".db",
        ".sqlite",
        ".sqlite3",
        ".log",
        ".pyc",
        ".tmp",
    } or name.endswith(
        (
            ".db-shm",
            ".db-wal",
            ".db-journal",
            ".sqlite-shm",
            ".sqlite-wal",
            ".sqlite-journal",
            ".sqlite3-shm",
            ".sqlite3-wal",
            ".sqlite3-journal",
        )
    )


def copy_tree(source: Path, destination: Path) -> None:
    if source.is_symlink():
        raise ValueError(f"심볼릭 링크는 인수인계본에 포함할 수 없습니다: {source}")
    if sensitive(source):
        raise ValueError(f"비밀 가능성이 있는 파일을 먼저 확인·제거하세요: {source}")
    if source.is_dir():
        for child in sorted(source.iterdir()):
            relative = child.relative_to(source)
            if sensitive(child):
                raise ValueError(f"비밀 가능성이 있는 파일을 먼저 확인·제거하세요: {child}")
            if not excluded(relative):
                copy_tree(child, destination / relative)
        return
    if not source.is_file():
        raise ValueError(f"일반 파일이 아닌 항목은 인수인계본에 포함할 수 없습니다: {source}")
    if excluded(source):
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def write_handoff(root: Path, output: Path, name: str) -> None:
    for relative_name in ROOT_FILES + SOURCE_FILES:
        source = root / relative_name
        if source.is_file():
            copy_tree(source, output / relative_name)
    for relative_name in SOURCE_DIRECTORIES:
        source = root / relative_name
        if source.is_dir():
            copy_tree(source, output / relative_name)
    (output / "SOURCE-HANDOFF.md").write_text(
        f"""# {name} 소스코드 인수인계

이 묶음은 React/FastAPI Template 기반 앱을 관리자에게 검토받기 위한 소스 전달본이다.
운영 데이터나 비밀값을 포함하지 않는다.

## 포함

- React/Vite frontend 소스와 정적 자산
- FastAPI backend 소스와 Alembic migration
- Compose, 서비스 manifest, Dockerfile, lockfile
- 현재 작업의 README와 AGENTS 규칙

## 제외

- `.git` 이력과 remote
- `.env`, 토큰, 비밀번호, 키와 인증서
- `node_modules`, Python 가상환경, 빌드 결과와 캐시
- 로컬 DB, 업로드 파일, 로그와 실제 회사 데이터

사용자는 이 폴더 또는 ZIP을 Nextcloud의
`공유 자료/VibeCoding/<프로젝트명>/`에 직접 업로드하고, 관리자는 검토 후 별도
private GitHub 저장소를 만든다.
""",
        encoding="utf-8",
    )


def validate(output: Path) -> list[Path]:
    for relative_name in REQUIRED_FILES:
        if not (output / relative_name).is_file():
            raise ValueError(f"배포 필수 파일이 없습니다: {relative_name}")
    files = sorted(path for path in output.rglob("*") if path.is_file())
    if not (output / "SOURCE-HANDOFF.md").is_file():
        raise ValueError("SOURCE-HANDOFF.md가 없습니다.")
    if not any((output / "frontend/src").rglob("*")):
        raise ValueError("frontend/src가 비어 있습니다.")
    if not any((output / "backend/app").rglob("*")):
        raise ValueError("backend/app이 비어 있습니다.")
    if not any((output / "backend/migrations/versions").glob("*.py")):
        raise ValueError("인수인계 결과에 Alembic migration revision이 없습니다.")
    for path in files:
        relative = path.relative_to(output)
        if excluded(relative):
            raise ValueError(f"제외 대상 파일이 포함되었습니다: {relative}")
    return files


def make_zip(output: Path, archive: Path) -> None:
    # The archive is extracted directly into the new repository root. Do not
    # add the local ``<project>-source`` directory as a wrapper folder.
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(output.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(output))


def validate_output_dir(root: Path, output_dir: Path) -> None:
    """Prevent an export directory from recursively becoming its own input."""
    handoff_root = (root / "_handoff").resolve()
    if output_dir.is_relative_to(root) and not output_dir.is_relative_to(handoff_root):
        raise ValueError("프로젝트 내부 출력은 _handoff 아래에만 만들 수 있습니다.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-name")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    name = project_name(args.project_name or root.name)
    output_dir = (args.output_dir or root / "_handoff").resolve()
    validate_output_dir(root, output_dir)
    output = output_dir / f"{name}-source"
    archive = output_dir / f"{name}-source.zip"
    if output.exists() or archive.exists():
        print(f"기존 인수인계본이 있습니다. 확인 후 직접 치우세요: {output_dir}")
        return 2
    output.mkdir(parents=True)
    try:
        write_handoff(root, output, name)
        files = validate(output)
        make_zip(output, archive)
    except Exception:
        if output.exists():
            shutil.rmtree(output)
        if archive.exists():
            archive.unlink()
        raise
    print(f"폴더: {output}")
    print(f"Nextcloud ZIP (저장소 루트 직결): {archive}")
    print(f"포함 파일: {len(files)}개")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
