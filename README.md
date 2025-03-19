# FastAPI Service (a.k.a. pipeline-api)

This repository contains a Dockerized FastAPI service that provides a high-performance API.

## Features
- Runs a FastAPI application inside a Docker container
- Runs a Celery application as a orchestration instance,
acting as a task distributor.
- Supports automatic reloading in development mode
- Configurable via environment variables
- Ready for deployment with Docker Compose

## Requirements
- Docker

## Environment Variables
The following environment variables can be set:

| Variable                    | Description                                              | Default                  |
|-----------------------------|----------------------------------------------------------|--------------------------|
| `API_BEARER_TOKEN`          | A bearer token for frontend authentification             | None                     |
| `CELERY_BROKER_CONNECTION`  | URL of the message broker (Redis, RabbitMQ)              | None                     |
| `CELERY_BACKEND_CONNECTION` | URL of the backend for storing task results              | None                     |
| `CELERY_DEFAULT_QUEUE`      | Default queue name used by celery if no custom specified | `tasks`                  |
| `S3_ENDPOINT_URL`           | URL of the s3-like storage system                        | None                     |
| `S3_BUCKET_NAME`            | Name of s3-like bucket for dumping accepted data         | `raw-data`               |
| `S3_ACCESS_KEY_ID`          | Access key id to access private s3-like bucket(s)        | None                     |
| `S3_SECRET_ACCESS_KEY`      | Secret access key to access private s3-like bucket(s)    | None                     |

[All needed environment variables can copied from the file.](.env.example)
## Usage

### Build and Run with Docker
```sh
# Build the Docker image
docker build -t pipeline-api .

# Run the container
docker run -d \
  -p 8080:8080 \
  pipeline-api
```

### Docker Compose
To deploy with Docker Compose, create a `docker-compose.yml` file:

```yaml
services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
```

Run the service:
```sh
docker-compose up -d
```

## Logs and Monitoring
To check logs:
```sh
docker logs -f pipeline-api
```

## API Documentation
FastAPI provides interactive API documentation:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Contributing
Contributions are welcome! Feel free to submit a pull request or open an issue.
