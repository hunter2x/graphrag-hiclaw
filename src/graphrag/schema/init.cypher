// GraphRAG Neo4j Schema Initialization
// =========================================

// --- Constraints ---
CREATE CONSTRAINT entity_name IF NOT EXISTS
FOR (e:Entity) REQUIRE e.name IS UNIQUE;

CREATE CONSTRAINT doc_id IF NOT EXISTS
FOR (d:Document) REQUIRE d.doc_id IS UNIQUE;

CREATE CONSTRAINT community_id IF NOT EXISTS
FOR (c:Community) REQUIRE c.community_id IS UNIQUE;

// --- Indexes ---
CREATE FULLTEXT INDEX entity_text IF NOT EXISTS
FOR (e:Entity) ON EACH [e.name, e.description];

CREATE VECTOR INDEX entity_embedding IF NOT EXISTS
FOR (e:Entity) ON (e.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type);
CREATE INDEX doc_source IF NOT EXISTS FOR (d:Document) ON (d.source);
