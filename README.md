# MCP Based Intelligent Travel Planning System

> Final-year B.Tech CSE major project — a multi-agent AI travel planner built around a custom Model Context Protocol (MCP) server.

A multi-agent AI travel planning system where 5 specialised agents collaborate to generate detailed, personalised travel itineraries. The agents do not call APIs directly — they speak only **Model Context Protocol** to a custom MCP server we authored, which exposes travel tools, resources, and prompts backed by free public APIs.

## What's interesting about this project

1. **Custom MCP server, not just a consumer** — implemented in Python using the official `mcp` SDK. Uses all three protocol primitives (Tools + Resources + Prompts), not just tools.
2. **Composite tools, not 1:1 API wrappers** — e.g. `plan_day_in_city` internally calls weather + attractions + routing + currency in one tool.
3. **Domain-reasoning tools** — TSP-based route ordering, deterministic 6-criterion itinerary scoring rubric.
4. **Multi-agent team as MCP client** — 5 Agno specialists + orchestrator share one MCP server.
5. **Dual transport** — same server runs `stdio` for local dev and `SSE` for cloud, switched by config.
6. **Production middleware** — LRU cache, rate-limit throttle, structured errors.
7. **Agent reasoning audit trail** — every tool call across all agents logged to Supabase, viewable in the UI.

## Architecture

```
Frontend (Next.js + Tailwind + shadcn/ui)
      ↓ HTTP
Backend (FastAPI + Agno multi-agent team)
      ↓ MCP protocol
MCP Server (custom — tools / resources / prompts)
      ↓ free travel APIs
Open-Meteo · OSM Nominatim · OSRM · Overpass · REST Countries · Frankfurter · Wikivoyage
```

Persistence: **Pinecone** (RAG knowledge base — 47 curated travel docs) + **Supabase Postgres** (saved trips + agent reasoning logs).

## Repo layout

```
.
├── mcp_server/        # Custom MCP server (Python `mcp` SDK + FastMCP)
├── backend/           # FastAPI + Agno multi-agent team
├── frontend/          # Next.js 15 + Tailwind + shadcn/ui
├── tests/             # pytest suite
├── docs/              # architecture, demo script, runbook
└── deploy/            # Railway + Vercel configs
```

## Quickstart

See [`docs/runbook.md`](docs/runbook.md) for full setup.

## Status

This project is being rebuilt in phases. See the build phases in the project root or the upstream task list. Currently the codebase is mid-rebuild — not all phases complete.
