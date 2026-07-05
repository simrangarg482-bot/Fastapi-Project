import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ENV = os.getenv('ENV', 'development')

# Dev-only fallbacks so the app still runs out of the box locally.
# In production these MUST come from real env vars / a secrets manager --
# we hard-fail instead of silently falling back so a bad deploy is loud,
# not a quiet security hole.
_DEV_API_KEY = 'demo-key'
_DEV_JWT_SECRET = 'insecure-dev-secret-do-not-use-in-prod'


def _require_secret(env_var: str, dev_fallback: str) -> str:
    value = os.getenv(env_var)
    if value:
        return value
    if ENV == 'production':
        raise RuntimeError(
            f"{env_var} must be set via environment variable in production."
        )
    logger.warning(
        "%s not set -- using insecure development fallback. "
        "Set %s in your .env for anything beyond local testing.",
        env_var, env_var,
    )
    return dev_fallback


class Settings:
    PROJECT_NAME = 'Car Price API'
    API_KEY = _require_secret('API_KEY', _DEV_API_KEY)
    JWT_SECRET_KEY = _require_secret('JWT_SECRET_KEY', _DEV_JWT_SECRET)
    JWT_ALGORITHM = 'HS256'
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    MODEL_PATH = 'app/models/model.joblib'


settings = Settings() 