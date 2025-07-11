package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * Metadata for the export session
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ExportMetadata {
    
    @JsonProperty("export_session_id")
    private String exportSessionId;
    
    @JsonProperty("start_timestamp")
    private String startTimestamp;
    
    @JsonProperty("total_surveys")
    private int totalSurveys;
    
    @JsonProperty("successful_exports")
    private int successfulExports;
    
    @JsonProperty("failed_exports")
    private int failedExports;
    
    @JsonProperty("output_directory")
    private String outputDirectory;
    
    private List<Map<String, Object>> surveys = new ArrayList<>();
    
    private List<Map<String, Object>> failures = new ArrayList<>();
    
    @JsonProperty("end_timestamp")
    private String endTimestamp;
    
    @JsonProperty("duration_seconds")
    private Double durationSeconds;

    public static ExportMetadata fromMap(Map<String, Object> data) {
        ExportMetadata metadata = new ExportMetadata();
        metadata.setExportSessionId((String) data.getOrDefault("export_session_id", ""));
        metadata.setStartTimestamp((String) data.getOrDefault("start_timestamp", ""));
        metadata.setTotalSurveys(((Number) data.getOrDefault("total_surveys", 0)).intValue());
        metadata.setSuccessfulExports(((Number) data.getOrDefault("successful_exports", 0)).intValue());
        metadata.setFailedExports(((Number) data.getOrDefault("failed_exports", 0)).intValue());
        metadata.setOutputDirectory((String) data.getOrDefault("output_directory", ""));
        
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> surveys = (List<Map<String, Object>>) data.get("surveys");
        metadata.setSurveys(surveys != null ? surveys : new ArrayList<>());
        
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> failures = (List<Map<String, Object>>) data.get("failures");
        metadata.setFailures(failures != null ? failures : new ArrayList<>());
        
        metadata.setEndTimestamp((String) data.get("end_timestamp"));
        
        Object durationObj = data.get("duration_seconds");
        if (durationObj instanceof Number) {
            metadata.setDurationSeconds(((Number) durationObj).doubleValue());
        }
        
        return metadata;
    }
} 