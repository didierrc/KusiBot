# Use a specific Python version as per your project's requirements
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Ensure Poetry's bin directory is in PATH
ENV PATH="/root/.local/bin:${PATH}"

# Install dependencies
RUN poetry env use python3.12
RUN poetry install

# Expose Flask port
EXPOSE 5000

# Run the Flask app
CMD ["poetry", "run", "python", "api/app.py"]