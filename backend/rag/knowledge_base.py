"""
RAG knowledge base backed by Pinecone with Pinecone's own
free embedding model (multilingual-e5-large, 1024 dims).
No OpenAI credits used for embeddings.
"""
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field

from pinecone import Pinecone, ServerlessSpec
from agno.knowledge.embedder.base import Embedder
from agno.vectordb.pineconedb import PineconeDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.document.base import Document
from backend.config import config

EMBEDDING_MODEL = "multilingual-e5-large"
EMBEDDING_DIM = 1024


@dataclass
class PineconeEmbedder(Embedder):
    """Uses Pinecone's free inference API for embeddings."""
    api_key: str = ""
    dimensions: Optional[int] = EMBEDDING_DIM
    _pc: Any = field(default=None, repr=False, init=False)

    def _client(self):
        if self._pc is None:
            key = self.api_key or config.pinecone_api_key
            self._pc = Pinecone(api_key=key)
        return self._pc

    def get_embedding(self, text: str) -> List[float]:
        result = self._client().inference.embed(
            model=EMBEDDING_MODEL,
            inputs=[text],
            parameters={"input_type": "query"},
        )
        return result.data[0].values

    def get_embedding_and_usage(self, text: str) -> Tuple[List[float], Optional[Dict]]:
        return self.get_embedding(text), None


def create_embedder():
    return PineconeEmbedder(api_key=config.pinecone_api_key)


def create_vector_db(embedder=None):
    if embedder is None:
        embedder = create_embedder()
    return PineconeDb(
        name=config.PINECONE_INDEX,
        dimension=EMBEDDING_DIM,
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
