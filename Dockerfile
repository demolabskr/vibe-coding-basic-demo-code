# 운영 서버용 이미지. 앱 플랫폼(PaaS)이나 가상 서버에서 이 파일로 사이트를 띄운다
FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra postgres

COPY . .
RUN DJANGO_SECRET_KEY=build-only uv run --no-sync python manage.py collectstatic --noinput

# 비밀 값은 이미지에 넣지 않고, 플랫폼의 환경 변수로 받는다
CMD uv run --no-sync python manage.py migrate --noinput && \
    uv run --no-sync gunicorn config.wsgi --bind 0.0.0.0:${PORT:-8000} --access-logfile -
