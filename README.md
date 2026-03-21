# AI Travel Planner — Multi-Agent System with MCP & RAG

A multi-agent AI travel planning system where 5 specialized agents collaborate in real-time to generate detailed, personalized travel itineraries. Uses Model Context Protocol (MCP) servers for live data from Airbnb and Google Maps, and Retrieval-Augmented Generation (RAG) with Pinecone for curated travel knowledge.

## How it works

Instead of a single AI prompt, this system uses a **coordinated team of agents** — each with a specific job:

| Agent | Role | Data Source |
|-------|------|-------------|
| Destination Researcher | Researches weather, culture, safety, attractions | SerpAPI + Pinecone RAG |
| Accommodation Agent | Finds real Airbnb listings with live prices | Airbnb MCP Server |
| Route Optimizer | Calculates distances and optimal routes | Google Maps MCP Server |
| Budget Optimizer | Analyses costs against regional benchmarks | Pinecone RAG |
| Itinerary Compiler | Combines everything into a structured plan | Synthesis (GPT-4o) |

An **orchestrator** (powered by Agno's Team framework in `coordinate` mode) delegates tasks to each agent and synthesises the final response. The UI streams agent activity in real-time so you can see each agent working.

## Features

- **Real-time agent collaboration** visible in the UI as agents work
- **Live Airbnb data** via MCP — real listings, real prices
- **Live route data** via Google Maps MCP — actual distances and travel times
- **RAG knowledge base** — 30+ curated destinations, regional budget benchmarks, climate-based packing guides
- **5-page Streamlit app**: Trip Planner, My Trips, Trip Dashboard, Destination Explorer, Trip Comparison
- **Interactive maps** with Folium
- **Cost analysis charts** with Plotly
- **Calendar export** (.ics) for Google Calendar / Apple Calendar / Outlook
- **Trip persistence** with Supabase (Postgres)
- **Semantic search** over the knowledge base — search by vibe, not just keywords

## Tech Stack

- **Agno Framework** — multi-agent orchestration
- **OpenAI GPT-4o** — powers all agents
- **MCP Servers** — Airbnb (`@openbnb/mcp-server-airbnb`) + Google Maps (`@gongrzhe/server-travelplanner-mcp`)
- **Pinecone** — vector database for RAG
- **Supabase** — Postgres database + auth
- **Streamlit** — multi-page frontend
- **Folium** — interactive maps
- **Plotly** — cost visualisation charts

## Project Structure

```
├── app.py                          # Landing page
├── config.py                       # Centralised config
├── agents/
│   ├── base.py                     # MCP tool factories + shared model
│   ├── destination_researcher.py   # SerpAPI + RAG
│   ├── accommodation_agent.py      # Airbnb MCP
│   ├── route_optimizer.py          # Google Maps MCP
│   ├── budget_optimizer.py         # RAG cost benchmarks
│   ├── itinerary_compiler.py       # Structured output (Pydantic)
│   └── team.py                     # Agno Team assembly
├── rag/
│   ├── knowledge_base.py           # Pinecone + Agno Knowledge
│   ├── seed_data.py                # Seed curated data
│   └── travel_documents/           # Destinations, budgets, packing guides
├── database/
│   ├── supabase_client.py
│   ├── crud.py
│   └── schema.sql                  # Supabase table definitions
├── services/
│   ├── trip_service.py             # Team execution + streaming
│   ├── export_service.py           # ICS calendar export
│   ├── map_service.py              # Folium map generation
│   └── cost_analysis_service.py    # Plotly charts
├── pages/
│   ├── 1_Trip_Planner.py           # Main planner + live agent panel
│   ├── 2_My_Trips.py              # Saved trip history
│   ├── 3_Trip_Dashboard.py        # Map, charts, packing list
│   ├── 4_Destination_Explorer.py  # Semantic search
│   └── 5_Trip_Comparison.py       # Side-by-side comparison
├── components/                     # Reusable Streamlit widgets
├── utils/                          # Parsers, validators
└── tests/                          # Test suite
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+ (for MCP servers via npx)

### API Keys Required

| Service | Get it from |
|---------|------------|
| OpenAI | https://platform.openai.com/api-keys |
| Google Maps | https://console.cloud.google.com/apis/credentials |
| Pinecone | https://app.pinecone.io |
| Supabase (optional) | https://supabase.com/dashboard |
| SerpAPI | https://serpapi.com/manage-api-key |

### Installation

```bash
git clone https://github.com/JustVarunsai/ai-travel-planner-mcp.git
cd ai-travel-planner-mcp

pip install -r requirements.txt
```

### Database Setup (optional — for saving trips)

1. Create a Supabase project
2. Run `database/schema.sql` in the Supabase SQL editor
3. Grab the project URL and anon key

### Seed the Knowledge Base

```bash
# set your keys first
export OPENAI_API_KEY=sk-...
export PINECONE_API_KEY=pc-...

python -m rag.seed_data
```

### Run

```bash
streamlit run app.py
```

Then enter your API keys in the sidebar and head to the Trip Planner page.

## Pages

### Trip Planner
The main page. Enter destination, dates, budget, and preferences. Hit "Plan My Trip" and watch the agents collaborate in real-time. Download the result as a calendar file or save to Supabase.

### My Trips
Browse and manage saved trips. Filter by destination.

### Trip Dashboard
Detailed view of a single trip — itinerary, interactive map, cost breakdown charts, and a packing checklist.

### Destination Explorer
Semantic search over the knowledge base. Type "cheap beach holiday" or "cultural city in Europe" and get matching destinations with key facts and budget info.

### Trip Comparison
Pick two saved trips and compare them side-by-side with a radar chart visualisation.

## Architecture

```
User Input
    ↓
Orchestrator (Team Leader)
    ├── Destination Researcher → SerpAPI + Pinecone
    ├── Accommodation Agent → Airbnb MCP
    ├── Route Optimizer → Google Maps MCP
    ├── Budget Optimizer → Pinecone benchmarks
    └── Itinerary Compiler → structured output
          ↓
Final Itinerary + Map + Charts + Calendar
          ↓
Supabase (persistence)
```

## Troubleshooting

- **MCP timeout**: MCP servers take ~30-60s to spin up on first run (npx downloads). Be patient.
- **Pinecone errors**: Make sure you've run `python -m rag.seed_data` at least once.
- **Missing distances**: Check your Google Maps API key has the Maps/Directions API enabled.
- **Slow first run**: The first MCP connection spawns a Node process. Subsequent calls in the same session are faster.
