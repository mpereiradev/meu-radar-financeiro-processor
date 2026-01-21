# Use an official Python runtime as a parent image
# Using slim version for minimal image size
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # UV configuration
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Set work directory
WORKDIR /app

# Install uv
# Copy the installer from the official image or install via pip
# Using pip for simplicity and minimal layers if using slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependencies definitions
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: use uv.lock
# --no-dev: only production dependencies
# --no-install-project: we install the project code separately to cache dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy project files
COPY . .

# Install the project itself (if needed, or just run with pythonpath)
# Since we are not packaging it as a library, we can just run it.
# However, uv sync might have created a virtualenv.
# We place the virtualenv on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose port (default for uvicorn)
EXPOSE 8000

# Command to run the application
# Using shell form to allow variable expansion if needed, but array form is preferred for signal handling.
# However, to support WORKERS variable, we need shell or an entrypoint script.
# Let's use array form with a fixed command that reads env or defaults.
# Uvicorn doesn't read WORKERS env var by default, so we'll pass it.
# To keep strictly JSON array (best for signals), we hardcode workers to 1 or rely on shell.
# "Shutdown limpo (SIGTERM)" works best with exec.
# Best practice: Use `exec` in a flexible CMD or ENTRYPOINT.
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
