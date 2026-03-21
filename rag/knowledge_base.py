from pinecone import ServerlessSpec
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.pineconedb import PineconeDb
from agno.knowledge.knowledge import Knowledge
from config import config


def create_embedder():
    return OpenAIEmbedder(
        id=config.EMBEDDING_MODEL,
        dimensions=config.EMBEDDING_DIMENSIONS,
        api_key=config.openai_api_key,
    )


def create_vector_db(embedder=None):
    if embedder is None:
        embedder = create_embedder()
    return PineconeDb(
        name=config.PINECONE_INDEX,
        dimension=config.EMBEDDING_DIMENSIONS,
        spec=ServerlessSpec(
            cloud=config.PINECONE_CLOUD,
            region=config.PINECONE_REGION,
        ),
        embedder=embedder,
        metric="cosine",
        api_key=config.pinecone_api_key,
    )


def create_knowledge_base():
    """Build the shared travel knowledge base backed by Pinecone."""
    embedder = create_embedder()
    vector_db = create_vector_db(embedder)
    return Knowledge(
        name="travel_knowledge",
        description="Curated travel destinations, budget benchmarks, and packing guides",
        vector_db=vector_db,
        max_results=5,
    )
