"""
FastAPI backend for the AI Travel Planner.

Run:
    uvicorn backend.main:app --reload --port 8001

Endpoints:
    POST /api/plan                       — kick off trip generation, returns run_id
    GET  /api/plan/{run_id}/status       — poll for live progress
    GET  /api/trips                      — list saved trips
    GET  /api/trips/{id}                 — fetch single trip
    DELETE /api/trips/{id}               — delete trip
    GET  /api/trips/{id}/logs            — agent reasoning audit trail
    GET  /api/explore?q=...              — semantic search over RAG
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import plan, trips, explore

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = FastAPI(
    title="AI Travel Planner",
    description="Multi-agent travel planning system with custom MCP server",
    version="0.2.0",
)

import os as _os
_allowed_origins = [o.strip() for o in _os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(plan.router)
app.include_router(trips.router)
app.include_router(explore.router)


@app.get("/health")
async def health():
    from backend.config import config
    return {
        "ok": True,
        "service": "travel-backend",
        "version": "0.2.0",
        "mcp_transport": "sse" if config.use_sse else "stdio",
        "mcp_url": config.MCP_SERVER_URL or None,
        "pinecone_configured": bool(config.pinecone_api_key),
        "supabase_configured": bool(config.database_url),
    }
