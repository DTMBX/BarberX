import json
import py_compile
from pathlib import Path

# Candidate base paths (original and _backend variant)
base_paths = [
    "backend/app/root_legacy/retrieval_service.py",
    "backend/app/root_legacy/_backend/retrieval_service.py",
    "backend/src/retrieval_service.py",
    "backend/src/_backend/retrieval_service.py",
    "backend/src-old/ai/pipeline/services/retrieval_service.py",
    "backend/src-old/ai/pipeline/services/_backend/retrieval_service.py",
    "src/ai/pipeline/services/retrieval_service.py",
    "src/ai/pipeline/services/_backend/retrieval_service.py",
]

errors = []

# Compile any candidate that actually exists; skip missing files
for p_str in base_paths:
    p = Path(p_str)
    if not p.exists():
        continue
    try:
        py_compile.compile(str(p), doraise=True)
    except Exception as e:
        errors.append({"path": str(p), "error": str(e)})

out = Path("_retrieval_fail.json")
out.write_text(json.dumps(errors, indent=2))
print("Errors:", len(errors))
