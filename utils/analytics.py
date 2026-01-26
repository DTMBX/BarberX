"""
Analytics Service for BarberX
Supports Mixpanel and Amplitude for user event tracking
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Try to import analytics SDKs
try:
    from mixpanel import Mixpanel
    MIXPANEL_AVAILABLE = True
except ImportError:
    MIXPANEL_AVAILABLE = False

try:
    from amplitude import Amplitude, BaseEvent
    AMPLITUDE_AVAILABLE = True
except ImportError:
    AMPLITUDE_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Unified analytics service that works with Mixpanel and/or Amplitude
    """
    
    def __init__(self):
        self.mixpanel = None
        self.amplitude = None
        
        # Initialize Mixpanel if token available
        mixpanel_token = os.getenv('MIXPANEL_TOKEN')
        if mixpanel_token and MIXPANEL_AVAILABLE:
            try:
                self.mixpanel = Mixpanel(mixpanel_token)
                logger.info("Mixpanel analytics initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Mixpanel: {e}")
        
        # Initialize Amplitude if API key available
        amplitude_key = os.getenv('AMPLITUDE_API_KEY')
        if amplitude_key and AMPLITUDE_AVAILABLE:
            try:
                self.amplitude = Amplitude(amplitude_key)
                logger.info("Amplitude analytics initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Amplitude: {e}")
        
        if not self.mixpanel and not self.amplitude:
            logger.warning(
                "No analytics service configured. "
                "Set MIXPANEL_TOKEN or AMPLITUDE_API_KEY environment variable."
            )
    
    def track_event(
        self, 
        user_id: str, 
        event_name: str, 
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track an event for a user
        
        Args:
            user_id: Unique user identifier
            event_name: Name of the event (e.g., 'user_registered', 'evidence_uploaded')
            properties: Additional event properties
        
        Returns:
            bool: True if event was tracked successfully
        """
        if not user_id or not event_name:
            logger.warning("Missing user_id or event_name")
            return False
        
        properties = properties or {}
        properties['timestamp'] = datetime.utcnow().isoformat()
        
        success = False
        
        # Track in Mixpanel
        if self.mixpanel:
            try:
                self.mixpanel.track(user_id, event_name, properties)
                success = True
            except Exception as e:
                logger.error(f"Mixpanel track error: {e}")
        
        # Track in Amplitude
        if self.amplitude:
            try:
                event = BaseEvent(
                    event_type=event_name,
                    user_id=user_id,
                    event_properties=properties
                )
                self.amplitude.track(event)
                success = True
            except Exception as e:
                logger.error(f"Amplitude track error: {e}")
        
        if success:
            logger.debug(f"Tracked event: {event_name} for user {user_id}")
        
        return success
    
    def identify_user(
        self, 
        user_id: str, 
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Identify a user and set their profile properties
        
        Args:
            user_id: Unique user identifier
            properties: User profile properties (email, name, tier, etc.)
        
        Returns:
            bool: True if user was identified successfully
        """
        if not user_id:
            logger.warning("Missing user_id")
            return False
        
        properties = properties or {}
        success = False
        
        # Identify in Mixpanel
        if self.mixpanel:
            try:
                self.mixpanel.people_set(user_id, properties)
                success = True
            except Exception as e:
                logger.error(f"Mixpanel identify error: {e}")
        
        # Identify in Amplitude
        if self.amplitude:
            try:
                identify_event = BaseEvent(
                    event_type='$identify',
                    user_id=user_id,
                    user_properties=properties
                )
                self.amplitude.track(identify_event)
                success = True
            except Exception as e:
                logger.error(f"Amplitude identify error: {e}")
        
        if success:
            logger.debug(f"Identified user: {user_id}")
        
        return success
    
    def track_revenue(
        self, 
        user_id: str, 
        amount: float,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track a revenue event
        
        Args:
            user_id: Unique user identifier
            amount: Revenue amount in dollars
            properties: Additional properties (plan, currency, etc.)
        
        Returns:
            bool: True if revenue was tracked successfully
        """
        if not user_id or amount <= 0:
            logger.warning("Invalid user_id or amount")
            return False
        
        properties = properties or {}
        properties['amount'] = amount
        properties['currency'] = properties.get('currency', 'USD')
        
        success = False
        
        # Track in Mixpanel
        if self.mixpanel:
            try:
                self.mixpanel.people_track_charge(user_id, amount, properties)
                self.track_event(user_id, 'revenue', properties)
                success = True
            except Exception as e:
                logger.error(f"Mixpanel revenue error: {e}")
        
        # Track in Amplitude
        if self.amplitude:
            try:
                event = BaseEvent(
                    event_type='revenue',
                    user_id=user_id,
                    event_properties=properties,
                    revenue=amount
                )
                self.amplitude.track(event)
                success = True
            except Exception as e:
                logger.error(f"Amplitude revenue error: {e}")
        
        if success:
            logger.debug(f"Tracked revenue: ${amount} for user {user_id}")
        
        return success
    
    def increment_property(
        self, 
        user_id: str, 
        property_name: str, 
        increment: int = 1
    ) -> bool:
        """
        Increment a user property (e.g., total_uploads, total_documents)
        
        Args:
            user_id: Unique user identifier
            property_name: Name of property to increment
            increment: Amount to increment (default: 1)
        
        Returns:
            bool: True if property was incremented successfully
        """
        if not user_id or not property_name:
            logger.warning("Missing user_id or property_name")
            return False
        
        success = False
        
        # Increment in Mixpanel
        if self.mixpanel:
            try:
                self.mixpanel.people_increment(user_id, {property_name: increment})
                success = True
            except Exception as e:
                logger.error(f"Mixpanel increment error: {e}")
        
        # Note: Amplitude doesn't have direct increment, use user properties instead
        if self.amplitude:
            # Track as event with increment info
            try:
                event = BaseEvent(
                    event_type='property_increment',
                    user_id=user_id,
                    event_properties={
                        'property_name': property_name,
                        'increment': increment
                    }
                )
                self.amplitude.track(event)
                success = True
            except Exception as e:
                logger.error(f"Amplitude increment error: {e}")
        
        return success


# Global analytics instance
_analytics = None


def get_analytics() -> AnalyticsService:
    """Get the global analytics instance"""
    global _analytics
    if _analytics is None:
        _analytics = AnalyticsService()
    return _analytics


# Convenience functions
def track_event(user_id: str, event_name: str, properties: Optional[Dict[str, Any]] = None) -> bool:
    """Track an event"""
    return get_analytics().track_event(user_id, event_name, properties)


def identify_user(user_id: str, properties: Optional[Dict[str, Any]] = None) -> bool:
    """Identify a user"""
    return get_analytics().identify_user(user_id, properties)


def track_revenue(user_id: str, amount: float, properties: Optional[Dict[str, Any]] = None) -> bool:
    """Track revenue"""
    return get_analytics().track_revenue(user_id, amount, properties)


def increment_property(user_id: str, property_name: str, increment: int = 1) -> bool:
    """Increment a user property"""
    return get_analytics().increment_property(user_id, property_name, increment)


# Common event helpers
def track_user_registration(user_id: str, email: str, tier: str = 'free', source: str = 'direct'):
    """Track user registration event"""
    identify_user(user_id, {
        'email': email,
        'tier': tier,
        'created_at': datetime.utcnow().isoformat(),
        'total_uploads': 0,
        'total_documents': 0
    })
    
    track_event(user_id, 'user_registered', {
        'tier': tier,
        'source': source
    })


def track_evidence_upload(user_id: str, file_type: str, file_size_mb: float, case_id: str):
    """Track evidence upload event"""
    track_event(user_id, 'evidence_uploaded', {
        'file_type': file_type,
        'file_size_mb': file_size_mb,
        'case_id': case_id
    })
    increment_property(user_id, 'total_uploads')


def track_document_generation(user_id: str, doc_type: str, word_count: int, generation_time: float):
    """Track document generation event"""
    track_event(user_id, 'document_generated', {
        'document_type': doc_type,
        'word_count': word_count,
        'generation_time': generation_time
    })
    increment_property(user_id, 'total_documents')


def track_subscription_change(user_id: str, old_tier: str, new_tier: str, amount: float):
    """Track subscription upgrade/downgrade"""
    track_event(user_id, 'subscription_changed', {
        'old_tier': old_tier,
        'new_tier': new_tier,
        'amount': amount
    })
    
    identify_user(user_id, {'tier': new_tier})
    
    if amount > 0:
        track_revenue(user_id, amount, {
            'plan': new_tier,
            'type': 'upgrade' if new_tier > old_tier else 'downgrade'
        })
