import logging
from typing import Optional

import chromadb

from app.config import settings
from app.embedding import get_embedding_provider

logger = logging.getLogger(__name__)

COLLECTION_NAME = "knowledge_base"

_client: Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def get_collection():
    return get_chroma_client().get_or_create_collection(name=COLLECTION_NAME)


def add_chunks(doc_ids: list[str], texts: list[str], metadatas: list[dict]):
    """添加文档到向量库"""
    provider = get_embedding_provider()
    embeddings = provider.embed(texts)
    collection = get_collection()
    collection.upsert(ids=doc_ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    logger.info(f"Upserted {len(doc_ids)} chunks")


def delete_by_file(file_path: str):
    """删除某个文件的所有 chunks"""
    collection = get_collection()
    results = collection.get(where={"file_path": file_path})
    if results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info(f"Deleted {len(results['ids'])} chunks for {file_path}")


def similarity_search(query_text: str, top_k: int = 5) -> list[dict]:
    """向量相似度检索"""
    provider = get_embedding_provider()
    query_embedding = provider.embed([query_text])[0]
    collection = get_collection()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    docs = []
    for i in range(len(results["ids"][0])):
        docs.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return docs
