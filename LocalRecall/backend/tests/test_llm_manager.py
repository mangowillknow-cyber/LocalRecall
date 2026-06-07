from unittest.mock import MagicMock
from app.core.llm_manager import LLMManager


def test_ollama_unavailable_fallback(test_settings):
    mgr = LLMManager(test_settings)
    mgr._ollama_available = False
    assert mgr.get_provider() == "local"


def test_ollama_available(test_settings):
    test_settings.use_ollama = True
    mgr = LLMManager(test_settings)
    mgr._ollama_available = True
    assert mgr.get_provider() == "ollama"


def test_generate_returns_string(test_settings):
    mgr = LLMManager(test_settings)
    mgr._ollama_available = False
    mgr._generate_local = MagicMock(return_value="hello world")
    result = mgr.generate("test prompt")
    assert isinstance(result, str)
    assert result == "hello world"
