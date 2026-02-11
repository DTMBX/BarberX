"""
Review Routes — Phase 10 Search & Review Platform (UI pages)
=============================================================
Blueprint: review_bp, mounted at /review

Serves the review workspace HTML pages. All data is loaded
via the /api/v1/review/* JSON endpoints from review_api.py.
"""

from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user

review_bp = Blueprint(
    "review", __name__,
    url_prefix="/review",
    template_folder="../templates/review",
)


@review_bp.route("/")
@login_required
def review_index():
    """Redirect to case selection or show case picker."""
    return render_template("review/index.html")


@review_bp.route("/case/<int:case_id>")
@login_required
def review_workspace(case_id):
    """
    Main review workspace for a case.
    Three-panel layout: results list | viewer | coding panel.
    """
    from models.legal_case import LegalCase
    case = LegalCase.query.get(case_id)
    if not case:
        abort(404)

    return render_template("review/workspace.html", case=case)
