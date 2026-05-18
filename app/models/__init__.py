from dataclasses import dataclass, field


@dataclass
class ParsedDocument:
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass
class FileRecord:
    file_path: str
    md5: str
    last_modified: float
