"""
AI Travel Planner — Multi-Agent System using MCP & RAG
Landing page and shared sidebar configuration.
"""
import streamlit as st

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── sidebar: API key inputs (shared via session state) ───────────

with st.sidebar:
    st.header("API Keys")

    st.text_input("OpenAI API Key", type="password", key="OPENAI_API_KEY",
                  help="Required — powers the AI agents")
    st.text_input("Google Maps API Key", type="password", key="GOOGLE_MAPS_API_KEY",
                  help="Required — route & distance calculations via MCP")
    st.text_input("Pinecone API Key", type="password", key="PINECONE_API_KEY",
                  help="Required — vector knowledge base for RAG")
    st.text_input("Supabase URL", key="SUPABASE_URL",
                  help="Optional — needed to save trips")
    st.text_input("Supabase Key", type="password", key="SUPABASE_KEY",
                  help="Optional — needed to save trips")

    keys_ok = all([
        st.session_state.get("OPENAI_API_KEY"),
        st.session_state.get("GOOGLE_MAPS_API_KEY"),
        st.session_state.get("PINECONE_API_KEY"),
    ])
    if keys_ok:
        st.success("Core API keys set")
    else:
        st.warning("Enter at least OpenAI, Google Maps, and Pinecone keys to start planning.")

    st.divider()
    st.caption("Built with Agno · OpenAI · MCP · Pinecone · Supabase")

# ── landing page ─────────────────────────────────────────────────

st.title("✈️ AI Travel Planner")
st.subheader("Multi-Agent System powered by MCP & RAG")

st.markdown("""
Plan your next trip with a team of AI agents that collaborate in real-time:

| Agent | What it does |
|-------|-------------|
| **Destination Researcher** | Pulls live info + curated knowledge about your destination |
| **Accommodation Agent** | Searches Airbnb via MCP for real listings and prices |
| **Route Optimizer** | Uses Google Maps MCP for distances and optimal routes |
| **Budget Optimizer** | Analyses costs against regional benchmarks |
| **Itinerary Compiler** | Stitches everything into a structured day-by-day plan |

---

**Get started** → head to the **Trip Planner** page in the sidebar.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Destinations in KB", "30+", help="Curated knowledge base entries")
with col2:
    st.metric("Budget Regions", "10", help="Regional cost benchmarks")
with col3:
    st.metric("Packing Guides", "6", help="Climate-based packing lists")
