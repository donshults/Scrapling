# Integrating Scrapling MCP with OpenClaw

This guide explains how to make the Scrapling MCP server available to OpenClaw.

## Quick Reference

- **Endpoint:** `https://crawl.callteksupport.net/mcp`
- **API Key:** Stored in Doppler `d2tek-agent` project as `SCRAPLING_API_KEY`
- **Tools:** 10 web scraping tools (get, bulk_get, fetch, bulk_fetch, stealthy_fetch, bulk_stealthy_fetch, open_session, close_session, list_sessions, screenshot)

## Integration Options

### Option 1: Direct MCP Integration (Native Tools)

Add Scrapling as an MCP server to OpenClaw's `.mcp.json`:

```json
{
  "mcpServers": {
    "scrapling": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch",
        "https://crawl.callteksupport.net/mcp"
      ],
      "env": {
        "SCRAPLING_API_KEY": "{{SCRAPLING_API_KEY}}"
      }
    }
  }
}
```

**How it works:**
- Uses the official MCP fetch server to bridge HTTP MCP to stdio MCP
- All 10 scraping tools appear as native OpenClaw capabilities
- Bearer token authentication handled automatically via env var

**Pros:**
- Tools available immediately in every session
- No skill invocation needed
- Full MCP protocol support

**Cons:**
- Adds 10 tool definitions to context window (~2-3KB)
- May impact token usage if not actively scraping

**Best for:** Deployments that frequently scrape websites

### Option 2: MCP Client Skill (Progressive Disclosure)

Use OpenClaw's built-in `mcp-client` skill to connect on-demand:

```
Connect to the Scrapling MCP server at https://crawl.callteksupport.net/mcp with bearer token [API_KEY]
```

The mcp-client skill will:
1. Establish connection to the remote MCP server
2. List available tools when needed
3. Execute tool calls without loading schemas into context

**Pros:**
- Zero context overhead until actively used
- Dynamic tool loading
- Supports any MCP server

**Cons:**
- Requires explicit skill invocation
- Connection state per session

**Best for:** Occasional scraping tasks

### Option 3: Direct HTTP Calls (No MCP)

Call the Scrapling API directly via `curl` or HTTP requests:

```bash
curl -X POST https://crawl.callteksupport.net/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{API_KEY}}" \
  -d '{
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
  }'
```

**Pros:**
- Complete control over requests
- No MCP dependency
- Works in any environment

**Cons:**
- Manual JSON-RPC formatting
- No tool discovery
- More verbose

**Best for:** Custom integrations or scripted workflows

## Recommended Setup

For most OpenClaw deployments, we recommend **Option 2 (MCP Client Skill)**:

1. The skill is already installed in OpenClaw
2. Zero context overhead when not in use
3. On-demand connection when scraping is needed
4. Consistent with OpenClaw's progressive disclosure philosophy

### Quick Start with MCP Client

In any OpenClaw session:

```
Connect to scrapling at https://crawl.callteksupport.net/mcp
```

Then use the tools:

```
List available scrapling tools
```

```
Use scrapling to scrape https://news.ycombinator.com and extract as markdown
```

## Environment Variables

If using Option 1 (direct MCP integration), store the API key securely:

```bash
# In OpenClaw's .env or Docker env file
SCRAPLING_API_KEY=yHNTJbvhAVhEU1I75IIfUb0RpKWB1vJDoOrCYtOzujw
```

Or pull from Doppler:

```bash
doppler secrets get SCRAPLING_API_KEY --project d2tek-agent --config prd --plain
```

## Tool Reference

Quick overview of available tools:

| Tool | Use Case | Browser? |
|------|----------|----------|
| `get` | Fast HTTP GET | No |
| `bulk_get` | Multiple URLs via HTTP | No |
| `fetch` | JavaScript-heavy sites | Yes (Playwright) |
| `bulk_fetch` | Multiple URLs with rendering | Yes |
| `stealthy_fetch` | Anti-bot protected sites | Yes (stealth mode) |
| `bulk_stealthy_fetch` | Multiple protected URLs | Yes |
| `open_session` | Start persistent browser | Yes |
| `close_session` | End browser session | - |
| `list_sessions` | Show active sessions | - |
| `screenshot` | Capture page as PNG | Yes |

**When to use what:**
- **Simple blog/news sites:** `get` (fastest)
- **SPAs / React apps:** `fetch` (waits for JS)
- **Cloudflare / bot detection:** `stealthy_fetch` (max stealth)
- **Multi-step flows (login, etc.):** `open_session` → actions → `close_session`

## Example Workflows

### Scrape a News Site

```
Use scrapling to get https://techcrunch.com in markdown format
```

### Handle Protected Site

```
Use scrapling stealthy_fetch to scrape https://protected-site.com
```

### Multi-Page Flow

```
1. Open a stealthy scrapling session named "login-flow"
2. Navigate to login page and extract form fields
3. Submit credentials
4. Scrape authenticated dashboard
5. Close the "login-flow" session
```

### Batch Scraping

```
Use scrapling bulk_get to scrape these URLs in parallel:
- https://example.com/page1
- https://example.com/page2
- https://example.com/page3
```

## Monitoring & Limits

- **Max concurrent sessions:** 10
- **Idle timeout:** 30 minutes (auto-cleanup)
- **Health check:** `GET https://crawl.callteksupport.net/health/live`

## Troubleshooting

### 401 Unauthorized
Check API key in Authorization header: `Bearer {{SCRAPLING_API_KEY}}`

### 404 Not Found
Service may be down. Verify: `curl https://crawl.callteksupport.net/health/live`

### Timeout on Browser Tools
Browser-based fetchers (fetch, stealthy_fetch) are slower than `get`. Increase client timeout or use `get` if the site doesn't require JavaScript.

### Session Limit Reached
Maximum 10 concurrent browser sessions. List and close unused sessions:
```
List scrapling sessions
Close scrapling session "old-session-id"
```

## Additional Resources

- **Full Usage Guide:** [SCRAPLING_MCP_USAGE.md](SCRAPLING_MCP_USAGE.md)
- **GitHub Repo:** https://github.com/donshults/Scrapling
- **Upstream Scrapling:** https://github.com/D4Vinci/Scrapling
- **Deployment:** Railway (auto-deploy on push to `main`)
- **Secrets:** Doppler project `d2tek-agent`

## Maintenance

The Scrapling MCP server auto-deploys on pushes to `main`. To check deployment status:

```bash
# Via Railway API
RAILWAY_TOKEN="ec81585d-e90f-4beb-b048-82e467fd6cc5"
SERVICE_ID="0d2541dc-ed80-4037-a0ce-483e5ee55874"

curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -d '{"query":"{ service(id: \"'$SERVICE_ID'\") { deployments(first: 1) { edges { node { status } } } } }"}'
```

Or check health directly:
```bash
curl https://crawl.callteksupport.net/health
```
