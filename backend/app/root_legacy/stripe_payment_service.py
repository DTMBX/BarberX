"""
Stripe Payment Integration Service
Handles subscription billing, one-time payments, and usage-based pricing
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import stripe


class StripePaymentService:
    """
    Professional Stripe integration for subscription management

    Features:
    - Subscription plans (Basic, Pro, Premium, Enterprise)
    - Usage-based billing
    - Payment method management
    - Invoice generation
    - Webhook handling
    - Trial periods
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Stripe service

        Args:
            api_key: Stripe secret key (or use STRIPE_SECRET_KEY env var)
        """
        stripe.api_key = api_key or os.getenv("STRIPE_SECRET_KEY")
        if not stripe.api_key:
            raise ValueError("Stripe API key not provided")

        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    def create_customer(self, email: str, name: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Create Stripe customer

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional customer data

        Returns:
            Stripe customer object
        """
        customer = stripe.Customer.create(email=email, name=name, metadata=metadata or {})

        return {
            "customer_id": customer.id,
            "email": customer.email,
            "name": customer.name,
            "created": datetime.fromtimestamp(customer.created).isoformat(),
        }

    def create_subscription(
        self, customer_id: str, price_id: str, trial_days: int = 14, metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create subscription for customer

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID for plan
            trial_days: Free trial period (0 = no trial)
            metadata: Additional subscription data

        Returns:
            Subscription details
        """
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            trial_period_days=trial_days if trial_days > 0 else None,
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
            metadata=metadata or {},
        )

        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "current_period_start": datetime.fromtimestamp(
                subscription.current_period_start
            ).isoformat(),
            "current_period_end": datetime.fromtimestamp(
                subscription.current_period_end
            ).isoformat(),
            "trial_end": (
                datetime.fromtimestamp(subscription.trial_end).isoformat()
                if subscription.trial_end
                else None
            ),
            "client_secret": (
                subscription.latest_invoice.payment_intent.client_secret
                if subscription.latest_invoice
                else None
            ),
        }

    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 14,
    ) -> Dict:
        """
        Create Stripe Checkout session

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            success_url: Redirect after successful payment
            cancel_url: Redirect if user cancels
            trial_days: Free trial period

        Returns:
            Checkout session with URL
        """
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            subscription_data={"trial_period_days": trial_days} if trial_days > 0 else None,
        )

        return {"session_id": session.id, "url": session.url, "status": session.status}

    def cancel_subscription(self, subscription_id: str, immediately: bool = False) -> Dict:
        """
        Cancel subscription

        Args:
            subscription_id: Stripe subscription ID
            immediately: Cancel now vs. at period end

        Returns:
            Updated subscription status
        """
        if immediately:
            subscription = stripe.Subscription.delete(subscription_id)
        else:
            subscription = stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)

        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "canceled_at": (
                datetime.fromtimestamp(subscription.canceled_at).isoformat()
                if subscription.canceled_at
                else None
            ),
        }

    def add_payment_method(
        self, customer_id: str, payment_method_id: str, set_as_default: bool = True
    ) -> Dict:
        """
        Attach payment method to customer

        Args:
            customer_id: Stripe customer ID
            payment_method_id: Payment method ID from Stripe.js
            set_as_default: Make this the default payment method

        Returns:
            Payment method details
        """
        # Attach payment method
        payment_method = stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

        # Set as default
        if set_as_default:
            stripe.Customer.modify(
                customer_id, invoice_settings={"default_payment_method": payment_method_id}
            )

        return {
            "payment_method_id": payment_method.id,
            "type": payment_method.type,
            "card": (
                {
                    "brand": payment_method.card.brand,
                    "last4": payment_method.card.last4,
                    "exp_month": payment_method.card.exp_month,
                    "exp_year": payment_method.card.exp_year,
                }
                if payment_method.type == "card"
                else None
            ),
        }

    def create_usage_record(
        self, subscription_item_id: str, quantity: int, timestamp: Optional[int] = None
    ) -> Dict:
        """
        Record usage for metered billing

        Args:
            subscription_item_id: Subscription item ID
            quantity: Usage quantity (e.g., minutes of transcription)
            timestamp: Unix timestamp (defaults to now)

        Returns:
            Usage record confirmation
        """
        usage = stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=quantity,
            timestamp=timestamp or int(datetime.now().timestamp()),
            action="set",  # or 'increment'
        )

        return {
            "id": usage.id,
            "quantity": usage.quantity,
            "timestamp": datetime.fromtimestamp(usage.timestamp).isoformat(),
        }

    def get_upcoming_invoice(self, customer_id: str) -> Dict:
        """Get next invoice preview"""
        invoice = stripe.Invoice.upcoming(customer=customer_id)

        return {
            "amount_due": invoice.amount_due / 100,  # Convert from cents
            "currency": invoice.currency,
            "period_start": datetime.fromtimestamp(invoice.period_start).isoformat(),
            "period_end": datetime.fromtimestamp(invoice.period_end).isoformat(),
            "subtotal": invoice.subtotal / 100,
            "tax": invoice.tax / 100 if invoice.tax else 0,
            "total": invoice.total / 100,
        }

    def list_invoices(self, customer_id: str, limit: int = 10) -> List[Dict]:
        """List customer invoices"""
        invoices = stripe.Invoice.list(customer=customer_id, limit=limit)

        return [
            {
                "invoice_id": inv.id,
                "amount_paid": inv.amount_paid / 100,
                "currency": inv.currency,
                "status": inv.status,
                "created": datetime.fromtimestamp(inv.created).isoformat(),
                "invoice_pdf": inv.invoice_pdf,
                "hosted_invoice_url": inv.hosted_invoice_url,
            }
            for inv in invoices.data
        ]

    def handle_webhook(self, payload: bytes, signature: str) -> Dict:
        """
        Process Stripe webhook events

        Args:
            payload: Raw request body
            signature: Stripe-Signature header

        Returns:
            Event data
        """
        if not self.webhook_secret:
            raise ValueError("Webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")

        event_type = event["type"]
        data = event["data"]["object"]

        # Handle different event types
        handlers = {
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_payment_failed,
            "payment_method.attached": self._handle_payment_method_attached,
        }

        handler = handlers.get(event_type, self._handle_default)
        return handler(data)

    def _handle_subscription_created(self, subscription):
        """Handle new subscription"""
        return {
            "action": "subscription_created",
            "customer_id": subscription["customer"],
            "subscription_id": subscription["id"],
            "status": subscription["status"],
        }

    def _handle_subscription_updated(self, subscription):
        """Handle subscription update"""
        return {
            "action": "subscription_updated",
            "subscription_id": subscription["id"],
            "status": subscription["status"],
        }

    def _handle_subscription_deleted(self, subscription):
        """Handle subscription cancellation"""
        return {
            "action": "subscription_deleted",
            "subscription_id": subscription["id"],
            "customer_id": subscription["customer"],
        }

    def _handle_invoice_paid(self, invoice):
        """Handle successful payment"""
        return {
            "action": "invoice_paid",
            "customer_id": invoice["customer"],
            "amount": invoice["amount_paid"] / 100,
            "invoice_id": invoice["id"],
        }

    def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        return {
            "action": "payment_failed",
            "customer_id": invoice["customer"],
            "amount": invoice["amount_due"] / 100,
            "invoice_id": invoice["id"],
        }

    def _handle_payment_method_attached(self, payment_method):
        """Handle payment method attachment"""
        return {
            "action": "payment_method_attached",
            "customer_id": payment_method["customer"],
            "payment_method_id": payment_method["id"],
        }

    def _handle_default(self, data):
        """Handle unknown event types"""
        return {"action": "unknown_event", "data": data}


# Subscription plan definitions
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "price_monthly": 29,
        "price_yearly": 290,  # 2 months free
        "features": [
            "10 evidence uploads/month",
            "PDF analysis",
            "Basic AI chat",
            "5GB storage",
            "Email support",
        ],
        "stripe_price_id_monthly": "price_basic_monthly",
        "stripe_price_id_yearly": "price_basic_yearly",
    },
    "pro": {
        "name": "Professional",
        "price_monthly": 99,
        "price_yearly": 990,
        "features": [
            "100 evidence uploads/month",
            "PDF + Video + Audio analysis",
            "Advanced AI agents",
            "50GB storage",
            "Transcription (10 hours/month)",
            "Priority support",
        ],
        "stripe_price_id_monthly": "price_pro_monthly",
        "stripe_price_id_yearly": "price_pro_yearly",
    },
    "premium": {
        "name": "Premium",
        "price_monthly": 299,
        "price_yearly": 2990,
        "features": [
            "Unlimited evidence uploads",
            "All analysis tools",
            "Custom AI agents",
            "Unlimited storage",
            "Transcription (unlimited)",
            "Team collaboration (5 users)",
            "24/7 priority support",
            "Custom integrations",
        ],
        "stripe_price_id_monthly": "price_premium_monthly",
        "stripe_price_id_yearly": "price_premium_yearly",
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": "custom",
        "price_yearly": "custom",
        "features": [
            "Everything in Premium",
            "Unlimited team members",
            "Dedicated account manager",
            "Custom SLA",
            "On-premise deployment option",
            "API access",
            "White-label option",
        ],
        "contact_sales": True,
    },
}


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("STRIPE PAYMENT SERVICE EXAMPLE")
    print("=" * 80)

    # This would work with actual Stripe keys:
    # stripe_service = StripePaymentService()

    # # Create customer
    # customer = stripe_service.create_customer(
    #     email="john.doe@example.com",
    #     name="John Doe",
    #     metadata={'user_id': '12345'}
    # )
    # print(f"\n✓ Customer created: {customer['customer_id']}")

    # # Create checkout session
    # checkout = stripe_service.create_checkout_session(
    #     customer_id=customer['customer_id'],
    #     price_id='price_pro_monthly',
    #     success_url='https://Evident.info/success',
    #     cancel_url='https://Evident.info/cancel',
    #     trial_days=14
    # )
    # print(f"✓ Checkout URL: {checkout['url']}")

    print("\n✓ Stripe Payment Service ready!")
    print("  Install: pip install stripe")
    print("  Set env: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET")
    print("=" * 80)


