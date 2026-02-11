"""
National Archives Document Webhook Handler

Provides Flask routes for:
- Webhook endpoints for document updates
- Manual refresh triggers
- Status monitoring
- Document verification

This module integrates with the main Flask application to provide
automated document management capabilities.
"""

import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import hashlib
import json

from services.nara_api_client import NARAAPIClient, NARAAPIError
from scripts.fetch_founding_documents import DocumentFetcher


# Configure logging
logger = logging.getLogger(__name__)


# Create Blueprint
nara_bp = Blueprint('nara', __name__, url_prefix='/api/nara')


# Document verification state
_last_check = None
_check_interval = timedelta(hours=24)


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature for security.
    
    Args:
        payload: Request payload bytes
        signature: Provided signature from headers
        secret: Webhook secret key
        
    Returns:
        True if signature is valid
    """
    expected_signature = hashlib.sha256(
        secret.encode() + payload
    ).hexdigest()
    return signature == expected_signature


@nara_bp.route('/webhook', methods=['POST'])
def webhook_handler():
    """
    Handle webhooks from National Archives (or custom update triggers).
    
    Expected payload:
    {
        "event": "document.updated",
        "naid": "1667751",
        "timestamp": "2026-01-01T00:00:00Z"
    }
    
    Note: NARA API doesn't currently support webhooks. This endpoint
    can be used with custom monitoring services or manual triggers.
    """
    try:
        # Verify webhook signature if configured
        webhook_secret = os.getenv('NARA_WEBHOOK_SECRET')
        if webhook_secret:
            signature = request.headers.get('X-NARA-Signature', '')
            if not verify_webhook_signature(request.data, signature, webhook_secret):
                logger.warning("Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 401
        
        payload = request.get_json()
        event = payload.get('event')
        naid = payload.get('naid')
        
        logger.info(f"Webhook received: {event} for NAID {naid}")
        
        # Handle different event types
        if event == 'document.updated':
            # Trigger document refresh
            result = refresh_document_by_naid(naid)
            return jsonify(result), 200
        
        elif event == 'document.refresh_all':
            # Trigger full refresh
            result = refresh_all_documents()
            return jsonify(result), 200
        
        else:
            return jsonify({'error': 'Unknown event type'}), 400
            
    except Exception as e:
        logger.error(f"Webhook handler error: {e}")
        return jsonify({'error': str(e)}), 500


@nara_bp.route('/refresh', methods=['POST'])
@login_required
def manual_refresh():
    """
    Manually trigger document refresh.
    
    Requires authentication.
    
    Request body (optional):
    {
        "document": "constitution",  // Specific document key
        "force": true              // Force refresh ignoring cache
    }
    """
    try:
        data = request.get_json() or {}
        document_key = data.get('document')
        force = data.get('force', False)
        
        logger.info(f"Manual refresh triggered by user")
        
        if document_key:
            result = refresh_document(document_key, force=force)
        else:
            result = refresh_all_documents(force=force)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Manual refresh error: {e}")
        return jsonify({'error': str(e)}), 500


@nara_bp.route('/status', methods=['GET'])
def status():
    """
    Get status of founding documents.
    
    Returns document metadata, last update times, and verification status.
    """
    try:
        docs_dir = Path('documents/founding')
        status_data = {
            'timestamp': datetime.now().isoformat(),
            'documents': [],
            'last_automatic_check': _last_check.isoformat() if _last_check else None,
            'next_check_due': (
                (_last_check + _check_interval).isoformat()
                if _last_check
                else 'Pending'
            )
        }
        
        # Check each document
        for doc_file in docs_dir.glob('*.md'):
            doc_stat = doc_file.stat()
            
            # Read metadata from file
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract NAID if present
                naid = None
                for line in content.split('\n'):
                    if '**NAID:**' in line:
                        naid = line.split('**NAID:**')[1].strip()
                        break
            
            status_data['documents'].append({
                'filename': doc_file.name,
                'naid': naid,
                'size_bytes': doc_stat.st_size,
                'last_modified': datetime.fromtimestamp(doc_stat.st_mtime).isoformat(),
                'exists': True
            })
        
        return jsonify(status_data), 200
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'error': str(e)}), 500


@nara_bp.route('/verify', methods=['GET'])
def verify_documents():
    """
    Verify integrity of stored documents.
    
    Checks:
    - File existence
    - File size reasonableness
    - Metadata presence
    - NAID validity
    """
    try:
        docs_dir = Path('documents/founding')
        verification_results = {
            'timestamp': datetime.now().isoformat(),
            'documents': [],
            'total': 0,
            'valid': 0,
            'warnings': []
        }
        
        for doc_file in docs_dir.glob('*.md'):
            result = {
                'filename': doc_file.name,
                'checks': {}
            }
            
            # Check file size
            size = doc_file.stat().st_size
            result['checks']['size'] = {
                'pass': size > 100,  # Minimum reasonable size
                'value': size
            }
            
            # Read and check content
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required metadata
            result['checks']['has_naid'] = {
                'pass': '**NAID:**' in content,
                'value': '**NAID:**' in content
            }
            
            result['checks']['has_source'] = {
                'pass': 'National Archives' in content,
                'value': 'National Archives' in content
            }
            
            result['checks']['has_timestamp'] = {
                'pass': '**Retrieved:**' in content,
                'value': '**Retrieved:**' in content
            }
            
            # Overall validation
            all_passed = all(check['pass'] for check in result['checks'].values())
            result['valid'] = all_passed
            
            if not all_passed:
                verification_results['warnings'].append(
                    f"{doc_file.name}: Some checks failed"
                )
            else:
                verification_results['valid'] += 1
            
            verification_results['documents'].append(result)
            verification_results['total'] += 1
        
        return jsonify(verification_results), 200
        
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return jsonify({'error': str(e)}), 500


def refresh_document(document_key: str, force: bool = False) -> Dict[str, Any]:
    """
    Refresh a specific document.
    
    Args:
        document_key: Document identifier
        force: Force refresh ignoring cache
        
    Returns:
        Refresh result
    """
    from scripts.fetch_founding_documents import FOUNDING_DOCUMENTS, TREATIES
    
    doc_info = FOUNDING_DOCUMENTS.get(document_key) or TREATIES.get(document_key)
    if not doc_info:
        raise ValueError(f"Unknown document: {document_key}")
    
    fetcher = DocumentFetcher()
    success = fetcher.fetch_document(document_key, doc_info, force_refresh=force)
    
    return {
        'document': document_key,
        'success': success,
        'timestamp': datetime.now().isoformat()
    }


def refresh_document_by_naid(naid: str) -> Dict[str, Any]:
    """
    Refresh document by NAID.
    
    Args:
        naid: National Archives Identifier
        
    Returns:
        Refresh result
    """
    from scripts.fetch_founding_documents import FOUNDING_DOCUMENTS, TREATIES
    
    # Find document with matching NAID
    for doc_key, doc_info in {**FOUNDING_DOCUMENTS, **TREATIES}.items():
        if doc_info.get('naid') == naid:
            return refresh_document(doc_key, force=True)
    
    raise ValueError(f"No document found with NAID: {naid}")


def refresh_all_documents(force: bool = False) -> Dict[str, Any]:
    """
    Refresh all documents.
    
    Args:
        force: Force refresh ignoring cache
        
    Returns:
        Refresh summary
    """
    global _last_check
    
    fetcher = DocumentFetcher()
    report = fetcher.fetch_all()
    
    _last_check = datetime.now()
    
    return {
        'success': True,
        'fetched': report['fetched'],
        'failed': report['failed'],
        'timestamp': datetime.now().isoformat()
    }


def check_for_updates():
    """
    Background task to check for document updates.
    
    This should be called periodically (e.g., via scheduler).
    """
    global _last_check
    
    try:
        # Check if it's time for automatic refresh
        if _last_check and datetime.now() - _last_check < _check_interval:
            logger.debug("Skipping update check - interval not reached")
            return
        
        logger.info("Starting automatic document update check")
        result = refresh_all_documents()
        logger.info(f"Update check complete: {result}")
        
    except Exception as e:
        logger.error(f"Automatic update check failed: {e}")


# Register blueprint with Flask app
def register_nara_routes(app):
    """
    Register NARA routes with Flask application.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(nara_bp)
    logger.info("National Archives routes registered")
