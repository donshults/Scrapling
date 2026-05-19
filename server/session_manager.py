"""Managed wrapper around ScraplingMCPServer with session limits and auto-cleanup."""
import asyncio
import time
import logging
from typing import Any

from scrapling.core.ai import ScraplingMCPServer
from server.config import get_settings

logger = logging.getLogger(__name__)


class ManagedScraplingServer:
    """Wraps ScraplingMCPServer with resource management.

    - Enforces max concurrent sessions
    - Tracks last-used timestamps per session
    - Background loop closes idle sessions
    - Forces headless=True (no display in Railway)
    - Rejects real_chrome=True (only Playwright Chromium available)
    """

    def __init__(self):
        self._server = ScraplingMCPServer()
        self._last_used: dict[str, float] = {}
        self._cleanup_task: asyncio.Task | None = None
        settings = get_settings()
        self._max_sessions = settings.max_concurrent_sessions
        self._idle_timeout = settings.session_idle_timeout
        self._cleanup_interval = settings.session_cleanup_interval

    @property
    def active_session_count(self) -> int:
        return len(self._server._sessions)

    @property
    def session_info(self) -> dict:
        """Current session stats for health checks."""
        return {
            "active_sessions": self.active_session_count,
            "max_sessions": self._max_sessions,
            "idle_timeout_seconds": self._idle_timeout,
        }

    async def start_cleanup_loop(self):
        """Start the background session cleanup loop."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(
            f"Session cleanup loop started (interval={self._cleanup_interval}s, "
            f"idle_timeout={self._idle_timeout}s, max_sessions={self._max_sessions})"
        )

    async def shutdown(self):
        """Close all sessions and stop cleanup loop."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Close all active sessions
        session_ids = list(self._server._sessions.keys())
        for sid in session_ids:
            try:
                await self._server.close_session(sid)
                logger.info(f"Shutdown: closed session {sid}")
            except Exception as e:
                logger.warning(f"Shutdown: failed to close session {sid}: {e}")

        self._last_used.clear()
        logger.info("All sessions closed, cleanup loop stopped")

    async def _cleanup_loop(self):
        """Periodically close idle sessions."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_idle_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")

    async def _cleanup_idle_sessions(self):
        """Close sessions that have been idle beyond the timeout."""
        now = time.monotonic()
        to_close = []

        for sid, last_used in list(self._last_used.items()):
            if now - last_used > self._idle_timeout:
                to_close.append(sid)

        for sid in to_close:
            try:
                await self._server.close_session(sid)
                self._last_used.pop(sid, None)
                logger.info(f"Auto-closed idle session {sid}")
            except Exception as e:
                logger.warning(f"Failed to auto-close session {sid}: {e}")
                # Remove from tracking even if close fails
                self._last_used.pop(sid, None)

    def _touch_session(self, session_id: str):
        """Update last-used timestamp for a session."""
        self._last_used[session_id] = time.monotonic()

    def _enforce_server_constraints(self, args: dict) -> dict:
        """Force headless=True, reject real_chrome=True."""
        args = dict(args)  # Don't mutate caller's dict
        if args.get("real_chrome"):
            raise ValueError(
                "real_chrome=True is not supported on the remote server. "
                "Only Playwright Chromium is available."
            )
        # Always force headless on server (no display)
        args["headless"] = True
        return args

    # --- Tool methods (delegate to ScraplingMCPServer) ---

    async def get(self, **kwargs) -> Any:
        return await self._server.get(**kwargs)

    async def bulk_get(self, **kwargs) -> Any:
        return await self._server.bulk_get(**kwargs)

    async def fetch(self, **kwargs) -> Any:
        kwargs = self._enforce_server_constraints(kwargs)
        if kwargs.get("session_id"):
            self._touch_session(kwargs["session_id"])
        return await self._server.fetch(**kwargs)

    async def bulk_fetch(self, **kwargs) -> Any:
        kwargs = self._enforce_server_constraints(kwargs)
        if kwargs.get("session_id"):
            self._touch_session(kwargs["session_id"])
        return await self._server.bulk_fetch(**kwargs)

    async def stealthy_fetch(self, **kwargs) -> Any:
        kwargs = self._enforce_server_constraints(kwargs)
        if kwargs.get("session_id"):
            self._touch_session(kwargs["session_id"])
        return await self._server.stealthy_fetch(**kwargs)

    async def bulk_stealthy_fetch(self, **kwargs) -> Any:
        kwargs = self._enforce_server_constraints(kwargs)
        if kwargs.get("session_id"):
            self._touch_session(kwargs["session_id"])
        return await self._server.bulk_stealthy_fetch(**kwargs)

    async def open_session(self, **kwargs) -> Any:
        if self.active_session_count >= self._max_sessions:
            raise ValueError(
                f"Maximum concurrent sessions ({self._max_sessions}) reached. "
                f"Close an existing session first."
            )
        kwargs = self._enforce_server_constraints(kwargs)
        result = await self._server.open_session(**kwargs)
        self._last_used[result.session_id] = time.monotonic()
        logger.info(f"Opened session {result.session_id} ({result.session_type})")
        return result

    async def close_session(self, **kwargs) -> Any:
        result = await self._server.close_session(**kwargs)
        self._last_used.pop(kwargs.get("session_id", ""), None)
        logger.info(f"Closed session {kwargs.get('session_id')}")
        return result

    async def list_sessions(self) -> Any:
        return await self._server.list_sessions()

    async def screenshot(self, **kwargs) -> Any:
        if kwargs.get("session_id"):
            self._touch_session(kwargs["session_id"])
        return await self._server.screenshot(**kwargs)
