import logging
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

from backend.api.state import (
    append_event, create_run, get_run, get_run_status, set_status,
)
from backend.services.trip_service import plan_trip_streaming

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/plan", tags=["plan"])


class PlanRequest(BaseModel):
    destination: str = Field(..., min_length=1)
    num_days: int = Field(..., ge=1, le=30)
    budget_usd: int = Field(..., ge=50, le=50000)
    preferences: str = Field("General sightseeing", max_length=500)
    user_email: str = Field("default@travel.app", max_length=200)


class PlanResponse(BaseModel):
    run_id: str
    status: str
    poll_url: str


def _persist_audit_log(trip_id: str, events: list[dict]) -> None:
    try:
        from backend.database.crud import AgentLogCRUD
        log_crud = AgentLogCRUD()
    except Exception:
        log.exception("Could not load AgentLogCRUD")
        return

    for ev in events:
        etype = ev.get("type", "")
        agent = ev.get("agent")
        if not agent and etype not in ("content", "completed", "warning", "error"):
            continue
        try:
            log_crud.log_event(
                trip_id=trip_id,
                agent_name=agent or "Orchestrator",
                event_type=etype,
                tool_name=ev.get("tool"),
                content=str(ev.get("content"))[:2000] if ev.get("content") else None,
                duration_ms=None,
            )
        except Exception:
            log.exception("audit log insert failed for one event")


async def _run_plan(run_id: str, req: PlanRequest) -> None:
    set_status(run_id, "running")
    try:
        async for event in plan_trip_streaming(
            destination=req.destination,
            num_days=req.num_days,
            preferences=req.preferences,
            budget=req.budget_usd,
        ):
            append_event(run_id, event)

        run = get_run(run_id) or {}
        content = run.get("content", "")
        events = run.get("events", [])
        trip_id = None

        if content:
            try:
                from backend.config import config
                if config.database_url:
                    from backend.database.crud import UserCRUD, TripCRUD
                    user = UserCRUD().get_or_create(req.user_email)
                    saved = TripCRUD().save_trip(
                        user_id=user["id"],
                        destination=req.destination,
                        duration_days=req.num_days,
                        budget_usd=req.budget_usd,
                        preferences=req.preferences,
                        itinerary_markdown=content,
                    )
                    trip_id = str(saved["id"])
                    _persist_audit_log(trip_id, events)
            except Exception as save_err:
                log.exception("Failed to save trip")
                append_event(run_id, {
                    "type": "warning",
                    "content": f"auto-save failed: {save_err}",
                })

        set_status(run_id, "completed", result={"content": content}, trip_id=trip_id)
    except Exception as e:
        log.exception("Plan run failed")
        set_status(run_id, "failed", error=str(e))


@router.post("", response_model=PlanResponse)
async def start_plan(req: PlanRequest, background: BackgroundTasks):
    run_id = str(uuid4())
    create_run(run_id, req.model_dump())
    background.add_task(_run_plan, run_id, req)
    return PlanResponse(
        run_id=run_id,
        status="queued",
        poll_url=f"/api/plan/{run_id}/status",
    )


@router.get("/{run_id}/status")
async def status(run_id: str, since: int = Query(0, ge=0)):
    snap = get_run_status(run_id, since=since)
    if snap is None:
        raise HTTPException(status_code=404, detail="run not found")
    return snap
