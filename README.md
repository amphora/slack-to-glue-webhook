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

# Run the application
python app.py
```

The service will be available at `http://localhost:8080`

### Docker Deployment

```bash
# Build the image
docker build -t slack-to-glue-webhook .

# Run the container
docker run -p 8080:8080 slack-to-glue-webhook
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
    glue_id: "glue-12345"
    thread_id: "thread-67890"
    webhook_url: "https://api.glue.example.com/webhook"
    description: "Example service for testing"
```

### Configuration Fields

- `glue_id`: The Glue.ai identifier for this service
- `thread_id`: The thread identifier for message threading
- `webhook_url`: The endpoint URL to forward processed webhooks
- `description`: Optional description of the service

## Environment Variables

- `PORT`: Server port (default: 8080)
- `DEBUG`: Enable debug mode (default: false)

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
