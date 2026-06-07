from app.core.vector_store import VectorStore
from app.config import Settings


def test_add_and_search(test_settings):
    vs = VectorStore(test_settings)
    vs.add_chunks(
        ids=["chunk_1", "chunk_2"],
        documents=["Docker bridge network", "Python virtual environment"],
        embeddings=[[0.1] * 512, [0.2] * 512],
        metadatas=[
            {"file_path": "/tmp/docker.md", "content_type": "markdown", "modified_at": 1700000000},
            {"file_path": "/tmp/python.md", "content_type": "markdown", "modified_at": 1700001000},
        ],
    )
    results = vs.search(query_embedding=[0.1] * 512, top_k=2)
    assert len(results) == 2
    assert results[0]["id"] == "chunk_1"


def test_search_with_metadata_filter(test_settings):
    vs = VectorStore(test_settings)
    vs.add_chunks(
        ids=["c1", "c2"],
        documents=["note A", "note B"],
        embeddings=[[0.1] * 512, [0.2] * 512],
        metadatas=[
            {"file_path": "/tmp/a.md", "content_type": "markdown", "modified_at": 1700000000},
            {"file_path": "/tmp/b.py", "content_type": "code", "modified_at": 1700000000},
        ],
    )
    results = vs.search(
        query_embedding=[0.1] * 512,
        top_k=10,
        where={"content_type": "markdown"},
    )
    assert len(results) == 1
    assert results[0]["id"] == "c1"


def test_delete_by_file(test_settings):
    vs = VectorStore(test_settings)
    vs.add_chunks(
        ids=["c1", "c2", "c3"],
        documents=["a", "b", "c"],
        embeddings=[[0.1] * 512] * 3,
        metadatas=[
            {"file_path": "/tmp/a.md", "content_type": "markdown", "modified_at": 0},
            {"file_path": "/tmp/a.md", "content_type": "markdown", "modified_at": 0},
            {"file_path": "/tmp/b.md", "content_type": "markdown", "modified_at": 0},
        ],
    )
    vs.delete_by_file("/tmp/a.md")
    remaining = vs.get_count()
    assert remaining == 1
