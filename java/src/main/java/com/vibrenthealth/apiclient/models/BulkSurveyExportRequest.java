package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

/**
 * Represents a bulk survey export request that can export multiple surveys in one call
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class BulkSurveyExportRequest {

    @JsonProperty("dateFrom")
    private Long dateFrom;

    @JsonProperty("dateTo")
    private Long dateTo;

    @JsonProperty("format")
    private String format = "JSON";

    @JsonProperty("removePII")
    private boolean removePII;

    @JsonProperty("includeLabels")
    private boolean includeLabels;

    @JsonProperty("surveyData")
    private SurveyData surveyData;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class SurveyData {

        @JsonProperty("allSurveys")
        private boolean allSurveys;

        @JsonProperty("surveyIds")
        private List<Integer> surveyIds;
    }
}
