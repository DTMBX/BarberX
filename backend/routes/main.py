# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

from flask import Blueprint

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return "Evident Legal Tech Platform API Root"
