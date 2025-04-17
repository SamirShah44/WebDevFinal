# Create our initial image with our dependancies
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /deps
RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=./uv.lock,target=uv.lock \
	--mount=type=bind,source=./pyproject.toml,target=pyproject.toml \
	uv sync --frozen --no-install-project --no-dev

# Then, use a final image without uv
FROM python:3.13-slim-bookworm
RUN useradd -m app

# Copy the virtual environment from builder
COPY --from=builder --chown=app:app /deps/.venv /deps/.venv
ENV PATH="/deps/.venv/bin:$PATH"
WORKDIR /app

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]