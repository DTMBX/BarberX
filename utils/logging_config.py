"""
Professional logging configuration for BarberX Legal Technologies
Replaces print() statements with structured logging
"""

import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored console output for better readability"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Add color to level name
        record.levelname = f"{color}{record.levelname}{reset}"
        
        return super().format(record)


class StructuredLogger:
    """
    Professional logging system with:
    - Console output with colors
    - File rotation
    - Structured format
    - Performance tracking
    """
    
    def __init__(self, app_name: str = "barberx", log_dir: str = "logs"):
        self.app_name = app_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Main logger
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        self._setup_console_handler()
        self._setup_file_handlers()
    
    def _setup_console_handler(self):
        """Setup colored console output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Colored format for console
        console_format = ColoredFormatter(
            '%(levelname)s [%(name)s] %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handlers(self):
        """Setup rotating file handlers"""
        
        # General application log (rotates daily)
        app_log = self.log_dir / f"{self.app_name}.log"
        app_handler = TimedRotatingFileHandler(
            app_log,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        app_handler.setLevel(logging.INFO)
        app_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        app_handler.setFormatter(app_format)
        self.logger.addHandler(app_handler)
        
        # Error log (rotates at 10MB)
        error_log = self.log_dir / f"{self.app_name}_errors.log"
        error_handler = RotatingFileHandler(
            error_log,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(pathname)s:%(lineno)d\n'
            '%(message)s\n'
            '%(exc_info)s\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_format)
        self.logger.addHandler(error_handler)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance
        
        Args:
            name: Logger name (defaults to app name)
        
        Returns:
            Logger instance
        """
        if name:
            return logging.getLogger(f"{self.app_name}.{name}")
        return self.logger


def setup_flask_logging(app, log_level: str = "INFO"):
    """
    Setup logging for Flask application
    
    Args:
        app: Flask application instance
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Remove default Flask handlers
    app.logger.handlers.clear()
    
    # Setup structured logging
    structured_logger = StructuredLogger(app_name="barberx")
    
    # Set app logger to use our structured logger
    app.logger = structured_logger.get_logger("flask")
    app.logger.setLevel(getattr(logging, log_level.upper()))
    
    # Log startup
    app.logger.info(f"BarberX Legal Technologies started in {app.config.get('ENV', 'unknown')} mode")
    
    # Add request logging
    @app.before_request
    def log_request_info():
        from flask import request
        
        # Skip health check logging
        if request.path == '/health':
            return
        
        app.logger.debug(
            f"Request: {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
    
    @app.after_request
    def log_response_info(response):
        from flask import request
        
        # Skip health check logging
        if request.path == '/health':
            return response
        
        # Log errors and warnings
        if response.status_code >= 400:
            app.logger.warning(
                f"Response: {request.method} {request.path} "
                f"-> {response.status_code}"
            )
        
        return response
    
    return app


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module
    
    Args:
        name: Module name (e.g., 'auth', 'api', 'database')
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"barberx.{name}")


# Create default logger instances for common modules
auth_logger = get_logger('auth')
api_logger = get_logger('api')
db_logger = get_logger('database')
security_logger = get_logger('security')
analysis_logger = get_logger('analysis')
