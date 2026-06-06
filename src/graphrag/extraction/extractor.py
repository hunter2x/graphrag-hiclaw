"""Entity & Relation Extraction Engine (LLM-based)"""
from openai import OpenAI
from ..config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from ..schema.models import Entity, Relationship
from typing import List, Tuple
import json
import logging

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extract entities and relationships from the text below.
Return JSON in this exact format:
{
  "entities": [{"name": "...", "type": "PERSON|ORG|LOC|CONCEPT|EVENT", "description": "..."}],
  "relationships": [{"source": "entity_name", "target": "entity_name", "type": "...", "description": "..."}]
}

Text:
{text}
"""

class EntityExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    def extract(self, text: str):
        prompt = EXTRACTION_PROMPT.format(text=text[:8000])
        try:
            resp = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            data = json.loads(resp.choices[0].message.content)
        except Exception as e:
            logger.error("Extraction failed: %s", e)
            return [], []

        entities = [
            Entity(name=e["name"], type=e.get("type", "CONCEPT"),
                   description=e.get("description", ""))
            for e in data.get("entities", [])
        ]
        rels = [
            Relationship(source=r["source"], target=r["target"],
                         type=r.get("type", "RELATED_TO"),
                         description=r.get("description", ""))
            for r in data.get("relationships", [])
        ]
        return entities, rels

    def extract_from_documents(self, documents):
        all_entities, all_rels = [], []
        seen = set()
        for doc in documents:
            ents, rels = self.extract(doc)
            for e in ents:
                if e.name not in seen:
                    seen.add(e.name)
                    all_entities.append(e)
            all_rels.extend(rels)
        return all_entities, all_rels
