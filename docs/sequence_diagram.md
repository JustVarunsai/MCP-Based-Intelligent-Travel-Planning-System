# Sequence Diagram — Trip Planning Flow

> Single-most-useful viva artifact: shows exactly how a user request flows through every layer.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant FE as Frontend<br/>(Next.js)
    participant BE as Backend<br/>(FastAPI)
    participant TM as Agno Team<br/>(Orchestrator)
    participant A1 as Destination<br/>Researcher
    participant A2 as Accommodation<br/>Agent
    participant A3 as Route<br/>Optimizer
    participant A4 as Budget<br/>Optimizer
    participant A5 as Itinerary<br/>Compiler
    participant MCP as Custom<br/>MCP Server
    participant API as Free<br/>Public APIs
    participant PC as Pinecone<br/>(RAG)
    participant DB as Supabase<br/>(Postgres)

    User->>FE: enter destination, days, budget, preferences
    FE->>BE: POST /api/plan
    BE-->>FE: { run_id, poll_url }
    FE->>BE: GET /api/plan/{run_id}/status?since=0  (poll loop)

    BE->>TM: team.arun(input=prompt, stream=True)
    activate TM

    TM->>A1: delegate "research destination"
    activate A1
    A1->>PC: search_knowledge("destination facts")
    PC-->>A1: top-K curated docs
    A1->>MCP: get_weather, country_info, search_destinations
    MCP->>API: Open-Meteo, REST Countries, Wikivoyage
    API-->>MCP: JSON
    MCP-->>A1: structured tool results
    A1-->>TM: weather + culture + attractions summary
    deactivate A1

    TM->>A2: delegate "find accommodation"
    activate A2
    A2->>MCP: search_destinations(sections=["Sleep"])
    MCP-->>A2: lodging guidance
    A2-->>TM: 3 options across price tiers
    deactivate A2

    TM->>A3: delegate "optimise routes"
    activate A3
    A3->>MCP: geocode + route + optimize_day_route
    MCP->>API: Nominatim + OSRM
    API-->>MCP: coords + distances
    Note over MCP: TSP: nearest-neighbour + 2-opt
    MCP-->>A3: ordered legs + total km
    A3-->>TM: optimal daily order
    deactivate A3

    TM->>A4: delegate "analyse budget"
    activate A4
    A4->>PC: search_knowledge("budget benchmarks")
    PC-->>A4: regional cost data
    A4->>MCP: convert_currency
    MCP->>API: Frankfurter
    API-->>MCP: live FX rate
    MCP-->>A4: USD + local-currency breakdown
    A4-->>TM: cost analysis + savings tips
    deactivate A4

    TM->>A5: delegate "compile final plan"
    activate A5
    A5->>MCP: score_itinerary(draft)
    Note over MCP: Deterministic 6-criterion rubric:<br/>coherence, feasibility, budget,<br/>diversity, pacing, opening hours
    MCP-->>A5: overall_score + per-criterion
    alt score < 60
        A5->>A5: revise once
        A5->>MCP: score_itinerary(revised)
    end
    A5-->>TM: TripItinerary (Pydantic)
    deactivate A5

    TM-->>BE: stream events (RunStarted, ToolCall*, Content)
    deactivate TM

    BE->>DB: INSERT INTO trips ...
    BE->>DB: INSERT INTO agent_logs (audit trail)
    DB-->>BE: trip_id

    BE-->>FE: status=completed, content, trip_id
    FE-->>User: rendered itinerary + score + audit trail
```

## Key non-obvious points

| Step | Detail |
|---|---|
| 4–6 | Polling, not SSE — Vercel Hobby has a 10s edge timeout; SSE would fail on a 30-second agent run |
| 8 | All MCP calls go over a single shared connection — opened once per `team.arun()` |
| 12, 25 | RAG is searched BEFORE hitting MCP/external APIs — anti-hallucination grounding |
| 16 | TSP algorithm is in the MCP server, not the LLM — the model just calls `optimize_day_route(stops)` |
| 32 | Self-evaluation loop with deterministic scorer; revision triggered only if score < 60 |
| 40–41 | Audit trail persisted to `agent_logs` for the "show your reasoning" UI tab |
