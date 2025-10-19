# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a webhook proxy service that receives webhooks (primarily from Slack and Zammad), transforms them, and forwards them to Glue.ai. The service is written in Python using Flask and configured via YAML.

## Development Commands

### Running the Server
```bash
# Run in debug mode (auto-reloads on code changes, reloads config.yml on each request)
DEBUG=true python app.py

# Run in production mode
python app.py
```

The server runs on port 8080 by default. Override with `PORT=<port>` environment variable.

### Testing with Ngrok
```bash
# First time setup: authenticate ngrok
ngrok config add-authtoken <your_ngrok_authtoken>

# Start ngrok tunnel
ngrok http --url=example.ngrok.io 8080
```

Ngrok UI is available at http://127.0.0.1:4040/inspect/http for replaying POST requests.

Test URL format: `https://<ngrok_url>/services/<service_id_from_config.yml>`

### Docker Commands
```bash
# Build image
docker build -t slack-to-glue-webhook .

# Run container
docker run -p 8080:8080 slack-to-glue-webhook
```

## Architecture

### Single-File Flask Application
All code is in `app.py` (260 lines). The architecture is intentionally simple:

1. **WebhookProcessor class** - Core business logic
   - Loads and manages YAML configuration
   - Transforms webhook payloads from Slack format to Glue format
   - Forwards transformed webhooks to Glue API

2. **Flask routes**:
   - `POST /services/<service_id>` - Main webhook endpoint
   - `GET /health` - Health check for monitoring

3. **Configuration-driven routing** - `config.yml` maps service IDs to Glue targets and webhook URLs

### Webhook Transformation Flow

The service performs these transformations (app.py:75-170):

1. **Parse incoming webhook**: Handles both JSON and form-encoded payloads (Slack often sends `application/x-www-form-urlencoded` with JSON in a `payload` field)

2. **Extract text content**:
   - Thread subject from `payload.text` (top-level)
   - Message text from `payload.attachments[0].text`
   - Fallback chain if neither exists

3. **Convert Slack markdown to standard markdown** (app.py:63-73):
   - `<url|text>` → `[text](url)`
   - `<url>` → `url`

4. **Format for Glue API**:
   ```json
   {
     "text": "message content",
     "target": "grp_xxx or thr_xxx",
     "threadSubject": "optional - creates new thread if present"
   }
   ```

### Configuration Structure

`config.yml` format:
```yaml
services:
  service-id:
    target: "grp_xxxxxxxxxxxxxxxxxxxxx"  # Glue group/thread ID
    webhook_url: "https://api.gluegroups.com/webhook/..."
    description: "Optional description"

global:
  timeout_seconds: 30
  retry_attempts: 3  # Not yet implemented
  log_level: "INFO"
```

**Important**: In DEBUG mode, config.yml is reloaded on every request (app.py:56-58), allowing configuration changes without restarting the server.

## Key Implementation Details

### Content-Type Handling
The service handles two content types (app.py:189-219):
- `application/x-www-form-urlencoded`: JSON embedded in `payload` form field (Slack's approach)
- `application/json`: Direct JSON payload

### Error Handling
- Returns JSON responses with `status` field: `success`, `warning`, or `error`
- HTTP status codes: 200 (success), 202 (warning), 400 (error), 500 (server error)
- All operations are logged with appropriate levels

### Development Environment
This project uses DevContainers as the primary development environment. The DevContainer includes Claude, Gemini, and Codex AI assistants pre-configured.

## Adding New Service Integrations

1. Add entry to `config.yml` under `services`
2. If in debug mode, config auto-reloads; otherwise restart server
3. Send test POST to `/services/<new-service-id>`

If the source webhook format differs significantly from Slack:
- Modify `process_webhook()` method in app.py:75-170
- Add new extraction logic for different payload structures
- Consider adding service-specific transformation functions like `_convert_slack_to_markdown()`
