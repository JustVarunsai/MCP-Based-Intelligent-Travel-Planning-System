import argparse
import hashlib
import json
import os
import sys
import time

from dotenv import load_dotenv

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(_ROOT, ".env"))

from pinecone import Pinecone, ServerlessSpec

DATA_DIR = os.path.join(os.path.dirname(__file__), "travel_documents")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "travel-knowledge")
EMBED_MODEL = "multilingual-e5-large"
EMBED_DIM = 1024
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")


def _load_json(filename: str):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


def _make_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def _destination_embedding_text(d: dict) -> str:
    parts = [
        d.get("name", ""),
        f"Country: {d.get('country', '')}",
        f"Region: {d.get('region', '')}",
        f"State/Province: {d.get('state', '')}" if d.get("state") else "",
        f"Type: {d.get('type', '')}",
        f"Subtypes: {', '.join(d.get('subtypes', []))}",
        f"Climate: {d.get('climate', '')}",
        f"Best months: {d.get('best_months', '')}",
        f"Tags: {', '.join(d.get('tags', []))}",
        f"Top attractions: {', '.join(d.get('top_attractions', []))}",
        d.get("description", ""),
    ]
    return "\n".join(p for p in parts if p)


def _destination_metadata(d: dict) -> dict:
    return {
        "type": "destination",
        "name": d.get("name", ""),
        "country": d.get("country", ""),
        "region": d.get("region", ""),
        "state": d.get("state", ""),
        "primary_type": d.get("type", ""),
        "subtypes": d.get("subtypes", []),
        "tags": d.get("tags", []),
        "trending_2026": bool(d.get("trending_2026", False)),
        "latitude": d.get("latitude"),
        "longitude": d.get("longitude"),
        "best_months": d.get("best_months", ""),
        "doc_json": json.dumps(d, ensure_ascii=False)[:8000],
    }


def _benchmark_embedding_text(b: dict) -> str:
    parts = [
        f"Budget benchmark for {b.get('region', '')}",
        f"Country: {b.get('country', '')}",
        json.dumps(b.get("daily_costs_usd", {})),
        b.get("notes", ""),
    ]
    return "\n".join(parts)


def _packing_embedding_text(g: dict) -> str:
    parts = [f"Packing guide for {g.get('climate', '')} climate"]
    if g.get("activities"):
        parts.append(f"Activities: {', '.join(g.get('activities', []))}")
    if g.get("essentials"):
        parts.append("Items: " + ", ".join(g.get("essentials", [])))
    return "\n".join(parts)


def _ensure_index(pc: Pinecone) -> None:
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME in existing:
        print(f"Index '{INDEX_NAME}' already exists.")
        return
    print(f"Creating index '{INDEX_NAME}' (dim={EMBED_DIM}, {PINECONE_CLOUD}/{PINECONE_REGION})...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBED_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
    )
    print("Waiting 20s for the index to become ready...")
    time.sleep(20)


def _embed_batch(pc: Pinecone, texts: list[str]) -> list[list[float]]:
    out: list[list[float]] = []
    for i in range(0, len(texts), 90):
        chunk = texts[i:i + 90]
        result = pc.inference.embed(
            model=EMBED_MODEL,
            inputs=chunk,
            parameters={"input_type": "passage"},
        )
        out.extend([d.values for d in result.data])
    return out


def seed(reset: bool = False) -> None:
    if not PINECONE_KEY:
        print("ERROR: PINECONE_API_KEY must be set in .env")
        sys.exit(1)

    pc = Pinecone(api_key=PINECONE_KEY)
    _ensure_index(pc)
    idx = pc.Index(INDEX_NAME)

    if reset:
        print("Deleting all existing vectors in the index...")
        try:
            idx.delete(delete_all=True)
            time.sleep(3)
        except Exception as e:
            print(f"  warn: delete_all returned {e}")

    destinations = _load_json("destinations.json")
    benchmarks = _load_json("budget_benchmarks.json")
    guides = _load_json("packing_guides.json")

    print(
        f"\nLoaded {len(destinations)} destinations, "
        f"{len(benchmarks)} budget benchmarks, "
        f"{len(guides)} packing guides."
    )

    all_records: list[tuple[str, str, dict]] = []

    for d in destinations:
        all_records.append((
            _make_id("dest_" + d["name"]),
            _destination_embedding_text(d),
            _destination_metadata(d),
        ))

    for b in benchmarks:
        all_records.append((
            _make_id("budget_" + b["region"]),
            _benchmark_embedding_text(b),
            {
                "type": "budget_benchmark",
                "region": b.get("region", ""),
                "country": b.get("country", ""),
                "doc_json": json.dumps(b, ensure_ascii=False)[:4000],
            },
        ))

    for g in guides:
        all_records.append((
            _make_id("pack_" + g["climate"]),
            _packing_embedding_text(g),
            {
                "type": "packing_guide",
                "climate": g.get("climate", ""),
                "doc_json": json.dumps(g, ensure_ascii=False)[:4000],
            },
        ))

    print(f"\nEmbedding {len(all_records)} documents (model={EMBED_MODEL}, dim={EMBED_DIM})...")
    texts = [r[1] for r in all_records]
    vectors = _embed_batch(pc, texts)

    payload = []
    for (rid, _text, meta), vec in zip(all_records, vectors):
        payload.append({"id": rid, "values": vec, "metadata": meta})

    print(f"Upserting {len(payload)} vectors in batches of 50...")
    for i in range(0, len(payload), 50):
        idx.upsert(vectors=payload[i:i + 50])
        print(f"  upserted {min(i + 50, len(payload))}/{len(payload)}")

    print("Waiting 8s for indexing to settle...")
    time.sleep(8)

    stats = idx.describe_index_stats()
    print(f"\nIndex now contains {stats.get('total_vector_count')} vectors.")

    sample_queries = [
        "beaches in India",
        "high-altitude mountain monastery",
        "tropical beach island Southeast Asia",
        "heritage UNESCO site Rajasthan",
        "cheap backpacker destination yoga",
        "honeymoon islands turquoise water",
    ]
    print("\nSmoke tests:")
    for q in sample_queries:
        emb = pc.inference.embed(
            model=EMBED_MODEL,
            inputs=[q],
            parameters={"input_type": "query"},
        )
        results = idx.query(
            vector=emb.data[0].values,
            top_k=4,
            include_metadata=True,
            filter={"type": "destination"},
        )
        names = [m.metadata.get("name", "?") for m in results.matches]
        print(f"  '{q}'  ->  {names}")

    print("\nSeed complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    seed(reset=args.reset)
