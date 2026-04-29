from __future__ import annotations
import threading
from datetime import datetime, timezone
from typing import Any

_lock = threading.Lock()
_runs: dict[str, dict[str, Any]] = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_run(run_id: str, request: dict[str, Any]) -> None:
    with _lock:
        _runs[run_id] = {
            "run_id": run_id,
            "status": "queued",
            "request": request,
            "events": [],
            "content": "",
            "agent_states": {},
            "result": None,
            "trip_id": None,
            "error": None,
            "started_at": now_iso(),
            "ended_at": None,
        }


def append_event(run_id: str, event: dict[str, Any]) -> None:
    with _lock:
        run = _runs.get(run_id)
        if not run:
            return
        event = {**event, "i": len(run["events"]), "ts": now_iso()}
        run["events"].append(event)

        agent = event.get("agent")
        etype = event.get("type")
        if agent:
            state = run["agent_states"].setdefault(agent, {"status": "idle", "tools": []})
            if etype == "agent_started":
                state["status"] = "working"
            elif etype == "agent_completed":
                state["status"] = "done"
            elif etype == "agent_tool_start":
                state["status"] = "working"
                tool = event.get("tool")
                if tool and tool not in state["tools"]:
                    state["tools"].append(tool)

        if etype in ("content", "completed"):
            chunk = event.get("content") or ""
            if chunk:
                run["content"] += chunk


def set_status(
    run_id: str,
    status: str,
    *,
    error: str | None = None,
    result: Any | None = None,
    trip_id: str | None = None,
) -> None:
    with _lock:
        run = _runs.get(run_id)
        if not run:
            return
        run["status"] = status
        if error is not None:
            run["error"] = error
        if result is not None:
            run["result"] = result
        if trip_id is not None:
            run["trip_id"] = trip_id
        if status in ("completed", "failed"):
            run["ended_at"] = now_iso()
            for state in run["agent_states"].values():
                if state.get("status") == "working":
                    state["status"] = "done"


def get_run(run_id: str) -> dict[str, Any] | None:
    with _lock:
        run = _runs.get(run_id)
        return dict(run) if run else None


def get_run_status(run_id: str, *, since: int = 0) -> dict[str, Any] | None:
    with _lock:
        run = _runs.get(run_id)
        if not run:
            return None
        events = run["events"][since:]
        return {
            "run_id": run["run_id"],
            "status": run["status"],
            "agent_states": dict(run["agent_states"]),
            "events": events,
            "next_since": len(run["events"]),
            "content": run["content"] if run["status"] == "completed" else None,
            "trip_id": run["trip_id"],
            "error": run["error"],
        }
