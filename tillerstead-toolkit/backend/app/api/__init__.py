"""
API routers module
"""
from app.api.jobs import router as jobs
from app.api.rooms import router as rooms
from app.api.calculators import router as calculators
from app.api.products import router as products
from app.api.imports import router as imports
from app.api.exports import router as exports
from app.api.settings import router as settings

__all__ = [
    "jobs",
    "rooms",
    "calculators",
    "products",
    "imports",
    "exports",
    "settings",
]
