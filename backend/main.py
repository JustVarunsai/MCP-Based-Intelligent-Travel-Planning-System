"""
FastAPI backend for the AI Travel Planner.

Run:
    uvicorn backend.main:app --reload --port 8001

Endpoints (filled out in Phase 5):
    POST /api/plan                   — kick off trip generation, returns run_id
    GET  /api/plan/{run_id}/status   — polling endpoint for live progress
    GET  /api/trips                  — list saved trips
    POST /api/trips                  — save a trip
    GET  /api/trips/{trip_id}        — fetch single trip
    DELETE /api/trips/{trip_id}      — delete trip
    GET  /api/trips/{trip_id}/logs   — agent reasoning audit trail
    GET  /api/explore                — semantic search over RAG knowledge
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Travel Planner", version="0.1.0")

# permissive CORS during dev; tighten before deploy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"ok": True, "service": "travel-backend"}
