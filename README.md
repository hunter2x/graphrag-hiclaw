# GraphRAG

> 图谱增强检索生成系统 — 基于 Neo4j + 向量化 + LLM 的知识图谱对话引擎

## 特性
- 结构化数据入图库（Neo4j）
- 实体/关系自动抽取
- 节点向量化 & 社区检测（Leiden）
- 混合检索（图谱遍历 + 向量相似度）
- LLM 图谱对话

## 快速开始
```bash
cp .env.example .env  # 编辑配置
docker compose up -d
```

## 架构
```
文档 → 实体抽取 → Neo4j 图谱 → 社区检测 → 向量化 → GraphRAG 对话
```
