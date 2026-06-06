# GraphRAG

> GraphRAG: **图谱增强检索生成系统** — 基于 Neo4j + 向量化 + LLM 的知识图谱对话引擎

[![CI](https://github.com/hunter2x/graphrag-hiclaw/actions/workflows/ci.yml/badge.svg)](https://github.com/hunter2x/graphrag-hiclaw/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)

## 特性

- **实体抽取** — LLM-based 自动实体/关系提取，支持中英文
- **知识图谱** — Neo4j 存储，Cypher 查询，APOC 扩展
- **向量化** — OpenAI/text-embedding 节点嵌入 + 向量检索
- **社区检测** — Leiden/Louvain 算法，自动发现知识群落
- **混合检索** — Local Search（图谱遍历+向量）+ Global Search（社区 map-reduce）
- **LLM 对话** — 基于 GraphRAG 上下文增强的问答生成
- **REST API** — FastAPI 接口，流式响应
- **Web UI** — 开箱即用的对话界面

## 架构

```
Documents -> EntityExtractor -> Neo4j Graph -> CommunityDetector
                                                    |
                                             EmbeddingEngine
                                                    |
                                            GraphRAGRetriever
                                              /          \
                                     Local Search    Global Search
                                              \          /
                                           LLM Answer
```

## 快速开始

### 1. 配置

```bash
cp .env.example .env
# 编辑 .env 填入 API Key 和 Neo4j 密码
```

### 2. 启动

```bash
docker compose up -d
```

### 3. API 使用

```bash
# 健康检查
curl http://localhost:8000/health

# 导入文档
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"documents":[{"doc_id":"1","title":"Hello","content":"GraphRAG combines knowledge graphs with RAG..."}]}'

# 问答
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"query":"What is GraphRAG?"}'
```

### 4. Web UI

打开 `web/index.html` 或访问 http://localhost:8000

## CLI

```bash
python -m src.graphrag ingest --file data.jsonl
python -m src.graphrag answer "How does GraphRAG work?"
python -m src.graphrag api --port 8000
```

## 项目结构

```
graphrag-hiclaw/
├── src/graphrag/
│   ├── schema/        # 数据模型 + Cypher
│   │   ├── models.py  # Pydantic Entity/Document/Community
│   │   └── init.cypher # Neo4j Schema + Indexes
│   ├── extraction/    # 实体/关系抽取
│   │   ├── extractor.py  # LLM-based extractor
│   │   └── ingest.py     # Document pipeline
│   ├── vectorize/     # 向量化 + 社区检测
│   │   ├── embeddings.py # OpenAI embeddings
│   │   └── community.py  # Leiden detection
│   ├── retrieval/     # 检索引擎
│   │   └── search.py     # GraphRAG Hybrid
│   ├── api/           # FastAPI
│   │   └── server.py
│   ├── graph.py       # Neo4j Builder
│   ├── config.py      # Configuration
│   └── __main__.py    # CLI entry
├── web/               # Demo UI
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── .env.example
```

## License

MIT
