# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Stripe Pricing Table Integration Script
Adds routes for Stripe pricing table checkout
"""

import os


def add_stripe_pricing_routes():
    """Add Stripe pricing table routes to app.py"""

    app_py_path = "app.py"

    if not os.path.exists(app_py_path):
        print(f"❌ {app_py_path} not found!")
        return False

    with open(app_py_path, encoding="utf-8") as f:
        content = f.read()

    # Check if routes already exist
    if "/pricing-stripe" in content:
        print("✅ Stripe pricing routes already exist!")
        return True

    # Find the pricing route section
    pricing_route = """
# Stripe Pricing Table Routes
@app.route('/pricing-stripe')
def pricing_stripe():
    \"\"\"Stripe embedded pricing table\"\"\"
    return render_template('pricing-stripe-embed.html')

@app.route('/pricing')
def pricing():
    \"\"\"Main pricing page with custom cards\"\"\"
    # Option 1: Use custom cards (pricing-5tier.html)
    return render_template('pricing.html')
    
    # Option 2: Use Stripe embed (uncomment to switch)
    # return render_template('pricing-stripe-embed.html')
"""

    # Find a good insertion point (after existing pricing route or near the end of routes)
    if "@app.route('/pricing')" in content:
        print("ℹ️  Pricing route already exists, skipping...")
        return True

    # Insert before the final if __name__ == '__main__':
    if "if __name__ == '__main__':" in content:
        content = content.replace(
            "if __name__ == '__main__':", f"{pricing_route}\n\nif __name__ == '__main__':"
        )
    else:
        # Append to end
        content += f"\n\n{pricing_route}\n"

    # Write back
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Added Stripe pricing routes to app.py")
    return True


def create_template_symlinks():
    """Create symlinks or copies for pricing templates"""

    templates_dir = "templates"

    if not os.path.exists(templates_dir):
        print(f"❌ {templates_dir} directory not found!")
        return False

    # Copy pricing-5tier.html to templates/pricing.html if needed
    if os.path.exists("pricing-5tier.html") and not os.path.exists(f"{templates_dir}/pricing.html"):
        import shutil

        shutil.copy("pricing-5tier.html", f"{templates_dir}/pricing.html")
        print(f"✅ Copied pricing-5tier.html to {templates_dir}/pricing.html")

    # Verify pricing-stripe-embed.html exists
    if not os.path.exists(f"{templates_dir}/pricing-stripe-embed.html"):
        print(f"⚠️  {templates_dir}/pricing-stripe-embed.html not found (should already exist)")
    else:
        print(f"✅ {templates_dir}/pricing-stripe-embed.html exists")

    return True


def update_env_file():
    """Add Stripe keys to .env file if not present"""

    env_path = ".env"

    stripe_vars = """
# Stripe Pricing Table Configuration
# Get these values from your Stripe Dashboard: https://dashboard.stripe.com
STRIPE_PRICING_TABLE_ID=prctbl_YOUR_PRICING_TABLE_ID_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
"""

    if not os.path.exists(env_path):
        print(f"ℹ️  Creating {env_path}...")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(stripe_vars)
        print(f"✅ Created {env_path} with Stripe configuration")
        return True

    with open(env_path, encoding="utf-8") as f:
        content = f.read()

    if "STRIPE_PRICING_TABLE_ID" in content:
        print(f"✅ Stripe configuration already in {env_path}")
        return True

    # Append to .env
    with open(env_path, "a", encoding="utf-8") as f:
        f.write(stripe_vars)

    print(f"✅ Added Stripe configuration to {env_path}")
    return True


def main():
    print("=" * 60)
    print("STRIPE PRICING TABLE INTEGRATION")
    print("=" * 60)
    print()

    print("Step 1: Adding Stripe pricing routes to app.py...")
    add_stripe_pricing_routes()
    print()

    print("Step 2: Setting up template files...")
    create_template_symlinks()
    print()

    print("Step 3: Updating environment variables...")
    update_env_file()
    print()

    print("=" * 60)
    print("✅ INTEGRATION COMPLETE!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print()
    print("1. Start the Flask app:")
    print("   python app.py")
    print()
    print("2. Visit pricing pages:")
    print("   http://localhost:5000/pricing           (Custom cards)")
    print("   http://localhost:5000/pricing-stripe    (Stripe embed)")
    print("   http://localhost:5000/pricing#stripe-checkout (Toggle)")
    print()
    print("3. Configure Stripe webhooks:")
    print("   See STRIPE-5TIER-SETUP-GUIDE.md for details")
    print()
    print("4. Test checkout flow:")
    print("   Use Stripe test mode first")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Add STRIPE_SECRET_KEY to .env (DO NOT COMMIT)")
    print("   - Configure webhook endpoint in Stripe Dashboard")
    print("   - Test in Stripe test mode before going live")
    print()


if __name__ == "__main__":
    main()
