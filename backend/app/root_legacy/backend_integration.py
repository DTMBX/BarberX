"""
Backend Services Integration Layer
Unified service orchestration for Evident Legal Platform

This module provides:
- Service registry and dependency injection
- Unified error handling
- Performance monitoring
- Caching layer
- Async task processing
- Event system for inter-service communication
"""

import functools
import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# ========================================
# SERVICE REGISTRY
# ========================================


class ServiceStatus(Enum):
    """Service availability status"""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"
    INITIALIZING = "initializing"


@dataclass
class ServiceInfo:
    """Information about a registered service"""

    name: str
    instance: Any
    status: ServiceStatus = ServiceStatus.AVAILABLE
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    initialized_at: datetime = field(default_factory=datetime.utcnow)
    error_count: int = 0
    last_error: Optional[str] = None


class ServiceRegistry:
    """Central registry for all platform services"""

    def __init__(self):
        self._services: Dict[str, ServiceInfo] = {}
        self._logger = logging.getLogger(__name__)
        self._lock = threading.Lock()

    def register(
        self, name: str, service: Any, version: str = "1.0.0", dependencies: List[str] = None
    ) -> None:
        """Register a service"""
        with self._lock:
            self._services[name] = ServiceInfo(
                name=name, instance=service, version=version, dependencies=dependencies or []
            )
            self._logger.info(f"Service registered: {name} v{version}")

    def get(self, name: str) -> Optional[Any]:
        """Get service instance"""
        service_info = self._services.get(name)
        if not service_info:
            self._logger.warning(f"Service not found: {name}")
            return None

        if service_info.status == ServiceStatus.UNAVAILABLE:
            self._logger.error(f"Service unavailable: {name}")
            return None

        return service_info.instance

    def is_available(self, name: str) -> bool:
        """Check if service is available"""
        service_info = self._services.get(name)
        return service_info and service_info.status == ServiceStatus.AVAILABLE

    def mark_error(self, name: str, error: str) -> None:
        """Mark service error"""
        with self._lock:
            if name in self._services:
                self._services[name].error_count += 1
                self._services[name].last_error = error

                # Auto-disable after 10 errors
                if self._services[name].error_count >= 10:
                    self._services[name].status = ServiceStatus.UNAVAILABLE
                    self._logger.error(f"Service disabled due to errors: {name}")

    def get_status(self) -> Dict[str, Dict]:
        """Get status of all services"""
        return {
            name: {
                "status": info.status.value,
                "version": info.version,
                "initialized_at": info.initialized_at.isoformat(),
                "error_count": info.error_count,
                "last_error": info.last_error,
            }
            for name, info in self._services.items()
        }


# Global service registry
service_registry = ServiceRegistry()


# ========================================
# CACHING LAYER
# ========================================


class CacheBackend(Enum):
    """Available cache backends"""

    MEMORY = "memory"
    REDIS = "redis"
    FILE = "file"


class Cache:
    """Simple in-memory cache with TTL support"""

    def __init__(self, default_ttl: int = 3600):
        self._cache: Dict[str, tuple] = {}  # key -> (value, expiry)
        self._lock = threading.Lock()
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]

                # Check expiry
                if datetime.utcnow() < expiry:
                    self._hits += 1
                    return value
                else:
                    # Expired, remove
                    del self._cache[key]

            self._misses += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        with self._lock:
            ttl = ttl or self._default_ttl
            expiry = datetime.utcnow() + timedelta(seconds=ttl)
            self._cache[key] = (value, expiry)

    def delete(self, key: str) -> None:
        """Delete value from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self) -> None:
        """Clear all cache"""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.2f}%",
            }


# Global cache instance
cache = Cache(default_ttl=3600)


def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching function results"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            # Try cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


# ========================================
# PERFORMANCE MONITORING
# ========================================


class PerformanceMonitor:
    """Monitor service performance"""

    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def record(self, operation: str, duration: float) -> None:
        """Record operation duration"""
        with self._lock:
            if operation not in self._metrics:
                self._metrics[operation] = []

            self._metrics[operation].append(duration)

            # Keep only last 1000 measurements
            if len(self._metrics[operation]) > 1000:
                self._metrics[operation] = self._metrics[operation][-1000:]

    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get performance statistics for operation"""
        with self._lock:
            if operation not in self._metrics or not self._metrics[operation]:
                return {}

            durations = self._metrics[operation]
            return {
                "count": len(durations),
                "min": min(durations),
                "max": max(durations),
                "avg": sum(durations) / len(durations),
                "p95": (
                    sorted(durations)[int(len(durations) * 0.95)]
                    if len(durations) > 20
                    else max(durations)
                ),
            }

    def get_all_stats(self) -> Dict[str, Dict]:
        """Get all performance statistics"""
        return {operation: self.get_stats(operation) for operation in self._metrics.keys()}


# Global performance monitor
perf_monitor = PerformanceMonitor()
performance_monitor = perf_monitor  # Alias for consistency


def monitored(operation_name: Optional[str] = None):
    """Decorator for monitoring function performance"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                perf_monitor.record(op_name, duration)

        return wrapper

    return decorator


# ========================================
# ERROR HANDLING
# ========================================


class ServiceError(Exception):
    """Base exception for service errors"""


class ServiceUnavailableError(ServiceError):
    """Service is unavailable"""


class ServiceTimeoutError(ServiceError):
    """Service operation timed out"""


class ValidationError(ServiceError):
    """Input validation failed"""


def handle_service_errors(service_name: str):
    """Decorator for unified error handling"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ServiceError:
                # Re-raise service errors
                raise
            except Exception as e:
                # Log and mark service error
                logging.error(f"Error in {service_name}.{func.__name__}: {str(e)}")
                service_registry.mark_error(service_name, str(e))
                raise ServiceError(f"{service_name} error: {str(e)}")

        return wrapper

    return decorator


# ========================================
# EVENT SYSTEM
# ========================================


class Event:
    """Event for inter-service communication"""

    def __init__(self, event_type: str, data: Dict, source: str):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.utcnow()
        self.event_id = str(uuid.uuid4())


class EventBus:
    """Simple event bus for service communication"""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to event type"""
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            self._logger.info(f"Handler subscribed to {event_type}")

    def publish(self, event: Event) -> None:
        """Publish event to all subscribers"""
        handlers = self._handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self._logger.error(f"Error in event handler: {str(e)}")


# Global event bus
event_bus = EventBus()


# ========================================
# UNIFIED API RESPONSE
# ========================================


def success_response(data: Any, message: str = "Success", meta: Dict = None) -> Dict:
    """Create standardized success response"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "meta": meta or {},
        "timestamp": datetime.utcnow().isoformat(),
    }


def error_response(error: str, code: str = "ERROR", details: Dict = None) -> Dict:
    """Create standardized error response"""
    return {
        "success": False,
        "error": error,
        "code": code,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat(),
    }


# ========================================
# VALIDATION HELPERS
# ========================================


def validate_required_fields(data: Dict, required: List[str]) -> None:
    """Validate required fields in data"""
    missing = [field for field in required if field not in data or not data[field]]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    if "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


# ========================================
# ASYNC TASK PROCESSING
# ========================================

import uuid
from queue import Empty, Queue
from threading import Thread


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Async task"""

    task_id: str
    func: Callable
    args: tuple
    kwargs: dict
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskQueue:
    """Simple async task queue"""

    def __init__(self, num_workers: int = 4):
        self._queue = Queue()
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()
        self._workers = []
        self._running = True

        # Start workers
        for _ in range(num_workers):
            worker = Thread(target=self._worker, daemon=True)
            worker.start()
            self._workers.append(worker)

    def _worker(self):
        """Worker thread"""
        while self._running:
            try:
                task = self._queue.get(timeout=1)
                self._execute_task(task)
            except Empty:
                continue

    def _execute_task(self, task: Task):
        """Execute a task"""
        with self._lock:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()

        try:
            result = task.func(*task.args, **task.kwargs)

            with self._lock:
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = datetime.utcnow()

        except Exception as e:
            with self._lock:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = datetime.utcnow()

    def submit(self, func: Callable, *args, **kwargs) -> str:
        """Submit task for async execution"""
        task_id = str(uuid.uuid4())
        task = Task(task_id=task_id, func=func, args=args, kwargs=kwargs)

        with self._lock:
            self._tasks[task_id] = task

        self._queue.put(task)
        return task_id

    def get_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None

            return {
                "task_id": task.task_id,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "result": task.result if task.status == TaskStatus.COMPLETED else None,
                "error": task.error if task.status == TaskStatus.FAILED else None,
            }

    def shutdown(self):
        """Shutdown task queue"""
        self._running = False
        for worker in self._workers:
            worker.join(timeout=5)


# Global instances
task_queue = TaskQueue(num_workers=4)


# ========================================
# UTILITY FUNCTIONS
# ========================================


def get_system_status() -> Dict:
    """Get overall system status"""
    return {
        "services": service_registry.get_status(),
        "cache": cache.get_stats(),
        "performance": perf_monitor.get_all_stats(),
        "timestamp": datetime.utcnow().isoformat(),
    }


# Example usage
if __name__ == "__main__":
    # Register a service
    class DummyService:
        def process(self, data):
            return {"processed": data}

    service_registry.register("dummy", DummyService(), version="1.0.0")

    # Use caching
    @cached(ttl=300)
    def expensive_operation(x):
        time.sleep(0.1)  # Simulate expensive operation
        return x * 2

    # Use monitoring
    @monitored("test_operation")
    def monitored_operation(x):
        time.sleep(0.05)
        return x + 1

    # Test
    print("Testing integration layer...")

    print("\n1. Service Registry:")
    print(f"Service available: {service_registry.is_available('dummy')}")

    print("\n2. Caching:")
    result1 = expensive_operation(5)
    result2 = expensive_operation(5)  # Should be cached
    print(f"Cache stats: {cache.get_stats()}")

    print("\n3. Performance Monitoring:")
    for _ in range(10):
        monitored_operation(1)
    print(f"Performance stats: {perf_monitor.get_stats('test_operation')}")

    print("\n4. Task Queue:")
    task_id = task_queue.submit(lambda x: x * 2, 5)
    time.sleep(0.1)
    print(f"Task status: {task_queue.get_status(task_id)}")

    print("\n5. System Status:")
    print(json.dumps(get_system_status(), indent=2))

    task_queue.shutdown()


