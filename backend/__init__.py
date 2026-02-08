import sys
from pathlib import Path

# Make the repository `_backend` folder act as the `backend` package root for tests
# by prepending it to this package's search path. This keeps the on-disk name
# private (`_backend`) while allowing imports like `backend.src...` to work.
_root = Path(__file__).resolve().parent.parent / "_backend"
if str(_root) not in sys.path:
    __path__.insert(0, str(_root))
