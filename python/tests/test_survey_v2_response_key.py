"""
Tests for the Survey V2 ``response_key`` option (AC-157602).

``response_key`` in the ``survey_v2_export`` config section is sent to the API
as ``responseKey``: ``VARIABLE_NAME`` (default) keys each ``qRes`` entry by the
question's variable name, ``QUESTION_ID`` keys it by question ID. The server
applies it to JSON exports only.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vibrent_api_client.exporters.survey_v2_exporter import SurveyV2Exporter
from vibrent_api_client.models import Survey, WideFormatReportRequest

DATE_RANGE = {"start_time": 1_700_000_000_000, "end_time": 1_700_086_400_000}

# The request body every Survey V2 export sent before response_key existed,
# built from an empty survey_v2_export section.
PRE_RESPONSE_KEY_BODY = {
    "fileType": "CSV",
    "removePII": False,
    "completedOnly": True,
    "includeWithdrawnUser": True,
    "combineValuesForMultipleChoices": True,
    "choiceValueFormat": "VALUE_AND_TEXT",
    "userType": "REAL_ONLY",
    "dateFrom": DATE_RANGE["start_time"],
    "dateTo": DATE_RANGE["end_time"],
}


class StubConfigManager:
    """Returns a fixed survey_v2_export section."""

    def __init__(self, section):
        self.section = section

    def get_export_config(self, export_type):
        assert export_type == "survey_v2"
        return self.section


def build_request_body(section):
    exporter = SurveyV2Exporter(client=None, config_manager=StubConfigManager(section))
    survey = Survey(id=1, name="Activate Kit", displayName="Activate Kit", platformFormId=1829)
    request = exporter.create_export_request(survey, DATE_RANGE)
    return request.to_dict()


# ── WideFormatReportRequest model ────────────────────────────────────────────

def test_request_defaults_to_variable_name():
    assert WideFormatReportRequest().responseKey == "VARIABLE_NAME"
    assert WideFormatReportRequest().to_dict()["responseKey"] == "VARIABLE_NAME"


def test_request_sends_question_id_when_set():
    request = WideFormatReportRequest(fileType="JSON", responseKey="QUESTION_ID")
    assert request.to_dict()["responseKey"] == "QUESTION_ID"


def test_from_dict_defaults_and_reads_response_key():
    assert WideFormatReportRequest.from_dict({}).responseKey == "VARIABLE_NAME"
    assert WideFormatReportRequest.from_dict({"responseKey": "QUESTION_ID"}).responseKey == "QUESTION_ID"


# ── SurveyV2Exporter: yaml -> request ────────────────────────────────────────

def test_without_response_key_request_is_unchanged_apart_from_default():
    body = build_request_body({})

    assert body.pop("responseKey") == "VARIABLE_NAME"
    assert body == PRE_RESPONSE_KEY_BODY


def test_response_key_question_id_reaches_request():
    body = build_request_body({"file_type": "JSON", "response_key": "QUESTION_ID"})

    assert body["responseKey"] == "QUESTION_ID"
    assert body["fileType"] == "JSON"


def test_explicit_variable_name_reaches_request():
    body = build_request_body({"file_type": "JSON", "response_key": "VARIABLE_NAME"})

    assert body["responseKey"] == "VARIABLE_NAME"


def test_question_id_with_csv_warns_that_server_ignores_it(caplog):
    with caplog.at_level(logging.WARNING, logger="SurveyV2Exporter"):
        body = build_request_body({"file_type": "CSV", "response_key": "QUESTION_ID"})

    # Still sent as configured; the server decides, the client only warns.
    assert body["responseKey"] == "QUESTION_ID"
    assert any("response_key" in r.getMessage() and "JSON" in r.getMessage() for r in caplog.records)


def test_question_id_with_json_does_not_warn(caplog):
    with caplog.at_level(logging.WARNING, logger="SurveyV2Exporter"):
        build_request_body({"file_type": "JSON", "response_key": "QUESTION_ID"})

    assert not caplog.records
