"""
Security utilities for BarberX Legal Technologies Platform
Provides input validation, sanitization, and security helpers
"""

import hashlib
import mimetypes
import os
import re
from pathlib import Path
from typing import Optional, Tuple
from werkzeug.utils import secure_filename


class InputValidator:
    """Validates and sanitizes user inputs"""
    
    # Allowed file extensions by category
    ALLOWED_EXTENSIONS = {
        'video': {'mp4', 'mov', 'avi', 'mkv', 'webm'},
        'document': {'pdf', 'doc', 'docx', 'txt'},
        'image': {'jpg', 'jpeg', 'png', 'gif', 'webp'},
        'audio': {'mp3', 'wav', 'ogg', 'm4a'}
    }
    
    # MIME type validation
    ALLOWED_MIMES = {
        'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm',
        'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4',
        'text/plain'
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'video': 20 * 1024 * 1024 * 1024,  # 20GB
        'document': 100 * 1024 * 1024,      # 100MB
        'image': 10 * 1024 * 1024,          # 10MB
        'audio': 500 * 1024 * 1024,         # 500MB
        'default': 100 * 1024 * 1024        # 100MB default
    }
    
    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validates filename for security issues
        
        Returns:
            (is_valid, error_message)
        """
        if not filename:
            return False, "Filename is required"
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename: path traversal detected"
        
        # Check for null bytes
        if '\0' in filename:
            return False, "Invalid filename: null byte detected"
        
        # Check length
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"
        
        # Check for valid extension
        if '.' not in filename:
            return False, "Filename must have an extension"
        
        ext = filename.rsplit('.', 1)[1].lower()
        all_extensions = set().union(*InputValidator.ALLOWED_EXTENSIONS.values())
        
        if ext not in all_extensions:
            return False, f"File type '.{ext}' not allowed"
        
        return True, None
    
    @staticmethod
    def validate_file_type(file, expected_category: str = None) -> Tuple[bool, Optional[str]]:
        """
        Validates file type by extension and MIME type
        
        Args:
            file: FileStorage object from Flask
            expected_category: Optional category ('video', 'document', 'image', 'audio')
        
        Returns:
            (is_valid, error_message)
        """
        if not file or not file.filename:
            return False, "No file provided"
        
        # Validate filename first
        is_valid, error = InputValidator.validate_filename(file.filename)
        if not is_valid:
            return False, error
        
        # Check extension
        ext = file.filename.rsplit('.', 1)[1].lower()
        
        # If category specified, check against that category
        if expected_category:
            allowed = InputValidator.ALLOWED_EXTENSIONS.get(expected_category, set())
            if ext not in allowed:
                return False, f"File must be {expected_category} type"
        
        # Validate MIME type if content_type available
        if hasattr(file, 'content_type') and file.content_type:
            if file.content_type not in InputValidator.ALLOWED_MIMES:
                return False, f"MIME type '{file.content_type}' not allowed"
        
        return True, None
    
    @staticmethod
    def validate_file_size(file, category: str = 'default') -> Tuple[bool, Optional[str]]:
        """
        Validates file size
        
        Args:
            file: FileStorage object
            category: File category for size limits
        
        Returns:
            (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"
        
        # Get file size by seeking to end
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size = InputValidator.MAX_FILE_SIZES.get(category, InputValidator.MAX_FILE_SIZES['default'])
        
        if size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f"File too large (max {max_mb:.0f}MB for {category})"
        
        if size == 0:
            return False, "File is empty"
        
        return True, None
    
    @staticmethod
    def sanitize_path(base_dir: str, filename: str) -> str:
        """
        Safely constructs file path preventing directory traversal
        
        Args:
            base_dir: Base directory path
            filename: User-provided filename
        
        Returns:
            Safe absolute path
        
        Raises:
            ValueError: If path traversal detected
        """
        # Secure the filename
        safe_name = secure_filename(filename)
        
        # Construct path
        base = Path(base_dir).resolve()
        target = (base / safe_name).resolve()
        
        # Ensure target is within base directory
        if not str(target).startswith(str(base)):
            raise ValueError("Path traversal detected")
        
        return str(target)
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validates email address format"""
        if not email:
            return False, "Email is required"
        
        # Basic email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        if len(email) > 320:  # RFC 5321
            return False, "Email too long"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validates password strength
        
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 128:
            return False, "Password too long (max 128 characters)"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, None
    
    @staticmethod
    def validate_case_number(case_number: str) -> Tuple[bool, Optional[str]]:
        """Validates case number format"""
        if not case_number:
            return False, "Case number is required"
        
        # Allow alphanumeric, hyphens, and underscores
        if not re.match(r'^[A-Za-z0-9\-_]+$', case_number):
            return False, "Case number can only contain letters, numbers, hyphens, and underscores"
        
        if len(case_number) > 50:
            return False, "Case number too long (max 50 characters)"
        
        return True, None
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000) -> str:
        """
        Sanitizes text input
        
        Args:
            text: Input text
            max_length: Maximum allowed length
        
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\0', '')
        
        # Trim to max length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text


class ErrorSanitizer:
    """Sanitizes error messages for safe display to users"""
    
    # Generic error messages
    GENERIC_MESSAGES = {
        'database': "Database operation failed. Please try again.",
        'file': "File operation failed. Please check the file and try again.",
        'authentication': "Authentication failed. Please check your credentials.",
        'authorization': "You don't have permission to perform this action.",
        'validation': "Invalid input provided. Please check your data.",
        'network': "Network operation failed. Please try again.",
        'default': "An error occurred. Please try again or contact support."
    }
    
    @staticmethod
    def sanitize_error(error: Exception, category: str = 'default') -> str:
        """
        Returns a safe error message for display to users
        
        Args:
            error: Exception object
            category: Error category for appropriate message
        
        Returns:
            Safe error message
        """
        # Never expose actual exception details to users
        return ErrorSanitizer.GENERIC_MESSAGES.get(category, ErrorSanitizer.GENERIC_MESSAGES['default'])
    
    @staticmethod
    def create_error_ticket() -> str:
        """Generates a unique error ticket ID for user support"""
        import uuid
        from datetime import datetime
        
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"ERR-{timestamp}-{unique_id}"


def hash_file(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Generates hash of file for integrity verification
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
    
    Returns:
        Hex digest of file hash
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def verify_csrf_token(session_token: str, request_token: str) -> bool:
    """
    Verifies CSRF token
    
    Args:
        session_token: Token stored in session
        request_token: Token from request
    
    Returns:
        True if tokens match
    """
    if not session_token or not request_token:
        return False
    
    return hashlib.sha256(session_token.encode()).hexdigest() == hashlib.sha256(request_token.encode()).hexdigest()
