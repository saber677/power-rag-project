from openai import OpenAI

from app.config import settings
from app.retriever import retrieve

SYSTEM_PROMPT = """你是企业内部研发知识助手。

请基于以下上下文回答问题。

如果上下文中不存在答案，请明确说明不知道。

上下文：
{context}

问题：
{question}"""


def chat(question: str, top_k: int = 5) -> dict:
    """RAG 问答：检索 + 生成"""
    docs = retrieve(question, top_k=top_k)

    context = "\n---\n".join(
        f"[来源: {d['metadata'].get('file_path', 'unknown')}]\n{d['text']}" for d in docs
    )

    client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)
    resp = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context, question=question)},
            {"role": "user", "content": question},
        ],
    )

    sources = [d["metadata"].get("file_path", "") for d in docs]
    return {"answer": resp.choices[0].message.content, "sources": list(set(sources))}
