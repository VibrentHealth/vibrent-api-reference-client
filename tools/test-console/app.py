"""
Vibrent Export API Test Console

Interactive Streamlit UI to test all export API endpoints using the Python SDK.
Run: streamlit run app.py
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta

import requests
import streamlit as st
from requests.auth import HTTPBasicAuth

# Add SDK to path
SDK_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "python", "src")
sys.path.insert(0, SDK_PATH)

from vibrent_api_client.core.constants import APIEndpoints
from vibrent_api_client.models import (
    CommunicationEventsExportRequest,
    DeviceDataExportRequest,
    EHRExportRequest,
    EHRMultiExportRequest,
    ExportRequest,
    ParticipantProfilesExportRequest,
    WideFormatReportRequest,
)

st.set_page_config(page_title="Vibrent Export API Test Console", layout="wide")
st.title("Vibrent Export API Test Console")


# ── Helpers ──────────────────────────────────────────────────────────────────

def epoch_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def make_authenticated_request(method, endpoint, body=None):
    if "access_token" not in st.session_state or not st.session_state.access_token:
        st.error("Not authenticated. Please authenticate first.")
        return None

    url = st.session_state.base_url + endpoint
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

    start = time.time()
    try:
        if method == "POST":
            resp = requests.post(url, json=body, headers=headers, timeout=60)
        else:
            resp = requests.get(url, headers=headers, timeout=60)
        elapsed = time.time() - start
        return resp, elapsed, url, body
    except requests.RequestException as e:
        st.error(f"Request failed: {e}")
        return None


def show_request_response(result, label="Export"):
    if result is None:
        return None
    resp, elapsed, url, body = result

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Status Code", resp.status_code)
    with col2:
        st.metric("Response Time", f"{elapsed:.2f}s")

    if resp.status_code == 200:
        try:
            data = resp.json()
            st.success(f"{label} successful")
            st.json(data)
            return data
        except Exception:
            st.warning("Response is not JSON")
            st.text(resp.text[:2000])
    else:
        st.error(f"HTTP {resp.status_code}")
        try:
            st.json(resp.json())
        except Exception:
            st.text(resp.text[:2000])

    with st.expander("Raw Request / Response"):
        st.markdown(f"**URL:** `{url}`")
        if body:
            st.markdown("**Request Body:**")
            st.json(body)
        st.markdown("**Response Headers:**")
        st.json(dict(resp.headers))

    return None


def parse_ids_long(text):
    if not text or not text.strip():
        return None
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def parse_ids_str(text):
    if not text or not text.strip():
        return None
    return [x.strip() for x in text.split(",") if x.strip()]


def parse_str_list(text):
    if not text or not text.strip():
        return None
    return [x.strip() for x in text.split(",") if x.strip()]


# ── Sidebar: Authentication ──────────────────────────────────────────────────

with st.sidebar:
    st.header("Authentication")

    env = st.selectbox("Environment", ["staging", "production", "custom"])

    if env == "custom":
        base_url = st.text_input("Base URL", placeholder="https://your-api.example.com")
        token_url = st.text_input("Token URL", placeholder="https://your-auth.example.com/oauth/token")
    else:
        base_url = st.text_input("Base URL", placeholder=f"https://{env}-api.vibrenthealth.com")
        token_url = st.text_input("Token URL", placeholder=f"https://{env}-auth.vibrenthealth.com/oauth/token")

    client_id = st.text_input("Client ID", type="default")
    client_secret = st.text_input("Client Secret", type="password")

    if st.button("Authenticate", type="primary", use_container_width=True):
        if not all([base_url, token_url, client_id, client_secret]):
            st.error("All fields are required")
        else:
            with st.spinner("Authenticating..."):
                try:
                    resp = requests.post(
                        token_url,
                        data={"grant_type": "client_credentials"},
                        auth=HTTPBasicAuth(client_id, client_secret),
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        token_data = resp.json()
                        st.session_state.access_token = token_data["access_token"]
                        st.session_state.token_expires = time.time() + token_data.get("expires_in", 3600)
                        st.session_state.base_url = base_url.rstrip("/")
                        st.success("Authenticated")
                    else:
                        st.error(f"Auth failed: HTTP {resp.status_code}")
                        try:
                            st.json(resp.json())
                        except Exception:
                            st.text(resp.text[:500])
                except requests.RequestException as e:
                    st.error(f"Connection error: {e}")

    st.divider()
    if "access_token" in st.session_state and st.session_state.access_token:
        remaining = int(st.session_state.token_expires - time.time())
        if remaining > 0:
            st.success(f"Token valid ({remaining}s remaining)")
        else:
            st.warning("Token expired — re-authenticate")
            st.session_state.access_token = None
    else:
        st.info("Not authenticated")

    st.divider()
    st.caption("SDK Path: " + SDK_PATH)


# ── Main tabs ────────────────────────────────────────────────────────────────

tabs = st.tabs([
    "List Surveys",
    "Survey V1",
    "Survey V2 (Wide)",
    "EHR (Single)",
    "EHR (Multi)",
    "Device (Single)",
    "Device (Multi)",
    "Profiles",
    "Comms Events",
    "Export Status",
    "Download",
])


# ── Tab: List Surveys ────────────────────────────────────────────────────────

with tabs[0]:
    st.subheader("List Available Surveys")
    st.caption(f"GET {APIEndpoints.SURVEYS}")

    if st.button("Fetch Surveys", key="fetch_surveys"):
        result = make_authenticated_request("GET", APIEndpoints.SURVEYS)
        if result:
            data = show_request_response(result, "Surveys fetch")
            if data and isinstance(data, list):
                st.markdown(f"**{len(data)} surveys found**")
                for s in data:
                    st.markdown(
                        f"- **ID {s.get('id', '?')}** / platformFormId={s.get('platformFormId', '?')} "
                        f"— {s.get('displayName', s.get('name', 'Unknown'))}"
                    )


# ── Tab: Survey V1 ───────────────────────────────────────────────────────────

with tabs[1]:
    st.subheader("Survey V1 Export")

    mode = st.radio("Mode", ["Single Survey", "Multi Survey"], key="sv1_mode", horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        sv1_date_from = st.date_input("Date From", value=datetime.now() - timedelta(days=7), key="sv1_df")
    with col2:
        sv1_date_to = st.date_input("Date To", value=datetime.now(), key="sv1_dt")

    sv1_format = st.selectbox("Format", ["JSON", "CSV"], key="sv1_fmt")

    if mode == "Single Survey":
        sv1_survey_id = st.number_input("Survey ID", min_value=1, step=1, key="sv1_sid")
        endpoint = APIEndpoints.EXPORT_REQUEST.format(survey_id=int(sv1_survey_id))
    else:
        sv1_survey_ids_text = st.text_input("Survey IDs (comma-separated)", key="sv1_sids", placeholder="123, 456, 789")
        endpoint = "/api/ext/export/survey/request"

    st.caption(f"POST {endpoint}")

    if st.button("Request Survey V1 Export", key="sv1_submit"):
        req = ExportRequest(
            dateFrom=epoch_ms(datetime.combine(sv1_date_from, datetime.min.time())),
            dateTo=epoch_ms(datetime.combine(sv1_date_to, datetime.max.time())),
            format=sv1_format,
        )
        body = req.to_dict()
        if mode == "Multi Survey":
            ids = parse_ids_long(sv1_survey_ids_text)
            body["surveyData"] = {"allSurveys": ids is None, "surveyIds": ids or []}
        result = make_authenticated_request("POST", endpoint, body)
        show_request_response(result, "Survey V1 Export")


# ── Tab: Survey V2 (Wide Format) ─────────────────────────────────────────────

with tabs[2]:
    st.subheader("Survey V2 Export (Wide Format)")

    sv2_survey_id = st.number_input("Survey ID", min_value=1, step=1, key="sv2_sid")

    col1, col2 = st.columns(2)
    with col1:
        sv2_date_from = st.date_input("Date From (optional)", value=None, key="sv2_df")
    with col2:
        sv2_date_to = st.date_input("Date To (optional)", value=None, key="sv2_dt")

    sv2_file_type = st.selectbox("File Type", ["CSV", "JSON"], key="sv2_ft")
    sv2_remove_pii = st.checkbox("Remove PII", value=False, key="sv2_pii")
    sv2_completed_only = st.checkbox("Completed Only", value=True, key="sv2_co")
    sv2_include_withdrawn = st.checkbox("Include Withdrawn Users", value=True, key="sv2_iw")
    sv2_combine_mc = st.checkbox("Combine Values for Multiple Choices", value=True, key="sv2_mc")
    sv2_choice_format = st.selectbox(
        "Choice Value Format", ["VALUE_AND_TEXT", "VALUE_ONLY", "TEXT_ONLY"], key="sv2_cvf"
    )
    sv2_user_type = st.selectbox("User Type", ["REAL_ONLY", "TEST_ONLY", "ALL_USERS"], key="sv2_ut")

    endpoint = APIEndpoints.EXPORT_REQUEST_V2.format(survey_id=int(sv2_survey_id))
    st.caption(f"POST {endpoint}")

    if st.button("Request Survey V2 Export", key="sv2_submit"):
        req = WideFormatReportRequest(
            dateFrom=epoch_ms(datetime.combine(sv2_date_from, datetime.min.time())) if sv2_date_from else 0,
            dateTo=epoch_ms(datetime.combine(sv2_date_to, datetime.max.time())) if sv2_date_to else 0,
            fileType=sv2_file_type,
            removePII=sv2_remove_pii,
            completedOnly=sv2_completed_only,
            includeWithdrawnUser=sv2_include_withdrawn,
            combineValuesForMultipleChoices=sv2_combine_mc,
            choiceValueFormat=sv2_choice_format,
            userType=sv2_user_type,
        )
        result = make_authenticated_request("POST", endpoint, req.to_dict())
        show_request_response(result, "Survey V2 Export")


# ── Tab: EHR (Single) ────────────────────────────────────────────────────────

with tabs[3]:
    st.subheader("EHR Export (Single Participant)")

    ehr1_pid = st.number_input("Participant ID", min_value=1, step=1, key="ehr1_pid")

    col1, col2 = st.columns(2)
    with col1:
        ehr1_date_from = st.date_input("Date From (optional)", value=None, key="ehr1_df")
    with col2:
        ehr1_date_to = st.date_input("Date To (optional)", value=None, key="ehr1_dt")

    endpoint = APIEndpoints.EHR_EXPORT_REQUEST.format(participant_id=int(ehr1_pid))
    st.caption(f"POST {endpoint}")

    if st.button("Request EHR Export", key="ehr1_submit"):
        req = EHRExportRequest(
            dateFrom=epoch_ms(datetime.combine(ehr1_date_from, datetime.min.time())) if ehr1_date_from else None,
            dateTo=epoch_ms(datetime.combine(ehr1_date_to, datetime.max.time())) if ehr1_date_to else None,
        )
        result = make_authenticated_request("POST", endpoint, req.to_dict())
        show_request_response(result, "EHR Export")


# ── Tab: EHR (Multi) ─────────────────────────────────────────────────────────

with tabs[4]:
    st.subheader("EHR Export (Multi-Participant)")

    col1, col2 = st.columns(2)
    with col1:
        ehrm_date_from = st.date_input("Date From", value=datetime.now() - timedelta(days=7), key="ehrm_df")
    with col2:
        ehrm_date_to = st.date_input("Date To", value=datetime.now(), key="ehrm_dt")

    ehrm_pids = st.text_area(
        "Participant IDs (comma-separated, integers — leave empty for all)",
        key="ehrm_pids",
        placeholder="12345, 67890, 11111",
    )
    ehrm_manifest = st.checkbox("Manifest Only", value=False, key="ehrm_mo")

    st.caption(f"POST {APIEndpoints.EHR_MULTI_EXPORT_REQUEST}")

    if st.button("Request Multi-EHR Export", key="ehrm_submit"):
        req = EHRMultiExportRequest(
            dateFrom=epoch_ms(datetime.combine(ehrm_date_from, datetime.min.time())),
            dateTo=epoch_ms(datetime.combine(ehrm_date_to, datetime.max.time())),
            participantIds=parse_ids_long(ehrm_pids),
            manifestOnly=ehrm_manifest,
        )
        result = make_authenticated_request("POST", APIEndpoints.EHR_MULTI_EXPORT_REQUEST, req.to_dict())
        show_request_response(result, "Multi-EHR Export")


# ── Tab: Device (Single) ─────────────────────────────────────────────────────

with tabs[5]:
    st.subheader("Device Data Export (Single Participant)")

    dev1_pid = st.number_input("Participant ID", min_value=1, step=1, key="dev1_pid")

    col1, col2 = st.columns(2)
    with col1:
        dev1_date_from = st.date_input("Date From (optional)", value=None, key="dev1_df")
    with col2:
        dev1_date_to = st.date_input("Date To (optional)", value=None, key="dev1_dt")

    dev1_device_types = st.multiselect(
        "Device Types", ["FITBIT", "GARMIN", "APPLE_HEALTHKIT"], key="dev1_devt"
    )
    dev1_data_types = st.multiselect(
        "Data Types",
        ["SLEEP", "STEPS", "HEART_RATE", "ACTIVITY", "DISTANCE", "RESPIRATORY", "STRESS", "DAILY_SUMMARY"],
        key="dev1_dat",
    )
    dev1_manifest = st.checkbox("Manifest Only", value=False, key="dev1_mo")

    endpoint = APIEndpoints.DEVICE_EXPORT_REQUEST.format(participant_id=int(dev1_pid))
    st.caption(f"POST {endpoint}")

    if st.button("Request Device Export", key="dev1_submit"):
        req = DeviceDataExportRequest(
            dateFrom=epoch_ms(datetime.combine(dev1_date_from, datetime.min.time())) if dev1_date_from else None,
            dateTo=epoch_ms(datetime.combine(dev1_date_to, datetime.max.time())) if dev1_date_to else None,
            deviceTypes=dev1_device_types or None,
            dataTypes=dev1_data_types or None,
            manifestOnly=dev1_manifest,
        )
        result = make_authenticated_request("POST", endpoint, req.to_dict())
        show_request_response(result, "Device Export")


# ── Tab: Device (Multi) ──────────────────────────────────────────────────────

with tabs[6]:
    st.subheader("Device Data Export (Multi-Participant)")

    col1, col2 = st.columns(2)
    with col1:
        devm_date_from = st.date_input("Date From", value=datetime.now() - timedelta(days=1), key="devm_df")
    with col2:
        devm_date_to = st.date_input("Date To", value=datetime.now(), key="devm_dt")

    devm_pids = st.text_area(
        "Participant IDs (comma-separated, integers — leave empty for all)",
        key="devm_pids",
        placeholder="12345, 67890",
    )
    devm_device_types = st.multiselect(
        "Device Types", ["FITBIT", "GARMIN", "APPLE_HEALTHKIT"], key="devm_devt"
    )
    devm_data_types = st.multiselect(
        "Data Types",
        ["SLEEP", "STEPS", "HEART_RATE", "ACTIVITY", "DISTANCE", "RESPIRATORY", "STRESS", "DAILY_SUMMARY"],
        key="devm_dat",
    )
    devm_manifest = st.checkbox("Manifest Only", value=False, key="devm_mo")

    st.caption(f"POST {APIEndpoints.DEVICE_MULTI_EXPORT_REQUEST}")

    if st.button("Request Multi-Device Export", key="devm_submit"):
        req = DeviceDataExportRequest(
            dateFrom=epoch_ms(datetime.combine(devm_date_from, datetime.min.time())),
            dateTo=epoch_ms(datetime.combine(devm_date_to, datetime.max.time())),
            participantIds=parse_ids_long(devm_pids),
            deviceTypes=devm_device_types or None,
            dataTypes=devm_data_types or None,
            manifestOnly=devm_manifest,
        )
        result = make_authenticated_request("POST", APIEndpoints.DEVICE_MULTI_EXPORT_REQUEST, req.to_dict())
        show_request_response(result, "Multi-Device Export")


# ── Tab: Participant Profiles ─────────────────────────────────────────────────

with tabs[7]:
    st.subheader("Participant Profiles Export")

    col1, col2 = st.columns(2)
    with col1:
        pp_date_from = st.date_input("Date From (optional)", value=None, key="pp_df")
    with col2:
        pp_date_to = st.date_input("Date To (optional)", value=None, key="pp_dt")

    pp_pids = st.text_area(
        "Participant IDs (comma-separated, strings — leave empty for all)",
        key="pp_pids",
        placeholder="12345, 67890",
    )

    st.caption(f"POST {APIEndpoints.PARTICIPANT_PROFILES_EXPORT_REQUEST}")

    if st.button("Request Profiles Export", key="pp_submit"):
        req = ParticipantProfilesExportRequest(
            dateFrom=epoch_ms(datetime.combine(pp_date_from, datetime.min.time())) if pp_date_from else None,
            dateTo=epoch_ms(datetime.combine(pp_date_to, datetime.max.time())) if pp_date_to else None,
            participantIds=parse_ids_str(pp_pids),
        )
        result = make_authenticated_request("POST", APIEndpoints.PARTICIPANT_PROFILES_EXPORT_REQUEST, req.to_dict())
        show_request_response(result, "Profiles Export")


# ── Tab: Communication Events ─────────────────────────────────────────────────

with tabs[8]:
    st.subheader("Communication Events Export")

    col1, col2 = st.columns(2)
    with col1:
        ce_date_from = st.date_input("Date From", value=datetime.now() - timedelta(days=1), key="ce_df")
    with col2:
        ce_date_to = st.date_input("Date To", value=datetime.now(), key="ce_dt")

    ce_pids = st.text_area(
        "Participant IDs (comma-separated, strings — leave empty for all)",
        key="ce_pids",
        placeholder="12345, 67890",
    )
    ce_manifest = st.checkbox("Manifest Only", value=False, key="ce_mo")

    ce_event_sources = st.multiselect("Event Sources", ["ITERABLE", "SES", "TWILIO"], key="ce_es")

    ce_event_types = st.multiselect(
        "Event Types",
        [
            "EMAIL_SENT", "EMAIL_DELIVERY", "EMAIL_OPEN", "EMAIL_CLICK",
            "EMAIL_BOUNCE", "EMAIL_COMPLAINT", "EMAIL_UNSUBSCRIBE", "EMAIL_SEND_SKIP",
            "SMS_SEND", "SMS_DELIVERED", "SMS_BOUNCE", "SMS_SEND_SKIP",
        ],
        key="ce_et",
    )

    st.caption(f"POST {APIEndpoints.COMMUNICATION_EVENTS_EXPORT_REQUEST}")

    if st.button("Request Comms Export", key="ce_submit"):
        req = CommunicationEventsExportRequest(
            dateFrom=epoch_ms(datetime.combine(ce_date_from, datetime.min.time())),
            dateTo=epoch_ms(datetime.combine(ce_date_to, datetime.max.time())),
            participantIds=parse_ids_str(ce_pids),
            manifestOnly=ce_manifest,
            eventSources=ce_event_sources or None,
            eventTypes=ce_event_types or None,
        )
        result = make_authenticated_request("POST", APIEndpoints.COMMUNICATION_EVENTS_EXPORT_REQUEST, req.to_dict())
        show_request_response(result, "Comms Export")


# ── Tab: Export Status ────────────────────────────────────────────────────────

with tabs[9]:
    st.subheader("Check Export Status")

    status_export_id = st.text_input("Export ID", key="status_eid", placeholder="abc-123-def-456")
    auto_poll = st.checkbox("Auto-poll until complete", value=False, key="status_poll")
    poll_interval = st.slider("Poll interval (seconds)", 5, 60, 10, key="status_pi") if auto_poll else 10

    if status_export_id:
        endpoint = APIEndpoints.EXPORT_STATUS.format(export_id=status_export_id)
        st.caption(f"GET {endpoint}")

    if st.button("Check Status", key="status_submit") and status_export_id:
        endpoint = APIEndpoints.EXPORT_STATUS.format(export_id=status_export_id)

        if auto_poll:
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            attempt = 0
            max_attempts = 120

            while attempt < max_attempts:
                result = make_authenticated_request("GET", endpoint)
                if result is None:
                    break

                resp, elapsed, url, body = result
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status", "UNKNOWN")
                    status_placeholder.markdown(
                        f"**Attempt {attempt + 1}** | Status: `{status}` | "
                        f"Export ID: `{status_export_id}`"
                    )
                    progress_bar.progress(min((attempt + 1) / 20, 1.0))

                    if status in ("COMPLETED", "FAILED", "NO_DATA", "EXPIRED"):
                        st.json(data)
                        if status == "COMPLETED":
                            st.success("Export completed")
                        elif status == "FAILED":
                            st.error(f"Export failed: {data.get('failureReason', 'Unknown')}")
                        else:
                            st.warning(f"Export ended with status: {status}")
                        break
                else:
                    st.error(f"HTTP {resp.status_code}")
                    break

                attempt += 1
                time.sleep(poll_interval)
            else:
                st.warning("Max polling attempts reached")
        else:
            result = make_authenticated_request("GET", endpoint)
            show_request_response(result, "Export Status")


# ── Tab: Download ─────────────────────────────────────────────────────────────

with tabs[10]:
    st.subheader("Download Export")

    dl_export_id = st.text_input("Export ID", key="dl_eid", placeholder="abc-123-def-456")

    if dl_export_id:
        endpoint = APIEndpoints.EXPORT_DOWNLOAD.format(export_id=dl_export_id)
        st.caption(f"GET {endpoint}")

    if st.button("Download", key="dl_submit") and dl_export_id:
        endpoint = APIEndpoints.EXPORT_DOWNLOAD.format(export_id=dl_export_id)

        with st.spinner("Downloading..."):
            if "access_token" not in st.session_state or not st.session_state.access_token:
                st.error("Not authenticated")
            else:
                url = st.session_state.base_url + endpoint
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

                try:
                    resp = requests.get(url, headers=headers, timeout=300, stream=True)
                    if resp.status_code == 200:
                        content_disp = resp.headers.get("Content-Disposition", "")
                        if "filename=" in content_disp:
                            filename = content_disp.split("filename=")[1].strip('"')
                        else:
                            filename = f"export_{dl_export_id}.zip"

                        content = resp.content
                        st.success(f"Downloaded: {filename} ({len(content):,} bytes)")
                        st.download_button(
                            label=f"Save {filename}",
                            data=content,
                            file_name=filename,
                            mime="application/zip",
                        )
                    else:
                        st.error(f"HTTP {resp.status_code}")
                        st.text(resp.text[:1000])
                except requests.RequestException as e:
                    st.error(f"Download failed: {e}")
