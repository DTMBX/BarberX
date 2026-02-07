# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""Test login flow"""

import re

from app import app

print("Testing login flow...")

with app.test_client() as client:
    # Get login page
    resp = client.get("/auth/login")
    print(f"GET /auth/login: {resp.status_code}")

    html = resp.data.decode("utf-8")
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', html)

    if not csrf_match:
        print("WARN: No CSRF token found; continuing without token")
        csrf = None
    else:
        csrf = csrf_match.group(1)
        print(f"CSRF token: {csrf[:20]}...")

    # Try login
    resp = client.post(
        "/auth/login",
        data=(
            {"email": "admin@Evident", "password": "AdminTest2026!"}
            if csrf is None
            else {"email": "admin@Evident", "password": "AdminTest2026!", "csrf_token": csrf}
        ),
        follow_redirects=False,
    )

    print(f"POST /auth/login: {resp.status_code}")
    location = resp.headers.get("Location", "none")
    print(f"Redirect to: {location}")

    if resp.status_code == 302 and "/dashboard" in location:
        print("\n✅ LOGIN SUCCESS!")
    else:
        print("\n❌ LOGIN FAILED")
        if "Invalid" in resp.data.decode("utf-8"):
            print("Reason: Invalid credentials")
        elif "Suspicious" in resp.data.decode("utf-8"):
            print("Reason: Blocked by security check")
