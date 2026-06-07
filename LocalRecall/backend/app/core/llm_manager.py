import httpx
from app.config import Settings


class LLMManager:
    def __init__(self, config: Settings):
        self.config = config
        self._local_model = None
        self._ollama_available = self._check_ollama()

    def _check_ollama(self) -> bool:
        if not self.config.use_ollama:
            return False
        try:
            r = httpx.get(f"{self.config.ollama_url}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def get_provider(self) -> str:
        if self.config.use_ollama and self._ollama_available:
            return "ollama"
        return "local"

    def _get_local_model(self):
        if self._local_model is None:
            from llama_cpp import Llama
            model_path = self.config.models_dir / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
            if not model_path.exists():
                raise FileNotFoundError(f"Local model not found: {model_path}")
            self._local_model = Llama(model_path=str(model_path), n_ctx=2048, n_threads=4)
        return self._local_model

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        if self.get_provider() == "ollama":
            return self._generate_ollama(prompt, max_tokens)
        return self._generate_local(prompt, max_tokens)

    def generate_stream(self, prompt: str, max_tokens: int = 1024):
        if self.get_provider() == "ollama":
            yield from self._generate_ollama_stream(prompt, max_tokens)
        else:
            yield self._generate_local(prompt, max_tokens)

    def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        r = httpx.post(
            f"{self.config.ollama_url}/api/generate",
            json={
                "model": self.config.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens},
            },
            timeout=120,
        )
        return r.json().get("response", "")

    def _generate_ollama_stream(self, prompt: str, max_tokens: int):
        import json as _json
        with httpx.stream(
            "POST",
            f"{self.config.ollama_url}/api/generate",
            json={
                "model": self.config.ollama_model,
                "prompt": prompt,
                "stream": True,
                "options": {"num_predict": max_tokens},
            },
            timeout=120,
        ) as r:
            for line in r.iter_lines():
                if line:
                    data = _json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done"):
                        break

    def _generate_local(self, prompt: str, max_tokens: int) -> str:
        model = self._get_local_model()
        output = model(prompt, max_tokens=max_tokens, stop=["</s>"])
        return output["choices"][0]["text"]
