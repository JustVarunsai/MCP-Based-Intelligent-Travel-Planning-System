# 10-Minute Demo Script (College Viva)

> Practice this 3 times. Click and speak the lines verbatim — improvising during a viva is how things go wrong.

## 0:00 — Opening (30 seconds)

> "This is **MCP Based Intelligent Travel Planning System**. The interesting bit is in the name: **MCP**. Most public AI travel demos consume one third-party MCP server. This project goes the other way — I authored my own MCP server in Python with the official SDK, and I wired five specialist agents to consume it as a multi-agent team. So MCP isn't a feature here, it's the architecture."

## 0:30 — Architecture slide (1 min)

Show `docs/architecture.md` diagram. Trace the path with a finger:

> "Frontend on Next.js, FastAPI in the middle, the MCP server on the right exposes all the travel tools, and persistence is Pinecone for RAG plus Supabase for trip history. The five agents in the middle of the backend are the consumers of the MCP server — that's the stack."

## 1:30 — Live MCP Inspector (1 min)

Open terminal:
```bash
npx @modelcontextprotocol/inspector python -m mcp_server.server
```

Click through:

> "**9 tools**, **2 resources**, **2 prompts** — these are the three MCP protocol primitives. Most servers only expose tools; using all three is a deliberate engineering choice. Tools are actions like `get_weather` or `route`. Resources are readable URIs — for example `travel://currency/rates` returns live FX rates. Prompts are reusable templates a client can invoke."

Click `optimize_day_route` and `score_itinerary`:

> "These two are different from the others — they're not API wrappers. `optimize_day_route` is a real **nearest-neighbour + 2-opt TSP** algorithm. `score_itinerary` is a **deterministic 6-criterion rubric** — coherence, feasibility, budget, diversity, pacing, opening hours. Zero LLM calls in the scorer; every criterion has a closed-form formula."

## 2:30 — Plan a real trip (3 min)

Open the frontend Trip Planner page:

- **Destination:** Goa
- **Days:** 5
- **Budget:** $800
- **Preferences:** beaches, seafood, nightlife

Click **Plan My Trip**.

While agents stream:

> "Each row you see is one agent calling MCP tools. Notice they're not all running at once — the Orchestrator delegates step by step. Destination Researcher first, then Accommodation, then the Route Optimizer is calling `geocode` and `optimize_day_route` on the MCP server, then Budget runs the cost math, then the Itinerary Compiler self-scores with `score_itinerary` before returning."

When done, show the rendered itinerary + agent score.

## 5:30 — Show the audit trail (1 min)

Click **My Trips → Goa → Audit Trail** tab.

> "Every tool call across all 5 agents is persisted to Supabase. This isn't just logging — it's **observability for multi-agent systems**, which is a live research area. If a panel asks 'how do you know your agents are doing the right thing?' — this is the answer. I can rewind and see exactly what each agent reasoned with."

## 6:30 — Destination Explorer (45s)

Open Destination Explorer. Type **"beaches in India"**.

> "This is RAG — semantic search over the curated knowledge base in Pinecone. 90 documents, India-heavy. Notice it returns Indian beaches: Andaman, Goa, Varkala, Gokarna. Now switch the query to 'high-altitude monastery'..."

Type that, click search.

> "Spiti, Ladakh, Tawang, Sikkim. Different category, same engine — embeddings handle both location and vibe."

## 7:15 — Local ↔ Cloud config switch (1 min)

Open `.env`:
```
MCP_SERVER_URL=http://localhost:8000/sse
```

> "One environment variable. Today the MCP server is running locally over stdio. Change this to the Railway URL and the same agents now hit the cloud-deployed server — without changing a line of agent code. **Transport-agnostic** is one of the things MCP gives you that REST doesn't."

## 8:15 — Tests (30s)

```bash
pytest tests/ -v
```

> "**28 deterministic tests** — every algorithm in the MCP server has unit tests. No LLM in any of them. The scorer rubric, the TSP optimizer, the geocode cache. If something breaks, this catches it before the demo."

## 8:45 — The Killer Q&A Answer (memorise verbatim)

When asked "what does MCP give you that a plain REST API wouldn't":

> "Three things. **First**, MCP separates *tools* — actions agents call — from *resources* — readable data at URIs — from *prompts* — reusable templates. REST conflates all three into endpoints. **Second**, MCP clients **auto-discover capabilities at runtime**, so adding a tool to the server requires zero client changes; my agents pick up new tools without redeployment. **Third**, the protocol is **transport-agnostic** — the same server runs locally over stdio for development and over SSE in cloud, swapped by a single config. REST forces HTTP."

Don't paraphrase. Don't shorten. Memorise.

## Anticipated panel questions — sharp answers ready

**Q: "Where in your backend do you actually consume an MCP Resource? Not just register it."**
> "The backend consumes Tools because Agno's `MCPTools` wrapper subscribes to the tool surface. Resources are exposed for **external MCP clients** — `mcp inspector`, Claude Desktop, or any other MCP-compatible LLM client. That's the standard division: tools are agent-facing, resources are client-facing. I demonstrated this earlier by opening `travel://currency/rates` in the Inspector."

**Q: "Your scorer weights — 0.20, 0.25, 0.20, 0.10, 0.15, 0.10 — where did those come from? Is it calibrated?"**
> "They reflect a design judgement, not an empirical calibration. **Feasibility** gets the highest weight because a plan that exceeds waking hours is broken — failure dominates everything else. **Coherence** and **budget** are second because both block real-world use. **Pacing** is third because uneven days are uncomfortable but not broken. **Diversity** and **opening_hours** are lower because they're quality signals, not failure signals. A future enhancement would calibrate by collecting human ratings on N sample itineraries, but for the scope of this project the weight ordering is the contribution, not the exact numbers."

**Q: "Show me one bug you actually caught using your audit trail."**
> "Yes — when I first wired up the Route Optimizer, I noticed in the audit log it was calling `geocode("Paris")` once per Route Optimizer invocation, three times across the team run. The logs made it obvious — same agent, same args, three timestamps. I added the LRU cache in `mcp_server/tools/_throttle.py` and the second and third calls became sub-millisecond cache hits. That's exactly the use case audit trails are for in multi-agent systems."

**Q: "Why coordinate-mode Agno team and not LangGraph or a planner-executor?"**
> "Coordinate mode forces a single Orchestrator to delegate sequentially, which gives me **a deterministic event ordering** to log and a single point to enforce 'all 5 agents must run' — see the orchestrator instructions in `backend/agents/team.py`. LangGraph adds graph-execution flexibility I don't need for a 5-step pipeline, and it would make the audit trail harder to interpret. The simpler tool fits the problem."

**Q: "Single LLM dependency — if OpenAI is down, your project dies."**
> "Correct, and that's a known limitation. The decision is documented in the architecture doc. The MCP server itself has zero LLM dependency — `score_itinerary`, `optimize_day_route`, `geocode`, `find_attractions` all work without any LLM. So the *tools* and *deterministic algorithms* are LLM-free; only the multi-agent orchestration above them depends on the LLM. Switching providers means changing one line in `backend/agents/base.py`."

## Closing (15s)

> "The headline contribution is the integration story: a custom MCP server, a multi-agent client, deterministic scoring algorithms, RAG-grounded answers, and full reasoning audit trails — all built on free public APIs. Thank you."

---

## Things NOT to do

- Don't say "I used GPT-4o-mini" without immediately following with "...as the LLM. The MCP server has zero LLM dependency."
- Don't promise multi-user support; this is single-user by design.
- If the live demo fails, **switch immediately** to `mcp inspector` (offline-friendly) — the protocol still demos cleanly.
- Don't run `pytest` for the full suite live if it includes Pinecone-dependent tests on a flaky network. Run only `tests/test_mcp_tools.py` (deterministic, network-free).
