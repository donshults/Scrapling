"""MCP tool definitions (JSON Schema) for all 10 Scrapling tools.

Translated from scrapling/core/ai.py ScraplingMCPServer method signatures.
"""

# Shared schema fragments
_EXTRACTION_TYPE = {
    "type": "string",
    "enum": ["markdown", "html", "text"],
    "default": "markdown",
    "description": "Content extraction format: markdown, html, or text.",
}

_CSS_SELECTOR = {
    "type": "string",
    "description": "CSS selector to extract specific content. If main_content_only is True, executed on main content.",
}

_MAIN_CONTENT_ONLY = {
    "type": "boolean",
    "default": True,
    "description": "Extract only the main body content (inside <body> tag).",
}

_PROXY_STRING = {
    "type": "string",
    "description": "Proxy URL. Format: http://username:password@host:port",
}

_PROXY_FLEXIBLE = {
    "oneOf": [
        {"type": "string", "description": "Proxy URL string."},
        {
            "type": "object",
            "properties": {
                "server": {"type": "string"},
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["server"],
            "description": "Proxy as dict with server, username, password.",
        },
    ],
    "description": "Proxy URL string or dict with server/username/password keys.",
}

_WAIT_SELECTOR_STATE = {
    "type": "string",
    "enum": ["attached", "detached", "visible", "hidden"],
    "default": "attached",
    "description": "State to wait for the CSS selector.",
}

# Shared browser params (for fetch, stealthy_fetch, open_session)
_BROWSER_COMMON = {
    "headless": {"type": "boolean", "default": True, "description": "Run browser headless (hidden). Always True on server."},
    "google_search": {"type": "boolean", "default": True, "description": "Set a Google referer header."},
    "wait": {"type": "number", "default": 0, "description": "Wait time in ms after page load before returning."},
    "proxy": _PROXY_FLEXIBLE,
    "timezone_id": {"type": "string", "description": "Browser timezone, e.g. America/New_York."},
    "locale": {"type": "string", "description": "User locale, e.g. en-GB, de-DE."},
    "extra_headers": {"type": "object", "description": "Extra HTTP headers as key-value pairs."},
    "useragent": {"type": "string", "description": "Custom User-Agent string."},
    "cdp_url": {"type": "string", "description": "CDP URL to connect to an existing browser."},
    "timeout": {"type": "number", "default": 30000, "description": "Timeout in ms for all page operations."},
    "disable_resources": {"type": "boolean", "default": False, "description": "Block fonts, images, media, etc. for speed."},
    "wait_selector": {"type": "string", "description": "CSS selector to wait for before proceeding."},
    "cookies": {"type": "array", "description": "Cookies in Playwright SetCookieParam format."},
    "network_idle": {"type": "boolean", "default": False, "description": "Wait until no network connections for 500ms."},
    "wait_selector_state": _WAIT_SELECTOR_STATE,
}

_STEALTHY_EXTRA = {
    "hide_canvas": {"type": "boolean", "default": False, "description": "Add random noise to canvas to prevent fingerprinting."},
    "block_webrtc": {"type": "boolean", "default": False, "description": "Force WebRTC to respect proxy settings."},
    "allow_webgl": {"type": "boolean", "default": True, "description": "Keep WebGL enabled (recommended)."},
    "solve_cloudflare": {"type": "boolean", "default": False, "description": "Solve Cloudflare Turnstile/Interstitial challenges."},
    "additional_args": {"type": "object", "description": "Additional Playwright context arguments."},
}


MCP_TOOLS = [
    # --- HTTP tools (no browser) ---
    {
        "name": "get",
        "description": "Make a GET HTTP request and return structured content. Fast, no browser needed. Suitable for low-mid protection sites. For JS-heavy or high-protection sites, use fetch or stealthy_fetch.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to request."},
                "impersonate": {"type": "string", "default": "chrome", "description": "Browser fingerprint to impersonate."},
                "extraction_type": _EXTRACTION_TYPE,
                "css_selector": _CSS_SELECTOR,
                "main_content_only": _MAIN_CONTENT_ONLY,
                "params": {"type": "object", "description": "Query string parameters."},
                "headers": {"type": "object", "description": "Request headers."},
                "cookies": {"type": "object", "description": "Request cookies."},
                "timeout": {"type": "number", "default": 30, "description": "Timeout in seconds."},
                "follow_redirects": {"type": ["string", "boolean"], "default": "safe", "description": "Redirect policy: 'safe' (SSRF protection), true, or false."},
                "max_redirects": {"type": "integer", "default": 30, "description": "Max redirects. -1 for unlimited."},
                "retries": {"type": "integer", "default": 3, "description": "Retry attempts."},
                "retry_delay": {"type": "integer", "default": 1, "description": "Seconds between retries."},
                "proxy": _PROXY_STRING,
                "proxy_auth": {"type": "object", "properties": {"username": {"type": "string"}, "password": {"type": "string"}}, "description": "Proxy auth credentials."},
                "auth": {"type": "object", "properties": {"username": {"type": "string"}, "password": {"type": "string"}}, "description": "HTTP basic auth credentials."},
                "verify": {"type": "boolean", "default": True, "description": "Verify HTTPS certificates."},
                "http3": {"type": "boolean", "default": False, "description": "Use HTTP/3."},
                "stealthy_headers": {"type": "boolean", "default": True, "description": "Generate real browser headers."},
            },
            "required": ["url"],
        },
    },
    {
        "name": "bulk_get",
        "description": "Make parallel GET HTTP requests to multiple URLs. Same capabilities as get() but for batch operations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "urls": {"type": "array", "items": {"type": "string"}, "description": "List of URLs to request."},
                "impersonate": {"type": "string", "default": "chrome", "description": "Browser fingerprint to impersonate."},
                "extraction_type": _EXTRACTION_TYPE,
                "css_selector": _CSS_SELECTOR,
                "main_content_only": _MAIN_CONTENT_ONLY,
                "params": {"type": "object", "description": "Query string parameters."},
                "headers": {"type": "object", "description": "Request headers."},
                "cookies": {"type": "object", "description": "Request cookies."},
                "timeout": {"type": "number", "default": 30, "description": "Timeout in seconds."},
                "follow_redirects": {"type": ["string", "boolean"], "default": "safe"},
                "max_redirects": {"type": "integer", "default": 30},
                "retries": {"type": "integer", "default": 3},
                "retry_delay": {"type": "integer", "default": 1},
                "proxy": _PROXY_STRING,
                "proxy_auth": {"type": "object", "properties": {"username": {"type": "string"}, "password": {"type": "string"}}},
                "auth": {"type": "object", "properties": {"username": {"type": "string"}, "password": {"type": "string"}}},
                "verify": {"type": "boolean", "default": True},
                "http3": {"type": "boolean", "default": False},
                "stealthy_headers": {"type": "boolean", "default": True},
            },
            "required": ["urls"],
        },
    },
    # --- Dynamic browser tools (Playwright) ---
    {
        "name": "fetch",
        "description": "Fetch a URL using a Playwright browser. Renders JavaScript. Suitable for JS-heavy sites with low-mid protection. For high-protection sites, use stealthy_fetch. Optionally reuse an existing session via session_id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to fetch."},
                "extraction_type": _EXTRACTION_TYPE,
                "css_selector": _CSS_SELECTOR,
                "main_content_only": _MAIN_CONTENT_ONLY,
                **_BROWSER_COMMON,
                "session_id": {"type": "string", "description": "Reuse an existing browser session (from open_session)."},
            },
            "required": ["url"],
        },
    },
    {
        "name": "bulk_fetch",
        "description": "Fetch multiple URLs in parallel using a Playwright browser. Same as fetch() but for batch operations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "urls": {"type": "array", "items": {"type": "string"}, "description": "List of URLs to fetch."},
                "extraction_type": _EXTRACTION_TYPE,
                "css_selector": _CSS_SELECTOR,
                "main_content_only": _MAIN_CONTENT_ONLY,
                **_BROWSER_COMMON,
                "session_id": {"type": "string", "description": "Reuse an existing browser session."},
            },
            "required": ["urls"],
        },
    },
    # --- Stealthy browser tools (anti-bot) ---
    {
        "name": "stealthy_fetch",
        "description": "Fetch a URL with full anti-bot bypass: TLS fingerprint spoofing, canvas noise, WebRTC proxy enforcement, Cloudflare Turnstile solving. Use for high-protection sites. Optionally reuse a session via session_id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to fetch."},
                "extraction_type": _EXTRACTION_TYPE,
                "css_selector": _CSS_SELECTOR,
                "main_content_only": _MAIN_CONTENT_ONLY,
                **_BROWSER_COMMON,
                **_STEALTHY_EXTRA,
                "session_id": {"type": "string", "description": "Reuse an existing stealthy session."},
            },
            "required": ["url"],
        },
    },
    {
        "name": "bulk_stealthy_fetch",
        "description": "Fetch multiple URLs in parallel with full anti-bot bypass. Same as stealthy_fetch() for batch operations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "urls": {"type": "array", "items": {"type": "string"}, "description": "List of URLs to fetch."},
                "extraction_type": _EXTRACTION_TYPE,
                "css_selector": _CSS_SELECTOR,
                "main_content_only": _MAIN_CONTENT_ONLY,
                **_BROWSER_COMMON,
                **_STEALTHY_EXTRA,
                "session_id": {"type": "string", "description": "Reuse an existing stealthy session."},
            },
            "required": ["urls"],
        },
    },
    # --- Session management ---
    {
        "name": "open_session",
        "description": "Open a persistent browser session for reuse across multiple fetch/screenshot calls. Avoids browser startup overhead per request. Use close_session when done.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_type": {"type": "string", "enum": ["dynamic", "stealthy"], "description": "Session type: 'dynamic' (standard Playwright) or 'stealthy' (anti-bot)."},
                "session_id": {"type": "string", "description": "Optional custom session ID. Auto-generated if omitted."},
                **_BROWSER_COMMON,
                "max_pages": {"type": "integer", "default": 5, "description": "Max concurrent pages/tabs in this session."},
                **_STEALTHY_EXTRA,
            },
            "required": ["session_type"],
        },
    },
    {
        "name": "close_session",
        "description": "Close a browser session and free its resources.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "ID of the session to close."},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "list_sessions",
        "description": "List all active browser sessions with their IDs, types, creation times, and status.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    # --- Screenshot ---
    {
        "name": "screenshot",
        "description": "Capture a screenshot of a web page using an existing browser session. Returns the image as base64. Requires an open session (from open_session).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to navigate to and capture."},
                "session_id": {"type": "string", "description": "ID of an open browser session."},
                "image_type": {"type": "string", "enum": ["png", "jpeg"], "default": "png", "description": "Image format."},
                "full_page": {"type": "boolean", "default": False, "description": "Capture full scrollable page."},
                "quality": {"type": "integer", "minimum": 0, "maximum": 100, "description": "JPEG quality (0-100). Only for jpeg."},
                "wait": {"type": "number", "default": 0, "description": "Wait time in ms after page load."},
                "wait_selector": {"type": "string", "description": "CSS selector to wait for."},
                "wait_selector_state": _WAIT_SELECTOR_STATE,
                "network_idle": {"type": "boolean", "default": False},
                "timeout": {"type": "number", "default": 30000},
            },
            "required": ["url", "session_id"],
        },
    },
]
