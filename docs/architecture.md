# System Architecture

## High-level diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│  FRONTEND  (Next.js 15 · Tailwind · shadcn/ui)                       │
│   • Trip Planner    • My Trips      • Trip Dashboard                 │
│   • Destination Explorer    • Audit Trail tab                        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTP (JSON, polling)
┌────────────────────────────────▼────────────────────────────────────┐
│  BACKEND  (FastAPI + Agno)                                          │
│   POST /api/plan          → kicks off team run, returns run_id      │
│   GET  /api/plan/{id}/status  (long-poll, returns events since N)   │
│   GET  /api/trips, /api/trips/{id}, /api/trips/{id}/logs            │
│   GET  /api/explore?q=...                                           │
│                                                                     │
│   Agno Multi-Agent Team (5 specialists + Orchestrator)              │
│     · Destination Researcher                                        │
│     · Accommodation Agent                                           │
│     · Route Optimizer                                               │
│     · Budget Optimizer                                              │
│     · Itinerary Compiler                                            │
└──────────┬───────────────────────────────────────┬──────────────────┘
           │ MCP protocol (stdio | SSE)            │
           │                                       │
           ▼                                       ▼
┌──────────────────────────┐    ┌──────────────────────────────────────┐
│  CUSTOM MCP SERVER       │    │  STORAGE                             │
│  (Python `mcp` SDK)      │    │  • Pinecone (vector RAG, 90 docs)    │
│                          │    │  • Supabase Postgres                 │
│  9 TOOLS                 │    │      ├ users                         │
│   data:                  │    │      ├ trips                         │
│   • get_weather          │    │      └ agent_logs (audit trail)      │
│   • geocode              │    └──────────────────────────────────────┘
│   • route                │
│   • find_attractions     │
│   • country_info         │
│   • convert_currency     │
│   • search_destinations  │
│   domain logic:          │
│   • optimize_day_route   │ ← TSP nearest-neighbour + 2-opt
│   • score_itinerary      │ ← deterministic 6-criterion rubric
│                          │
│  2 RESOURCES             │
│   • travel://currency/   │
│      rates               │
│   • travel://            │
│      destinations/{name} │
│                          │
│  2 PROMPTS               │
│   • itinerary-template   │
│   • destination-         │
│      comparison          │
│                          │
│  Middleware: LRU cache,  │
│  rate-limit throttle,    │
│  structured errors       │
└─────────────┬────────────┘
              │
              ▼
   Free public APIs (no key required, fair-use throttled):
   Open-Meteo · OSM Nominatim · OSRM · Overpass · REST Countries ·
   Frankfurter · Wikivoyage MediaWiki
```

## Why this architecture

| Concern | Choice | Reason |
|---|---|---|
| Custom MCP server | Authored, not consumed | Aligns with project title; demonstrates protocol-level engineering |
| All 3 MCP primitives | Tools + Resources + Prompts | Most public MCP servers only do tools — using all three is a real flex |
| Multi-agent team | 5 specialists + 1 orchestrator | Each agent has a clear role; mirrors real consulting workflows |
| Polling, not SSE for UI | GET /api/plan/{id}/status?since=N | Vercel free tier has 10s edge timeout; long agent runs would fail SSE |
| Deterministic scorer | Closed-form 6-criterion rubric | Defends against "circular LLM-as-judge" challenges in viva |
| Local + cloud transports | stdio for dev, SSE for prod | One env var (`MCP_SERVER_URL`) flips between them |
| Free APIs only | Open-Meteo, OSM, etc. | Eliminates billing/key-expiry failures on demo day |
| RAG over 90 curated docs | Pinecone serverless | Grounds LLM answers in vetted facts (anti-hallucination) |

## Repository layout

```
mcp_server/         — custom MCP server (Python `mcp` SDK)
  _app.py             FastMCP instance shared by all decorators
  server.py           CLI entry: --sse or stdio
  config.py
  tools/              9 tools, one file per concern
  resources/          2 resources (parameterised + static)
  prompts/            2 reusable prompt templates

backend/            — FastAPI + Agno multi-agent team
  api/                FastAPI routers (plan, trips, explore)
  agents/             5 specialist agents + Team factory
  services/           orchestration helpers (trip_service)
  rag/                Pinecone knowledge base + seed data
  database/           SQLAlchemy CRUD against Supabase Postgres
  utils/              parsers, validators
  config.py
  main.py             ASGI entry

frontend/           — Next.js 15 + Tailwind + shadcn/ui (Phase 6)

tests/              — pytest suite (28 tests, all deterministic)

docs/               — architecture, demo script, runbook,
                      sequence diagram

deploy/             — Railway (mcp_server + backend) + Vercel (frontend)
```
