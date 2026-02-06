import sys
import os

# Ensure backend paths are importable when running tools directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "backend", "src"))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from app import app

app.testing = True
with app.test_client() as client:
    resp = client.get('/auth/login')
    print('STATUS', resp.status_code)
    print(resp.data.decode('utf-8'))
