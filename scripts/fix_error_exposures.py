# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Batch fix error exposure vulnerabilities in app.py
Replaces all instances of exposed error messages with sanitized versions
"""

import re
from pathlib import Path


def fix_error_exposures():
    """Fix all error exposure vulnerabilities"""

    app_path = Path("app.py")

    with open(app_path, encoding="utf-8") as f:
        content = f.read()

    # Pattern 1: return jsonify({"error": str(e)}), STATUS_CODE
    pattern1 = r'return jsonify\(\{"error": str\(e\)\}\), (\d+)'

    # Count occurrences
    matches = list(re.finditer(pattern1, content))
    print(f"Found {len(matches)} error exposure vulnerabilities")

    # Create replacement function
    def replace_error(match):
        status_code = match.group(1)

        # Determine error category based on status code
        if status_code in ["400", "422"]:
            category = "validation"
        elif status_code in ["401"]:
            category = "authentication"
        elif status_code in ["403"]:
            category = "authorization"
        elif status_code in ["404"]:
            category = "database"
        else:
            category = "default"

        return f"""# Log error server-side
        logger.error(f"{{request.path}} failed: {{type(e).__name__}}: {{e}}", exc_info=True)
        error_ticket = ErrorSanitizer.create_error_ticket()
        return error_response(
            ErrorSanitizer.sanitize_error(e, '{category}'),
            error_code='OPERATION_FAILED',
            status_code={status_code},
            error_ticket=error_ticket
        )"""

    # Replace all occurrences
    fixed_content = re.sub(pattern1, replace_error, content)

    # Check if we need to add imports
    if "from utils.security import ErrorSanitizer" not in fixed_content:
        # Find the first function that uses error handling
        import_position = fixed_content.find("def ")
        if import_position > 0:
            # Insert imports before first function
            imports = """from utils.security import ErrorSanitizer
from utils.responses import error_response
from utils.logging_config import get_logger

logger = get_logger('api')

"""
            fixed_content = (
                fixed_content[:import_position] + imports + fixed_content[import_position:]
            )

    # Write back
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    print(f"✓ Fixed {len(matches)} error exposure vulnerabilities")
    print("✓ Added proper error sanitization")
    print("✓ Added error ticket generation")
    print("✓ Added server-side logging")

    return len(matches)


if __name__ == "__main__":
    print("=" * 60)
    print("BATCH ERROR EXPOSURE FIX")
    print("=" * 60)
    print()

    fixed_count = fix_error_exposures()

    print()
    print("=" * 60)
    print(f"COMPLETE: Fixed {fixed_count} vulnerabilities")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the changes in app.py")
    print("2. Test the endpoints")
    print("3. Commit the changes")
