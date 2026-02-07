# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Integration Script: Add Subscription System to app.py
Adds Stripe integration, tier gating, and usage dashboard
"""

import os
import sys


def add_imports_to_app():
    """Add necessary imports to app.py"""
    print("📦 Adding imports to app.py...")

    imports_to_add = """
# Subscription & tier gating imports
from stripe_subscription_service import stripe_bp, StripeSubscriptionService
from tier_gating import (
    require_tier,
    check_usage_limit,
    require_feature,
    TierGate,
    register_tier_gate_helpers
)
"""

    # Read app.py
    with open("app.py", encoding="utf-8") as f:
        content = f.read()

    # Check if already added
    if "stripe_subscription_service" in content:
        print("✅ Imports already present")
        return

    # Find the last import statement
    lines = content.split("\n")
    import_end_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            import_end_idx = i

    # Insert imports
    lines.insert(import_end_idx + 1, imports_to_add)

    # Write back
    with open("app.py", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("✅ Added imports")


def register_blueprints():
    """Register Stripe blueprint"""
    print("\n📝 Registering Stripe blueprint...")

    with open("app.py", encoding="utf-8") as f:
        content = f.read()

    if "app.register_blueprint(stripe_bp)" in content:
        print("✅ Blueprint already registered")
        return

    # Find app creation
    blueprint_registration = """
# Register Stripe subscription blueprint
app.register_blueprint(stripe_bp)

# Register tier gating template helpers
register_tier_gate_helpers(app)
"""

    # Find where to insert (after app = Flask())
    lines = content.split("\n")
    app_creation_idx = 0
    for i, line in enumerate(lines):
        if "app = Flask(__name__)" in line or "app = create_app()" in line:
            app_creation_idx = i
            break

    # Find next empty line after app creation
    insert_idx = app_creation_idx + 1
    while insert_idx < len(lines) and lines[insert_idx].strip():
        insert_idx += 1

    # Insert blueprint registration
    lines.insert(insert_idx, blueprint_registration)

    with open("app.py", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("✅ Registered blueprints")


def add_usage_dashboard_route():
    """Add route for usage dashboard"""
    print("\n🎯 Adding usage dashboard route...")

    with open("app.py", encoding="utf-8") as f:
        content = f.read()

    if "@app.route('/dashboard/usage')" in content:
        print("✅ Route already exists")
        return

    route_code = '''
@app.route('/dashboard/usage')
@login_required
def usage_dashboard():
    """Usage dashboard showing subscription and limits"""
    from tier_gating import TierGate
    
    usage_stats = TierGate.get_usage_stats(current_user)
    
    return render_template(
        'usage_dashboard.html',
        usage_stats=usage_stats
    )
'''

    # Find a good place to insert (after other dashboard routes)
    lines = content.split("\n")
    insert_idx = len(lines) - 10  # Near end but before __main__

    # Find the line with "if __name__ == '__main__':"
    for i, line in enumerate(lines):
        if "if __name__ == '__main__':" in line or 'if __name__ == "__main__":' in line:
            insert_idx = i - 2
            break

    # Insert route
    lines.insert(insert_idx, route_code)

    with open("app.py", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("✅ Added usage dashboard route")


def update_env_file():
    """Add Stripe environment variables"""
    print("\n🔐 Updating .env file...")

    env_additions = """

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
STRIPE_PRICE_PRO=price_YOUR_PRO_PRICE_ID_HERE
STRIPE_PRICE_PREMIUM=price_YOUR_PREMIUM_PRICE_ID_HERE
"""

    if not os.path.exists(".env"):
        print("⚠️  .env file not found")
        return

    with open(".env", encoding="utf-8") as f:
        content = f.read()

    if "STRIPE_SECRET_KEY" in content:
        print("✅ Stripe keys already in .env")
        return

    with open(".env", "a", encoding="utf-8") as f:
        f.write(env_additions)

    print("✅ Added Stripe config to .env")


def create_test_accounts_script():
    """Create script for test accounts"""
    print("\n👥 Creating test accounts script...")

    script_content = '''"""
Create test accounts for subscription testing
"""

from app import app, db
from models_auth import User, TierLevel

def create_test_accounts():
    """Create test accounts for each tier"""
    with app.app_context():
        test_accounts = [
            {
                "email": "free@Evident.test",
                "password": "test123",
                "full_name": "Free Tier User",
                "tier": TierLevel.FREE
            },
            {
                "email": "pro@Evident.test",
                "password": "test123",
                "full_name": "Professional Tier User",
                "tier": TierLevel.PROFESSIONAL
            },
            {
                "email": "premium@Evident.test",
                "password": "test123",
                "full_name": "Premium Tier User",
                "tier": TierLevel.PREMIUM
            },
            {
                "email": "enterprise@Evident.test",
                "password": "test123",
                "full_name": "Enterprise Tier User",
                "tier": TierLevel.ENTERPRISE
            },
            {
                "email": "admin@Evident.test",
                "password": "admin123",
                "full_name": "Admin User",
                "tier": TierLevel.ADMIN,
                "is_admin": True
            }
        ]
        
        print("Creating test accounts...")
        for account in test_accounts:
            # Check if user exists
            existing = User.query.filter_by(email=account["email"]).first()
            if existing:
                print(f"  ⏭️  {account['email']} already exists")
                continue
            
            # Create user
            user = User(
                email=account["email"],
                full_name=account["full_name"],
                tier=account["tier"],
                is_verified=True,
                is_admin=account.get("is_admin", False)
            )
            user.set_password(account["password"])
            
            db.session.add(user)
            print(f"  ✅ Created {account['email']} ({account['tier'].name})")
        
        db.session.commit()
        print("\\n✅ Test accounts created successfully!")
        print("\\nLogin credentials:")
        print("  free@Evident.test / test123")
        print("  pro@Evident.test / test123")
        print("  premium@Evident.test / test123")
        print("  enterprise@Evident.test / test123")
        print("  admin@Evident.test / admin123")

if __name__ == "__main__":
    create_test_accounts()
'''

    with open("create_test_subscription_accounts.py", "w", encoding="utf-8") as f:
        f.write(script_content)

    print("✅ Created create_test_subscription_accounts.py")


def main():
    """Run integration"""
    print("=" * 70)
    print("SUBSCRIPTION SYSTEM INTEGRATION")
    print("=" * 70)

    try:
        add_imports_to_app()
        register_blueprints()
        add_usage_dashboard_route()
        update_env_file()
        create_test_accounts_script()

        print("\n" + "=" * 70)
        print("✅ INTEGRATION COMPLETE!")
        print("=" * 70)
        print("\n📋 NEXT STEPS:")
        print("\n1. Run database migration:")
        print("   python migrate_add_stripe_subscriptions.py")
        print("\n2. Create test accounts:")
        print("   python create_test_subscription_accounts.py")
        print("\n3. Configure Stripe:")
        print("   a. Create products in Stripe Dashboard:")
        print("      - PRO: $49/month with 3-day trial")
        print("      - PREMIUM: $249/month")
        print("   b. Copy price IDs to .env:")
        print("      - STRIPE_PRICE_PRO=price_...")
        print("      - STRIPE_PRICE_PREMIUM=price_...")
        print("   c. Get API keys and update .env:")
        print("      - STRIPE_SECRET_KEY=sk_...")
        print("      - STRIPE_PUBLISHABLE_KEY=pk_...")
        print("\n4. Set up webhook:")
        print("   URL: https://Evident.info/api/stripe/webhook")
        print("   Events: checkout.session.completed,")
        print("          customer.subscription.updated,")
        print("          customer.subscription.deleted")
        print("\n5. Test subscription flow:")
        print("   a. Login as free@Evident.test")
        print("   b. Go to /pricing")
        print("   c. Click upgrade button")
        print("   d. Complete checkout")
        print("   e. Check /dashboard/usage")
        print("\n6. Restart Flask app to load new code")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
