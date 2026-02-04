"""Quick validation script for tier system configuration"""

from flask import Flask

from .models_auth import TierLevel, User, db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    print("\n" + "=" * 60)
    print("TIER SYSTEM VALIDATION")
    print("=" * 60 + "\n")

    # Test each tier
    for tier in TierLevel:
        if tier.name == "ADMIN":
            continue

        print(f"\n{tier.name} TIER (${tier.value}/mo)")
        print("-" * 40)

        # Get limits
        limits = User.get_tier_limits(None, tier)

        # Display key limits
        print(f"  Videos/month: {limits.get('bwc_videos_per_month', 'N/A')}")
        print(f"  PDFs/month: {limits.get('pdf_documents_per_month', 'N/A')}")
        print(f"  Cases: {limits.get('case_limit', 'N/A')}")
        print(f"  Storage: {limits.get('storage_gb', 'N/A')} GB")
        print(f"  Trial days: {limits.get('trial_days', 0)}")
        print(f"  Overage allowed: {limits.get('overage_allowed', False)}")

        if limits.get("overage_allowed"):
            print(f"  Overage fee/video: ${limits.get('overage_fee_per_video', 0)}")
            print(f"  Overage fee/PDF: ${limits.get('overage_fee_per_pdf', 0)}")

    print("\n" + "=" * 60)
    print("✅ VALIDATION COMPLETE")
    print("=" * 60)


