import hashlib
import time
from pathlib import Path
from app.config import Settings
from app.core.database import Database
from app.core.vector_store import VectorStore
from app.plugins.loader import PluginLoader


class Indexer:
    def __init__(self, config: Settings, db: Database, vs: VectorStore,
                 plugin_loader: PluginLoader | None = None):
        self.config = config
        self.db = db
        self.vs = vs
        self.plugin_loader = plugin_loader or PluginLoader()
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

    def _embed(self, texts: list[str]) -> list[list[float]]:
        model = self._get_embedding_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def _file_hash(self, file_path: Path) -> str:
        return hashlib.sha256(file_path.read_bytes()).hexdigest()

    def index_file(self, file_path: Path) -> dict:
        file_hash = self._file_hash(file_path)
        existing = self.db.get_file_by_path(str(file_path))
        if existing and existing.hash == file_hash:
            return {"status": "skipped", "path": str(file_path)}

        plugin = self.plugin_loader.get_plugin(file_path)
        if plugin is None:
            return {"status": "unsupported", "path": str(file_path)}

        try:
            doc = plugin.parse(file_path)
            chunks = plugin.chunk(doc)
        except Exception as e:
            return {"status": "error", "path": str(file_path), "error": str(e)}

        if not chunks:
            return {"status": "empty", "path": str(file_path)}

        self.vs.delete_by_file(str(file_path))

        texts = [c.text for c in chunks]
        embeddings = self._embed(texts)

        chunk_ids = [f"{file_hash}_{c.index}" for c in chunks]
        metadatas = []
        for c in chunks:
            meta = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "content_type": doc.content_type,
                "chunk_index": c.index,
                "modified_at": file_path.stat().st_mtime,
            }
            if doc.content_type == "code" and "language" in doc.metadata:
                meta["language"] = doc.metadata["language"]
            metadatas.append(meta)

        self.vs.add_chunks(
            ids=chunk_ids, documents=texts,
            embeddings=embeddings, metadatas=metadatas,
        )

        self.db.upsert_file(
            path=str(file_path), hash=file_hash,
            size=file_path.stat().st_size, content_type=doc.content_type,
        )
        with self.db.get_session() as session:
            from app.models.database import FileRecord
            f = session.query(FileRecord).filter_by(path=str(file_path)).first()
            if f:
                f.chunk_count = len(chunks)
                f.status = "indexed"
                f.indexed_at = time.time()
                session.commit()

        return {"status": "indexed", "path": str(file_path), "chunk_count": len(chunks)}

    def index_directory(self, directory: Path, callback=None) -> dict:
        stats = {"indexed": 0, "skipped": 0, "errors": 0, "unsupported": 0}
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
            if any(part in self.config.exclude_dirs for part in file_path.parts):
                continue
            result = self.index_file(file_path)
            status = result.get("status", "error")
            if status in stats:
                stats[status] += 1
            if callback:
                callback(result)
        return stats
