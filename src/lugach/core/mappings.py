import json
from typing import Dict, Optional
from lugach.config import ROOT_DIR

MAPPING_FILE = ROOT_DIR / ".course_id_mappings.json"


def _load_mappings() -> Dict[str, str]:
    """
    Load all stored Canvas -> Top Hat course ID mappings.
    """
    if not MAPPING_FILE.exists():
        return {}

    with MAPPING_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _save_mappings(mappings: Dict[str, str]) -> None:
    """
    Persist all Canvas -> Top Hat course ID mappings to disk.
    """
    MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MAPPING_FILE.open("w", encoding="utf-8") as f:
        json.dump(mappings, f, indent=2, sort_keys=True)


def save_course_mapping(
    canvas_course_id: int,
    tophat_course_id: int,
) -> None:
    """
    Save or update a mapping between a Canvas course ID and a Top Hat course ID.
    """
    mappings = _load_mappings()
    mappings[str(canvas_course_id)] = str(tophat_course_id)
    _save_mappings(mappings)


def get_tophat_course_id(
    canvas_course_id: int,
) -> Optional[int]:
    """
    Retrieve the Top Hat course ID for a given Canvas course ID.

    Returns None if no mapping exists.
    """
    mappings = _load_mappings()
    value = mappings.get(str(canvas_course_id))
    return int(value) if value is not None else None


def delete_course_mapping(
    canvas_course_id: int,
) -> None:
    """
    Delete a Canvas -> Top Hat course mapping if it exists.
    """
    mappings = _load_mappings()
    removed = mappings.pop(str(canvas_course_id), None) is not None
    if removed:
        _save_mappings(mappings)


def get_all_mappings() -> Dict[int, int]:
    """
    Return all Canvas -> Top Hat course mappings as integers.
    """
    mappings = _load_mappings()
    return {
        int(cv_course_id): int(th_course_id)
        for cv_course_id, th_course_id in mappings.items()
    }
