"""
AI Travel Planner — Multi-Agent System using MCP & RAG
Landing page and shared sidebar configuration.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── light neutral theme ──────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #FAFAF9;
        color: #27272A;
    }
    [data-testid="stSidebar"] {
        background-color: #F4F4F5;
        border-right: 1px solid #E4E4E7;
    }
    [data-testid="stSidebar"] * {
        color: #27272A;
    }
    .stButton > button {
        background-color: #27272A;
        color: #FAFAF9;
        border: 1px solid #27272A;
        border-radius: 6px;
    }
    .stButton > button:hover {
        background-color: #3F3F46;
        border-color: #3F3F46;
        color: #FAFAF9;
    }
    .stButton > button[kind="primary"] {
        background-color: #18181B;
        color: #FAFAF9;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E4E4E7;
        padding: 1rem;
        border-radius: 8px;
    }
    div[data-baseweb="input"] {
        background-color: #FFFFFF;
    }
    /* expander styling */
    .streamlit-expanderHeader {
        background-color: #FFFFFF;
        border: 1px solid #E4E4E7;
        border-radius: 6px;
    }
    h1, h2, h3, h4, h5 {
        color: #18181B;
    }
    a {
        color: #52525B;
    }
    /* container borders */
    div[data-testid="stContainer"] {
        border-color: #E4E4E7 !important;
    }
    /* status widget */
    [data-testid="stStatusWidget"] {
        background-color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# ── pre-load API keys from .env into session state ───────────────
_ENV_KEYS = [
    "OPENAI_API_KEY",
    "PINECONE_API_KEY",
    "SERPER_API_KEY",
    "SUPABASE_DATABASE_URL",
]
for k in _ENV_KEYS:
    if k not in st.session_state:
        st.session_state[k] = os.getenv(k, "")

# ── sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### API Keys")

    with st.expander("Configure", expanded=False):
        st.text_input("OpenAI", type="password", key="OPENAI_API_KEY",
                      help="Powers the AI agents")
        st.text_input("Pinecone", type="password", key="PINECONE_API_KEY",
                      help="Vector knowledge base for RAG")
        st.text_input("Serper", type="password", key="SERPER_API_KEY",
                      help="Web search for live travel info")
        st.text_input("Supabase DB URL", type="password", key="SUPABASE_DATABASE_URL",
                      help="Optional — to save trips")

    keys_ok = all([
        st.session_state.get("OPENAI_API_KEY"),
        st.session_state.get("PINECONE_API_KEY"),
        st.session_state.get("SERPER_API_KEY"),
    ])
    if keys_ok:
        st.success("All keys configured")
    else:
        st.warning("Missing required API keys")

    st.divider()
    st.caption("Maps powered by OpenStreetMap — free, no key needed.")
    st.caption("Built with Agno · OpenAI · MCP · Pinecone · Supabase")

# ── landing page ─────────────────────────────────────────────────

st.title("AI Travel Planner")
st.markdown("##### Multi-Agent System powered by MCP & RAG")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("AI Agents", "5", help="Specialized agents coordinating together")
with col2:
    st.metric("Destinations", "30+", help="Curated knowledge base entries")
with col3:
    st.metric("Budget Regions", "10", help="Regional cost benchmarks")
with col4:
    st.metric("Packing Guides", "6", help="Climate-based packing lists")

st.markdown("---")

left, right = st.columns([1, 1])

with left:
    st.markdown("### The Agent Team")
    st.markdown("""
- **Destination Researcher** — live web search + curated knowledge
- **Accommodation Agent** — real Airbnb listings via MCP
- **Route Optimizer** — free OpenStreetMap + OSRM routing
- **Budget Optimizer** — regional cost benchmarks from RAG
- **Itinerary Compiler** — structured day-by-day plan
""")

with right:
    st.markdown("### How it works")
    st.markdown("""
1. You enter a destination, dates, budget, preferences
2. An Orchestrator delegates tasks to each specialist agent
3. Agents fetch live data via MCP servers and RAG
4. The Itinerary Compiler produces a structured plan
5. Save, view on map, export to calendar
""")

st.markdown("---")
st.info("Head to the **Trip Planner** page in the sidebar to start planning.")
