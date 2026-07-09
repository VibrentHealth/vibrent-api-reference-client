"""
Regression tests for ExportOrchestrator._merge_extracted_files.

Bug: export_metadata.surveys holds plain dicts (via asdict), but the merge
step passed them to exporter.get_item_identifier(), which does attribute
access on model objects -> AttributeError: 'dict' object has no attribute
'platformFormId'. Also, the non-recursive glob matched top-level
manifest_part_N.json files instead of the response JSONs that V2 exports
place in subdirectories.
"""

import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vibrent_api_client.core.orchestrator import ExportOrchestrator
from vibrent_api_client.models import ExportMetadata


def make_orchestrator(tmp_path: Path) -> ExportOrchestrator:
    """Build an orchestrator without running its heavy __init__."""
    orchestrator = object.__new__(ExportOrchestrator)
    orchestrator.logger = logging.getLogger("test")
    orchestrator.export_format = "JSON"
    orchestrator.output_dir = tmp_path
    orchestrator.exporter = None  # merge must not need the exporter
    orchestrator.export_metadata = ExportMetadata(
        export_session_id="test_session",
        start_timestamp="2026-07-09T00:00:00+00:00",
        total_surveys=1,
        successful_exports=2,
        failed_exports=0,
        output_directory=str(tmp_path),
        surveys=[],
        failures=[],
        failed_exports_details=[],
    )
    return orchestrator


def make_item_dict(item_id: str, num_chunks: int) -> dict:
    """Mimic the dict stored in export_metadata.surveys by _request_exports."""
    return {
        "id": 1,
        "name": "Survey-Cancer_History",
        "displayName": "Cancer History",
        "platformFormId": int(item_id),
        "item_identifier": item_id,
        "export_details": [
            {
                "exportId": f"export-{i}",
                "chunk_index": i,
                "total_chunks": num_chunks,
                "sequential_part_number": i + 1,
                "status": "COMPLETED",
                "file_path": f"/tmp/fake_part_{i + 1}.zip",
            }
            for i in range(num_chunks)
        ],
    }


def test_merge_with_dict_items_does_not_raise(tmp_path):
    """The original crash: dict items must not be passed to exporter methods."""
    orchestrator = make_orchestrator(tmp_path)
    responses_dir = tmp_path / "responses" / "1973_Survey-Cancer_Histor"
    responses_dir.mkdir(parents=True)
    (responses_dir / "v45620_resp_part_1.json").write_text(json.dumps([{"a": 1}]))
    (responses_dir / "v45620_resp_part_2.json").write_text(json.dumps([{"b": 2}]))

    orchestrator.export_metadata.surveys.append(make_item_dict("1973", 2))

    orchestrator._merge_extracted_files()  # raised AttributeError before the fix

    merged = tmp_path / "item_1973_merged.json"
    assert merged.exists()
    assert json.loads(merged.read_text()) == [{"a": 1}, {"b": 2}]


def test_merge_skips_manifest_files(tmp_path):
    """Top-level manifest_part_N.json files must not be merged as data."""
    orchestrator = make_orchestrator(tmp_path)
    (tmp_path / "manifest_part_1.json").write_text(json.dumps({"manifest": 1}))
    (tmp_path / "manifest_part_2.json").write_text(json.dumps({"manifest": 2}))
    responses_dir = tmp_path / "responses" / "1973_Survey-Cancer_Histor"
    responses_dir.mkdir(parents=True)
    (responses_dir / "v45620_resp_part_1.json").write_text(json.dumps([{"a": 1}]))
    (responses_dir / "v45620_resp_part_2.json").write_text(json.dumps([{"b": 2}]))

    orchestrator.export_metadata.surveys.append(make_item_dict("1973", 2))

    orchestrator._merge_extracted_files()

    merged = tmp_path / "item_1973_merged.json"
    assert json.loads(merged.read_text()) == [{"a": 1}, {"b": 2}]


def test_merge_scopes_parts_to_item(tmp_path):
    """Parts from another item exported in the same run must not be mixed in."""
    orchestrator = make_orchestrator(tmp_path)
    for item_id, payload in (("1973", "cancer"), ("50", "other")):
        item_dir = tmp_path / "responses" / f"{item_id}_Survey"
        item_dir.mkdir(parents=True)
        (item_dir / "resp_part_1.json").write_text(json.dumps([{payload: 1}]))
        (item_dir / "resp_part_2.json").write_text(json.dumps([{payload: 2}]))

    orchestrator.export_metadata.surveys.append(make_item_dict("1973", 2))
    orchestrator.export_metadata.surveys.append(make_item_dict("50", 2))

    orchestrator._merge_extracted_files()

    assert json.loads((tmp_path / "item_1973_merged.json").read_text()) == [
        {"cancer": 1},
        {"cancer": 2},
    ]
    assert json.loads((tmp_path / "item_50_merged.json").read_text()) == [
        {"other": 1},
        {"other": 2},
    ]


def test_merge_skipped_for_single_export(tmp_path):
    orchestrator = make_orchestrator(tmp_path)
    orchestrator.export_metadata.surveys.append(make_item_dict("1973", 1))

    orchestrator._merge_extracted_files()

    assert not list(tmp_path.glob("*_merged.json"))
