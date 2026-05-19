"""Health check endpoints for Railway deployment."""
import time
import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

_start_time = time.monotonic()


def _uptime_seconds() -> int:
    return int(time.monotonic() - _start_time)


@router.get("/health/live")
async def liveness():
    """Liveness probe - always 200 if the process is running."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness():
    """Readiness probe - verifies Playwright/Chromium is available."""
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()
        return {"status": "ready", "chromium": "ok"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "chromium": str(e)}


@router.get("/health")
async def full_health():
    """Full health status including session info and uptime."""
    from server.mcp_router import get_server

    try:
        server = get_server()
        sessions = server.session_info
    except RuntimeError:
        sessions = {"error": "server not initialized"}

    return {
        "status": "ok",
        "uptime_seconds": _uptime_seconds(),
        "sessions": sessions,
        "tool_count": 10,
    }
