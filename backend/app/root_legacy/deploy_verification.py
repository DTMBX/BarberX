# Deployment Verification Script
# This script checks if your GitHub Pages and Render deployments are live.

import requests

def check_url(url):
    try:
        response = requests.get(url, timeout=10)
        print(f"{url}: {response.status_code} {response.reason}")
        if response.status_code == 200:
            print(f"SUCCESS: {url} is live.")
        else:
            print(f"WARNING: {url} returned status {response.status_code}.")
    except Exception as e:
        print(f"ERROR: Could not reach {url}. Reason: {e}")

if __name__ == "__main__":
    urls = [
        "https://evident.info",
        "https://www.evident.info",
        "https://app.evident.info"
    ]
    for url in urls:
        check_url(url)


