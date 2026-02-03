"""
Stripe Subscription Service
Handles subscription creation, webhooks, and billing management
"""

import os
from datetime import datetime, timedelta
from functools import wraps

from dotenv import load_dotenv

load_dotenv()  # Load env vars before accessing them

import stripe
from flask import Blueprint, jsonify, redirect, request, session, url_for

from models_auth import TierLevel, User, db

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Stripe Price IDs (set these in .env after creating products in Stripe)
STRIPE_PRICE_PRO = os.getenv("STRIPE_PRICE_PRO", "")
STRIPE_PRICE_PREMIUM = os.getenv("STRIPE_PRICE_PREMIUM", "")

# Stripe Product IDs for tier mapping
STRIPE_PRODUCT_IDS = {
    os.getenv("STRIPE_PRODUCT_ENTERPRISE", ""): TierLevel.ENTERPRISE,
    os.getenv("STRIPE_PRODUCT_PREMIUM", ""): TierLevel.PREMIUM,
    os.getenv("STRIPE_PRODUCT_PROFESSIONAL", ""): TierLevel.PROFESSIONAL,
    os.getenv("STRIPE_PRODUCT_STARTER", ""): TierLevel.PROFESSIONAL,  # Starter maps to Professional
    os.getenv("STRIPE_PRODUCT_DEMO", ""): TierLevel.FREE,
}


def get_tier_from_subscription(subscription):
    """Determine tier from Stripe subscription product ID"""
    try:
        # Get product ID from subscription items
        items = subscription.get("items", {}).get("data", [])
        if items:
            product_id = items[0].get("price", {}).get("product")
            if product_id and product_id in STRIPE_PRODUCT_IDS:
                return STRIPE_PRODUCT_IDS[product_id]

        # Fallback: check metadata
        metadata = subscription.get("metadata", {})
        tier_name = metadata.get("tier", "").upper()
        if tier_name and hasattr(TierLevel, tier_name):
            return TierLevel[tier_name]
    except Exception as e:
        print(f"Error determining tier: {e}")

    return TierLevel.PROFESSIONAL  # Default fallback


# Create Flask blueprint
stripe_bp = Blueprint("stripe", __name__, url_prefix="/api/stripe")


def require_login(f):
    """Decorator to require login"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


class StripeSubscriptionService:
    """Service class for Stripe subscription management"""

    @staticmethod
    def create_customer(user):
        """Create or retrieve Stripe customer for user"""
        if user.stripe_customer_id:
            try:
                # Retrieve existing customer
                customer = stripe.Customer.retrieve(user.stripe_customer_id)
                return customer
            except stripe.error.StripeError:
                # Customer not found, create new one
                pass

        # Create new Stripe customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name or user.email,
            metadata={"user_id": user.id, "organization": user.organization or ""},
        )

        # Save customer ID
        user.stripe_customer_id = customer.id
        db.session.commit()

        return customer

    @staticmethod
    def create_checkout_session(user, tier, success_url, cancel_url):
        """
        Create Stripe checkout session for subscription

        Args:
            user: User model instance
            tier: TierLevel enum (PROFESSIONAL or PREMIUM)
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if user cancels
        """
        # Get or create customer
        customer = StripeSubscriptionService.create_customer(user)

        # Determine price ID and trial days
        if tier == TierLevel.PROFESSIONAL:
            price_id = STRIPE_PRICE_PRO
            trial_days = 3  # 3-day free trial for PRO
        elif tier == TierLevel.PREMIUM:
            price_id = STRIPE_PRICE_PREMIUM
            trial_days = 0  # No trial for PREMIUM
        else:
            raise ValueError(f"Invalid tier for checkout: {tier}")

        if not price_id:
            raise ValueError(f"Stripe price ID not configured for {tier.name}")

        # Create checkout session
        session_params = {
            "customer": customer.id,
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            "mode": "subscription",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {"user_id": user.id, "tier": tier.name},
            "allow_promotion_codes": True,  # Allow discount codes
        }

        # Add trial period for PRO
        if trial_days > 0:
            session_params["subscription_data"] = {
                "trial_period_days": trial_days,
                "metadata": {"user_id": user.id, "tier": tier.name},
            }

        checkout_session = stripe.checkout.Session.create(**session_params)

        return checkout_session

    @staticmethod
    def create_portal_session(user, return_url):
        """
        Create Stripe customer portal session for subscription management
        Allows users to update payment, cancel subscription, etc.
        """
        if not user.stripe_customer_id:
            raise ValueError("User has no Stripe customer ID")

        portal_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=return_url,
        )

        return portal_session

    @staticmethod
    def handle_checkout_completed(session):
        """Handle successful checkout completion"""
        user_id = session.get("metadata", {}).get("user_id")
        if not user_id:
            print("No user_id in checkout session metadata")
            return

        user = User.query.get(int(user_id))
        if not user:
            print(f"User {user_id} not found")
            return

        # Get subscription details
        subscription_id = session.get("subscription")
        customer_id = session.get("customer")

        # Update customer ID if provided
        if customer_id and not user.stripe_customer_id:
            user.stripe_customer_id = customer_id

        if subscription_id:
            try:
                # Try to retrieve full subscription from Stripe
                subscription = stripe.Subscription.retrieve(subscription_id)

                # Determine tier from product or metadata
                new_tier = get_tier_from_subscription(subscription.to_dict())
                user.tier = new_tier
                user.stripe_subscription_id = subscription.id
                user.stripe_subscription_status = subscription.status
                user.stripe_current_period_end = datetime.fromtimestamp(
                    subscription.current_period_end
                )

                # Check if trial
                if subscription.trial_end:
                    user.trial_end = datetime.fromtimestamp(subscription.trial_end)
                    user.is_on_trial = True
                else:
                    user.is_on_trial = False

            except stripe.error.StripeError as e:
                # Fallback: use metadata if Stripe API fails
                print(f"Could not retrieve subscription {subscription_id}: {e}")
                tier_name = session.get("metadata", {}).get("tier", "PROFESSIONAL")
                user.tier = TierLevel[tier_name]
                user.stripe_subscription_id = subscription_id
                user.stripe_subscription_status = "active"
                user.is_on_trial = False
        else:
            # No subscription (one-time payment or free tier)
            tier_name = session.get("metadata", {}).get("tier", "FREE")
            if hasattr(TierLevel, tier_name):
                user.tier = TierLevel[tier_name]

        user.subscription_start = datetime.utcnow()
        db.session.commit()
        print(f"✅ User {user.email} upgraded to {user.tier.value}")

    @staticmethod
    def handle_subscription_updated(subscription):
        """Handle subscription update (status change, renewal, plan change, etc.)"""
        # Support both object and dict access patterns
        sub_id = subscription.id if hasattr(subscription, "id") else subscription.get("id")
        sub_status = (
            subscription.status if hasattr(subscription, "status") else subscription.get("status")
        )

        # Find user by subscription ID
        user = User.query.filter_by(stripe_subscription_id=sub_id).first()
        if not user:
            # Try finding by customer ID as fallback
            customer_id = (
                subscription.customer
                if hasattr(subscription, "customer")
                else subscription.get("customer")
            )
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            if user:
                user.stripe_subscription_id = sub_id

        if not user:
            print(f"User not found for subscription {sub_id}")
            return

        # Check for plan/tier changes
        new_tier = get_tier_from_subscription(
            subscription if isinstance(subscription, dict) else subscription.to_dict()
        )
        if user.tier != new_tier and sub_status in ["active", "trialing"]:
            old_tier = user.tier
            user.tier = new_tier
            print(f"🔄 User {user.email} tier changed: {old_tier.value} → {new_tier.value}")

        # Update subscription status
        user.stripe_subscription_status = sub_status

        period_end = (
            subscription.current_period_end
            if hasattr(subscription, "current_period_end")
            else subscription.get("current_period_end")
        )
        if period_end:
            user.stripe_current_period_end = datetime.fromtimestamp(period_end)

        # Check trial status
        trial_end = (
            subscription.trial_end
            if hasattr(subscription, "trial_end")
            else subscription.get("trial_end")
        )
        if trial_end:
            user.trial_end = datetime.fromtimestamp(trial_end)
            user.is_on_trial = datetime.utcnow() < datetime.fromtimestamp(trial_end)
        else:
            user.is_on_trial = False

        # Handle status changes
        if sub_status in ["active", "trialing"]:
            # Subscription is active - tier already updated above
            pass
        elif sub_status in ["canceled", "unpaid", "past_due"]:
            # Downgrade to FREE if subscription ended
            if sub_status == "canceled":
                user.tier = TierLevel.FREE
                user.subscription_end = datetime.utcnow()
                print(f"⚠️ User {user.email} downgraded to FREE (subscription canceled)")

        db.session.commit()
        print(f"✅ Updated subscription for {user.email}: {sub_status}")

    @staticmethod
    def handle_subscription_deleted(subscription):
        """Handle subscription cancellation"""
        user = User.query.filter_by(stripe_subscription_id=subscription.id).first()
        if not user:
            return

        # Downgrade to FREE
        user.tier = TierLevel.FREE
        user.stripe_subscription_status = "canceled"
        user.subscription_end = datetime.utcnow()
        user.is_on_trial = False

        db.session.commit()
        print(f"❌ User {user.email} subscription canceled, downgraded to FREE")

    @staticmethod
    def handle_subscription_created(subscription):
        """Handle new subscription creation"""
        customer_id = subscription.get("customer")
        user = User.query.filter_by(stripe_customer_id=customer_id).first()

        if not user:
            print(f"⚠️ No user found for customer {customer_id}")
            return

        # Determine tier from product
        new_tier = get_tier_from_subscription(subscription)
        user.tier = new_tier

        # Update subscription details
        user.stripe_subscription_id = subscription.get("id")
        user.stripe_subscription_status = subscription.get("status")
        user.subscription_start = datetime.utcnow()

        if subscription.get("current_period_end"):
            user.stripe_current_period_end = datetime.fromtimestamp(
                subscription.get("current_period_end")
            )

        # Set trial info if applicable
        if subscription.get("trial_end"):
            user.trial_end = datetime.fromtimestamp(subscription.get("trial_end"))
            user.is_on_trial = True

        db.session.commit()
        print(
            f"✅ Subscription created for {user.email}: {subscription.get('id')} → {new_tier.value}"
        )

    @staticmethod
    def handle_subscription_paused(subscription):
        """Handle subscription pause"""
        user = User.query.filter_by(stripe_subscription_id=subscription.get("id")).first()
        if not user:
            return

        user.stripe_subscription_status = "paused"
        db.session.commit()
        print(f"⏸️ Subscription paused for {user.email}")

        # TODO: Send email notification about paused subscription

    @staticmethod
    def handle_subscription_resumed(subscription):
        """Handle subscription resume after pause"""
        user = User.query.filter_by(stripe_subscription_id=subscription.get("id")).first()
        if not user:
            return

        user.stripe_subscription_status = subscription.get("status", "active")
        if subscription.get("current_period_end"):
            user.stripe_current_period_end = datetime.fromtimestamp(
                subscription.get("current_period_end")
            )

        db.session.commit()
        print(f"▶️ Subscription resumed for {user.email}")

    @staticmethod
    def handle_trial_ending(subscription):
        """Handle trial ending notification (3 days before)"""
        user = User.query.filter_by(stripe_subscription_id=subscription.get("id")).first()
        if not user:
            return

        trial_end = subscription.get("trial_end")
        if trial_end:
            trial_end_date = datetime.fromtimestamp(trial_end)
            print(f"⏰ Trial ending for {user.email} on {trial_end_date}")

            # TODO: Send trial ending email
            # send_trial_ending_email(user, trial_end_date)

    @staticmethod
    def handle_invoice_paid(invoice):
        """Handle successful invoice payment (subscription renewal)"""
        customer_id = invoice.get("customer")
        user = User.query.filter_by(stripe_customer_id=customer_id).first()

        if not user:
            return

        # Update payment status
        user.stripe_subscription_status = "active"

        # Get subscription to update period end
        subscription_id = invoice.get("subscription")
        if subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(subscription_id)
                user.stripe_current_period_end = datetime.fromtimestamp(
                    subscription.current_period_end
                )
            except stripe.error.StripeError as e:
                print(f"⚠️ Error retrieving subscription: {e}")

        db.session.commit()

        amount = invoice.get("amount_paid", 0) / 100  # Convert from cents
        print(f"💰 Invoice paid: ${amount:.2f} for {user.email}")

        # TODO: Send payment receipt email
        # send_payment_receipt(user, invoice)

    @staticmethod
    def handle_invoice_payment_failed(invoice):
        """Handle failed invoice payment (dunning)"""
        customer_id = invoice.get("customer")
        user = User.query.filter_by(stripe_customer_id=customer_id).first()

        if not user:
            return

        # Update status to past_due
        user.stripe_subscription_status = "past_due"
        db.session.commit()

        attempt_count = invoice.get("attempt_count", 1)
        print(f"⚠️ Payment failed for {user.email} (attempt {attempt_count})")

        # TODO: Send payment failed email with update payment link
        # send_payment_failed_email(user, invoice)

    @staticmethod
    def handle_payment_action_required(invoice):
        """Handle payment requiring action (3D Secure, etc.)"""
        customer_id = invoice.get("customer")
        user = User.query.filter_by(stripe_customer_id=customer_id).first()

        if not user:
            return

        print(f"🔐 Payment action required for {user.email}")

        # Get the payment intent for the hosted invoice URL
        hosted_invoice_url = invoice.get("hosted_invoice_url")

        # TODO: Send email with link to complete payment
        # send_payment_action_email(user, hosted_invoice_url)

    @staticmethod
    def handle_invoice_upcoming(invoice):
        """Handle upcoming invoice notification"""
        customer_id = invoice.get("customer")
        user = User.query.filter_by(stripe_customer_id=customer_id).first()

        if not user:
            return

        amount = invoice.get("amount_due", 0) / 100
        print(f"📅 Upcoming invoice: ${amount:.2f} for {user.email}")

        # Good place to add usage-based charges before invoice is finalized
        # add_usage_charges(user, invoice)

    @staticmethod
    def handle_customer_updated(customer):
        """Handle customer info update"""
        user = User.query.filter_by(stripe_customer_id=customer.get("id")).first()

        if not user:
            return

        # Sync email if changed in Stripe
        new_email = customer.get("email")
        if new_email and new_email != user.email:
            print(f"📧 Customer email updated: {user.email} → {new_email}")
            # Note: You may want to verify before updating
            # user.email = new_email
            # db.session.commit()

    @staticmethod
    def handle_payment_succeeded(payment_intent):
        """Handle successful one-time payment"""
        customer_id = payment_intent.get("customer")
        if not customer_id:
            return

        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if not user:
            return

        amount = payment_intent.get("amount", 0) / 100
        print(f"💳 One-time payment: ${amount:.2f} from {user.email}")

        # Handle usage credits, add-ons, etc.
        metadata = payment_intent.get("metadata", {})
        if metadata.get("type") == "usage_credits":
            credits = int(metadata.get("credits", 0))
            # Add credits to user account
            # user.usage_credits += credits
            # db.session.commit()


# ============================================================================
# FLASK ROUTES
# ============================================================================


@stripe_bp.route("/create-checkout-session", methods=["POST"])
@require_login
def create_checkout_session():
    """Create Stripe checkout session"""
    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    tier_name = data.get("tier", "PROFESSIONAL").upper()

    try:
        tier = TierLevel[tier_name]
    except KeyError:
        return jsonify({"error": f"Invalid tier: {tier_name}"}), 400

    if tier not in [TierLevel.PROFESSIONAL, TierLevel.PREMIUM]:
        return jsonify({"error": "Invalid tier for checkout"}), 400

    # Build URLs
    base_url = request.host_url.rstrip("/")
    success_url = f"{base_url}/dashboard?checkout=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base_url}/pricing?checkout=canceled"

    try:
        checkout_session = StripeSubscriptionService.create_checkout_session(
            user=user, tier=tier, success_url=success_url, cancel_url=cancel_url
        )

        return jsonify({"url": checkout_session.url})

    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return jsonify({"error": str(e)}), 500


@stripe_bp.route("/create-portal-session", methods=["POST"])
@require_login
def create_portal_session():
    """Create Stripe customer portal session"""
    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.stripe_customer_id:
        return jsonify({"error": "No subscription found"}), 404

    base_url = request.host_url.rstrip("/")
    return_url = f"{base_url}/dashboard"

    try:
        portal_session = StripeSubscriptionService.create_portal_session(user, return_url)
        return jsonify({"url": portal_session.url})

    except Exception as e:
        print(f"Error creating portal session: {e}")
        return jsonify({"error": str(e)}), 500


@stripe_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    """
    Handle Stripe webhook events
    Configure this endpoint in Stripe Dashboard: https://dashboard.stripe.com/webhooks

    Required events to enable in Stripe Dashboard:
    - checkout.session.completed
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - customer.subscription.paused
    - customer.subscription.resumed
    - customer.subscription.trial_will_end
    - invoice.paid
    - invoice.payment_failed
    - invoice.payment_action_required
    - invoice.upcoming
    - customer.created
    - customer.updated
    - payment_intent.succeeded
    - payment_intent.payment_failed
    """
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    if not STRIPE_WEBHOOK_SECRET:
        print("⚠️ STRIPE_WEBHOOK_SECRET not configured")
        return jsonify({"error": "Webhook secret not configured"}), 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        print("❌ Webhook: Invalid payload")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        print("❌ Webhook: Invalid signature")
        return jsonify({"error": "Invalid signature"}), 400

    # Handle event
    event_type = event["type"]
    data = event["data"]["object"]

    print(f"📥 Stripe webhook received: {event_type}")

    # ===========================================
    # CHECKOUT & SUBSCRIPTION CREATION
    # ===========================================

    if event_type == "checkout.session.completed":
        # Payment successful, subscription created
        StripeSubscriptionService.handle_checkout_completed(data)

    elif event_type == "customer.subscription.created":
        # New subscription created (may also fire with checkout.session.completed)
        StripeSubscriptionService.handle_subscription_created(data)

    # ===========================================
    # SUBSCRIPTION LIFECYCLE
    # ===========================================

    elif event_type == "customer.subscription.updated":
        # Subscription updated (status change, plan change, renewal)
        StripeSubscriptionService.handle_subscription_updated(data)

    elif event_type == "customer.subscription.deleted":
        # Subscription canceled/expired
        StripeSubscriptionService.handle_subscription_deleted(data)

    elif event_type == "customer.subscription.paused":
        # Subscription paused (if you enable pause collection)
        StripeSubscriptionService.handle_subscription_paused(data)

    elif event_type == "customer.subscription.resumed":
        # Subscription resumed after pause
        StripeSubscriptionService.handle_subscription_resumed(data)

    elif event_type == "customer.subscription.trial_will_end":
        # Trial ending in 3 days - send reminder email
        StripeSubscriptionService.handle_trial_ending(data)

    # ===========================================
    # INVOICES & PAYMENTS
    # ===========================================

    elif event_type == "invoice.paid":
        # Successful recurring payment
        StripeSubscriptionService.handle_invoice_paid(data)

    elif event_type == "invoice.payment_failed":
        # Payment failed - handle dunning
        StripeSubscriptionService.handle_invoice_payment_failed(data)

    elif event_type == "invoice.payment_action_required":
        # Payment requires action (3D Secure, etc.)
        StripeSubscriptionService.handle_payment_action_required(data)

    elif event_type == "invoice.upcoming":
        # Invoice will be created soon - good for usage-based billing
        StripeSubscriptionService.handle_invoice_upcoming(data)

    # ===========================================
    # CUSTOMER EVENTS
    # ===========================================

    elif event_type == "customer.created":
        # New Stripe customer created
        print(f"✅ New Stripe customer: {data.get('email')}")

    elif event_type == "customer.updated":
        # Customer info updated
        StripeSubscriptionService.handle_customer_updated(data)

    # ===========================================
    # PAYMENT INTENTS (one-time payments)
    # ===========================================

    elif event_type == "payment_intent.succeeded":
        # One-time payment succeeded (usage charges, add-ons)
        StripeSubscriptionService.handle_payment_succeeded(data)

    elif event_type == "payment_intent.payment_failed":
        # One-time payment failed
        print(f"⚠️ Payment failed: {data.get('id')}")

    else:
        print(f"ℹ️ Unhandled webhook event: {event_type}")

    return jsonify({"status": "success", "event": event_type}), 200


@stripe_bp.route("/config", methods=["GET"])
def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    return jsonify(
        {
            "publishableKey": STRIPE_PUBLISHABLE_KEY,
            "prices": {"pro": STRIPE_PRICE_PRO, "premium": STRIPE_PRICE_PREMIUM},
        }
    )
