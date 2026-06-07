from unittest.mock import MagicMock
from app.core.query_engine import QueryEngine


def test_query_returns_answer_and_sources(test_settings):
    mock_vs = MagicMock()
    mock_vs.search.return_value = [
        {"id": "c1", "document": "Docker bridge network",
         "metadata": {"file_path": "/tmp/d.md", "file_name": "d.md", "content_type": "markdown"},
         "distance": 0.1},
    ]

    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Docker bridge network 是..."

    qe = QueryEngine(test_settings, mock_vs, mock_llm)
    qe._embed = MagicMock(return_value=[0.1] * 512)
    result = qe.query("什么是 Docker bridge")

    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) == 1
    assert result["sources"][0]["file_name"] == "d.md"


def test_query_empty_results(test_settings):
    mock_vs = MagicMock()
    mock_vs.search.return_value = []

    mock_llm = MagicMock()

    qe = QueryEngine(test_settings, mock_vs, mock_llm)
    qe._embed = MagicMock(return_value=[0.1] * 512)
    result = qe.query("不存在的问题")

    assert result["answer"] == "未找到相关笔记。"
    assert result["sources"] == []
