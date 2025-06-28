# --- Builder Stage [This stage installs dependencies into a venv] ---
FROM python:3.12-bookworm AS builder

# Set environment variables for Poetry initialisation
# https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Installing poetry
RUN pip install poetry
  
# Seting working directory
WORKDIR /app

# Copying the needed files to install dependencies
COPY poetry.lock pyproject.toml ./

# Install dependencies in the virtual environment
RUN poetry install --no-root --only main && rm -rf $POETRY_CACHE_DIR

# --- Final Stage [This stage copies the venv and application code] ---
FROM python:3.12-slim-bookworm AS runtime

# Same env files
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    PATH="/app/.venv/bin:$PATH" \
    FLASK_APP=app.py

# Seting working directory
WORKDIR /app

# Copying the before created venv
COPY --from=builder /app/.venv ./.venv

# Copying source code
COPY app.py config.py ./
COPY kusibot/ ./kusibot/
COPY deploy/docker-entrypoint.sh ./

# Making entrypoint script executable
RUN chmod +x ./docker-entrypoint.sh

# Run the entrypoint
ENTRYPOINT [ "./docker-entrypoint.sh" ]