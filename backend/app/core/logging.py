import structlog
from app.core.config import settings

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),  # Machine-parseable JSON logs
    ],
)

logger = structlog.get_logger()


def log_security_event(event: str, user_id: str = None, details: dict = None):
    """Call this on EVERY security-relevant action."""
    logger.warning(
        event,
        user_id=user_id,
        details=details or {},
        env=settings.APP_ENV,
    )
