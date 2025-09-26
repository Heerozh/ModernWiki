#!/usr/bin/env python3
"""
Webhook controller for ModernWiki.
Handles webhook requests to trigger site rebuilds.
"""

import os
import hmac
import hashlib
import logging
import docker
from sanic import Sanic, request, response
import asyncio
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Sanic("ModernWikiWebhook")

# Docker client
docker_client = docker.from_env()

# Get webhook secret from environment variable
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')

def verify_github_signature(payload_body, signature_header):
    """Verify GitHub webhook signature."""
    if not WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not configured - skipping signature verification")
        return True  # Allow requests if no secret is configured
    
    if not signature_header:
        logger.warning("No signature header found")
        return False
    
    try:
        # GitHub sends signature as 'sha256=<hash>'
        sha_name, signature = signature_header.split('=', 1)
        if sha_name != 'sha256':
            logger.warning(f"Unsupported signature algorithm: {sha_name}")
            return False
        
        # Calculate expected signature
        expected_signature = hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures using secure comparison
        if hmac.compare_digest(signature, expected_signature):
            logger.info("GitHub signature verification successful")
            return True
        else:
            logger.warning("GitHub signature verification failed")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False

async def rebuild_site():
    """Rebuild the Hugo site by restarting the hugo-builder container."""
    try:
        logger.info("Starting site rebuild...")
        
        # Find the hugo-builder container
        containers = docker_client.containers.list(all=True)
        hugo_container = None
        
        for container in containers:
            if 'hugo-builder' in container.name or 'modernwiki-hugo-builder' in container.name:
                hugo_container = container
                break
        
        if not hugo_container:
            logger.error("Hugo builder container not found")
            return False
        
        logger.info(f"Found hugo-builder container: {hugo_container.name}")
        
        # Stop the container if it's running
        if hugo_container.status == 'running':
            logger.info("Stopping hugo-builder container...")
            hugo_container.stop()
            
        logger.info("Restart hugo-builder container...")
        hugo_container.restart()
        
        logger.info("Site rebuild triggered successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during site rebuild: {str(e)}")
        return False

@app.route('/webhook', methods=['POST'])
async def webhook(request):
    """Handle webhook requests to trigger site rebuild."""
    try:
        # Log the incoming request
        logger.info(f"Webhook received from {request.ip}")
        
        # Verify GitHub signature
        signature_header = request.headers.get('X-Hub-Signature-256')
        payload_body = request.body
        
        if not verify_github_signature(payload_body, signature_header):
            logger.warning("GitHub signature verification failed")
            return response.json({'error': 'Unauthorized'}, status=401)
        
        # Validate request content type
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            logger.warning(f"Invalid content type: {content_type}")
            return response.json({'error': 'Invalid content type'}, status=400)
        
        # Get webhook data
        data = request.json
        
        # Log webhook event type and action (if available)
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        action = data.get('action', 'N/A') if data else 'N/A'
        logger.info(f"GitHub event: {event_type}, action: {action}")
        
        # Trigger rebuild in background
        await rebuild_site()
        
        return response.json({
            'status': 'success',
            'message': 'Site rebuild triggered'
        })
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return response.json({
            'status': 'error',
            'message': str(e)
        }, status=500)


@app.route('/webhook/health', methods=['GET'])
async def health(request):
    """Health check endpoint."""
    return response.json({
        'status': 'healthy',
        'service': 'ModernWiki Webhook Controller'
    })

if __name__ == '__main__':
    logger.info("Starting ModernWiki Webhook Controller...")
    app.run(host='0.0.0.0', port=5000, debug=True)