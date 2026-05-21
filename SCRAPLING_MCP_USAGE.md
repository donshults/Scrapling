# Scrapling MCP Server - Usage Guide

## Overview

The Scrapling MCP Server provides web scraping capabilities via a JSON-RPC 2.0 API hosted on Railway. It wraps the [Scrapling](https://github.com/D4Vinci/Scrapling) Python library and exposes 10 MCP tools for scraping websites with varying levels of protection.

**Production Endpoint:** `https://crawl.callteksupport.net/mcp`
**Railway Endpoint:** `https://scrapling-mcp-production.up.railway.app/mcp`

## Authentication

All MCP requests require Bearer token authentication:

```bash
Authorization: Bearer yHNTJbvhAVhEU1I75IIfUb0RpKWB1vJDoOrCYtOzujw
```

The API key is stored in:
- Doppler: `d2tek-agent` project (both `dev` and `prd` configs)
- Railway: Environment variable `SCRAPLING_API_KEY`

## Available Tools

### 1. `get` - Simple HTTP GET
Fast scraping without a browser. Best for low-to-medium protection sites.

**Parameters:**
- `url` (required): Target URL
- `impersonate` (optional, default: `"chrome"`): Browser fingerprint
- `extraction_type` (optional, default: `"markdown"`): Output format (`"markdown"`, `"html"`, `"text"`)
- `css_selector` (optional): Extract specific elements
- `main_content_only` (optional, default: `false`): Extract only main content

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "get",
    "arguments": {
      "url": "https://example.com",
      "extraction_type": "markdown"
    }
  }
}
```

### 2. `bulk_get` - Batch HTTP GET
Scrape multiple URLs in parallel using HTTP requests.

**Parameters:**
- `urls` (required): Array of URLs
- `impersonate` (optional): Browser fingerprint
- `extraction_type` (optional): Output format
- `css_selector` (optional): CSS selector for content extraction
- `main_content_only` (optional): Extract main content only

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 2,
  "params": {
    "name": "bulk_get",
    "arguments": {
      "urls": ["https://example.com/page1", "https://example.com/page2"],
      "extraction_type": "text"
    }
  }
}
```

### 3. `fetch` - Browser-based Scraping
Uses Playwright/Chromium for JavaScript-heavy sites. Good for medium-to-high protection.

**Parameters:**
- `url` (required): Target URL
- `extraction_type` (optional): Output format
- `css_selector` (optional): Content selector
- `main_content_only` (optional): Main content only
- `wait_selector` (optional): Wait for element before extracting
- `js_code` (optional): Execute custom JavaScript

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 3,
  "params": {
    "name": "fetch",
    "arguments": {
      "url": "https://spa-site.com",
      "wait_selector": ".dynamic-content",
      "extraction_type": "markdown"
    }
  }
}
```

### 4. `bulk_fetch` - Batch Browser Scraping
Scrape multiple URLs with full browser rendering.

**Parameters:**
- `urls` (required): Array of URLs
- `extraction_type` (optional): Output format
- `css_selector` (optional): Content selector
- `main_content_only` (optional): Main content only
- `wait_selector` (optional): Wait for element
- `js_code` (optional): Custom JavaScript

### 5. `stealthy_fetch` - Anti-Detection Scraping
Maximum stealth mode for heavily protected sites. Uses advanced anti-bot evasion.

**Parameters:**
- `url` (required): Target URL
- `extraction_type` (optional): Output format
- `css_selector` (optional): Content selector
- `main_content_only` (optional): Main content only
- `wait_selector` (optional): Wait for element
- `js_code` (optional): Custom JavaScript

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 4,
  "params": {
    "name": "stealthy_fetch",
    "arguments": {
      "url": "https://cloudflare-protected.com",
      "extraction_type": "html"
    }
  }
}
```

### 6. `bulk_stealthy_fetch` - Batch Anti-Detection
Scrape multiple URLs with full stealth capabilities.

**Parameters:**
- `urls` (required): Array of URLs
- `extraction_type` (optional): Output format
- `css_selector` (optional): Content selector
- `main_content_only` (optional): Main content only
- `wait_selector` (optional): Wait for element
- `js_code` (optional): Custom JavaScript

### 7. `open_session` - Create Persistent Browser
Opens a named browser session for sequential operations (login flows, multi-page scraping).

**Parameters:**
- `session_id` (required): Unique session identifier
- `session_type` (required): `"fetch"` or `"stealthy_fetch"`

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 5,
  "params": {
    "name": "open_session",
    "arguments": {
      "session_id": "my-login-session",
      "session_type": "stealthy_fetch"
    }
  }
}
```

### 8. `close_session` - Terminate Browser Session
Closes and cleans up a named session.

**Parameters:**
- `session_id` (required): Session identifier to close

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 6,
  "params": {
    "name": "close_session",
    "arguments": {
      "session_id": "my-login-session"
    }
  }
}
```

### 9. `list_sessions` - Show Active Sessions
Returns all currently active browser sessions with their types and last-used timestamps.

**Parameters:** None

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 7
}
```

### 10. `screenshot` - Capture Page Screenshot
Takes a full-page screenshot and returns base64-encoded PNG.

**Parameters:**
- `url` (required): Target URL
- `full_page` (optional, default: `true`): Capture full scrollable page
- `wait_selector` (optional): Wait for element before capturing

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 8,
  "params": {
    "name": "screenshot",
    "arguments": {
      "url": "https://example.com",
      "full_page": true
    }
  }
}
```

## Session Management

The server automatically manages browser sessions with:
- **Max concurrent sessions:** 10 (configurable via `MAX_CONCURRENT_SESSIONS`)
- **Idle timeout:** 1800 seconds / 30 minutes (configurable via `SESSION_IDLE_TIMEOUT_SECONDS`)
- **Auto-cleanup:** Runs every 60 seconds (configurable via `SESSION_CLEANUP_INTERVAL_SECONDS`)

Sessions are automatically cleaned up when idle to prevent resource exhaustion.

## Health Endpoints

### Liveness Probe
```bash
GET https://crawl.callteksupport.net/health/live
```
Returns 200 if the service is running.

### Readiness Probe
```bash
GET https://crawl.callteksupport.net/health/ready
```
Verifies Playwright/Chromium is available.

### Full Health Status
```bash
GET https://crawl.callteksupport.net/health
```
Returns uptime, active sessions, and tool count.

## Response Format

All MCP responses follow JSON-RPC 2.0:

**Success:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Status: 200 | URL: https://example.com\n\n[scraped content]"
      }
    ]
  }
}
```

**Screenshot Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "image",
        "data": "iVBORw0KGgoAAAANSUhEUgAA...",
        "mimeType": "image/png"
      }
    ]
  }
}
```

**Error:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error: [error details]"
  }
}
```

## Usage Examples

### cURL

```bash
# List available tools
curl -X POST https://crawl.callteksupport.net/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer yHNTJbvhAVhEU1I75IIfUb0RpKWB1vJDoOrCYtOzujw" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Scrape a page
curl -X POST https://crawl.callteksupport.net/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer yHNTJbvhAVhEU1I75IIfUb0RpKWB1vJDoOrCYtOzujw" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
      "name": "get",
      "arguments": {
        "url": "https://news.ycombinator.com",
        "extraction_type": "markdown"
      }
    }
  }'
```

### Python

```python
import requests

MCP_URL = "https://crawl.callteksupport.net/mcp"
API_KEY = "yHNTJbvhAVhEU1I75IIfUb0RpKWB1vJDoOrCYtOzujw"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Scrape a page
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "get",
        "arguments": {
            "url": "https://example.com",
            "extraction_type": "markdown"
        }
    }
}

response = requests.post(MCP_URL, json=payload, headers=headers)
result = response.json()

if "result" in result:
    content = result["result"]["content"][0]["text"]
    print(content)
else:
    print(f"Error: {result['error']['message']}")
```

### JavaScript/Node.js

```javascript
const MCP_URL = "https://crawl.callteksupport.net/mcp";
const API_KEY = "yHNTJbvhAVhEU1I75IIfUb0RpKWB1vJDoOrCYtOzujw";

async function scrapePage(url) {
  const response = await fetch(MCP_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "tools/call",
      id: 1,
      params: {
        name: "get",
        arguments: {
          url: url,
          extraction_type: "markdown"
        }
      }
    })
  });

  const data = await response.json();

  if (data.result) {
    return data.result.content[0].text;
  } else {
    throw new Error(data.error.message);
  }
}

scrapePage("https://example.com")
  .then(content => console.log(content))
  .catch(err => console.error(err));
```

## Use Case Patterns

### Simple Page Scraping
Use `get` for static sites or sites with minimal JavaScript:
```json
{"name": "get", "arguments": {"url": "https://blog.example.com", "extraction_type": "markdown"}}
```

### JavaScript-Heavy Sites
Use `fetch` for SPAs or dynamically loaded content:
```json
{"name": "fetch", "arguments": {"url": "https://app.example.com", "wait_selector": ".content-loaded"}}
```

### Protected Sites
Use `stealthy_fetch` for sites with Cloudflare, bot detection, or anti-scraping:
```json
{"name": "stealthy_fetch", "arguments": {"url": "https://protected.example.com"}}
```

### Login Flows
Use sessions for multi-step operations:
```json
// 1. Open session
{"name": "open_session", "arguments": {"session_id": "login-flow", "session_type": "stealthy_fetch"}}

// 2. Navigate and interact (via fetch with session_id)
// 3. Scrape authenticated pages
// 4. Close session
{"name": "close_session", "arguments": {"session_id": "login-flow"}}
```

### Batch Processing
Use bulk methods for multiple URLs:
```json
{"name": "bulk_get", "arguments": {"urls": ["https://example.com/1", "https://example.com/2"]}}
```

## Configuration

Environment variables (set in Railway):
- `SCRAPLING_API_KEY` - Bearer token for authentication
- `PORT` - Server port (auto-assigned by Railway)
- `LOG_LEVEL` - Logging verbosity (`INFO`, `DEBUG`, `WARNING`, `ERROR`)
- `MAX_CONCURRENT_SESSIONS` - Maximum browser sessions (default: 10)
- `SESSION_IDLE_TIMEOUT_SECONDS` - Session timeout (default: 1800)
- `SESSION_CLEANUP_INTERVAL_SECONDS` - Cleanup frequency (default: 60)
- `ALLOWED_ORIGINS` - CORS origins (default: `*`)

## Deployment Info

- **Platform:** Railway (US West region)
- **Project ID:** `b1a056a9-aff8-4ae8-b129-4464f701d446`
- **Service ID:** `0d2541dc-ed80-4037-a0ce-483e5ee55874`
- **Custom Domain:** `crawl.callteksupport.net` (via Cloudflare CNAME)
- **Railway Domain:** `scrapling-mcp-production.up.railway.app`
- **Auto-deploy:** Enabled on pushes to `main` branch
- **GitHub:** `donshults/Scrapling`

## Maintenance

### Secrets Management
All secrets stored in Doppler project `d2tek-agent`:
- `SCRAPLING_API_KEY` - API authentication token
- `SCRAPLING_MCP_URL` - Full MCP endpoint URL
- `RAILWAY_PROJECT_ID` - Railway project identifier
- `RAILWAY_SERVICE_ID` - Railway service identifier

### Upstream Sync
The `server/` directory is our custom code on top of upstream Scrapling. To pull upstream updates:

```bash
cd /home/callteksupport/projects/Scrapling
git fetch upstream
git merge upstream/main
# Conflicts unlikely since we only added files, didn't modify upstream code
```

### Manual Deployment
Push to `main` triggers auto-deploy. For manual redeploy without code changes:

```bash
cd /home/callteksupport/projects/Scrapling
git commit --allow-empty -m "chore: manual redeploy"
git push
```

### Monitoring
Check deployment status and logs via Railway API:

```bash
RAILWAY_TOKEN="ec81585d-e90f-4beb-b048-82e467fd6cc5"
SERVICE_ID="0d2541dc-ed80-4037-a0ce-483e5ee55874"

# Get latest deployment status
curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -d '{"query":"{ service(id: \"'$SERVICE_ID'\") { deployments(first: 1) { edges { node { id status createdAt } } } } }"}'
```

## Troubleshooting

### 401 Unauthorized
Check that the `Authorization` header includes `Bearer` prefix and correct API key.

### 404 Not Found
The service may be down. Check health endpoint: `GET https://crawl.callteksupport.net/health/live`

### Timeout on `fetch`/`stealthy_fetch`
Browser-based fetchers are slower than `get`. Increase client timeout or use `get` if the site doesn't require JavaScript rendering.

### Session Limit Reached
Maximum 10 concurrent sessions. List active sessions and close unused ones:
```json
{"method": "tools/call", "params": {"name": "list_sessions"}}
{"method": "tools/call", "params": {"name": "close_session", "arguments": {"session_id": "unused-session"}}}
```

### Rate Limiting
If scraping at high volume, the target site may rate-limit. Use `bulk_*` methods sparingly and add delays between requests if needed.

## Support

- **Upstream Scrapling Docs:** https://github.com/D4Vinci/Scrapling
- **Railway Docs:** https://docs.railway.app
- **MCP Spec:** https://spec.modelcontextprotocol.io

## License

This server wrapper is custom code. The underlying Scrapling library follows its own license (check upstream repo).
