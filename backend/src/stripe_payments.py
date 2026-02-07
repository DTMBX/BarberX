# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Stripe Payment Service for Evident Legal Technologies
Handles subscriptions, checkouts, and customer management
"""

import os

import stripe
from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Create blueprint
payments_bp = Blueprint("payments", __name__, url_prefix="/payments")

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "price_id": None,
        "features": [
            "5 evidence uploads/month",
            "Basic AI analysis",
            "2 document generations/month",
            "Email support",
        ],
    },
    "pro": {
        "name": "Pro",
        "price": 199,
        "price_id": os.getenv("STRIPE_PRICE_PRO", "price_pro_monthly"),
        "features": [
            "Unlimited evidence uploads",
            "Advanced AI analysis",
            "Unlimited document generation",
            "BWC video analysis",
            "Timeline builder",
            "Priority support",
            "Command palette",
        ],
    },
    "premium": {
        "name": "Premium",
        "price": 499,
        "price_id": os.getenv("STRIPE_PRICE_PREMIUM", "price_premium_monthly"),
        "features": [
            "Everything in Pro",
            "Multi-user team access (up to 10)",
            "API access",
            "Custom integrations",
            "White-label options",
            "Dedicated account manager",
            "24/7 phone support",
        ],
    },
}


@payments_bp.route("/pricing")
def pricing():
    """Display pricing page"""
    return render_template("payments/pricing.html", plans=SUBSCRIPTION_PLANS)


@payments_bp.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    """Create Stripe checkout session for subscription"""
    try:
        data = request.get_json()
        plan = data.get("plan", "pro")

        if plan not in SUBSCRIPTION_PLANS or plan == "free":
            return jsonify({"error": "Invalid plan"}), 400

        plan_info = SUBSCRIPTION_PLANS[plan]

        # Create or retrieve Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.full_name,
                metadata={"user_id": str(current_user.id), "tier": plan},
            )
            current_user.stripe_customer_id = customer.id

            from app import db

            db.session.commit()
        else:
            current_user.stripe_customer_id

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": plan_info["price_id"],
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"{request.host_url}payments/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}pricing",
            metadata={"user_id": str(current_user.id), "plan": plan},
        )

        return jsonify({"checkout_url": checkout_session.url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payments_bp.route("/success")
@login_required
def payment_success():
    """Handle successful payment"""
    session_id = request.args.get("session_id")

    if not session_id:
        return redirect(url_for("payments.pricing"))

    try:
        # Retrieve checkout session
        session = stripe.checkout.Session.retrieve(session_id)

        # Update user tier
        plan = session.metadata.get("plan", "pro")
        current_user.subscription_tier = plan
        current_user.subscription_status = "active"

        from app import db

        db.session.commit()

        # Track analytics
        try:
            from utils.analytics import track_revenue, track_subscription_change

            track_subscription_change(
                str(current_user.id), "free", plan, SUBSCRIPTION_PLANS[plan]["price"]
            )
            track_revenue(
                str(current_user.id),
                SUBSCRIPTION_PLANS[plan]["price"],
                {"plan": plan, "type": "subscription"},
            )
        except Exception as e:
            # Log analytics failure but don't block success page
            print(f"Analytics tracking failed: {e}")

        return render_template("payments/success.html", plan=SUBSCRIPTION_PLANS[plan])

    except Exception as e:
        print(f"Success page error: {e}")
        return redirect(url_for("payments.pricing"))


@payments_bp.route("/cancel")
@login_required
def payment_cancel():
    """Handle cancelled payment"""
    return render_template("payments/cancel.html")


@payments_bp.route("/portal", methods=["POST"])
@login_required
def customer_portal():
    """Create Stripe customer portal session"""
    try:
        if not current_user.stripe_customer_id:
            return jsonify({"error": "No active subscription"}), 400

        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{request.host_url}dashboard",
        )

        return jsonify({"portal_url": portal_session.url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payments_bp.route("/webhook", methods=["POST"])
def webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Security: Verify webhook is configured
    if not webhook_secret:
        return jsonify({"error": "Webhook not configured"}), 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    # Handle different event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_checkout_complete(session)

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        handle_subscription_updated(subscription)

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        handle_subscription_cancelled(subscription)

    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        handle_payment_succeeded(invoice)

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        handle_payment_failed(invoice)

    return jsonify({"status": "success"})


def handle_checkout_complete(session):
    """Handle completed checkout"""
    from app import User, db

    user_id = session["metadata"].get("user_id")
    plan = session["metadata"].get("plan")

    if user_id:
        user = User.query.get(user_id)
        if user:
            user.subscription_tier = plan
            user.subscription_status = "active"
            user.stripe_customer_id = session["customer"]
            db.session.commit()


def handle_subscription_updated(subscription):
    """Handle subscription updates"""
    from app import User, db

    customer_id = subscription["customer"]
    user = User.query.filter_by(stripe_customer_id=customer_id).first()

    if user:
        user.subscription_status = subscription["status"]
        db.session.commit()


def handle_subscription_cancelled(subscription):
    """Handle subscription cancellations"""
    from app import User, db

    customer_id = subscription["customer"]
    user = User.query.filter_by(stripe_customer_id=customer_id).first()

    if user:
        user.subscription_tier = "free"
        user.subscription_status = "cancelled"
        db.session.commit()


def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    from app import User

    customer_id = invoice["customer"]
    user = User.query.filter_by(stripe_customer_id=customer_id).first()

    if user:
        # Track revenue
        try:
            from utils.analytics import track_revenue

            track_revenue(
                str(user.id),
                invoice["amount_paid"] / 100,  # Convert cents to dollars
                {"plan": user.subscription_tier, "invoice_id": invoice["id"]},
            )
        except Exception as e:
            # Log analytics failure but don't block payment processing
            print(f"Analytics tracking failed: {e}")


def handle_payment_failed(invoice):
    """Handle failed payment"""
    from app import User, db

    customer_id = invoice["customer"]
    user = User.query.filter_by(stripe_customer_id=customer_id).first()

    if user:
        user.subscription_status = "past_due"
        db.session.commit()

        # TODO: Send email notification


# Helper functions for other modules
def get_user_plan_limits(tier):
    """Get usage limits for a tier"""
    limits = {
        "free": {"max_uploads": 5, "max_documents": 2, "max_storage_gb": 1, "max_api_calls": 100},
        "pro": {
            "max_uploads": -1,
            "max_documents": -1,
            "max_storage_gb": 100,
            "max_api_calls": 10000,
        },  # Unlimited
        "premium": {
            "max_uploads": -1,
            "max_documents": -1,
            "max_storage_gb": 1000,
            "max_api_calls": 100000,
        },
    }
    return limits.get(tier, limits["free"])


def check_feature_access(user, feature):
    """Check if user has access to a feature"""
    feature_tiers = {
        "bwc_analysis": ["pro", "premium"],
        "timeline_builder": ["pro", "premium"],
        "api_access": ["premium"],
        "team_access": ["premium"],
        "white_label": ["premium"],
    }

    required_tiers = feature_tiers.get(feature, ["free"])
    return user.subscription_tier in required_tiers
