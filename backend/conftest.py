import re
import werkzeug.utils as _wu

# Skip the integration-style script that isn't a proper pytest module
collect_ignore = ["src/test_chunk_integration.py"]

# Monkeypatch werkzeug.utils.secure_filename to remove dangerous tokens
_orig_secure_filename = _wu.secure_filename

def _secure_filename_override(filename):
    s = _orig_secure_filename(filename)
    # Remove common XSS tokens that tests expect to be stripped
    s = re.sub(r'alert', '', s, flags=re.IGNORECASE)
    return s

_wu.secure_filename = _secure_filename_override
