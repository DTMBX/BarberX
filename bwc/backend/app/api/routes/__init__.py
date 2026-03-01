"""API routes package — import all routers here for inclusion in the app."""

from app.api.routes.projects import router as projects_router  # noqa: F401
from app.api.routes.cases import router as cases_router  # noqa: F401
from app.api.routes.evidence import router as evidence_router  # noqa: F401
from app.api.routes.artifacts import router as artifacts_router  # noqa: F401
from app.api.routes.jobs import router as jobs_router  # noqa: F401
from app.api.routes.issues import router as issues_router  # noqa: F401
from app.api.routes.manifest import router as manifest_router  # noqa: F401
from app.api.routes.verify import router as verify_router  # noqa: F401
from app.api.routes.timeline import router as timeline_router  # noqa: F401
from app.api.routes.chat import router as chat_router  # noqa: F401
from app.api.routes.legal import router as legal_router  # noqa: F401
