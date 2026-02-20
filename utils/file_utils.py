import os
import hashlib
from pathlib import Path

SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".env", ".sh"}
SUPPORTED_PREVIEW_EXTENSIONS = {".pdf", ".docx", ".csv", ".xlsx"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".rar", ".7z"}

PREVIEW_CHAR_LIMIT = 600

def compute_md5(filepath: str) -> str:
    h = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""
    
def read_content_preview(filepath: str) -> str:
    pass