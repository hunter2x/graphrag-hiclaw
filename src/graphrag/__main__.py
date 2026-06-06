"""GraphRAG CLI Entry Point"""
import argparse
from .graph import GraphBuilder
from .extraction.ingest import IngestionPipeline
from .retrieval.search import GraphRAGRetriever
from .schema.models import Document
import json

def main():
    parser = argparse.ArgumentParser(description="GraphRAG CLI")
    sub = parser.add_subparsers(dest="cmd")

    ingest_p = sub.add_parser("ingest", help="Ingest documents")
    ingest_p.add_argument("--file", required=True, help="JSONL file with documents")

    search_p = sub.add_parser("search", help="Search knowledge graph")
    search_p.add_argument("query", help="Search query")

    answer_p = sub.add_parser("answer", help="Ask a question")
    answer_p.add_argument("query", help="Question")

    api_p = sub.add_parser("api", help="Start API server")
    api_p.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.cmd == "ingest":
        graph = GraphBuilder()
        pipeline = IngestionPipeline(graph)
        with open(args.file) as f:
            for line in f:
                data = json.loads(line)
                doc = Document(**data)
                pipeline.ingest_document(doc)
        print("Ingestion complete.")

    elif args.cmd == "search":
        retriever = GraphRAGRetriever()
        retriever.build_index()
        results = retriever.local_search(args.query)
        for r in results:
            print("- %s (%s): %s" % (r["name"], r.get("type",""), r.get("description","")))

    elif args.cmd == "answer":
        retriever = GraphRAGRetriever()
        retriever.build_index()
        print(retriever.answer(args.query))

    elif args.cmd == "api":
        import uvicorn
        from .api.server import app
        uvicorn.run(app, host="0.0.0.0", port=args.port)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
