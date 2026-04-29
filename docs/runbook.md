# Runbook

## Prerequisites

- Python 3.10+
- Node.js 18+ (for the Next.js frontend and `mcp inspector`)
- A `.env` file at the project root — see `.env.example`

## First-time setup

```bash
# 1. clone + cd
git clone <repo>
cd ai_travel_planner_mcp_agent_team

# 2. install per-package deps
pip install -r mcp_server/requirements.txt
pip install -r backend/requirements.txt

# 3. copy env template, fill in keys
cp .env.example .env
# edit .env → OPENAI_API_KEY, PINECONE_API_KEY, SUPABASE_DATABASE_URL

# 4. seed Pinecone (one time, ~30 seconds)
python -m backend.rag.seed_data --reset
```

## Local dev — run all three

Open three terminals:

**Terminal 1 — MCP server (SSE mode, port 8000)**
```bash
python -m mcp_server.server --sse
```

**Terminal 2 — FastAPI backend (port 8001)**
```bash
uvicorn backend.main:app --reload --port 8001
```

**Terminal 3 — Frontend (port 3000)**
```bash
cd frontend
npm install         # first time only
npm run dev
```

Open **http://localhost:3000**.

## Run the MCP server in stdio mode (for `mcp inspector`)

Drop the `--sse` flag. The Inspector launches it as a subprocess:

```bash
npx @modelcontextprotocol/inspector python -m mcp_server.server
```

In the Inspector UI, click **Connect**, then explore Tools / Resources / Prompts.

## Run tests

```bash
# all tests
pytest tests/ -v

# only the deterministic tool tests (no network)
pytest tests/test_mcp_tools.py -v
```

## Switching between local and cloud

In `.env`, set `MCP_SERVER_URL`:

| Use case | Value |
|---|---|
| Local stdio (default) | leave empty or unset |
| Local SSE | `http://localhost:8000/sse` |
| Railway-deployed | `https://travel-mcp-XXXX.railway.app/sse` |

The backend auto-detects: empty → stdio subprocess, set → SSE.

## Cloud deploy

The deployment is split into **3 services**: MCP server (Railway), FastAPI backend (Railway), Next.js frontend (Vercel).

### 1. MCP server → Railway

```bash
npm i -g @railway/cli
railway login
railway init                                          # creates the project
railway service create travel-mcp-server
railway up --service travel-mcp-server \
  -c deploy/railway.mcp_server.toml
```

Set `MCP_AUTH_TOKEN` (any random string) in the Railway service environment.

After deploy, Railway gives you a URL like `https://travel-mcp-server-prod.up.railway.app`. Note it.

### 2. Backend → Railway (same project, second service)

```bash
railway service create travel-backend
railway up --service travel-backend \
  -c deploy/railway.backend.toml
```

Set these env vars on the Railway backend service:
| Var | Value |
|---|---|
| `OPENAI_API_KEY` | from OpenAI |
| `PINECONE_API_KEY` | from Pinecone |
| `SUPABASE_DATABASE_URL` | postgres connection string |
| `MCP_SERVER_URL` | `https://travel-mcp-server-prod.up.railway.app/sse` |
| `MCP_AUTH_TOKEN` | same value used in MCP service |
| `CORS_ALLOWED_ORIGINS` | `https://<your>.vercel.app` |

Note the backend URL too.

### 3. Frontend → Vercel

```bash
cd frontend
npx vercel               # first time, follow prompts
```

Set the Vercel project env var:
| Var | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://travel-backend-prod.up.railway.app` |

Redeploy: `npx vercel --prod`.

### 4. Verify cloud setup

```bash
curl https://<backend>.railway.app/health
# expect mcp_transport: "sse" and mcp_url showing your MCP service URL
curl "https://<backend>.railway.app/api/explore?q=beaches+in+India"
# expect 4 Indian beach destinations as the top hits
```

The frontend at the Vercel URL should now be talking to Railway end-to-end.

## One-line config switch

The same code runs locally or in cloud, swapped by **a single env var**:

```bash
# local
unset MCP_SERVER_URL                                  # backend spawns stdio subprocess

# cloud
export MCP_SERVER_URL=https://travel-mcp-server-prod.up.railway.app/sse
```

That's the demo for "transport-agnostic protocol" — point at the env in the cloud dashboard, change it, redeploy. Same code.

## Common issues

| Symptom | Fix |
|---|---|
| `pinecone.UnauthorizedException: 401` | `PINECONE_API_KEY` missing/wrong in `.env` |
| Agents hang and time out | `MCP_SERVER_URL` set but server not running |
| `Set your API keys` toast in UI | `.env` not loaded — restart backend |
| Vercel function timeout (10s) | Long agent runs require polling — confirm frontend isn't using SSE |
| "Database is locked" SQLite-style | Not applicable — we use Postgres; check `SUPABASE_DATABASE_URL` |
| Nominatim 429 rate-limit | Already throttled; if it persists, the public endpoint is overloaded — add Mapbox key (optional) |
