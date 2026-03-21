"""
Seed script to load curated travel data into Pinecone via the Knowledge base.
Run once: python -m rag.seed_data
"""
import json
import os
import sys

# allow running as a script from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.knowledge_base import create_knowledge_base

DATA_DIR = os.path.join(os.path.dirname(__file__), "travel_documents")


def _load_json(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


def seed():
    kb = create_knowledge_base()

    # destinations
    destinations = _load_json("destinations.json")
    print(f"Seeding {len(destinations)} destinations...")
    for dest in destinations:
        kb.insert(
            text_content=json.dumps(dest, indent=2),
            metadata={"type": "destination", "name": dest["name"]},
            upsert=True,
        )

    # budget benchmarks
    benchmarks = _load_json("budget_benchmarks.json")
    print(f"Seeding {len(benchmarks)} budget benchmarks...")
    for bench in benchmarks:
        kb.insert(
            text_content=json.dumps(bench, indent=2),
            metadata={"type": "budget_benchmark", "region": bench["region"]},
            upsert=True,
        )

    # packing guides
    guides = _load_json("packing_guides.json")
    print(f"Seeding {len(guides)} packing guides...")
    for guide in guides:
        kb.insert(
            text_content=json.dumps(guide, indent=2),
            metadata={"type": "packing_guide", "climate": guide["climate"]},
            upsert=True,
        )

    print("Done — all travel data loaded into Pinecone.")


if __name__ == "__main__":
    seed()
