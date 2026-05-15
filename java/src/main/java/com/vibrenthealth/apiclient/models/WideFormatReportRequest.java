package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

/**
 * Represents a wide-format (V2) survey export request.
 * Used with POST /api/ext/export/v2/survey/{surveyId}/request
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class WideFormatReportRequest {

    /** Ignored by server — overridden from the {surveyId} path parameter. */
    @JsonProperty("formIds")
    private List<Integer> formIds;

    /** Valid values: "CSV", "JSON" */
    @JsonProperty("fileType")
    private String fileType = "CSV";

    @JsonProperty("dateFrom")
    private Long dateFrom;

    @JsonProperty("dateTo")
    private Long dateTo;

    @JsonProperty("removePII")
    private boolean removePII = false;

    @JsonProperty("combineValuesForMultipleChoices")
    private boolean combineValuesForMultipleChoices = true;

    /** Valid values: "VALUE_ONLY", "TEXT_ONLY", "VALUE_AND_TEXT" */
    @JsonProperty("choiceValueFormat")
    private String choiceValueFormat = "VALUE_AND_TEXT";

    @JsonProperty("completedOnly")
    private boolean completedOnly = true;

    @JsonProperty("includeWithdrawnUser")
    private boolean includeWithdrawnUser = true;

    /** Valid values: "REAL_ONLY", "TEST_ONLY", "ALL_USERS" */
    @JsonProperty("userType")
    private String userType = "REAL_ONLY";

    @SuppressWarnings("unchecked")
    public static WideFormatReportRequest fromMap(Map<String, Object> data) {
        WideFormatReportRequest request = new WideFormatReportRequest();
        request.setFormIds((List<Integer>) data.get("formIds"));
        request.setFileType((String) data.getOrDefault("fileType", "CSV"));
        request.setDateFrom(data.get("dateFrom") != null ? ((Number) data.get("dateFrom")).longValue() : null);
        request.setDateTo(data.get("dateTo") != null ? ((Number) data.get("dateTo")).longValue() : null);
        request.setRemovePII((Boolean) data.getOrDefault("removePII", false));
        request.setCombineValuesForMultipleChoices((Boolean) data.getOrDefault("combineValuesForMultipleChoices", true));
        request.setChoiceValueFormat((String) data.getOrDefault("choiceValueFormat", "VALUE_AND_TEXT"));
        request.setCompletedOnly((Boolean) data.getOrDefault("completedOnly", true));
        request.setIncludeWithdrawnUser((Boolean) data.getOrDefault("includeWithdrawnUser", true));
        request.setUserType((String) data.getOrDefault("userType", "REAL_ONLY"));
        return request;
    }
}
