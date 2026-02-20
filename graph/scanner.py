import os
from pathlib import Path
from graph.state import FileMetadata, OrganizerState
from utils.file_utils import compute_md5

SKIP_FOLDERS = {"_organized", "_duplicates", ".git", "__pycache__", "node_modules", ".DS_Store"}

SKIP_EXTENSIONS = {".ds_store", ".tmp", ".temp", ".lnk", ".sys", ".dll", ".exe", ".app"}

def scanner_node(state: OrganizerState) -> dict:
    target = state["target_directory"]
    manifest: list[FileMetadata] = []
    
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        
        for filename in files:
            filepath = os.path.join(root, filename)
            ext = Path(filename).suffix.lower()
            
            if ext in SKIP_EXTENSIONS or filename.startswith("."):
                continue
            
            try:
                size = os.path.getsize(filepath)
                md5 = compute_md5(filepath)

                manifest.append(FileMetadata(
                    original_path=filepath,
                    filename=filename,
                    extension=ext,
                    size_bytes=size,
                    md5_hash=md5
                ))
            except (OSError, PermissionError):
                continue
    return {"file_manifest": manifest}