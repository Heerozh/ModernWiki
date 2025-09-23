#!/usr/bin/env python3
"""
Webhook controller for ModernWiki.
Handles webhook requests to trigger site rebuilds.
"""

import os
import logging
import docker
from flask import Flask, request, jsonify
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Docker client
docker_client = docker.from_env()

def rebuild_site():
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
            
        # Remove the container
        logger.info("Removing hugo-builder container...")
        hugo_container.remove()
        
        # Restart the container (docker-compose will recreate it)
        logger.info("Hugo builder container removed. Docker Compose will recreate it.")
        
        # Alternative: Use docker-compose restart if available
        # This requires docker-compose to be installed in the container
        # os.system("docker-compose restart hugo-builder")
        
        logger.info("Site rebuild triggered successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during site rebuild: {str(e)}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook requests to trigger site rebuild."""
    try:
        # Log the incoming request
        logger.info(f"Webhook received from {request.remote_addr}")
        
        # Validate request (basic security)
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type and 'application/x-www-form-urlencoded' not in content_type:
            logger.warning(f"Invalid content type: {content_type}")
            return jsonify({'error': 'Invalid content type'}), 400
        
        # Get webhook data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        logger.info(f"Webhook data: {data}")
        
        # Trigger rebuild in background
        thread = threading.Thread(target=rebuild_site)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Site rebuild triggered'
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/webhook', methods=['GET'])
def webhook_info():
    """Provide information about the webhook endpoint."""
    return jsonify({
        'service': 'ModernWiki Webhook Controller',
        'endpoint': '/webhook',
        'methods': ['POST'],
        'description': 'Send POST requests to this endpoint to trigger site rebuilds'
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ModernWiki Webhook Controller'
    })

@app.route('/rebuild', methods=['POST'])
def manual_rebuild():
    """Manual rebuild endpoint for testing."""
    try:
        success = rebuild_site()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Manual rebuild triggered'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Rebuild failed'
            }), 500
    except Exception as e:
        logger.error(f"Error during manual rebuild: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting ModernWiki Webhook Controller...")
    app.run(host='0.0.0.0', port=5000, debug=True)