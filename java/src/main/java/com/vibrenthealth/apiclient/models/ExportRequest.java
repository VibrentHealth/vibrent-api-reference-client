package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Map;

/**
 * Represents an export request
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ExportRequest {

    @JsonProperty("dateFrom")
    private Long dateFrom;

    @JsonProperty("dateTo")
    private Long dateTo;

    private String format = "JSON";

    public static ExportRequest fromMap(Map<String, Object> data) {
        ExportRequest request = new ExportRequest();
        request.setDateFrom(data.get("dateFrom") != null ? ((Number) data.get("dateFrom")).longValue() : null);
        request.setDateTo(data.get("dateTo") != null ? ((Number) data.get("dateTo")).longValue() : null);
        request.setFormat((String) data.getOrDefault("format", "JSON"));
        return request;
    }
} 