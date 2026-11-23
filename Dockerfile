FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

RUN useradd --create-home --uid 1000 app && mkdir /app && chown app /app
WORKDIR /app
USER app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH"

COPY --chown=app pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=app weather ./weather
COPY --chown=app api ./api
COPY --chown=app frontend ./frontend
COPY --chown=app data ./data
COPY --chown=app main.py ./
RUN mkdir -p /app/db  # owned by app, so the compose volume is writable

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
