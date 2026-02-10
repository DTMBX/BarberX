"""
Scheduled Task Runner for National Archives Document Updates

Provides automated scheduling for:
- Periodic document updates
- Health checks
- Cache management
- Integrity verification

Can be run as:
1. Standalone script via cron/Task Scheduler
2. Background thread in Flask application
3. Celery/APScheduler task
"""

import os
import sys
import time
import logging
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.fetch_founding_documents import DocumentFetcher
from services.nara_api_client import NARAAPIClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nara_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DocumentScheduler:
    """Manages scheduled updates for founding documents."""
    
    def __init__(
        self,
        update_interval_hours: int = 24,
        verify_interval_hours: int = 12,
        cleanup_interval_hours: int = 168  # 1 week
    ):
        """
        Initialize scheduler.
        
        Args:
            update_interval_hours: Hours between document updates
            verify_interval_hours: Hours between integrity checks
            cleanup_interval_hours: Hours between cache cleanups
        """
        self.update_interval = timedelta(hours=update_interval_hours)
        self.verify_interval = timedelta(hours=verify_interval_hours)
        self.cleanup_interval = timedelta(hours=cleanup_interval_hours)
        
        self.last_update = None
        self.last_verify = None
        self.last_cleanup = None
        
        self.fetcher = DocumentFetcher()
        self.client = NARAAPIClient()
        
        self.running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def should_update(self) -> bool:
        """Check if it's time for document update."""
        if not self.last_update:
            return True
        return datetime.now() - self.last_update >= self.update_interval
    
    def should_verify(self) -> bool:
        """Check if it's time for integrity verification."""
        if not self.last_verify:
            return True
        return datetime.now() - self.last_verify >= self.verify_interval
    
    def should_cleanup(self) -> bool:
        """Check if it's time for cache cleanup."""
        if not self.last_cleanup:
            return True
        return datetime.now() - self.last_cleanup >= self.cleanup_interval
    
    def update_documents(self):
        """Fetch latest documents from National Archives."""
        try:
            logger.info("Starting scheduled document update...")
            report = self.fetcher.fetch_all()
            
            if report['failed'] == 0:
                logger.info(
                    f"Update successful: {report['fetched']} documents fetched"
                )
            else:
                logger.warning(
                    f"Update completed with errors: {report['failed']} failed"
                )
            
            self.last_update = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"Document update failed: {e}")
            return False
    
    def verify_documents(self):
        """Verify integrity of stored documents."""
        try:
            logger.info("Starting document integrity verification...")
            
            docs_dir = Path('documents/founding')
            issues = []
            
            for doc_file in docs_dir.glob('*.md'):
                # Check file size
                size = doc_file.stat().st_size
                if size < 100:
                    issues.append(f"{doc_file.name}: File too small ({size} bytes)")
                
                # Check required content
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if '**NAID:**' not in content:
                    issues.append(f"{doc_file.name}: Missing NAID metadata")
                
                if 'National Archives' not in content:
                    issues.append(f"{doc_file.name}: Missing source attribution")
            
            if issues:
                logger.warning(
                    f"Verification found {len(issues)} issues:\n" +
                    "\n".join(f"  - {issue}" for issue in issues)
                )
            else:
                logger.info("Verification successful: All documents valid")
            
            self.last_verify = datetime.now()
            return len(issues) == 0
            
        except Exception as e:
            logger.error(f"Document verification failed: {e}")
            return False
    
    def cleanup_cache(self):
        """Clean up old cached API responses."""
        try:
            logger.info("Starting cache cleanup...")
            count = self.client.clear_cache()
            logger.info(f"Cache cleanup complete: {count} files removed")
            
            self.last_cleanup = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return False
    
    def run_once(self):
        """Run all due tasks once."""
        logger.info("Running scheduled tasks check...")
        
        if self.should_update():
            self.update_documents()
        
        if self.should_verify():
            self.verify_documents()
        
        if self.should_cleanup():
            self.cleanup_cache()
    
    def run_forever(self, check_interval_seconds: int = 3600):
        """
        Run scheduler continuously.
        
        Args:
            check_interval_seconds: Seconds between schedule checks
        """
        self.running = True
        logger.info("Starting scheduler daemon...")
        logger.info(f"Update interval: {self.update_interval}")
        logger.info(f"Verify interval: {self.verify_interval}")
        logger.info(f"Cleanup interval: {self.cleanup_interval}")
        
        while self.running:
            try:
                self.run_once()
                
                if self.running:
                    logger.debug(f"Sleeping for {check_interval_seconds} seconds...")
                    time.sleep(check_interval_seconds)
                    
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait before retry
        
        logger.info("Scheduler stopped")


def main():
    """Main entry point for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='National Archives document scheduler'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon (continuous)'
    )
    parser.add_argument(
        '--update-interval',
        type=int,
        default=24,
        help='Hours between document updates (default: 24)'
    )
    parser.add_argument(
        '--verify-interval',
        type=int,
        default=12,
        help='Hours between integrity checks (default: 12)'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=3600,
        help='Seconds between schedule checks when in daemon mode (default: 3600)'
    )
    
    args = parser.parse_args()
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    # Create scheduler
    scheduler = DocumentScheduler(
        update_interval_hours=args.update_interval,
        verify_interval_hours=args.verify_interval
    )
    
    if args.daemon:
        # Run continuously
        scheduler.run_forever(check_interval_seconds=args.check_interval)
    else:
        # Run once
        scheduler.run_once()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
