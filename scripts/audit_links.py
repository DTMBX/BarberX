import os
import re
from urllib.parse import urlparse

# Simple broken link checker for local HTML files
SITE_DIR = os.path.join(os.path.dirname(__file__), '..', '_site')
link_pattern = re.compile(r'href=["\'](.*?)["\']')
missing_links = []

for root, _, files in os.walk(SITE_DIR, followlinks=False):
    if os.path.islink(root) or 'sandbox' in root:
        continue
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, encoding='utf-8') as f:
                html = f.read()
                for match in link_pattern.findall(html):
                    parsed = urlparse(match)
                    if parsed.scheme in ('http', 'https', 'mailto', 'tel'):
                        continue
                    target = os.path.normpath(os.path.join(root, match.lstrip('/')))
                    if not os.path.exists(target):
                        missing_links.append((path, match))

if missing_links:
    print('Broken links found:')
    for src, link in missing_links:
        print(f'{src} -> {link}')
else:
    print('No broken links found.')
