"""
API Key Manager for Evident Chat
Handles secure storage, retrieval, validation, and rotation of API keys
"""

import os
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import requests
import logging

from auth.chat_models import UserAPIKey
from auth.models import db

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manages user API keys with encryption, validation, and usage tracking"""
    
    # Service-specific configurations
    SERVICE_CONFIGS = {
        'openai': {
            'name': 'OpenAI',
            'validation_url': 'https://api.openai.com/v1/models',
            'header_key': 'Authorization',
            'header_prefix': 'Bearer',
            'requirements': ['text-davinci-003', 'gpt-4', 'gpt-3.5-turbo'],
            'cost_per_1k_input': 0.05,  # GPT-4, adjust as needed
            'cost_per_1k_output': 0.15,
        },
        'anthropic': {
            'name': 'Anthropic Claude',
            'validation_url': 'https://api.anthropic.com/v1/models',
            'header_key': 'x-api-key',
            'header_prefix': '',
            'cost_per_1k_input': 0.008,
            'cost_per_1k_output': 0.024,
        },
        'cohere': {
            'name': 'Cohere',
            'validation_url': 'https://api.cohere.ai/v1/generate',
            'header_key': 'Authorization',
            'header_prefix': 'Bearer',
            'cost_per_1k_input': 0.001,
            'cost_per_1k_output': 0.002,
        },
        'huggingface': {
            'name': 'Hugging Face',
            'validation_url': 'https://huggingface.co/api/whoami',
            'header_key': 'Authorization',
            'header_prefix': 'Bearer',
            'cost_per_1k_input': 0.0001,
            'cost_per_1k_output': 0.0001,
        },
    }
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize API Key Manager
        
        Args:
            master_key: Master encryption key (defaults to environment variable)
        """
        if master_key is None:
            master_key = os.environ.get('API_KEY_MASTER', 'default-master-key-change-in-production')
        
        self.master_key = self._derive_key(master_key)
        self.cipher = Fernet(self.master_key)
    
    @staticmethod
    def _derive_key(password: str, salt: str = 'evident-chat-salt') -> bytes:
        """
        Derive a Fernet-compatible key from a password
        
        Args:
            password: Master password/key
            salt: Salt for key derivation
            
        Returns:
            Base64-encoded Fernet key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_key(self, api_key: str) -> str:
        """
        Encrypt an API key
        
        Args:
            api_key: Raw API key to encrypt
            
        Returns:
            Encrypted key as string
        """
        try:
            encrypted = self.cipher.encrypt(api_key.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt API key: {e}")
            raise ValueError("Failed to encrypt API key")
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """
        Decrypt an API key
        
        Args:
            encrypted_key: Encrypted key string
            
        Returns:
            Decrypted API key
        """
        try:
            if isinstance(encrypted_key, str):
                encrypted_key = encrypted_key.encode()
            decrypted = self.cipher.decrypt(encrypted_key)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {e}")
            raise ValueError("Failed to decrypt API key")
    
    def store_api_key(
        self,
        user_id: int,
        service_name: str,
        api_key: str,
        metadata: Optional[Dict] = None,
    ) -> Tuple[UserAPIKey, str]:
        """
        Store a user's API key with encryption
        
        Args:
            user_id: User ID
            service_name: Service name (openai, anthropic, etc.)
            api_key: Raw API key
            metadata: Optional metadata dict (e.g., endpoint URL for custom services)
            
        Returns:
            Tuple of (UserAPIKey model, status message)
        """
        try:
            # Validate service
            if service_name not in self.SERVICE_CONFIGS and service_name != 'custom':
                return None, f"Unknown service: {service_name}"
            
            # Encrypt the key
            encrypted_key = self.encrypt_key(api_key)
            
            # Check if key already exists
            existing_key = UserAPIKey.query.filter_by(
                user_id=user_id,
                service_name=service_name,
                is_active=True
            ).first()
            
            if existing_key:
                # Archive old key, increment version
                existing_key.is_active = False
                db.session.add(existing_key)
                db.session.flush()
            
            # Store new key
            user_api_key = UserAPIKey(
                user_id=user_id,
                service_name=service_name,
                encrypted_key=encrypted_key,
                key_version=existing_key.key_version + 1 if existing_key else 1,
                metadata=metadata or {}
            )
            
            db.session.add(user_api_key)
            db.session.commit()
            
            logger.info(f"API key stored for user {user_id}/{service_name}")
            return user_api_key, "API key stored successfully"
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing API key: {e}")
            return None, f"Failed to store API key: {str(e)}"
    
    def get_api_key(self, user_id: int, service_name: str) -> Optional[str]:
        """
        Retrieve and decrypt a user's API key
        
        Args:
            user_id: User ID
            service_name: Service name
            
        Returns:
            Decrypted API key or None if not found
        """
        try:
            user_key = UserAPIKey.query.filter_by(
                user_id=user_id,
                service_name=service_name,
                is_active=True
            ).first()
            
            if not user_key:
                return None
            
            return self.decrypt_key(user_key.encrypted_key)
        
        except Exception as e:
            logger.error(f"Error retrieving API key: {e}")
            return None
    
    def delete_api_key(self, key_id: str, user_id: int) -> bool:
        """
        Securely delete an API key (soft delete - mark as inactive)
        
        Args:
            key_id: API key ID
            user_id: User ID (for security check)
            
        Returns:
            True if successful
        """
        try:
            user_key = UserAPIKey.query.filter_by(
                id=key_id,
                user_id=user_id
            ).first()
            
            if not user_key:
                logger.warning(f"Attempted to delete non-existent key {key_id}")
                return False
            
            user_key.is_active = False
            db.session.commit()
            logger.info(f"API key {key_id} deleted for user {user_id}")
            return True
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting API key: {e}")
            return False
    
    def list_api_keys(self, user_id: int, include_inactive: bool = False) -> List[Dict]:
        """
        List all API keys for a user (without decrypted values)
        
        Args:
            user_id: User ID
            include_inactive: Whether to include inactive (deleted) keys
            
        Returns:
            List of API key dicts (keys not included for security)
        """
        try:
            query = UserAPIKey.query.filter_by(user_id=user_id)
            
            if not include_inactive:
                query = query.filter_by(is_active=True)
            
            keys = query.all()
            return [key.to_dict() for key in keys]
        
        except Exception as e:
            logger.error(f"Error listing API keys: {e}")
            return []
    
    def validate_api_key(
        self,
        service_name: str,
        api_key: str,
        custom_validation_url: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Validate an API key with the service provider
        
        Args:
            service_name: Service name (openai, anthropic, custom, etc.)
            api_key: API key to validate
            custom_validation_url: URL to validate against (for custom services)
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            if service_name == 'custom':
                if not custom_validation_url:
                    return False, "Custom service requires validation_url"
                config = {'validation_url': custom_validation_url}
            else:
                config = self.SERVICE_CONFIGS.get(service_name)
                if not config:
                    return False, f"Unknown service: {service_name}"
            
            # Make test request to validate key
            headers = {
                config['header_key']: f"{config.get('header_prefix', '')} {api_key}".strip()
            }
            
            timeout = 5
            response = requests.get(
                config['validation_url'],
                headers=headers,
                timeout=timeout
            )
            
            is_valid = response.status_code in [200, 401]  # 401 means key format is right but invalid
            
            if response.status_code == 200:
                message = f"✓ {service_name} API key is valid"
            elif response.status_code == 401:
                message = f"✗ {service_name} API key is invalid or revoked"
            else:
                message = f"? Could not validate {service_name} API key (HTTP {response.status_code})"
            
            return is_valid and response.status_code == 200, message
        
        except requests.Timeout:
            return False, f"Validation timeout - {service_name} service unreachable"
        except requests.ConnectionError:
            return False, f"Connection error - cannot reach {service_name}"
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False, f"Validation failed: {str(e)}"
    
    def validate_user_key(self, user_id: int, service_name: str) -> Tuple[bool, str]:
        """
        Validate an existing user API key
        
        Args:
            user_id: User ID
            service_name: Service name
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            user_key = UserAPIKey.query.filter_by(
                user_id=user_id,
                service_name=service_name,
                is_active=True
            ).first()
            
            if not user_key:
                return False, f"No {service_name} API key found"
            
            api_key = self.decrypt_key(user_key.encrypted_key)
            is_valid, message = self.validate_api_key(
                service_name,
                api_key,
                user_key.metadata.get('endpoint_url') if user_key.metadata else None
            )
            
            # Update validation status
            user_key.mark_validated(is_valid, None if is_valid else message)
            db.session.commit()
            
            return is_valid, message
        
        except Exception as e:
            logger.error(f"Error validating user key: {e}")
            return False, f"Validation error: {str(e)}"
    
    def rotate_api_key(
        self,
        user_id: int,
        service_name: str,
        new_api_key: str,
    ) -> Tuple[bool, str]:
        """
        Rotate an API key (replace with new one)
        
        Args:
            user_id: User ID
            service_name: Service name
            new_api_key: New API key
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate new key first
            is_valid, validation_msg = self.validate_api_key(service_name, new_api_key)
            if not is_valid:
                return False, f"New key validation failed: {validation_msg}"
            
            # Archive old key
            old_key = UserAPIKey.query.filter_by(
                user_id=user_id,
                service_name=service_name,
                is_active=True
            ).first()
            
            if old_key:
                old_key.is_active = False
                db.session.add(old_key)
                db.session.flush()
                version = old_key.key_version + 1
            else:
                version = 1
            
            # Store new key
            encrypted_key = self.encrypt_key(new_api_key)
            new_key = UserAPIKey(
                user_id=user_id,
                service_name=service_name,
                encrypted_key=encrypted_key,
                key_version=version,
                is_validated=True
            )
            
            db.session.add(new_key)
            db.session.commit()
            
            logger.info(f"API key rotated for user {user_id}/{service_name} (v{version})")
            return True, f"API key rotated successfully (v{version})"
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error rotating API key: {e}")
            return False, f"Key rotation failed: {str(e)}"
    
    def get_service_cost_config(self, service_name: str) -> Optional[Dict]:
        """Get cost configuration for a service"""
        return self.SERVICE_CONFIGS.get(service_name, {}).get('cost_per_1k_input')
    
    def reset_monthly_costs(self, user_id: int) -> int:
        """Reset monthly costs for all user keys (call at start of month)"""
        try:
            keys = UserAPIKey.query.filter_by(user_id=user_id).all()
            for key in keys:
                key.monthly_cost = 0.0
            
            db.session.commit()
            logger.info(f"Monthly costs reset for user {user_id}")
            return len(keys)
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error resetting monthly costs: {e}")
            return 0
    
    def get_total_usage(self, user_id: int) -> Dict:
        """Get total API usage for a user"""
        try:
            keys = UserAPIKey.query.filter_by(user_id=user_id).all()
            
            total_requests = sum(key.total_requests for key in keys)
            total_cost = sum(key.total_cost for key in keys)
            monthly_cost = sum(key.monthly_cost for key in keys)
            
            return {
                'total_api_keys': len(keys),
                'active_keys': sum(1 for k in keys if k.is_active),
                'total_requests': total_requests,
                'total_cost': total_cost,
                'monthly_cost': monthly_cost,
                'average_cost_per_request': total_cost / total_requests if total_requests > 0 else 0
            }
        
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {}


# Initialize global instance
api_key_manager = APIKeyManager()
