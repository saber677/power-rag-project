import hashlib
import logging
import os

from app.config import settings
from app.models import FileRecord

logger = logging.getLogger(__name__)

DOC_EXTENSIONS = {".md", ".txt", ".pdf", ".docx"}
CODE_EXTENSIONS = {".java", ".xml", ".yaml", ".yml", ".sql"}


def file_md5(filepath: str) -> str:
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_directory(paths: list[str]) -> list[FileRecord]:
    """递归扫描目录，返回所有符合条件的文件记录"""
    all_extensions = DOC_EXTENSIONS | CODE_EXTENSIONS
    records: list[FileRecord] = []

    for base_path in paths:
        if not os.path.exists(base_path):
            logger.warning(f"Path not found: {base_path}")
            continue
        for root, dirs, files in os.walk(base_path):
            # 过滤忽略目录
            dirs[:] = [d for d in dirs if d not in settings.IGNORE_DIRS]
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in all_extensions:
                    continue
                filepath = os.path.join(root, fname)
                records.append(FileRecord(
                    file_path=filepath,
                    md5=file_md5(filepath),
                    last_modified=os.path.getmtime(filepath),
                ))
    logger.info(f"Scanned {len(records)} files from {paths}")
    return records
