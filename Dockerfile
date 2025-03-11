FROM python:3.11-slim

WORKDIR /usr/src/app

# Use this space for installing any system dependencies (like curl etc.)
RUN apt-get update -y && \
    apt-get install -y \
    curl && \
    rm -rf /var/lib/apt/lists/*
###

# Install dependencies
RUN pip install poetry
RUN poetry self add poetry-plugin-export

COPY ./poetry.lock ./poetry.lock
COPY ./pyproject.toml ./pyproject.toml

RUN poetry export --without-hashes --format=requirements.txt > requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt
RUN opentelemetry-bootstrap -a install
###

# Copy project
COPY . .
###

# Open port(s) for internal communication only
EXPOSE 8080
###

# Start FastAPI application
ENTRYPOINT ["opentelemetry-instrument", "python3", "main.py"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8080/health || exit 1
