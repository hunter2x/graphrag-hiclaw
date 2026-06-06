"""Neo4j Graph Builder"""
from neo4j import GraphDatabase, Driver
from .config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from .schema.models import Entity, Relationship, Document, Community
from typing import List
import logging

logger = logging.getLogger(__name__)

class GraphBuilder:
    def __init__(self):
        self._driver: Driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self._driver.close()

    def init_schema(self):
        with self._driver.session() as session:
            import os
            path = os.path.join(os.path.dirname(__file__), "schema", "init.cypher")
            with open(path) as f:
                content = f.read()
            for stmt in content.split(";\n"):
                stmt = stmt.strip()
                if stmt and not stmt.startswith("//"):
                    try:
                        session.run(stmt)
                    except Exception as e:
                        logger.debug(f"Schema warning: {e}")

    def upsert_entity(self, entity: Entity):
        with self._driver.session() as session:
            session.run("""
                MERGE (e:Entity {name: $name})
                SET e.type = $type, e.description = $description,
                    e.source = $source, e.weight = $weight,
                    e.embedding = $embedding
            """, name=entity.name, type=entity.type,
                description=entity.description, source=entity.source,
                weight=entity.weight, embedding=entity.embedding)

    def upsert_entities(self, entities):
        for e in entities:
            self.upsert_entity(e)

    def create_relationship(self, rel: Relationship):
        with self._driver.session() as session:
            session.run("""
                MATCH (a:Entity {name: $source})
                MATCH (b:Entity {name: $target})
                MERGE (a)-[r:RELATED_TO]->(b)
                SET r.type = $type, r.description = $description, r.weight = $weight
            """, source=rel.source, target=rel.target,
                type=rel.type, description=rel.description, weight=rel.weight)

    def create_relationships(self, rels):
        for r in rels:
            self.create_relationship(r)

    def upsert_document(self, doc: Document):
        with self._driver.session() as session:
            session.run("""
                MERGE (d:Document {doc_id: $doc_id})
                SET d.title = $title, d.content = $content, d.source = $source
            """, doc_id=doc.doc_id, title=doc.title,
                content=doc.content, source=doc.source)

    def link_entity_to_doc(self, entity_name: str, doc_id: str):
        with self._driver.session() as session:
            session.run("""
                MATCH (e:Entity {name: $name})
                MATCH (d:Document {doc_id: $doc_id})
                MERGE (e)-[:MENTIONED_IN]->(d)
            """, name=entity_name, doc_id=doc_id)
