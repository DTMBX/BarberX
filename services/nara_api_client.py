"""
National Archives API Client
Professional-grade client for interacting with the National Archives NextGen Catalog API v2.

This module provides:
- Record search and retrieval
- Document metadata extraction
- Contribution management (tags, transcriptions, comments)
- Rate limiting and error handling
- Response caching

Official API Documentation: https://catalog.archives.gov/api/v2/swagger.json
Contact: Catalog_API@nara.gov
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configure logging
logger = logging.getLogger(__name__)


class NARAAPIError(Exception):
    """Base exception for National Archives API errors."""
    pass


class NARAAuthenticationError(NARAAPIError):
    """Raised when API authentication fails."""
    pass


class NARARateLimitError(NARAAPIError):
    """Raised when API rate limit is exceeded."""
    pass


class NARAAPIClient:
    """
    Client for the National Archives NextGen Catalog API v2.
    
    Handles authentication, rate limiting, caching, and error recovery.
    All operations preserve evidence integrity and auditability.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        user_uuid: Optional[str] = None,
        cache_dir: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the NARA API client.
        
        Args:
            api_key: National Archives API key (or set NARA_API_KEY env var)
            base_url: API base URL (defaults to production endpoint)
            user_uuid: User UUID for write operations (or set NARA_USER_UUID env var)
            cache_dir: Directory for caching responses (optional)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts for failed requests
        """
        self.api_key = api_key or os.getenv('NARA_API_KEY')
        self.base_url = base_url or os.getenv(
            'NARA_API_BASE_URL',
            'https://catalog.archives.gov/api/v2'
        )
        self.user_uuid = user_uuid or os.getenv('NARA_USER_UUID')
        self.timeout = timeout
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        if not self.api_key:
            raise NARAAuthenticationError(
                "NARA API key required. Set NARA_API_KEY environment variable "
                "or pass api_key parameter. Contact Catalog_API@nara.gov to obtain a key."
            )
        
        # Initialize cache directory
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "PUT", "DELETE"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Rate limiting state
        self._last_request_time = 0
        self._min_request_interval = 0.5  # 2 requests per second max
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate request headers with API key."""
        return {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'User-Agent': 'Evident-Technologies/1.0 (Legal Evidence Processing)'
        }
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _get_cache_path(self, cache_key: str) -> Optional[Path]:
        """Generate cache file path for a given key."""
        if not self.cache_dir:
            return None
        # Use hash to avoid filesystem issues with special characters
        import hashlib
        safe_key = hashlib.md5(cache_key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.json"
    
    def _read_cache(self, cache_key: str, max_age_hours: int = 24) -> Optional[Dict]:
        """Read from cache if available and not expired."""
        cache_path = self._get_cache_path(cache_key)
        if not cache_path or not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            age = datetime.now() - cached_time
            if age < timedelta(hours=max_age_hours):
                logger.debug(f"Cache hit: {cache_key}")
                return cached_data['data']
            else:
                logger.debug(f"Cache expired: {cache_key}")
                cache_path.unlink()  # Remove expired cache
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Invalid cache file: {cache_path} - {e}")
            cache_path.unlink()
        
        return None
    
    def _write_cache(self, cache_key: str, data: Dict):
        """Write data to cache."""
        cache_path = self._get_cache_path(cache_key)
        if not cache_path:
            return
        
        try:
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'cache_key': cache_key,
                'data': data
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            logger.debug(f"Cached: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to write cache: {e}")
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True,
        cache_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the NARA API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data
            use_cache: Whether to use cache for GET requests
            cache_hours: Cache expiration time in hours
            
        Returns:
            Response data as dictionary
            
        Raises:
            NARAAPIError: On API errors
            NARAAuthenticationError: On authentication failure
            NARARateLimitError: On rate limit exceeded
        """
        url = f"{self.base_url}{endpoint}"
        
        # Check cache for GET requests
        if method == 'GET' and use_cache:
            cache_key = f"{url}?{json.dumps(params, sort_keys=True)}"
            cached_result = self._read_cache(cache_key, cache_hours)
            if cached_result is not None:
                return cached_result
        
        # Rate limiting
        self._rate_limit()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                json=data,
                timeout=self.timeout
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise NARAAuthenticationError(
                    f"Authentication failed. Verify your API key. "
                    f"Contact Catalog_API@nara.gov if issues persist."
                )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                raise NARARateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds."
                )
            
            # Handle other errors
            response.raise_for_status()
            
            result = response.json() if response.text else {}
            
            # Cache GET requests
            if method == 'GET' and use_cache:
                self._write_cache(cache_key, result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            raise NARAAPIError(f"API request failed: {e}")
    
    # =========================
    # Record Search Operations
    # =========================
    
    def search_records(
        self,
        query: str,
        rows: int = 10,
        offset: int = 0,
        sort: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search catalog records.
        
        Args:
            query: Search query string
            rows: Number of results to return (max 100)
            offset: Result offset for pagination
            sort: Sort field (e.g., 'naId asc', 'title desc')
            **kwargs: Additional search parameters
            
        Returns:
            Search results with record metadata
        """
        params = {
            'q': query,
            'rows': min(rows, 100),
            'offset': offset,
            **kwargs
        }
        if sort:
            params['sort'] = sort
        
        return self._request('GET', '/records/search', params=params)
    
    def get_record_by_naid(self, naid: str) -> Dict[str, Any]:
        """
        Get a specific record by National Archives Identifier (NAID).
        
        Args:
            naid: National Archives Identifier
            
        Returns:
            Record metadata
        """
        results = self.search_records(query=f"naId:{naid}", rows=1)
        if results.get('opaResponse', {}).get('results', {}).get('total', 0) > 0:
            return results['opaResponse']['results']['result'][0]
        raise NARAAPIError(f"Record not found: NAID {naid}")
    
    def get_child_records(self, parent_naid: str) -> Dict[str, Any]:
        """
        Get records that are immediate children of a parent record.
        
        Args:
            parent_naid: Parent record NAID
            
        Returns:
            Child records
        """
        return self._request('GET', f'/records/parentNaId/{parent_naid}')
    
    def search_by_tag(self, tag: str, **kwargs) -> Dict[str, Any]:
        """Search records by tag."""
        params = {'tag': tag, **kwargs}
        return self._request('GET', '/records/search/by-tag', params=params)
    
    def search_by_transcription(self, transcription: str, **kwargs) -> Dict[str, Any]:
        """Search records by transcription content."""
        params = {'transcription': transcription, **kwargs}
        return self._request('GET', '/records/search/by-transcription', params=params)
    
    # =========================
    # Contribution Operations
    # =========================
    
    def get_contributions(
        self,
        target_naid: Optional[str] = None,
        user_id: Optional[str] = None,
        contribution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get contributions (tags, transcriptions, comments).
        
        Args:
            target_naid: Filter by target record NAID
            user_id: Filter by contributor user ID
            contribution_id: Get specific contribution by ID
            
        Returns:
            Contribution data
        """
        if contribution_id:
            return self._request('GET', f'/contributions/contributionId/{contribution_id}')
        elif target_naid:
            return self._request('GET', f'/contributions/targetNaId/{target_naid}')
        elif user_id:
            return self._request('GET', f'/contributions/userId/{user_id}')
        else:
            return self._request('GET', '/contributions/')
    
    # =========================
    # Tag Operations
    # =========================
    
    def add_tag(self, tag: str, target_naid: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a tag to a record.
        
        Args:
            tag: Tag text
            target_naid: Target record NAID
            user_id: User UUID (uses configured UUID if not provided)
            
        Returns:
            Created tag data
        """
        uid = user_id or self.user_uuid
        if not uid:
            raise NARAAPIError(
                "User UUID required for write operations. "
                "Set NARA_USER_UUID environment variable or pass user_id parameter."
            )
        
        data = {
            'tag': tag,
            'targetNaId': target_naid,
            'userId': uid
        }
        return self._request('POST', '/tags/', data=data, use_cache=False)
    
    def get_tags_by_naid(self, naid: str) -> Dict[str, Any]:
        """Get all tags for a record."""
        return self._request('GET', f'/tags/naId/{naid}')
    
    def delete_tag(self, contribution_id: str) -> Dict[str, Any]:
        """Deactivate/remove a tag."""
        return self._request('DELETE', f'/tags/{contribution_id}', use_cache=False)
    
    # =========================
    # Transcription Operations
    # =========================
    
    def add_transcription(
        self,
        transcription: str,
        target_naid: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a transcription to a record."""
        uid = user_id or self.user_uuid
        if not uid:
            raise NARAAPIError("User UUID required for write operations.")
        
        data = {
            'transcription': transcription,
            'targetNaId': target_naid,
            'userId': uid
        }
        return self._request('POST', '/transcriptions/', data=data, use_cache=False)
    
    def get_transcriptions_by_naid(self, naid: str) -> Dict[str, Any]:
        """Get all transcriptions for a record."""
        return self._request('GET', f'/transcriptions/naId/{naid}')
    
    # =========================
    # Utility Methods
    # =========================
    
    def get_extracted_text(self, naid: str) -> Optional[str]:
        """
        Get extracted text content for a record.
        
        Args:
            naid: National Archives Identifier
            
        Returns:
            Extracted text or None if not available
        """
        try:
            result = self._request('GET', f'/extractedText/{naid}')
            return result.get('extractedText')
        except NARAAPIError:
            return None
    
    def clear_cache(self):
        """Clear all cached responses."""
        if not self.cache_dir:
            return
        
        count = 0
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
            count += 1
        
        logger.info(f"Cleared {count} cached responses")
        return count


# Convenience function for one-off requests
def create_client(**kwargs) -> NARAAPIClient:
    """
    Create a NARA API client with default configuration.
    
    Args:
        **kwargs: Override default configuration
        
    Returns:
        Configured NARAAPIClient instance
    """
    return NARAAPIClient(**kwargs)
