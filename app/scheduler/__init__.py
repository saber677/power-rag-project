import json
import logging
import os

from app.chunker import chunk_document
from app.config import settings
from app.models import FileRecord
from app.parser import parse_file
from app.scanner import scan_directory
from app.vectorstore import add_chunks, delete_by_file

logger = logging.getLogger(__name__)

HASH_STORE_PATH = "./data/file_hashes.json"


def _load_hash_store() -> dict[str, str]:
    if os.path.exists(HASH_STORE_PATH):
        with open(HASH_STORE_PATH) as f:
            return json.load(f)
    return {}


def _save_hash_store(store: dict[str, str]):
    os.makedirs(os.path.dirname(HASH_STORE_PATH), exist_ok=True)
    with open(HASH_STORE_PATH, "w") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def _index_file(filepath: str):
    """解析 -> 切分 -> 写入向量库"""
    doc = parse_file(filepath)
    if not doc or not doc.text.strip():
        return

    chunks = chunk_document(doc)
    if not chunks:
        return

    doc_ids = [f"{filepath}#chunk{c.metadata['chunk_index']}" for c in chunks]
    texts = [c.text for c in chunks]
    metadatas = [c.metadata for c in chunks]

    add_chunks(doc_ids, texts, metadatas)


def run_increment():
    """增量扫描：只处理新增/修改的文件"""
    hash_store = _load_hash_store()
    records = scan_directory(settings.SCAN_PATHS)
    updated = 0

    current_files = set()
    for record in records:
        current_files.add(record.file_path)
        if hash_store.get(record.file_path) == record.md5:
            continue
        # 文件有变更，先删旧 chunks 再重建
        delete_by_file(record.file_path)
        _index_file(record.file_path)
        hash_store[record.file_path] = record.md5
        updated += 1

    _save_hash_store(hash_store)
    logger.info(f"Increment done: {updated} files updated")


def run_rebuild():
    """全量重建索引"""
    # 清空 hash store
    _save_hash_store({})
    # 清空 collection
    from app.vectorstore import get_chroma_client, COLLECTION_NAME
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    run_increment()
    logger.info("Full rebuild done")
