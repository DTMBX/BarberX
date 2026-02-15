"""
Algorithm Registry
===================
Discoverable, versioned registry for all court-defensible algorithms.

Usage:
    from algorithms.registry import registry

    # Register via decorator
    @registry.register
    class MyAlgorithm(AlgorithmBase):
        ...

    # Discover
    registry.list_algorithms()        # → [{"id": ..., "version": ...}, ...]
    registry.get("bulk_dedup")        # → BulkDedupAlgorithm instance
    registry.get("bulk_dedup", "1.0.0")  # specific version
"""

import logging
from typing import Dict, List, Optional, Type

from algorithms.base import AlgorithmBase

logger = logging.getLogger(__name__)


class AlgorithmRegistry:
    """Thread-safe registry mapping (algorithm_id, version) → AlgorithmBase."""

    def __init__(self):
        self._algorithms: Dict[str, Dict[str, AlgorithmBase]] = {}

    def register(self, cls: Type[AlgorithmBase]) -> Type[AlgorithmBase]:
        """
        Class decorator that registers an algorithm.

        Usage:
            @registry.register
            class MyAlgo(AlgorithmBase):
                algorithm_id = "my_algo"
                algorithm_version = "1.0.0"
        """
        instance = cls()
        aid = instance.algorithm_id
        ver = instance.algorithm_version

        if aid not in self._algorithms:
            self._algorithms[aid] = {}

        if ver in self._algorithms[aid]:
            logger.warning(
                "Overwriting algorithm %s v%s in registry", aid, ver
            )

        self._algorithms[aid][ver] = instance
        logger.info("Registered algorithm %s v%s", aid, ver)
        return cls

    def get(
        self, algorithm_id: str, version: Optional[str] = None
    ) -> Optional[AlgorithmBase]:
        """
        Retrieve an algorithm by ID and optional version.

        If version is None, returns the latest registered version
        (lexicographic sort on semver strings).
        """
        versions = self._algorithms.get(algorithm_id)
        if not versions:
            return None
        if version:
            return versions.get(version)
        # Return latest version (sorted semver)
        latest = sorted(versions.keys())[-1]
        return versions[latest]

    def list_algorithms(self) -> List[Dict[str, str]]:
        """Return metadata for all registered algorithms."""
        result = []
        for aid, versions in sorted(self._algorithms.items()):
            for ver, algo in sorted(versions.items()):
                result.append(
                    {
                        "algorithm_id": aid,
                        "version": ver,
                        "description": algo.description.strip().split("\n")[0]
                        if algo.description
                        else "",
                    }
                )
        return result

    def ids(self) -> List[str]:
        """Return all registered algorithm IDs."""
        return sorted(self._algorithms.keys())


# Singleton registry
registry = AlgorithmRegistry()
