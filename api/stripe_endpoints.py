# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Stripe/Billing API Endpoints
Handles checkout sessions, webhooks, and subscription management
"""

import os

import stripe
from flask import current_app, jsonify, request
from models_auth import User, db

from api import stripe_api
from api.auth import jwt_required

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@stripe_api.route("/create-checkout-session", methods=["POST"])
@jwt_required
def create_checkout_session():
    """
    Create Stripe checkout session for subscription

    POST /api/v1/billing/create-checkout-session
    Headers: Authorization: Bearer <token>
    Body: {"price_id": "price_xxx", "tier": "PRO"}
    Returns: {"session_id": "cs_xxx", "url": "https://checkout.stripe.com/..."}
    """
    user = request.current_user
    data = request.get_json()

    if not data or not data.get("price_id"):
        return jsonify({"error": "price_id required"}), 400

    try:
        # Create or get Stripe customer
        if not hasattr(user, "stripe_customer_id") or not user.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email, metadata={"user_id": user.id})
            # TODO: Save customer_id to user model
            customer_id = customer.id
        else:
            customer_id = user.stripe_customer_id

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": data["price_id"],
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"{request.host_url}billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}pricing",
            metadata={"user_id": user.id, "tier": data.get("tier", "PRO")},
        )

        return jsonify({"session_id": session.id, "url": session.url}), 200

    except Exception as e:
        current_app.logger.error(f"Stripe checkout error: {str(e)}")
        return jsonify({"error": "Failed to create checkout session"}), 500


@stripe_api.route("/webhook", methods=["POST"])
def stripe_webhook():
    """
    Handle Stripe webhooks

    POST /api/v1/billing/webhook
    Headers: Stripe-Signature
    Body: Stripe event payload
    Returns: {"status": "success"}
    """
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    # Handle different event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"].get("user_id")
        tier = session["metadata"].get("tier")

        if user_id:
            user = User.query.get(user_id)
            if user:
                user.tier = tier
                # TODO: Save subscription_id
                db.session.commit()
                current_app.logger.info(f"User {user_id} upgraded to {tier}")

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        # TODO: Handle subscription updates
        pass

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        # TODO: Downgrade user to FREE tier
        pass

    return jsonify({"status": "success"}), 200


@stripe_api.route("/portal", methods=["POST"])
@jwt_required
def create_billing_portal_session():
    """
    Create Stripe customer portal session

    POST /api/v1/billing/portal
    Headers: Authorization: Bearer <token>
    Returns: {"url": "https://billing.stripe.com/..."}
    """
    user = request.current_user

    if not hasattr(user, "stripe_customer_id") or not user.stripe_customer_id:
        return jsonify({"error": "No active subscription"}), 400

    try:
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id, return_url=f"{request.host_url}account/billing"
        )

        return jsonify({"url": session.url}), 200
    except Exception as e:
        current_app.logger.error(f"Stripe portal error: {str(e)}")
        return jsonify({"error": "Failed to create portal session"}), 500
