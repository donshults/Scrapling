"""MCP JSON-RPC 2.0 endpoint for Scrapling tools.

Follows the same pattern as Context Vault (Dons-Brain) routes_mcp.py.
"""
import time
import logging
import json
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from server.auth import verify_mcp_auth
from server.tools import MCP_TOOLS
from server.session_manager import ManagedScraplingServer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["MCP"])

# Singleton server instance (initialized in app.py lifespan)
_server: ManagedScraplingServer | None = None


def get_server() -> ManagedScraplingServer:
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server


def set_server(server: ManagedScraplingServer):
    global _server
    _server = server


# --- JSON-RPC helpers ---

def create_mcp_response(request_id: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def create_mcp_error(request_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def format_text_response(text: str) -> dict:
    """Format a text result as MCP tool content."""
    return {"content": [{"type": "text", "text": text}]}


def format_response_model(result: Any) -> dict:
    """Format a Scrapling ResponseModel (or list thereof) as MCP text content."""
    if isinstance(result, list):
        parts = []
        for i, item in enumerate(result):
            header = f"--- Result {i + 1} (status: {item.status}, url: {item.url}) ---\n"
            content = "\n\n".join(item.content) if item.content else "(empty)"
            parts.append(header + content)
        return format_text_response("\n\n".join(parts))
    else:
        header = f"Status: {result.status} | URL: {result.url}\n\n"
        content = "\n\n".join(result.content) if result.content else "(empty)"
        return format_text_response(header + content)


def format_session_list(sessions: list) -> dict:
    """Format session list as text."""
    if not sessions:
        return format_text_response("No active sessions.")

    lines = [f"Active sessions ({len(sessions)}):"]
    for s in sessions:
        status = "alive" if s.is_alive else "dead"
        lines.append(f"  [{s.session_type}] {s.session_id} - {status} (created: {s.created_at})")
    return format_text_response("\n".join(lines))


# --- Tool dispatch ---

TOOL_HANDLERS = {
    "get": "get",
    "bulk_get": "bulk_get",
    "fetch": "fetch",
    "bulk_fetch": "bulk_fetch",
    "stealthy_fetch": "stealthy_fetch",
    "bulk_stealthy_fetch": "bulk_stealthy_fetch",
    "open_session": "open_session",
    "close_session": "close_session",
    "list_sessions": "list_sessions",
    "screenshot": "screenshot",
}


async def handle_tools_call(tool_name: str, arguments: dict) -> dict:
    """Dispatch a tool call to the managed server and format the result."""
    server = get_server()

    if tool_name not in TOOL_HANDLERS:
        return format_text_response(f"Unknown tool: {tool_name}")

    method_name = TOOL_HANDLERS[tool_name]
    start = time.monotonic()

    try:
        if tool_name == "list_sessions":
            result = await server.list_sessions()
            formatted = format_session_list(result)
        elif tool_name == "screenshot":
            result = await server.screenshot(**arguments)
            # screenshot returns List[ImageContent | TextContent] - pass through as-is
            formatted = {"content": [item.model_dump() if hasattr(item, "model_dump") else item for item in result]}
        elif tool_name in ("open_session", "close_session"):
            method = getattr(server, method_name)
            result = await method(**arguments)
            formatted = format_text_response(result.model_dump_json(indent=2))
        elif tool_name in ("get", "fetch", "stealthy_fetch"):
            method = getattr(server, method_name)
            result = await method(**arguments)
            formatted = format_response_model(result)
        elif tool_name in ("bulk_get", "bulk_fetch", "bulk_stealthy_fetch"):
            method = getattr(server, method_name)
            result = await method(**arguments)
            formatted = format_response_model(result)
        else:
            method = getattr(server, method_name)
            result = await method(**arguments)
            formatted = format_text_response(str(result))

        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(json.dumps({
            "event": "mcp_tool_call",
            "tool": tool_name,
            "duration_ms": duration_ms,
            "success": True,
        }))
        return formatted

    except Exception as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.error(json.dumps({
            "event": "mcp_tool_call",
            "tool": tool_name,
            "duration_ms": duration_ms,
            "success": False,
            "error": str(e),
        }))
        return format_text_response(f"Error in {tool_name}: {str(e)}")


# --- MCP endpoint ---

@router.post("")
async def mcp_handler(
    request: Request,
    _auth: bool = Depends(verify_mcp_auth),
) -> JSONResponse:
    """MCP JSON-RPC 2.0 endpoint."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            create_mcp_error(None, -32700, "Parse error"),
            status_code=400,
        )

    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")

    if method == "initialize":
        return JSONResponse(create_mcp_response(request_id, {
            "protocolVersion": "2025-11-25",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "scrapling-mcp",
                "version": "1.0.0",
            },
        }))

    elif method == "notifications/initialized":
        return JSONResponse(create_mcp_response(request_id, {}))

    elif method == "tools/list":
        return JSONResponse(create_mcp_response(request_id, {"tools": MCP_TOOLS}))

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            return JSONResponse(
                create_mcp_error(request_id, -32602, "Missing tool name"),
                status_code=400,
            )

        result = await handle_tools_call(tool_name, arguments)
        return JSONResponse(create_mcp_response(request_id, result))

    else:
        return JSONResponse(
            create_mcp_error(request_id, -32601, f"Unknown method: {method}"),
            status_code=400,
        )


@router.get("/health")
async def mcp_health():
    """Lightweight MCP-specific health check."""
    server = get_server()
    return {
        "status": "ok",
        "tool_count": len(MCP_TOOLS),
        "sessions": server.session_info,
    }
