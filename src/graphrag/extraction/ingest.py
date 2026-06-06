"""Document Ingestion Pipeline"""
from ..graph import GraphBuilder
from ..schema.models import Document
from .extractor import EntityExtractor
import logging

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self, graph: GraphBuilder = None):
        self.graph = graph or GraphBuilder()
        self.extractor = EntityExtractor()

    def ingest_document(self, doc: Document):
        logger.info("Ingesting: %s", doc.doc_id)
        self.graph.upsert_document(doc)
        entities, rels = self.extractor.extract(doc.content)
        self.graph.upsert_entities(entities)
        self.graph.create_relationships(rels)
        for e in entities:
            self.graph.link_entity_to_doc(e.name, doc.doc_id)
        logger.info("Done: %d entities, %d relationships",
                     len(entities), len(rels))
        return entities, rels

    def ingest_documents(self, documents):
        for doc in documents:
            self.ingest_document(doc)
