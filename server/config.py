"""Environment variable configuration with fail-fast validation."""
import os
import sys
import logging

logger = logging.getLogger(__name__)


class Settings:
    """Server settings loaded from environment variables."""

    def __init__(self):
        # Required
        self.api_key: str = self._require("SCRAPLING_API_KEY")

        # Optional with defaults
        self.port: int = int(os.getenv("PORT", "8000"))
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.max_concurrent_sessions: int = int(os.getenv("MAX_CONCURRENT_SESSIONS", "10"))
        self.session_idle_timeout: int = int(os.getenv("SESSION_IDLE_TIMEOUT_SECONDS", "1800"))
        self.session_cleanup_interval: int = int(os.getenv("SESSION_CLEANUP_INTERVAL_SECONDS", "60"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")

        # Derived: split comma-separated keys for rotation support
        self.api_keys: list[str] = [k.strip() for k in self.api_key.split(",") if k.strip()]

    @staticmethod
    def _require(name: str) -> str:
        value = os.getenv(name)
        if not value:
            logger.critical(f"Required environment variable {name} is not set")
            sys.exit(1)
        return value


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
