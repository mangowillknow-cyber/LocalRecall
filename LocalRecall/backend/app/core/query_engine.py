from app.config import Settings
from app.core.vector_store import VectorStore
from app.core.llm_manager import LLMManager


RAG_PROMPT = """你是一个个人知识助手。根据以下检索到的用户笔记片段回答问题。
如果信息不足，如实说明。回答要简洁准确，用中文。

用户问题：{question}

检索到的相关笔记：
{context}

请基于以上笔记内容回答："""


class QueryEngine:
    def __init__(self, config: Settings, vs: VectorStore, llm: LLMManager):
        self.config = config
        self.vs = vs
        self.llm = llm
        self._embedding_model = None

    def _get_embedding_model(self):
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            model_path = self.config.models_dir / self.config.embedding_model
            if model_path.exists():
                self._embedding_model = SentenceTransformer(str(model_path))
            else:
                self._embedding_model = SentenceTransformer(f"BAAI/{self.config.embedding_model}")
        return self._embedding_model

    def _embed(self, text: str) -> list[float]:
        model = self._get_embedding_model()
        return model.encode([text], normalize_embeddings=True)[0].tolist()

    def _build_context(self, results: list[dict]) -> str:
        parts = []
        for i, r in enumerate(results, 1):
            meta = r["metadata"]
            source = f"[{i}] {meta.get('file_name', 'unknown')}"
            if meta.get("heading"):
                source += f" > {meta['heading']}"
            parts.append(f"{source}:\n{r['document']}")
        return "\n\n".join(parts)

    def _extract_sources(self, results: list[dict]) -> list[dict]:
        sources = []
        seen = set()
        for r in results:
            fp = r["metadata"].get("file_path", "")
            if fp not in seen:
                seen.add(fp)
                sources.append({
                    "file_path": fp,
                    "file_name": r["metadata"].get("file_name", ""),
                    "content_type": r["metadata"].get("content_type", ""),
                    "snippet": r["document"][:200],
                })
        return sources

    def query(self, question: str) -> dict:
        query_vec = self._embed(question)
        results = self.vs.search(query_embedding=query_vec, top_k=self.config.retrieval_top_k)
        if not results:
            return {"answer": "未找到相关笔记。", "sources": []}
        context = self._build_context(results)
        prompt = RAG_PROMPT.format(question=question, context=context)
        answer = self.llm.generate(prompt)
        sources = self._extract_sources(results)
        return {"answer": answer, "sources": sources}

    def query_stream(self, question: str):
        query_vec = self._embed(question)
        results = self.vs.search(query_embedding=query_vec, top_k=self.config.retrieval_top_k)
        sources = self._extract_sources(results)
        if not results:
            yield {"type": "answer", "text": "未找到相关笔记。"}
            yield {"type": "sources", "data": []}
            return
        context = self._build_context(results)
        prompt = RAG_PROMPT.format(question=question, context=context)
        yield {"type": "sources", "data": sources}
        for token in self.llm.generate_stream(prompt):
            yield {"type": "token", "text": token}
        yield {"type": "done"}
