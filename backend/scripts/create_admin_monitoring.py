# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Create admin monitoring dashboard route for tracking all users' usage and profitability.
Add this to app.py after deployment.
"""

# Add to app.py:


@app.route("/admin/monitoring", methods=["GET"])
@login_required
def admin_monitoring():
    """Admin dashboard to monitor all users' usage, costs, and profit margins."""

    # Check if user is admin
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("index"))

    from sqlalchemy import func

    from models_auth import User
    from usage_meter import SmartMeterEvent, UsageQuota

    # Get all users with their quotas
    users = (
        db.session.query(User, UsageQuota)
        .outerjoin(UsageQuota, User.id == UsageQuota.user_id)
        .all()
    )

    # Calculate aggregate stats
    total_users = len(users)
    active_users = sum(1 for u, q in users if q and q.usage_this_period > 0)

    total_cost = db.session.query(func.sum(UsageQuota.cost_this_period)).scalar() or 0.0

    total_revenue = sum(
        (
            19.0
            if (u.tier == "STARTER")
            else 49.0
            if (u.tier == "PROFESSIONAL")
            else 149.0
            if (u.tier == "PREMIUM")
            else 0.0
        )
        for u, q in users
    )

    total_profit = total_revenue - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    # User breakdown by tier
    tier_breakdown = {
        "STARTER": {"count": 0, "cost": 0, "revenue": 0},
        "PROFESSIONAL": {"count": 0, "cost": 0, "revenue": 0},
        "PREMIUM": {"count": 0, "cost": 0, "revenue": 0},
        "ENTERPRISE": {"count": 0, "cost": 0, "revenue": 0},
    }

    for user, quota in users:
        tier = user.tier or "FREE"
        if tier in tier_breakdown:
            tier_breakdown[tier]["count"] += 1
            if quota:
                tier_breakdown[tier]["cost"] += quota.cost_this_period

            # Add revenue
            if tier == "STARTER":
                tier_breakdown[tier]["revenue"] += 19.0
            elif tier == "PROFESSIONAL":
                tier_breakdown[tier]["revenue"] += 49.0
            elif tier == "PREMIUM":
                tier_breakdown[tier]["revenue"] += 149.0

    # Get top users by cost
    top_users_by_cost = (
        db.session.query(User, UsageQuota)
        .join(UsageQuota, User.id == UsageQuota.user_id)
        .order_by(UsageQuota.cost_this_period.desc())
        .limit(10)
        .all()
    )

    # Recent high-cost events
    recent_events = (
        db.session.query(SmartMeterEvent).order_by(SmartMeterEvent.timestamp.desc()).limit(50).all()
    )

    return render_template(
        "admin/monitoring.html",
        total_users=total_users,
        active_users=active_users,
        total_cost=total_cost,
        total_revenue=total_revenue,
        total_profit=total_profit,
        profit_margin=profit_margin,
        tier_breakdown=tier_breakdown,
        top_users=top_users_by_cost,
        recent_events=recent_events,
        users=users,
    )
