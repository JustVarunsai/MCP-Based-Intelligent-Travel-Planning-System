"""
Explore destinations via semantic search over the Pinecone knowledge base.
"""
import json
import streamlit as st

st.set_page_config(page_title="Destination Explorer", page_icon="🌍", layout="wide")
st.title("🌍 Destination Explorer")

if not st.session_state.get("PINECONE_API_KEY"):
    st.info("Enter your Pinecone API key in the sidebar to search destinations.")
    st.stop()

st.markdown("Search for destinations by vibe, activity, or anything you're looking for.")

query = st.text_input("What kind of trip?", placeholder="e.g. cheap beach holiday, cultural city in Europe, hiking...")

if query:
    try:
        from rag.knowledge_base import create_knowledge_base
        kb = create_knowledge_base()
        results = kb.search(query=query, max_results=8)

        if not results:
            st.info("No matching destinations found. Try a different search.")
        else:
            st.caption(f"Found {len(results)} results")
            for doc in results:
                meta = doc.meta_data or {}
                doc_type = meta.get("type", "")

                # only show destination results nicely
                if doc_type == "destination":
                    try:
                        data = json.loads(doc.content)
                    except json.JSONDecodeError:
                        data = {}

                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"### {data.get('name', meta.get('name', 'Destination'))}")
                            st.write(data.get("description", ""))
                            tags = data.get("tags", [])
                            if tags:
                                st.caption(" · ".join(tags))
                        with c2:
                            best = data.get("best_months", "")
                            if best:
                                st.metric("Best months", best)
                            budget = data.get("budget_per_day_usd", {})
                            if budget:
                                st.caption(
                                    f"~${budget.get('budget', '?')}-"
                                    f"${budget.get('mid', '?')}/day"
                                )
                            if st.button("Plan a trip here", key=f"plan_{data.get('name', '')}"):
                                st.session_state["prefill_destination"] = data.get("name", "")
                                st.switch_page("pages/1_Trip_Planner.py")
                else:
                    # budget benchmark or packing guide
                    with st.expander(f"{doc_type}: {meta.get('region', meta.get('climate', 'Info'))}"):
                        st.text(doc.content[:500])

    except Exception as e:
        st.error(f"Search failed: {e}")
