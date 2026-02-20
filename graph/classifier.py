import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from graph.state import OrganizerState, FileMetadata, ClassifiedFile
from prompts.prompts import CLASSIFIER_SYSTEM_PROMPT, CLASSIFIER_USER_TEMPLATE
from utils.file_utils import format_size

FALLBACK_CATEGORY = "Misc"
FALLBACK_SUBCATEGORY = "Unknown"

load_dotenv()

def _classify_single_file(llm: ChatOpenAI, file_meta: FileMetadata) -> ClassifiedFile:
    """Call the LLM to classify a single file."""
    user_msg = CLASSIFIER_USER_TEMPLATE.format(
        filename=file_meta.filename,
        extension=file_meta.extension,
        size_bytes=format_size(file_meta.size_bytes),
        content_preview=file_meta.content_preview or "(no preview available)",
    )

    try:
        response = llm.invoke([
            SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT),
            HumanMessage(content=user_msg),
        ])

        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw.strip())

        return ClassifiedFile(
            original_path=file_meta.original_path,
            filename=file_meta.filename,
            extension=file_meta.extension,
            size_bytes=file_meta.size_bytes,
            content_preview=file_meta.content_preview,
            md5_hash=file_meta.md5_hash,
            category=data.get("category", FALLBACK_CATEGORY),
            subcategory=data.get("subcategory", FALLBACK_SUBCATEGORY),
            suggested_folder=data.get("suggested_folder", f"{FALLBACK_CATEGORY}/{FALLBACK_SUBCATEGORY}"),
            suggested_name=data.get("suggested_name", file_meta.filename),
            action=data.get("action", "move"),
            confidence=float(data.get("confidence", 0.5)),
        )

    except Exception as e:
        return ClassifiedFile(
            original_path=file_meta.original_path,
            filename=file_meta.filename,
            extension=file_meta.extension,
            size_bytes=file_meta.size_bytes,
            content_preview=file_meta.content_preview,
            md5_hash=file_meta.md5_hash,
            category=FALLBACK_CATEGORY,
            subcategory=FALLBACK_SUBCATEGORY,
            suggested_folder="Misc/Unknown",
            suggested_name=file_meta.filename,
            action="skip",
            confidence=0.0,
        )
        
def classifier_node(state: OrganizerState) -> dict:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )
    
    classified: list[ClassifiedFile] = []
    
    for file_meta in state["file_manifest"]:
        result = _classify_single_file(llm, file_meta)
        classified.append(result)
    
    return {"classified_files": classified}
