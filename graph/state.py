from typing import TypedDict, Optional, Dict
from pydantic import BaseModel

class FileMetadata(BaseModel):
    original_path: str
    filename: str
    extension: str
    size_bytes: int
    content_preview: str = ""
    md5_hash: str = ""
    
class ClassifiedFile(BaseModel):
    original_path: str
    filename: str
    extension: str
    size_bytes: int
    content_preview: str = ""
    md5_hash: str = ""
    category: str
    sub_category: str
    suggested_folder: str
    suggested_name: str
    action: str
    confidence: float
    
class DuplicateGroup(BaseModel):
    md5_hash: str
    files: list[str]
    keep: str
    remove: list[str]

class ApprovedAction(BaseModel):
    original_path: str
    new_path: str
    action: str

class ActionLog(BaseModel):
    action: str
    original_path: str
    new_path: str
    success: bool
    error: str = ""
    
class OrganizerState(TypedDict):
    target_directory: str
    options: Dict

    file_manifest: list[FileMetadata]
    classified_files: list[ClassifiedFile]
    duplicated_files: list[DuplicateGroup]

    approved_actions: list[ApprovedAction]
    human_approved: bool

    execution_log: list[ActionLog]
    undo_manifest: list[ActionLog]

    summary: dict
    error: Optional[dict]