package com.vibrenthealth.apiclient.models;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * Tests for the Survey V2 {@code responseKey} option (AC-157602).
 *
 * <p>{@code VARIABLE_NAME} (default) keys each {@code qRes} entry by the question's
 * variable name, {@code QUESTION_ID} keys it by question ID. The server applies it
 * to JSON exports only.
 */
class WideFormatReportRequestTest {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void defaultsToVariableName() throws Exception {
        WideFormatReportRequest request = new WideFormatReportRequest();

        assertEquals("VARIABLE_NAME", request.getResponseKey());
        assertEquals("VARIABLE_NAME", toJson(request).get("responseKey").asText());
    }

    @Test
    void sendsQuestionIdWhenSet() throws Exception {
        WideFormatReportRequest request = new WideFormatReportRequest();
        request.setFileType("JSON");
        request.setResponseKey("QUESTION_ID");

        assertEquals("QUESTION_ID", toJson(request).get("responseKey").asText());
    }

    @Test
    void fromMapWithoutResponseKeyDefaultsToVariableName() {
        WideFormatReportRequest request = WideFormatReportRequest.fromMap(Map.of("fileType", "JSON"));

        assertEquals("VARIABLE_NAME", request.getResponseKey());
    }

    @Test
    void fromMapReadsResponseKey() {
        WideFormatReportRequest request =
                WideFormatReportRequest.fromMap(Map.of("fileType", "JSON", "responseKey", "QUESTION_ID"));

        assertEquals("QUESTION_ID", request.getResponseKey());
    }

    @Test
    void otherFieldsKeepTheirDefaults() throws Exception {
        JsonNode body = toJson(new WideFormatReportRequest());

        assertEquals("CSV", body.get("fileType").asText());
        assertEquals("VALUE_AND_TEXT", body.get("choiceValueFormat").asText());
        assertEquals("REAL_ONLY", body.get("userType").asText());
        assertEquals(true, body.get("combineValuesForMultipleChoices").asBoolean());
    }

    private JsonNode toJson(WideFormatReportRequest request) throws Exception {
        return objectMapper.readTree(objectMapper.writeValueAsString(request));
    }
}
