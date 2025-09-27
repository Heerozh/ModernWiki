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

def detect_webhook_provider(headers):
    """Detect webhook provider based on request headers."""
    if 'X-GitHub-Event' in headers:
        return 'github'
    elif 'X-Gitea-Event' in headers:
        return 'gitea'
    elif 'X-Gitlab-Event' in headers or 'X-Gitlab-Token' in headers:
        return 'gitlab'
    else:
        # Default fallback - try to detect by signature headers
        if 'X-Hub-Signature-256' in headers:
            return 'github'
        elif 'X-Gitea-Signature' in headers:
            return 'gitea'
        elif 'X-Gitlab-Token' in headers:
            return 'gitlab'
        return 'unknown'

def verify_webhook_signature(payload_body, headers, provider=None):
    """
    Verify webhook signature for multiple Git platforms.
    
    Args:
        payload_body: Request body as bytes
        headers: Request headers dictionary
        provider: Force specific provider ('github', 'gitea', 'gitlab') or None for auto-detection
    
    Returns:
        bool: True if signature is valid or verification is skipped
    """
    if not WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not configured - skipping signature verification")
        return True  # Allow requests if no secret is configured
    
    # Auto-detect provider if not specified
    if provider is None:
        provider = detect_webhook_provider(headers)
        logger.info(f"Detected webhook provider: {provider}")
    
    try:
        if provider == 'github':
            return _verify_github_signature(payload_body, headers)
        elif provider == 'gitea':
            return _verify_gitea_signature(payload_body, headers)
        elif provider == 'gitlab':
            return _verify_gitlab_signature(payload_body, headers)
        else:
            logger.warning(f"Unknown webhook provider: {provider}")
            # Try all verification methods as fallback
            return (_verify_github_signature(payload_body, headers) or
                    _verify_gitea_signature(payload_body, headers) or
                    _verify_gitlab_signature(payload_body, headers))
            
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False

def _verify_github_signature(payload_body, headers):
    """Verify GitHub webhook signature."""
    signature_header = headers.get('X-Hub-Signature-256')
    if not signature_header:
        logger.debug("No GitHub signature header found")
        return False
    
    try:
        # GitHub sends signature as 'sha256=<hash>'
        sha_name, signature = signature_header.split('=', 1)
        if sha_name != 'sha256':
            logger.warning(f"Unsupported GitHub signature algorithm: {sha_name}")
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
            logger.debug("GitHub signature verification failed")
            return False
            
    except Exception as e:
        logger.debug(f"GitHub signature verification error: {str(e)}")
        return False

def _verify_gitea_signature(payload_body, headers):
    """Verify Gitea webhook signature."""
    signature_header = headers.get('X-Gitea-Signature')
    if not signature_header:
        logger.debug("No Gitea signature header found")
        return False
    
    try:
        # Gitea sends signature as direct hex string (no prefix)
        expected_signature = hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures using secure comparison
        if hmac.compare_digest(signature_header, expected_signature):
            logger.info("Gitea signature verification successful")
            return True
        else:
            logger.debug("Gitea signature verification failed")
            return False
            
    except Exception as e:
        logger.debug(f"Gitea signature verification error: {str(e)}")
        return False

def _verify_gitlab_signature(payload_body, headers):
    """Verify GitLab webhook token."""
    token_header = headers.get('X-Gitlab-Token')
    if not token_header:
        logger.debug("No GitLab token header found")
        return False
    
    try:
        # GitLab uses simple token comparison (not HMAC)
        if hmac.compare_digest(token_header, WEBHOOK_SECRET):
            logger.info("GitLab token verification successful")
            return True
        else:
            logger.debug("GitLab token verification failed")
            return False
            
    except Exception as e:
        logger.debug(f"GitLab token verification error: {str(e)}")
        return False

# Legacy function for backward compatibility
def verify_github_signature(payload_body, signature_header):
    """Legacy GitHub signature verification function."""
    headers = {'X-Hub-Signature-256': signature_header}
    return _verify_github_signature(payload_body, headers)


def test_webhook_signature_verification():
    """Test webhook signature verification for multiple platforms."""
    # Mock request data
    payload_body = b'Hello, World!'
    
    # Set the webhook secret
    os.environ['WEBHOOK_SECRET'] = "It's a Secret to Everybody"
    
    # Test GitHub signature
    github_signature = 'sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17'
    github_headers = {'X-Hub-Signature-256': github_signature, 'X-GitHub-Event': 'push'}
    is_valid_github = verify_webhook_signature(payload_body, github_headers, 'github')
    assert is_valid_github, "GitHub signature verification failed"
    print("GitHub signature verification test passed")
    
    # Test Gitea signature (same HMAC calculation but no sha256= prefix)
    gitea_signature = '757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17'
    gitea_headers = {'X-Gitea-Signature': gitea_signature, 'X-Gitea-Event': 'push'}
    is_valid_gitea = verify_webhook_signature(payload_body, gitea_headers, 'gitea')
    assert is_valid_gitea, "Gitea signature verification failed"
    print("Gitea signature verification test passed")
    
    # Test GitLab token (simple token comparison)
    gitlab_headers = {'X-Gitlab-Token': "It's a Secret to Everybody", 'X-Gitlab-Event': 'Push Hook'}
    is_valid_gitlab = verify_webhook_signature(payload_body, gitlab_headers, 'gitlab')
    assert is_valid_gitlab, "GitLab token verification failed"
    print("GitLab token verification test passed")
    
    print("All webhook signature verification tests passed")


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
        
        # Verify webhook signature (supports GitHub, Gitea, GitLab)
        payload_body = request.body
        
        if not verify_webhook_signature(payload_body, request.headers):
            logger.warning("Webhook signature verification failed")
            return response.json({'error': 'Unauthorized'}, status=401)
        
        # Validate request content type
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            logger.warning(f"Invalid content type: {content_type}")
            return response.json({'error': 'Invalid content type'}, status=400)
        
        # Get webhook data
        data = request.json
        
        # Log webhook event type and action (if available)
        provider = detect_webhook_provider(request.headers)
        if provider == 'github':
            event_type = request.headers.get('X-GitHub-Event', 'unknown')
        elif provider == 'gitea':
            event_type = request.headers.get('X-Gitea-Event', 'unknown')
        elif provider == 'gitlab':
            event_type = request.headers.get('X-Gitlab-Event', 'unknown')
        else:
            event_type = 'unknown'
        
        action = data.get('action', 'N/A') if data else 'N/A'
        logger.info(f"{provider.capitalize()} webhook event: {event_type}, action: {action}")
        
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
        'service': 'ModernWiki Webhook Controller',
        'supported_platforms': ['GitHub', 'Gitea', 'GitLab']
    })

if __name__ == '__main__':
    # test_webhook_signature_verification()
    # asyncio.run(rebuild_site())
    # os._exit(0)
    logger.info("Starting ModernWiki Webhook Controller...")
    logger.info("Supported platforms: GitHub, Gitea, GitLab")
    app.run(host='0.0.0.0', port=5000, debug=True)