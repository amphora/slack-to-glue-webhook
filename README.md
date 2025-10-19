# Slack-to-Glue Webhook Service

A Python web application that accepts HTTP POST requests to `/services/<ID>` endpoints, processes them according to YAML configuration, and forwards them to configured Glue.ai endpoints.

## Features

- RESTful API endpoint for webhook processing
- YAML-based configuration mapping service IDs to Glue configurations
- Docker containerization for easy deployment
- DevContainer support for development
- Automated CI/CD pipeline with GitHub Actions
- Health check endpoint for monitoring
- Structured logging and error handling

## Quick Start

### Development with DevContainer

1. Open the project in VS Code
2. Click "Reopen in Container" when prompted
3. The development environment will be set up automatically
4. Run the application: `python app.py`

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application with default config (config.yml)
python app.py

# Run with a different config file (e.g., for development)
CONFIG_FILE=dev-config.yml python app.py

# Run with debug mode and custom config
DEBUG=true CONFIG_FILE=dev-config.yml python app.py
```

The service will be available at `http://localhost:8080`

### Docker Deployment

```bash
# Build the image
docker build -t slack-to-glue-webhook .

# Run the container with default config
docker run -p 8080:8080 slack-to-glue-webhook

# Run with a custom config file
docker run -p 8080:8080 \
  -v /path/to/your/dev-config.yml:/app/dev-config.yml \
  -e CONFIG_FILE=dev-config.yml \
  slack-to-glue-webhook
```

## API Endpoints

### POST /services/<service_id>

Processes a webhook for the specified service ID.

**Request:**
- Content-Type: `application/json`
- Body: JSON payload from the source webhook

**Response:**
```json
{
  "status": "success|warning|error",
  "message": "Description of the result",
  "response_code": 200
}
```

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "slack-to-glue-webhook"
}
```

## Configuration

The service uses a YAML configuration file (`config.yml`) to map service IDs to their corresponding Glue configurations:

```yaml
services:
  example-service:
    target: "grp_xxxxxxxxxxxxxxxxxxxxx"  # Glue group/thread ID
    webhook_url: "https://api.gluegroups.com/webhook/wbh_xxxxx/xxxxx"
    description: "Example service for testing"

# Global configuration (optional)
global:
  timeout_seconds: 30
  retry_attempts: 3
  log_level: "INFO"
```

### Configuration Fields

**Service Configuration:**
- `target`: The Glue.ai group or thread identifier (e.g., `grp_xxxxxxxxxxxxxxxxxxxxx`)
- `webhook_url`: The Glue webhook endpoint URL to forward processed webhooks
- `description`: Optional description of the service

**Global Configuration (optional):**
- `timeout_seconds`: Request timeout in seconds (default: 30)
- `retry_attempts`: Number of retry attempts for failed requests (default: 3)
- `log_level`: Logging level - INFO, DEBUG, WARNING, ERROR (default: INFO)

## Environment Variables

- `PORT`: Server port (default: 8080)
- `DEBUG`: Enable debug mode (default: false)
- `CONFIG_FILE`: Path to configuration file (default: config.yml)

## Deployment

### GitHub Container Registry

The project includes a GitHub Actions workflow that automatically builds and publishes Docker images to GitHub Container Registry on pushes to main/master branches.

### Manual Deployment

1. Build the Docker image: `docker build -t slack-to-glue-webhook .`
2. Push to your registry: `docker push your-registry/slack-to-glue-webhook`
3. Deploy using your preferred container orchestration platform

## Development

### Project Structure

```
├── app.py                    # Main Flask application
├── config.yml               # Service configuration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker build configuration
├── .devcontainer/          # VS Code DevContainer setup
│   └── devcontainer.json
└── .github/workflows/      # CI/CD pipeline
    └── docker-build-deploy.yml
```

### Adding New Services

1. Add a new entry to `config.yml` under the `services` section
2. Restart the application to load the new configuration
3. Send POST requests to `/services/<your-new-service-id>`

## License

See [LICENSE](LICENSE) file for details.
