"""
Seed curated travel data directly into Pinecone.
Uses Pinecone's free built-in embeddings — zero OpenAI cost.
Run: python -m rag.seed_data
"""
import json
import os
import sys
import time
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from pinecone import Pinecone, ServerlessSpec

DATA_DIR = os.path.join(os.path.dirname(__file__), "travel_documents")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "travel-knowledge"
EMBED_MODEL = "multilingual-e5-large"
EMBED_DIM = 1024


def _load_json(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


def _make_id(text):
    return hashlib.md5(text.encode()).hexdigest()


def seed():
    if not PINECONE_KEY:
        print("ERROR: PINECONE_API_KEY must be set in .env")
        sys.exit(1)

    pc = Pinecone(api_key=PINECONE_KEY)
    print(f"Using Pinecone's free embeddings ({EMBED_MODEL})")

    # create index if it doesn't exist
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing:
        print(f"Creating index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBED_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print("Waiting 20s for index to be ready...")
        time.sleep(20)
    else:
        print(f"Index '{INDEX_NAME}' already exists")

    idx = pc.Index(INDEX_NAME)

    # collect all documents
    docs = []

    destinations = _load_json("destinations.json")
    for dest in destinations:
        docs.append({
            "id": _make_id(dest["name"]),
            "text": json.dumps(dest, indent=2),
            "metadata": {"type": "destination", "name": dest["name"]},
        })

    benchmarks = _load_json("budget_benchmarks.json")
    for bench in benchmarks:
        docs.append({
            "id": _make_id("budget_" + bench["region"]),
            "text": json.dumps(bench, indent=2),
            "metadata": {"type": "budget_benchmark", "region": bench["region"]},
        })

    guides = _load_json("packing_guides.json")
    for guide in guides:
        docs.append({
            "id": _make_id("packing_" + guide["climate"]),
            "text": json.dumps(guide, indent=2),
            "metadata": {"type": "packing_guide", "climate": guide["climate"]},
        })

    print(f"\nEmbedding and upserting {len(docs)} documents...")

    # batch embed and upsert (Pinecone inference supports batches of up to 96)
    batch_size = 20
    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]
        texts = [d["text"] for d in batch]

        embeddings = pc.inference.embed(
            model=EMBED_MODEL,
            inputs=texts,
            parameters={"input_type": "passage"},
        )

        vectors = []
        for doc, emb in zip(batch, embeddings.data):
            meta = doc["metadata"].copy()
            meta["text"] = doc["text"][:500]  # store snippet for retrieval
            vectors.append({
                "id": doc["id"],
                "values": emb.values,
                "metadata": meta,
            })

        idx.upsert(vectors=vectors)
        print(f"  Upserted batch {i // batch_size + 1}: {[d['metadata'].get('name') or d['metadata'].get('region') or d['metadata'].get('climate') for d in batch]}")

    # wait for indexing
    print("\nWaiting 10s for indexing...")
    time.sleep(10)

    # verify
    stats = idx.describe_index_stats()
    print(f"Total vectors in index: {stats.get('total_vector_count')}")

    # test search
    q_emb = pc.inference.embed(
        model=EMBED_MODEL,
        inputs=["beach tropical island vacation"],
        parameters={"input_type": "query"},
    )
    results = idx.query(vector=q_emb.data[0].values, top_k=3, include_metadata=True)
    print(f"\nTest search 'beach tropical island' ({len(results.matches)} results):")
    for m in results.matches:
        name = m.metadata.get("name") or m.metadata.get("region") or m.metadata.get("climate")
        print(f"  [{m.metadata.get('type')}] {name} (score: {m.score:.3f})")

    print("\nDone!")


if __name__ == "__main__":
    seed()
