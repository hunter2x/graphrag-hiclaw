"""GraphRAG FastAPI Server"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..graph import GraphBuilder
from ..extraction.ingest import IngestionPipeline
from ..retrieval.search import GraphRAGRetriever
from ..schema.models import Document, Entity, Relationship
from typing import List, Optional
import asyncio
import json

app = FastAPI(title="GraphRAG API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

graph = GraphBuilder()
ingestion = IngestionPipeline(graph)
retriever = GraphRAGRetriever(graph)
retriever.build_index()

class IngestRequest(BaseModel):
    documents: List[dict]

class QueryRequest(BaseModel):
    query: str
    top_k: int = 10

class AnswerRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/ingest")
def ingest(req: IngestRequest):
    docs = [Document(**d) for d in req.documents]
    results = []
    for doc in docs:
        ents, rels = ingestion.ingest_document(doc)
        results.append({
            "doc_id": doc.doc_id,
            "entities": len(ents),
            "relationships": len(rels)
        })
    return {"status": "ok", "results": results}

@app.post("/search")
def search(req: QueryRequest):
    entities = retriever.local_search(req.query, req.top_k)
    return {"query": req.query, "results": entities}

@app.post("/answer")
def answer(req: AnswerRequest):
    result = retriever.answer(req.query)
    return {"query": req.query, "answer": result}

@app.post("/answer/stream")
async def answer_stream(req: AnswerRequest):
    async def generate():
        result = retriever.answer(req.query)
        for chunk in result.split():
            yield chunk + " "
            await asyncio.sleep(0.05)
    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/graph/summary")
def graph_summary():
    with graph._driver.session() as session:
        nodes = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        rels = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    return {"nodes": nodes, "relationships": rels}

@app.get("/communities")
def list_communities():
    return {"communities": [
        {"id": c.community_id, "title": c.title, "entities": len(c.entities)}
        for c in retriever._communities
    ]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
