# MCP Based Intelligent Travel Planning System

A travel planner where five AI agents work together to build a day-by-day trip plan.
The agents talk to a custom Model Context Protocol (MCP) server I wrote in Python.
That server exposes weather, geocoding, routing, places, country data, currency,
and Wikivoyage destination guides as MCP tools, plus a couple of resources and
prompt templates.

This is my final-year B.Tech CSE major project.

## What it does

You enter a destination, days, budget and preferences. The five agents then
coordinate through the MCP server to research the place, find accommodation,
order the daily route, run a budget check and compile a full itinerary with
self-scoring before showing it to you. The plan, plus the full reasoning trail
of every tool each agent called, is saved to Supabase so you can come back to it.

## Stack

- Python `mcp` SDK + FastMCP for the server
- FastAPI + the Agno framework for the multi-agent backend
- Next.js 15 + Tailwind for the frontend
- Pinecone as the vector store (uses Pinecone's own free hosted embedding model,
  so no OpenAI credits are spent on embeddings)
- Supabase Postgres for trips and agent activity logs
- OpenAI gpt-4o-mini as the only LLM

## Free APIs the MCP server uses

Open-Meteo, OpenStreetMap Nominatim, OSRM, Overpass, REST Countries,
Frankfurter, Wikivoyage. None of these need an API key.

## Repo layout

```
mcp_server/        custom MCP server
backend/           FastAPI app + Agno agents
frontend/          Next.js app
tests/             pytest for the deterministic tools (TSP + scorer)
deploy/            Railway and Vercel config
```

## Local setup

```bash
pip install -r mcp_server/requirements.txt
pip install -r backend/requirements.txt

cp .env.example .env
# fill in OPENAI_API_KEY, PINECONE_API_KEY, SUPABASE_DATABASE_URL

python -m backend.rag.seed_data --reset   # one time, loads 90 docs into Pinecone
```

Then in three terminals:

```bash
python -m mcp_server.server --sse                   # MCP server on :8000
uvicorn backend.main:app --reload --port 8001       # API on :8001
cd frontend && npm install && npm run dev           # UI on :3000
```

Open http://localhost:3000.

## Tests

```bash
pytest tests/test_mcp_tools.py
```

## License

Personal academic project.
