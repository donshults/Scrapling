"""Bearer token authentication for MCP endpoint."""
import logging
from typing import Optional

from fastapi import Header, HTTPException

from server.config import get_settings

logger = logging.getLogger(__name__)


async def verify_mcp_auth(
    authorization: Optional[str] = Header(None),
) -> bool:
    """Verify Bearer token authentication.

    Supports comma-separated keys for rotation (set multiple in SCRAPLING_API_KEY).
    """
    if not authorization:
        logger.warning("MCP auth failed: no Authorization header")
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.lower().startswith("bearer "):
        logger.warning("MCP auth failed: not a Bearer token")
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")

    token = authorization[7:].strip()
    settings = get_settings()

    if token not in settings.api_keys:
        logger.warning(f"MCP auth failed: invalid token {token[:8]}...")
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return True
