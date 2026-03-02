"""
Python Client Library for Advanced Video Processing
Simplifies interaction with the batch video processing API
"""

import asyncio
import json
import time
from typing import List, Dict, Optional, Callable, Any
from pathlib import Path
import logging

import socketio
import aiohttp
import requests

logger = logging.getLogger(__name__)


class VideoProcessingClient:
    """Main client for video batch uploading and processing"""
    
    def __init__(
        self,
        base_url: str = 'http://localhost:5000',
        auth_token: str = '',
        timeout: int = 30,
    ):
        """
        Initialize the client
        
        Args:
            base_url: API base URL
            auth_token: JWT authentication token
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = timeout
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Accept': 'application/json',
        }
        
        # WebSocket setup
        self.sio = socketio.Client()
        self._setup_websocket_handlers()
    
    # ======================== HTTP REQUESTS ========================
    
    def upload_single_video(
        self,
        file_path: str,
        case_id: str,
        quality: str = 'high',
        extract_transcription: bool = True,
    ) -> Dict[str, Any]:
        """
        Upload and process single video
        
        Args:
            file_path: Path to video file
            case_id: Case identifier
            quality: one of: ultra_low, low, medium, high, ultra_high
            extract_transcription: Enable audio transcription
            
        Returns:
            {file_id, filename, status, task_id, metadata}
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'case_id': case_id,
                'quality': quality,
                'transcription': 'true' if extract_transcription else 'false',
            }
            
            response = requests.post(
                f'{self.base_url}/api/upload/single',
                files=files,
                data=data,
                headers=self.headers,
                timeout=self.timeout,
            )
        
        response.raise_for_status()
        return response.json()
    
    def upload_batch_videos(
        self,
        file_paths: List[str],
        case_id: str,
        quality: str = 'high',
        extract_transcription: bool = True,
        sync_bwc: bool = True,
    ) -> Dict[str, Any]:
        """
        Upload and process multiple videos in parallel
        
        Args:
            file_paths: List of video file paths
            case_id: Case identifier
            quality: one of: ultra_low, low, medium, high, ultra_high
            extract_transcription: Enable audio transcription
            sync_bwc: Auto-synchronize multiple BWC feeds
            
        Returns:
            {batch_id, total_files, files, ws_endpoint, status_endpoint}
        """
        data = {
            'case_id': case_id,
            'quality': quality,
            'transcription': 'true' if extract_transcription else 'false',
            'sync_bwc': 'true' if sync_bwc else 'false',
        }
        
        # Open file handles and ensure they are closed after upload
        file_handles = []
        try:
            for fp in file_paths:
                fh = open(fp, 'rb')
                file_handles.append(fh)
            
            files_param = [('files', fh) for fh in file_handles]
            
            response = requests.post(
                f'{self.base_url}/api/upload/batch',
                files=files_param,
                data=data,
                headers=self.headers,
                timeout=self.timeout,
            )
        finally:
            for fh in file_handles:
                fh.close()
        
        response.raise_for_status()
        return response.json()
    
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get current status of batch processing"""
        response = requests.get(
            f'{self.base_url}/api/upload/batch/{batch_id}/status',
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
    
    def get_file_status(self, file_id: str) -> Dict[str, Any]:
        """Get status of individual file processing"""
        response = requests.get(
            f'{self.base_url}/api/upload/file/{file_id}/status',
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
    
    def get_transcription(self, file_id: str) -> Dict[str, Any]:
        """Get completed transcription"""
        response = requests.get(
            f'{self.base_url}/api/upload/file/{file_id}/transcription',
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
    
    def get_quality_options(self) -> Dict[str, Any]:
        """Get available quality presets"""
        response = requests.get(
            f'{self.base_url}/api/upload/quality-options',
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
    
    # ======================== WEBSOCKET REAL-TIME ========================
    
    def _setup_websocket_handlers(self):
        """Initialize WebSocket event handlers"""
        
        @self.sio.on('connect')
        def on_connect():
            logger.info("Connected to WebSocket server")
        
        @self.sio.on('disconnect')
        def on_disconnect():
            logger.info("Disconnected from WebSocket server")
        
        @self.sio.on('batch_status')
        def on_batch_status(data):
            logger.info(f"Batch status: {data}")
        
        @self.sio.on('batch_progress')
        def on_batch_progress(data):
            logger.info(f"Progress: {data['progress']}")
        
        @self.sio.on('file_processed')
        def on_file_processed(data):
            logger.info(f"File processed: {data['file_id']}")
        
        @self.sio.on('transcription_ready')
        def on_transcription_ready(data):
            logger.info(f"Transcription ready for {data['file_id']}")
        
        @self.sio.on('sync_point_detected')
        def on_sync_point(data):
            logger.info(f"Sync point found: {data}")
        
        @self.sio.on('error')
        def on_error(data):
            logger.error(f"WebSocket error: {data}")
    
    def connect_websocket(self):
        """Connect to WebSocket for real-time updates"""
        auth_headers = {
            'Authorization': self.headers['Authorization']
        }
        self.sio.connect(
            self.base_url,
            headers=auth_headers
        )
    
    def subscribe_batch_updates(self, batch_id: str):
        """Subscribe to batch processing updates"""
        self.sio.emit('subscribe_batch', {'batch_id': batch_id})
    
    def subscribe_sync_updates(self, batch_id: str):
        """Subscribe to BWC synchronization updates"""
        self.sio.emit('subscribe_sync_status', {'batch_id': batch_id})
    
    def request_transcription_updates(self, file_id: str):
        """Request transcription status updates"""
        self.sio.emit('request_file_transcription', {'file_id': file_id})
    
    def disconnect_websocket(self):
        """Disconnect from WebSocket"""
        self.sio.disconnect()
    
    # ======================== POLLING INTERFACE ========================
    
    def wait_for_batch_completion(
        self,
        batch_id: str,
        poll_interval: float = 2.0,
        max_wait: Optional[float] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Poll batch status until completion
        
        Args:
            batch_id: Batch ID to wait for
            poll_interval: Seconds between status checks
            max_wait: Maximum wait time in seconds (None = no limit)
            progress_callback: Function called with progress updates
            
        Returns:
            Final batch status
        """
        start_time = time.time()
        
        while True:
            if max_wait and (time.time() - start_time) > max_wait:
                raise TimeoutError(f"Batch {batch_id} did not complete within {max_wait}s")
            
            status = self.get_batch_status(batch_id)
            
            if progress_callback:
                progress_callback(status)
            
            if status['status'] in ['SUCCESS', 'FAILURE', 'ERROR']:
                return status
            
            time.sleep(poll_interval)
    
    def wait_for_file_completion(
        self,
        file_id: str,
        poll_interval: float = 2.0,
        max_wait: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Poll file status until completion
        
        Args:
            file_id: File ID to wait for
            poll_interval: Seconds between status checks  
            max_wait: Maximum wait time in seconds (None = no limit)
            
        Returns:
            Final file status with transcription if available
        """
        start_time = time.time()
        
        while True:
            if max_wait and (time.time() - start_time) > max_wait:
                raise TimeoutError(f"File {file_id} did not complete within {max_wait}s")
            
            status = self.get_file_status(file_id)
            
            if status['status'] in ['SUCCESS', 'FAILURE', 'ERROR']:
                # Try to get transcription
                try:
                    transcription = self.get_transcription(file_id)
                    status['transcription'] = transcription
                except:
                    pass
                
                return status
            
            time.sleep(poll_interval)


# ======================== CONVENIENCE FUNCTIONS ========================

def upload_and_process_batch(
    file_paths: List[str],
    case_id: str,
    auth_token: str,
    base_url: str = 'http://localhost:5000',
    quality: str = 'high',
    wait_for_completion: bool = True,
    use_websocket: bool = False,
) -> Dict[str, Any]:
    """
    High-level function to upload batch and optionally wait for completion
    
    Example:
        result = upload_and_process_batch(
            file_paths=['video1.mp4', 'video2.mp4'],
            case_id='case_2026_001',
            auth_token=token,
        )
    """
    client = VideoProcessingClient(
        base_url=base_url,
        auth_token=auth_token,
    )
    
    logger.info(f"Uploading {len(file_paths)} videos to case {case_id}...")
    
    # Upload
    batch_result = client.upload_batch_videos(
        file_paths=file_paths,
        case_id=case_id,
        quality=quality,
    )
    
    batch_id = batch_result['batch_id']
    logger.info(f"Batch created: {batch_id}")
    
    if not wait_for_completion:
        return batch_result
    
    # Wait for completion
    if use_websocket:
        client.connect_websocket()
        client.subscribe_batch_updates(batch_id)
    
    def progress_callback(status):
        logger.info(status['progress'])
    
    final_status = client.wait_for_batch_completion(
        batch_id,
        progress_callback=progress_callback if not use_websocket else None,
        max_wait=3600,  # 1 hour max
    )
    
    if use_websocket:
        client.disconnect_websocket()
    
    logger.info(f"Batch {batch_id} completed with status: {final_status['status']}")
    
    return final_status


# ======================== EXPORTS ========================

__all__ = [
    'VideoProcessingClient',
    'upload_and_process_batch',
]


# ======================== EXAMPLE USAGE ========================

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Example 1: Basic batch upload
    print("Example 1: Batch Upload with Polling")
    result = upload_and_process_batch(
        file_paths=[
            'bwc_camera_001.mp4',
            'bwc_camera_002.mp4',
            'bwc_camera_003.mp4',
        ],
        case_id='case_2026_001',
        auth_token='your_jwt_token',
        wait_for_completion=True,
    )
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Example 2: Using WebSocket for real-time updates
    print("\nExample 2: Real-Time WebSocket Updates")
    client = VideoProcessingClient(auth_token='your_jwt_token')
    
    # Upload
    batch_result = client.upload_batch_videos(
        file_paths=['video1.mp4', 'video2.mp4'],
        case_id='case_2026_002',
    )
    
    # Connect and subscribe
    client.connect_websocket()
    client.subscribe_batch_updates(batch_result['batch_id'])
    
    # Keep connection alive for updates
    time.sleep(60)
    client.disconnect_websocket()
    
    # Example 3: Get transcription
    print("\nExample 3: Get Transcription")
    transcription = client.get_transcription(file_id='f47ac10b-58cc-4372-a567-0e02b2c3d479')
    print(f"Full text: {transcription['full_text'][:200]}...")
    print(f"Segments: {len(transcription['segments'])}")
