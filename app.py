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

# ── custom theme via CSS ─────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }
    .stButton > button[kind="primary"] {
        background-color: #2563EB;
        color: white;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8;
    }
    .stMetric label, .stMetric [data-testid="stMetricValue"] {
        color: #F8FAFC;
    }
    div[data-testid="stContainer"] {
        border-color: #334155;
    }
    h1, h2, h3, h4 {
        color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)

# ── pre-load API keys from .env into session state ───────────────
_ENV_KEYS = [
    "OPENAI_API_KEY",
    "GOOGLE_MAPS_API_KEY",
    "PINECONE_API_KEY",
    "SERPER_API_KEY",
    "SUPABASE_DATABASE_URL",
]
for k in _ENV_KEYS:
    if k not in st.session_state:
        st.session_state[k] = os.getenv(k, "")

# ── sidebar: API key inputs ──────────────────────────────────────
with st.sidebar:
    st.header("API Keys")

    st.text_input("OpenAI API Key", type="password", key="OPENAI_API_KEY",
                  help="Required — powers the AI agents")
    st.text_input("Google Maps API Key", type="password", key="GOOGLE_MAPS_API_KEY",
                  help="Route & distance calculations via MCP")
    st.text_input("Pinecone API Key", type="password", key="PINECONE_API_KEY",
                  help="Required — vector knowledge base for RAG")
    st.text_input("Serper API Key", type="password", key="SERPER_API_KEY",
                  help="Required — web search for live travel info")
    st.text_input("Supabase DB URL", type="password", key="SUPABASE_DATABASE_URL",
                  help="Optional — Postgres connection string to save trips")

    keys_ok = all([
        st.session_state.get("OPENAI_API_KEY"),
        st.session_state.get("PINECONE_API_KEY"),
        st.session_state.get("SERPER_API_KEY"),
    ])
    if keys_ok:
        st.success("Core API keys set")
    else:
        st.warning("Enter OpenAI, Pinecone, and Serper keys to start planning.")

    st.divider()
    st.caption("Built with Agno · OpenAI · MCP · Pinecone · Supabase")

# ── landing page ─────────────────────────────────────────────────

st.title("AI Travel Planner")
st.subheader("Multi-Agent System powered by MCP & RAG")

st.markdown("""
Plan your next trip with a team of AI agents that collaborate in real-time:

| Agent | What it does |
|-------|-------------|
| **Destination Researcher** | Pulls live info + curated knowledge about your destination |
| **Accommodation Agent** | Searches Airbnb via MCP for real listings and prices |
| **Route Optimizer** | Calculates distances and optimal daily routes |
| **Budget Optimizer** | Analyses costs against regional benchmarks |
| **Itinerary Compiler** | Stitches everything into a structured day-by-day plan |

---

**Get started** head to the **Trip Planner** page in the sidebar.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Destinations in KB", "30+", help="Curated knowledge base entries")
with col2:
    st.metric("Budget Regions", "10", help="Regional cost benchmarks")
with col3:
    st.metric("Packing Guides", "6", help="Climate-based packing lists")
