import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_handoff_exporter():
    path = ROOT / "scripts/export_handoff.py"
    spec = importlib.util.spec_from_file_location("react_handoff_exporter", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nginx_preserves_api_proxy_contract() -> None:
    nginx = read("frontend/nginx.conf")

    assert "location ~ ^/api(?:/|$)" in nginx
    assert "proxy_pass http://backend:8000;" in nginx
    assert "proxy_pass http://backend:8000/;" not in nginx
    assert "proxy_set_header X-Forwarded-Proto $public_scheme;" in nginx
    assert "proxy_set_header X-Forwarded-For $remote_addr;" in nginx
    assert "$proxy_add_x_forwarded_for" not in nginx
    assert "default $scheme;" in nginx
    assert "https   https;" in nginx


def test_nginx_supports_bounded_uploads_and_websockets() -> None:
    nginx = read("frontend/nginx.conf")

    assert "client_max_body_size 50m;" in nginx
    assert "proxy_set_header Upgrade $http_upgrade;" in nginx
    assert "proxy_set_header Connection $connection_upgrade;" in nginx
    assert "proxy_read_timeout 3600s;" in nginx
    assert "proxy_send_timeout 3600s;" in nginx


def test_vite_matches_production_api_and_websocket_routing() -> None:
    vite = read("frontend/vite.config.ts")

    assert '"^/api(?:/|$)"' in vite
    assert "rewrite:" not in vite
    assert "changeOrigin: false" in vite
    assert "ws: true" in vite


def test_compose_fails_closed_and_hides_database_from_frontend() -> None:
    compose = read("compose.yaml")

    assert 'DATABASE_URL: "__NOT_AVAILABLE_IN_FRONTEND__"' in compose
    assert "${COOLIFY_RESOURCE_UUID:?COOLIFY_RESOURCE_UUID must be provided by Coolify}" in compose
    assert compose.count("${APP_BASE_URL:?APP_BASE_URL must be configured in Coolify}") == 2


def test_frontend_uses_a_supported_unprivileged_nginx_release() -> None:
    dockerfile = read("frontend/Dockerfile")
    manifest = read("samwoo-service.yaml")
    nginx = read("frontend/nginx.conf")

    assert "FROM nginxinc/nginx-unprivileged:1.30.4-alpine" in dockerfile
    assert "EXPOSE 8080" in dockerfile
    assert "public_port: 8080" in manifest
    assert "listen 8080;" in nginx


def test_container_images_are_pinned_by_digest() -> None:
    backend = read("backend/Dockerfile")
    frontend = read("frontend/Dockerfile")

    assert backend.count("@sha256:") == 2
    assert frontend.count("@sha256:") == 2
    assert "COPY --from=ghcr.io/astral-sh/uv:0.11.32@sha256:" in backend


def test_docs_describe_public_by_default_access() -> None:
    readme = read("README.md")
    agents = read("AGENTS.md")
    frontend = read("frontend/src/main.tsx")

    assert "기본 공개" in readme
    assert "기본 공개" in agents
    assert "회사 공용 HTTP Basic Auth가 적용되지 않습니다" in readme
    assert "APP_BASE_URL" in agents
    assert "공개 방문자" in frontend
    assert "인증 미구현" in frontend
    assert "samwooax" not in frontend


def test_local_environment_defines_the_canonical_base_url() -> None:
    env_example = read(".env.example")

    assert "APP_BASE_URL=http://127.0.0.1:5173" in env_example


def test_compose_limits_cpu_for_every_service() -> None:
    compose = read("compose.yaml")

    assert compose.count('cpus: "1.0"') == 2
    assert compose.count("pids_limit: 256") == 2
    assert compose.count("- ALL") == 2
    assert compose.count("- no-new-privileges:true") == 2
    assert 'user: "101:101"' in compose
    assert 'user: "10001:10001"' in compose


def test_backend_bounds_concurrent_connections() -> None:
    dockerfile = read("backend/Dockerfile")

    assert "ENTRYPOINT []" in dockerfile
    assert "--limit-concurrency 100" in dockerfile


def test_postgresql_pool_fits_the_provisioned_role_limit() -> None:
    database = read("backend/app/db.py")

    assert "pool_size=5" in database
    assert "max_overflow=3" in database
    assert "pool_timeout=5" in database
    assert 'connect_args={"connect_timeout": 5}' in database
    assert '"connect_timeout": 5' in read("backend/migrations/env.py")


def test_frontend_does_not_depend_on_external_fonts() -> None:
    styles = read("frontend/src/styles.css")
    nginx = read("frontend/nginx.conf")

    assert "fonts.googleapis.com" not in styles
    assert 'add_header X-Content-Type-Options "nosniff" always;' in nginx
    assert 'add_header X-Frame-Options "DENY" always;' in nginx
    assert 'add_header Referrer-Policy "no-referrer" always;' in nginx


def test_handoff_rejects_environment_and_private_key_files(tmp_path: Path) -> None:
    exporter = load_handoff_exporter()

    assert exporter.excluded(Path(".env.production"))
    assert exporter.excluded(Path(".envrc"))
    assert exporter.excluded(Path("client-secret.txt"))
    assert exporter.excluded(Path("signing.key"))
    assert exporter.excluded(Path("id_ed25519"))
    assert exporter.excluded(Path(".ssh/id_ecdsa"))
    assert exporter.excluded(Path("config/secrets.toml"))
    assert exporter.excluded(Path("config/credentials.json"))
    assert exporter.excluded(Path(".aws/credentials"))
    assert exporter.excluded(Path("application_default_credentials.json"))
    assert exporter.excluded(Path("data/cache.sqlite-wal"))
    assert exporter.excluded(Path("data/cache.db-journal"))
    assert exporter.excluded(Path("backups/prod.db.bak"))
    assert exporter.excluded(Path("copies/cache.sqlite.copy"))
    assert not exporter.excluded(Path(".env.example"))
    sensitive_file = tmp_path / "client-secret.txt"
    sensitive_file.touch()
    with pytest.raises(ValueError, match="비밀 가능성"):
        exporter.copy_tree(sensitive_file, tmp_path / "exported.txt")


def test_dockerignore_excludes_nested_credentials() -> None:
    for relative_name in ("backend/.dockerignore", "frontend/.dockerignore"):
        dockerignore = read(relative_name)
        for pattern in (
            "**/.git",
            "**/.env",
            "**/.env.*",
            ".env*",
            "**/.env*",
            "**/*.pem",
            "**/.npmrc",
            "**/.ssh",
            "**/id_ed25519",
            "**/secrets.*",
            "**/credentials.*",
            "*.db*",
            "**/*.db*",
            "*.sqlite*",
            "**/*.sqlite*",
        ):
            assert pattern in dockerignore

    gitignore = read(".gitignore")
    assert "secrets.*" in gitignore
    assert "credentials.*" in gitignore
    assert "id_ed25519" in gitignore
    assert ".ssh/" in gitignore
    assert "*.sqlite-*" in gitignore
    assert "*.db*" in gitignore
    assert "*.sqlite*" in gitignore


def test_handoff_rejects_recursive_project_output() -> None:
    exporter = load_handoff_exporter()

    with pytest.raises(ValueError, match="_handoff"):
        exporter.validate_output_dir(ROOT, ROOT / "frontend" / "src" / "export")
