import chromadb
from app.config import Settings


class VectorStore:
    def __init__(self, config: Settings):
        self.client = chromadb.PersistentClient(path=str(config.chroma_dir))
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, ids: list[str], documents: list[str],
                   embeddings: list[list[float]], metadatas: list[dict]):
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(self, query_embedding: list[float], top_k: int = 10,
               where: dict | None = None) -> list[dict]:
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where
        results = self.collection.query(**kwargs)
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return output

    def delete_by_file(self, file_path: str):
        self.collection.delete(where={"file_path": file_path})

    def get_count(self) -> int:
        return self.collection.count()
