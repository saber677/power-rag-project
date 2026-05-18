from app.vectorstore import similarity_search


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """检索与 query 最相关的 chunks"""
    return similarity_search(query, top_k=top_k)
