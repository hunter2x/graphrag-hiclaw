"""Node & Community Embedding Engine"""
from openai import OpenAI
from ..config import LLM_API_KEY, LLM_BASE_URL, EMBEDDING_MODEL, VECTOR_DIM
from ..graph import GraphBuilder
from ..schema.models import Community
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    def __init__(self, graph: GraphBuilder = None):
        self.graph = graph or GraphBuilder()
        self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    def compute_embedding(self, text: str):
        try:
            resp = self.client.embeddings.create(
                model=EMBEDDING_MODEL, input=text[:8000]
            )
            return resp.data[0].embedding
        except Exception as e:
            logger.error("Embedding failed: %s", e)
            return [0.0] * VECTOR_DIM

    def embed_all_entities(self):
        with self.graph._driver.session() as session:
            result = session.run(
                "MATCH (e:Entity) WHERE e.embedding IS NULL RETURN e.name, e.description"
            )
            for record in result:
                text = record["e.name"] + " " + (record.get("e.description") or "")
                vec = self.compute_embedding(text)
                session.run(
                    "MATCH (e:Entity {name: $name}) SET e.embedding = $vec",
                    name=record["e.name"], vec=vec
                )
        logger.info("All entities embedded")

    def embed_communities(self, communities):
        for c in communities:
            text = c.title + ". " + c.summary
            vec = self.compute_embedding(text)
            c.embedding = vec
        return communities

    def vector_search(self, query: str, top_k: int = 10):
        qvec = self.compute_embedding(query)
        with self.graph._driver.session() as session:
            result = session.run("""
                CALL db.index.vector.queryNodes('entity_embedding', $k, $vec)
                YIELD node, score
                RETURN node.name AS name, node.type AS type,
                       node.description AS description, score
                ORDER BY score DESC
            """, k=top_k, vec=qvec)
            return [dict(r) for r in result]
