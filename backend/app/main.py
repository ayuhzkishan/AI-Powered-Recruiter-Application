from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.middleware import SecurityHeadersMiddleware
from app.api.routes import candidates, jobs, matches, auth

limiter = Limiter(key_func=get_remote_address)


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Recruiter API",
        docs_url="/docs" if settings.APP_ENV == "development" else None,
        redoc_url=None,
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS — strict allowlist (A05)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Security headers on every response
    app.add_middleware(SecurityHeadersMiddleware)

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "healthy", "env": settings.APP_ENV}

    # Routes
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(
        candidates.router, prefix="/api/candidates", tags=["candidates"]
    )
    app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(matches.router, prefix="/api/matches", tags=["matches"])

    return app


app = create_app()
