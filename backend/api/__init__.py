# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident REST API
Modular API structure for cross-platform client support
"""

from flask import Blueprint

# API version prefix
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Create blueprints for each module
auth_api = Blueprint("auth_api", __name__, url_prefix=f"{API_PREFIX}/auth")
upload_api = Blueprint("upload_api", __name__, url_prefix=f"{API_PREFIX}/upload")
analysis_api = Blueprint("analysis_api", __name__, url_prefix=f"{API_PREFIX}/analysis")
user_api = Blueprint("user_api", __name__, url_prefix=f"{API_PREFIX}/user")
stripe_api = Blueprint("stripe_api", __name__, url_prefix=f"{API_PREFIX}/billing")
admin_api = Blueprint("admin_api", __name__, url_prefix=f"{API_PREFIX}/admin")
evidence_api = Blueprint("evidence_api", __name__, url_prefix=f"{API_PREFIX}/evidence")
trinity_api = Blueprint("trinity_api", __name__, url_prefix=f"{API_PREFIX}/trinity")


def register_api_blueprints(app):
    """Register all API blueprints with the Flask app"""
    from . import admin, analysis, auth, evidence, stripe_endpoints, trinity, upload, user

    # Register blueprints
    app.register_blueprint(auth_api)
    app.register_blueprint(upload_api)
    app.register_blueprint(analysis_api)
    app.register_blueprint(user_api)
    app.register_blueprint(stripe_api)
    app.register_blueprint(admin_api)
    app.register_blueprint(evidence_api)
    app.register_blueprint(trinity_api)

    print(f"[OK] API blueprints registered at {API_PREFIX}/*")


__all__ = [
    "auth_api",
    "upload_api",
    "analysis_api",
    "user_api",
    "stripe_api",
    "admin_api",
    "evidence_api",
    "trinity_api",
    "register_api_blueprints",
    "API_VERSION",
    "API_PREFIX",
]
