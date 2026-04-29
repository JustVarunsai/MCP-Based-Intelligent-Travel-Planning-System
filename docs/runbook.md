# Runbook (placeholder — finalised in Phase 11)

## Local dev

```bash
# 1. install per-package deps
pip install -r mcp_server/requirements.txt
pip install -r backend/requirements.txt

# 2. set up .env (see .env.example)
cp .env.example .env

# 3. seed Pinecone (one time)
python -m backend.rag.seed_data

# 4. start MCP server (terminal 1, SSE mode)
python -m mcp_server.server --sse

# 5. start FastAPI backend (terminal 2)
uvicorn backend.main:app --reload --port 8001

# 6. start frontend (terminal 3)
cd frontend && npm run dev
```

## Inspect the MCP server

```bash
npx -y @modelcontextprotocol/inspector python -m mcp_server.server
```

## Cloud deploy (filled in Phase 11)

- Frontend → Vercel
- MCP server + backend → Railway
