package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Map;
import java.util.Objects;

/**
 * Represents an export request
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ExportRequest {
    
    @JsonProperty("dateFrom")
    private long dateFrom;
    
    @JsonProperty("dateTo")
    private long dateTo;
    
    private String format = "JSON";

    public static ExportRequest fromMap(Map<String, Object> data) {
        ExportRequest request = new ExportRequest();
        request.setDateFrom(((Number) data.getOrDefault("dateFrom", 0L)).longValue());
        request.setDateTo(((Number) data.getOrDefault("dateTo", 0L)).longValue());
        request.setFormat((String) data.getOrDefault("format", "JSON"));
        return request;
    }
} 