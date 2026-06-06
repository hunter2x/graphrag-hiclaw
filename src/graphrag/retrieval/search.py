"""GraphRAG Hybrid Search Engine"""
from ..graph import GraphBuilder
from ..vectorize.embeddings import EmbeddingEngine
from ..vectorize.community import CommunityDetector
from ..schema.models import Community
from openai import OpenAI
from ..config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class GraphRAGRetriever:
    def __init__(self, graph: GraphBuilder = None):
        self.graph = graph or GraphBuilder()
        self.embedder = EmbeddingEngine(self.graph)
        self.detector = CommunityDetector(self.graph)
        self.llm = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        self._communities = []

    def build_index(self):
        self._communities = self.detector.detect()
        logger.info("Detected %d communities", len(self._communities))

    def local_search(self, query: str, top_k: int = 10):
        entities = self.embedder.vector_search(query, top_k)
        for ent in entities:
            rels = self._get_entity_relations(ent["name"])
            ent["relations"] = rels
        return entities

    def global_search(self, query: str, top_k: int = 3):
        qvec = self.embedder.compute_embedding(query)
        import numpy as np
        scored = []
        for c in self._communities:
            if hasattr(c, "embedding") and c.embedding:
                sim = np.dot(qvec, c.embedding) / (
                    np.linalg.norm(qvec) * np.linalg.norm(c.embedding) + 1e-8
                )
                scored.append((sim, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k]]

    def _get_entity_relations(self, name: str):
        with self.graph._driver.session() as session:
            result = session.run("""
                MATCH (e:Entity {name: $name})-[r:RELATED_TO]-(other:Entity)
                RETURN other.name AS name, other.type AS type, type(r) AS rel_type
                LIMIT 20
            """, name=name)
            return [dict(r) for r in result]

    def answer(self, query: str):
        local = self.local_search(query)
        global_ctx = self.global_search(query)
        context = self._build_context(local, global_ctx)
        return self._generate_answer(query, context)

    def _build_context(self, local, global_ctx):
        parts = []
        parts.append("=== Related Entities ===")
        for e in local[:5]:
            parts.append("- %s (%s): %s" % (
                e["name"], e.get("type", ""), e.get("description", "")))
        parts.append("\n=== Community Summaries ===")
        for c in global_ctx:
            parts.append("- %s: %s" % (c.title, c.summary))
        return "\n".join(parts)

    def _generate_answer(self, query: str, context: str):
        prompt = """Answer based on the knowledge graph context below.

Context:
{context}

Question: {query}

Answer:"""
        try:
            resp = self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt.format(
                    context=context, query=query)}],
                temperature=0.3
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.error("Answer generation failed: %s", e)
            return "Unable to generate answer."
