# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""Test login flow"""

import os
import re

from app import app

"""Test login flow.

Credentials are read from environment variables to avoid committing secrets in
test code. Set `EVIDENT_TEST_ADMIN_EMAIL` and `EVIDENT_TEST_ADMIN_PASSWORD`
in CI or your local environment. Defaults are provided for convenience in
local development but should not be used for real credentials.
"""

ADMIN_EMAIL = os.environ.get("EVIDENT_TEST_ADMIN_EMAIL", "admin@Evident")
ADMIN_PASSWORD = os.environ.get("EVIDENT_TEST_ADMIN_PASSWORD", "AdminTest2026!")


print("Testing login flow...")

with app.test_client() as client:
    resp = client.get("/auth/login")
    print(f"GET /auth/login: {resp.status_code}")

    html = resp.data.decode("utf-8")
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    csrf = csrf_match.group(1) if csrf_match else None

    data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    if csrf:
        data["csrf_token"] = csrf

    resp = client.post("/auth/login", data=data, follow_redirects=False)

    print(f"POST /auth/login: {resp.status_code}")
    location = resp.headers.get("Location", "none")
    print(f"Redirect to: {location}")

    if resp.status_code == 302 and "/dashboard" in location:
        print("\n✅ LOGIN SUCCESS!")
    else:
        print("\n❌ LOGIN FAILED")
        body = resp.data.decode("utf-8")
        if "Invalid" in body:
            print("Reason: Invalid credentials")
        elif "Suspicious" in body:
            print("Reason: Blocked by security check")
