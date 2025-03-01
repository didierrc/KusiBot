# Using specific version of Python from Poetry toml.
FROM python:3.12

# Seting working directory
WORKDIR /app

# Installing Poetry
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Ensuring Poetry's bin directory is in PATH
ENV PATH="/root/.local/bin:${PATH}"

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Copying the poetry.lock and pyproject.toml files
COPY poetry.lock pyproject.toml README.md ./

# Copying application code
COPY kusibot ./kusibot/
COPY tests ./tests/

# Install dependencies
RUN poetry install --only main

# Expose Flask port
EXPOSE 5000

# Health check: Telling Docker how to test the container to check that it's still working.
HEALTHCHECK --interval=1m --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Run the Flask app
CMD ["poetry","run", "kusibot"]