# HTTP Log Generator

A Python application that generates fake HTTP logs simulating nginx access logs for testing scaling systems.

## Features

- Configurable routes via YAML
- Adjustable request rate per route (logs per second)
- Configurable failure rate (HTTP 500 errors) per route
- Generates nginx-style access logs
- Runs in Docker
- Multi-threaded for concurrent route simulation
- Health check endpoint for Kubernetes (`/health` on port 8080)

## Configuration

Edit `config.yaml` to configure your routes:

```yaml
routes:
  - endpoint: "alfa"
    rate: 10      # 10 logs per second
    fail: 50      # 50% of requests return HTTP 500
  - endpoint: "beta"
    rate: 20      # 20 logs per second
    fail: 10      # 10% of requests return HTTP 500
  - endpoint: "gama"
    rate: 5       # 5 logs per second
    fail: 30      # 30% of requests return HTTP 500
```

### Configuration Options

- `endpoint`: The route name (will be logged as /endpoint)
- `rate`: Number of log entries per second
- `fail`: Percentage (0-100) of requests that should return HTTP 500

## Running with Docker

### Build and run with docker-compose:

```bash
docker-compose up --build
```

### Or build and run manually:

```bash
# Build the image
docker build -t log-generator .

# Run the container
docker run --rm log-generator
```

### View logs:

```bash
docker logs -f http-log-generator
```

## Running without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Run the generator
python log_generator.py
```

## Log Format

The application generates logs in standard nginx access log format:

```
192.168.1.100 - - [03/Nov/2025:10:30:45 +0000] "GET /alfa HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
```

## Use Cases

- Testing log aggregation systems
- Load testing monitoring solutions
- Simulating traffic patterns
- Testing scaling behaviors
- Developing log parsing tools

## Health Check Endpoint

The application exposes a `/health` endpoint on port 8080 for Kubernetes liveness and readiness probes:

```bash
# Test the health endpoint
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "routes": 3,
  "timestamp": "2025-11-03T10:30:45.123456"
}
```

### Kubernetes Configuration Example

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

## Stopping the Generator

Press `Ctrl+C` or stop the Docker container:

```bash
docker-compose down
```
