import re

from app.models import Chunk, ParsedDocument


def chunk_document(doc: ParsedDocument, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[Chunk]:
    """根据文档类型选择切分策略"""
    if doc.metadata.get("source_type") == "code" and doc.metadata.get("language") == "java":
        chunks = _chunk_java(doc.text)
        if chunks:
            return _build_chunks(chunks, doc.metadata)

    return _chunk_by_size(doc.text, doc.metadata, chunk_size, chunk_overlap)


def _chunk_by_size(text: str, metadata: dict, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """按固定长度切分"""
    chunks: list[Chunk] = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        if chunk_text.strip():
            chunks.append(Chunk(
                text=chunk_text,
                metadata={**metadata, "chunk_index": idx},
            ))
            idx += 1
        start = end - chunk_overlap
    return chunks


def _chunk_java(text: str) -> list[str]:
    """尝试按 class/method/interface 切分 Java 代码"""
    # 简单正则匹配 class/interface/method 块
    pattern = r'((?:public|private|protected|static|\s)*(?:class|interface|enum)\s+\w+[^{]*\{)'
    parts = re.split(pattern, text)
    if len(parts) <= 1:
        # 尝试按方法切分
        method_pattern = r'((?:public|private|protected|static|\s)*\w+\s+\w+\s*\([^)]*\)\s*(?:throws\s+[^{]*)?\{)'
        parts = re.split(method_pattern, text)

    if len(parts) <= 1:
        return []

    # 合并 split 结果（分隔符和内容交替）
    chunks = []
    i = 0
    while i < len(parts):
        chunk = parts[i]
        if i + 1 < len(parts):
            chunk += parts[i + 1]
            i += 2
        else:
            i += 1
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def _build_chunks(texts: list[str], metadata: dict) -> list[Chunk]:
    return [
        Chunk(text=t, metadata={**metadata, "chunk_index": i})
        for i, t in enumerate(texts)
    ]
