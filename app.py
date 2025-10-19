#!/usr/bin/env python3
"""
Slack-to-Glue Webhook Service
A simple Python web app that accepts POST requests to /services/<ID>
and forwards them to configured endpoints based on YAML configuration.
"""

import os
import yaml
import logging
from flask import Flask, request, jsonify
import requests
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ConfigError(Exception):
    """Raised when there's an issue with configuration"""
    pass

class WebhookProcessor:
    """Handles webhook processing and forwarding"""

    def __init__(self, config_path: str = "config.yml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            raise ConfigError(f"Configuration file {self.config_path} not found")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise ConfigError(f"Error parsing YAML configuration: {e}")

    def reload_config(self) -> None:
        """Reload configuration from YAML file (useful in debug mode)"""
        self.config = self._load_config()

    def get_service_config(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific service ID"""
        # Reload config in debug mode for easier development
        if app.debug or os.environ.get('DEBUG', 'false').lower() == 'true':
            self.reload_config()
            logger.debug(f"Config reloaded in debug mode")

        services = self.config.get('services', {})
        return services.get(service_id)
    
    def _convert_slack_to_markdown(self, text: str) -> str:
        """Convert Slack markdown format to standard markdown"""
        import re

        # Convert Slack links: <url|text> to [text](url)
        text = re.sub(r'<([^|>]+)\|([^>]+)>', r'[\2](\1)', text)

        # Convert bare URLs: <url> to just url (or keep as-is for markdown)
        text = re.sub(r'<(https?://[^>]+)>', r'\1', text)

        return text

    def process_webhook(self, service_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook and forward to configured endpoint"""
        service_config = self.get_service_config(service_id)

        if not service_config:
            logger.warning(f"No configuration found for service ID: {service_id}")
            return {
                'status': 'error',
                'message': f'No configuration found for service ID: {service_id}'
            }

        # Get required configuration values
        target = service_config.get('target')
        webhook_url = service_config.get('webhook_url')

        if not all([target, webhook_url]):
            logger.error(f"Incomplete configuration for service {service_id}")
            return {
                'status': 'error',
                'message': 'Incomplete service configuration (missing target or webhook_url)'
            }

        # Extract the thread subject from the top-level text field
        thread_subject = payload.get('text', '').strip()
        # Remove markdown heading symbols if present
        if thread_subject.startswith('#'):
            thread_subject = thread_subject.lstrip('#').strip()

        # Extract the main message text from the attachments
        message_text = ''
        attachments = payload.get('attachments', [])
        if attachments and len(attachments) > 0:
            message_text = attachments[0].get('text', '')

        # If no text in attachments, fall back to top-level text
        if not message_text:
            message_text = payload.get('text', '')
            # If we used the text as subject, don't duplicate it
            if message_text == payload.get('text', ''):
                thread_subject = ''  # Don't create a thread if there's only one piece of text

        # If still no text, try other fields
        if not message_text and 'message' in payload:
            message_text = payload['message'].get('text', '')

        if not message_text:
            logger.warning(f"No text content found in webhook payload for service {service_id}")
            message_text = str(payload)  # Fallback to stringified payload

        # Convert Slack markdown to standard markdown
        message_text = self._convert_slack_to_markdown(message_text)

        # Prepare the Glue-formatted payload
        # Glue expects: { "text": "...", "target": "grp_xxx or thr_xxx" }
        # Optionally with "threadSubject" to create a new thread
        forward_payload = {
            'text': message_text,
            'target': target
        }

        # Add threadSubject if we have one (creates a new thread in Glue)
        if thread_subject:
            forward_payload['threadSubject'] = thread_subject
            logger.info(f"Creating Glue thread with subject: {thread_subject}")
        
        # Forward the request
        try:
            logger.info(f"Forwarding webhook for service {service_id} to {webhook_url}")
            response = requests.post(
                webhook_url,
                json=forward_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully forwarded webhook for service {service_id}")
                return {
                    'status': 'success',
                    'message': 'Webhook forwarded successfully',
                    'response_code': response.status_code
                }
            else:
                logger.warning(f"Target server returned status {response.status_code}")
                return {
                    'status': 'warning',
                    'message': f'Target server returned status {response.status_code}',
                    'response_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error forwarding webhook: {e}")
            return {
                'status': 'error',
                'message': 'Error forwarding webhook to target server'
            }

# Initialize the webhook processor with config file from environment or default
config_file = os.environ.get('CONFIG_FILE', 'config.yml')
logger.info(f"Using configuration file: {config_file}")
processor = WebhookProcessor(config_path=config_file)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'slack-to-glue-webhook'})

@app.route('/services/<service_id>', methods=['POST'])
def handle_webhook(service_id: str):
    """Handle incoming webhook requests"""
    try:
        logger.info(f"Received request for service {service_id}")
        logger.info(f"Content-Type: {request.content_type}")

        payload = None

        # Handle form-encoded data (common for Slack-style webhooks)
        if request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
            # Data is form-encoded with JSON in a 'payload' field
            form_data = request.form.get('payload')
            if form_data:
                try:
                    import json
                    payload = json.loads(form_data)
                    logger.info(f"Successfully parsed form-encoded JSON for service {service_id}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from form payload: {e}")
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid JSON in payload field'
                    }), 400
            else:
                logger.warning(f"No 'payload' field found in form data")
                return jsonify({
                    'status': 'error',
                    'message': 'Form data must contain a "payload" field with JSON'
                }), 400
        else:
            # Try to parse as direct JSON
            try:
                payload = request.get_json(force=True)
            except Exception as e:
                logger.warning(f"Failed to parse JSON from request for service {service_id}: {e}")
                return jsonify({
                    'status': 'error',
                    'message': 'Request body must be valid JSON'
                }), 400

        if not payload:
            logger.warning(f"Empty payload received for service {service_id}")
            return jsonify({
                'status': 'error',
                'message': 'Request body cannot be empty'
            }), 400

        logger.info(f"Successfully parsed webhook for service {service_id}")
        
        # Process the webhook
        result = processor.process_webhook(service_id, payload)
        
        # Return appropriate status code based on result
        if result['status'] == 'success':
            return jsonify(result), 200
        elif result['status'] == 'warning':
            return jsonify(result), 202  # Accepted but with warnings
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting webhook service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)