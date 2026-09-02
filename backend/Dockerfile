FROM python:3.13-slim@sha256:9d2e5553305c7c7b0097999bb17187c69b921ccd6bc9d40e4bb5ebe652c00285
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
COPY --from=ghcr.io/astral-sh/uv:0.11.32@sha256:df4cae8f3a96d175e2e5f992e597550000edbe78fdc2594d5cd8de1a217f504c /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app
USER appuser
EXPOSE 8000
# --proxy-headers: HTTPS 종단은 Traefik이고 컨테이너에는 평문으로 도달한다.
# 없으면 무한 리다이렉트, 잘못된 절대 URL, CSRF 실패가 생긴다(배포 규약 R6-2).
ENTRYPOINT []
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*' --limit-concurrency 100"]
