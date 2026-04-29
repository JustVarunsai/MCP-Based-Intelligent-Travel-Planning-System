"""
Destination Explorer — semantic search over the Pinecone RAG knowledge base.
Returns destinations that match a free-text query (e.g. "beaches in India",
"high-altitude trek", "cheap southeast asia").
"""
import json
import logging

from fastapi import APIRouter, HTTPException, Query

from backend.config import config

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/explore", tags=["explore"])


@router.get("")
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    top_k: int = Query(8, ge=1, le=25),
    only_destinations: bool = Query(True),
):
    """Semantic search across the curated travel knowledge base."""
    if not config.pinecone_api_key:
        raise HTTPException(status_code=503, detail="pinecone not configured")

    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=config.pinecone_api_key)
        idx = pc.Index(config.PINECONE_INDEX)

        emb = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[q],
            parameters={"input_type": "query"},
        )
        flt = {"type": "destination"} if only_destinations else None
        result = idx.query(
            vector=emb.data[0].values,
            top_k=top_k,
            include_metadata=True,
            filter=flt,
        )
    except Exception as e:
        log.exception("Pinecone query failed")
        raise HTTPException(status_code=500, detail=f"search failed: {e}")

    out = []
    for m in result.matches:
        meta = dict(m.metadata or {})
        doc_json = meta.pop("doc_json", None)
        try:
            doc = json.loads(doc_json) if doc_json else {}
        except json.JSONDecodeError:
            doc = {}
        out.append({
            "score": round(float(m.score), 4),
            "name": meta.get("name"),
            "country": meta.get("country"),
            "region": meta.get("region"),
            "primary_type": meta.get("primary_type"),
            "tags": meta.get("tags", []),
            "trending_2026": meta.get("trending_2026", False),
            "latitude": meta.get("latitude"),
            "longitude": meta.get("longitude"),
            "doc": doc,
        })
    return {"query": q, "count": len(out), "results": out}
