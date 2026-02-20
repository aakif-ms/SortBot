from graph.state import OrganizerState, FileMetadata
from utils.file_utils import read_content_preview

def content_reader_node(state: OrganizerState) -> dict:
    options = state.get("options", {})
    should_read = options.get("read_content", True)

    updated_manifest: list[FileMetadata] = []
    
    for file_meta in state["file_manifest"]:
        if should_read:
            preview = read_content_preview(file_meta.original_path)
        else:
            preview = ""

        updated = file_meta.model_copy(update={"content_preview": preview})
        updated_manifest.append(updated)

    return {"file_manifest": updated_manifest}