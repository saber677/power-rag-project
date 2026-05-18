from abc import ABC, abstractmethod
from typing import Optional

from openai import OpenAI

from app.config import settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        pass


class OpenAICompatibleEmbedding(EmbeddingProvider):
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.EMBEDDING_API_KEY,
            base_url=settings.EMBEDDING_BASE_URL,
        )
        self.model = settings.EMBEDDING_MODEL

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self.client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in resp.data]


# 默认实例
_provider: Optional[EmbeddingProvider] = None


def get_embedding_provider() -> EmbeddingProvider:
    global _provider
    if _provider is None:
        _provider = OpenAICompatibleEmbedding()
    return _provider
