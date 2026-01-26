FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# System dependencies (ffmpeg for yt-dlp)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

# Set ownership before any operations
RUN chown -R nonroot:nonroot /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_TOOL_BIN_DIR=/usr/local/bin \
    PORT=8008

# Switch to nonroot user for all subsequent operations
USER nonroot

# Install dependencies using lockfile (no project install yet)
RUN --mount=type=cache,target=/home/nonroot/.cache/uv,uid=999,gid=999 \
    --mount=type=bind,source=uv.lock,target=/app/uv.lock \
    --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
    uv sync --locked --no-install-project

# Copy source and install project
COPY --chown=nonroot:nonroot . /app
RUN --mount=type=cache,target=/home/nonroot/.cache/uv,uid=999,gid=999 \
    uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8008

ENTRYPOINT []

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008"]
