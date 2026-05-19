"""FastAPI application for Scrapling Remote MCP Server."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.config import get_settings
from server.session_manager import ManagedScraplingServer
from server.mcp_router import router as mcp_router, set_server
from server.health import router as health_router

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init server + cleanup loop. Shutdown: close all sessions."""
    server = ManagedScraplingServer()
    set_server(server)
    await server.start_cleanup_loop()
    logger.info(
        f"Scrapling MCP server started "
        f"(max_sessions={settings.max_concurrent_sessions}, "
        f"idle_timeout={settings.session_idle_timeout}s)"
    )
    yield
    logger.info("Shutting down - closing all browser sessions...")
    await server.shutdown()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Scrapling MCP Server",
    version="1.0.0",
    description="Remote MCP server for Scrapling web scraping tools",
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router)
app.include_router(mcp_router)


@app.get("/")
async def root():
    return {
        "service": "scrapling-mcp",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "health": "/health",
    }
