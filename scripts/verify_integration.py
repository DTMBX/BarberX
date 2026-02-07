# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Verify Stripe Integration - Run this to check everything is set up correctly
"""

import os
import sys

import requests


def check_env_vars():
    """Check all required environment variables"""
    print("🔍 Checking Environment Variables...\n")

    required_vars = {
        "STRIPE_SECRET_KEY": "Stripe Secret Key",
        "STRIPE_PUBLISHABLE_KEY": "Stripe Publishable Key",
        "STRIPE_PRICE_PRO": "Pro Plan Price ID",
        "STRIPE_PRICE_PREMIUM": "Premium Plan Price ID",
        "STRIPE_WEBHOOK_SECRET": "Webhook Signing Secret",
        "AMPLITUDE_API_KEY": "Amplitude API Key",
    }

    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Show partial value for security
            if "KEY" in var or "SECRET" in var:
                display = f"{value[:10]}...{value[-4:]}"
            else:
                display = value
            print(f"✅ {description:30s} {display}")
        else:
            print(f"❌ {description:30s} NOT SET")
            all_set = False

    print()
    return all_set


def check_stripe_connection():
    """Test Stripe API connection"""
    print("🔍 Testing Stripe Connection...\n")

    try:
        import stripe

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        # Try to list products
        products = stripe.Product.list(limit=3)
        print("✅ Connected to Stripe")
        print(f"✅ Found {len(products.data)} products")

        for product in products.data:
            print(f"   - {product.name}")

        print()
        return True

    except Exception as e:
        print(f"❌ Stripe connection failed: {e}\n")
        return False


def check_price_ids():
    """Verify price IDs exist in Stripe"""
    print("🔍 Verifying Price IDs...\n")

    try:
        import stripe

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        pro_price = os.getenv("STRIPE_PRICE_PRO")
        premium_price = os.getenv("STRIPE_PRICE_PREMIUM")

        if not pro_price or not premium_price:
            print("❌ Price IDs not set in environment\n")
            return False

        # Check Pro price
        try:
            price = stripe.Price.retrieve(pro_price)
            print(f"✅ Pro Plan: ${price.unit_amount / 100}/month")
        except:
            print(f"❌ Pro price ID not found: {pro_price}")
            return False

        # Check Premium price
        try:
            price = stripe.Price.retrieve(premium_price)
            print(f"✅ Premium Plan: ${price.unit_amount / 100}/month")
        except:
            print(f"❌ Premium price ID not found: {premium_price}")
            return False

        print()
        return True

    except Exception as e:
        print(f"❌ Error checking prices: {e}\n")
        return False


def check_amplitude():
    """Test Amplitude connection"""
    print("🔍 Testing Amplitude Connection...\n")

    api_key = os.getenv("AMPLITUDE_API_KEY")
    if not api_key:
        print("❌ Amplitude API key not set\n")
        return False

    try:
        # Try to send a test event
        response = requests.post(
            "https://api2.amplitude.com/2/httpapi",
            json={
                "api_key": api_key,
                "events": [
                    {
                        "user_id": "test_verification",
                        "event_type": "integration_check",
                        "time": int(__import__("time").time() * 1000),
                    }
                ],
            },
        )

        if response.status_code == 200:
            print("✅ Amplitude connected")
            print()
            return True
        else:
            print(f"❌ Amplitude error: {response.status_code}")
            print()
            return False

    except Exception as e:
        print(f"❌ Amplitude connection failed: {e}\n")
        return False


def check_webhook_endpoint():
    """Check if webhook endpoint is accessible"""
    print("🔍 Checking Webhook Endpoint...\n")

    # Try common URLs
    urls = ["https://Evident-backend.onrender.com", "https://Evident.info", "http://localhost:5000"]

    for base_url in urls:
        try:
            response = requests.get(f"{base_url}/payments/pricing", timeout=5)
            if response.status_code == 200:
                print(f"✅ App is live at: {base_url}")
                print(f"✅ Webhook URL: {base_url}/payments/webhook")
                print()
                return True
        except:
            continue

    print("❌ Could not reach app (may not be deployed yet)")
    print()
    return False


def main():
    """Run all checks"""
    print("\n" + "=" * 60)
    print("🚀 STRIPE INTEGRATION VERIFICATION")
    print("=" * 60 + "\n")

    results = []

    # Run all checks
    results.append(("Environment Variables", check_env_vars()))
    results.append(("Stripe Connection", check_stripe_connection()))
    results.append(("Price IDs", check_price_ids()))
    results.append(("Amplitude", check_amplitude()))
    results.append(("Webhook Endpoint", check_webhook_endpoint()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {check}")

    print(f"\n{passed}/{total} checks passed\n")

    if passed == total:
        print("🎉 ALL CHECKS PASSED - READY FOR PAYMENTS!")
        print("\nNext steps:")
        print("1. Test checkout: https://YOUR-URL/payments/pricing")
        print("2. Use test card: 4242 4242 4242 4242")
        print("3. Verify payment in Stripe dashboard")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nFix the failed items above, then run this script again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
