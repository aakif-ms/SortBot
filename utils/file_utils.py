import os
import hashlib
from pathlib import Path
import fitz
from docx import Document
from PIL import Image
from PIL.ExifTags import TAGS

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
    ext = Path(filepath).suffix.lower()
    try:
        if ext in SUPPORTED_PREVIEW_EXTENSIONS:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(PREVIEW_CHAR_LIMIT)
        elif ext == ".pdf":
            try:
                doc = fitz.open(filepath)
                text = ""
                for page in doc[:2]:
                    text += page.get_text()
                    if len(text) > PREVIEW_CHAR_LIMIT:
                        break
                doc.close()
                return text[:PREVIEW_CHAR_LIMIT]
            except ImportError:
                return "[PDF - PYMuPDF not installed]"
        
        elif ext == ".docx":
            try:
                doc = Document(filepath)
                text = " ".join([p.text for p in doc.paragraphs[:10]])
                return text[:PREVIEW_CHAR_LIMIT]
            except ImportError:
                return "[DOCX - python-docx not installed]"       
        
        elif ext == ".csv":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = [f.readlines() for _ in range(5)]
            return "".join(lines)[:PREVIEW_CHAR_LIMIT]
        
        elif ext in IMAGE_EXTENSIONS:
            try:
                img = Image.open(filepath)
                exif_data = img._getexif()
                if exif_data:
                    tags = {TAGS.get(k, k): v for k, v in exif_data.items() if isinstance(v, (str, int))}
                    relevant = {k: v for k, v in tags.items() if k in ("DateTime", "Make", "Model", "Software")}
                    return f"Image {img.size[0]}x{img.size[1]} | EXIF: {relevant}"
                return f"Image file {img.size[0]}x{img.size[1]} {img.mode}"
            except Exception:
                return f"Image file ({ext})"
        
        elif ext in ARCHIVE_EXTENSIONS:
            try:
                import zipfile
                if ext == ".zip":
                    with zipfile.ZipFile(filepath, "r") as z:
                        names = z.namelist()[:10]
                    return f"Archive containing: {', '.join(names)}"
            except Exception:
                pass
            return f"Archive file ({ext})"

        else:
            return f"Binary file ({ext})"
        
    except Exception as e:
        return f"[Could not read: {str(e)[:100]}]"
        
def get_unique_path(destination: str) -> str:
    if not os.path.exists(destination):
        return destination
    base, ext = os.path.splitext(destination)
    counter = 1
    while os.path.exists(f"{base}_{counter}-{ext}"):
        counter += 1
    return f"{base}_{counter}-{ext}"

def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"