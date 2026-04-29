# Architecture

> Full architecture documentation will be written in Phase 8.
> For now, see the high-level diagram in `architecture_diagram.png` (regenerated in Phase 8).

## High-level layers

1. **Frontend** — Next.js 15 + Tailwind + shadcn/ui (`frontend/`)
2. **Backend** — FastAPI exposing the multi-agent team (`backend/`)
3. **MCP Server** — Custom Python MCP server with travel tools, resources, prompts (`mcp_server/`)
4. **Knowledge** — Pinecone (vector RAG) + Supabase Postgres (trips, audit logs)

The backend acts as both an HTTP API for the frontend AND an MCP client to the custom MCP server.
