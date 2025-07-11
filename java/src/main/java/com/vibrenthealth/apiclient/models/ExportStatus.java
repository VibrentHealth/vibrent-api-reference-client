package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Map;
import java.util.Objects;

/**
 * Represents the status of an export request
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ExportStatus {
    
    @JsonProperty("exportId")
    private String exportId;
    
    private String status;
    
    private String fileName;
    
    private String submittedOn;
    
    private String completedOn;
    
    private String downloadEndpoint;
    
    private String failureReason;

    public static ExportStatus fromMap(Map<String, Object> data) {
        ExportStatus status = new ExportStatus();
        status.setExportId((String) data.getOrDefault("exportId", ""));
        status.setStatus((String) data.getOrDefault("status", "UNKNOWN"));
        status.setFileName((String) data.get("fileName"));
        status.setSubmittedOn((String) data.get("submittedOn"));
        status.setCompletedOn((String) data.get("completedOn"));
        status.setDownloadEndpoint((String) data.get("downloadEndpoint"));
        status.setFailureReason((String) data.get("failureReason"));
        return status;
    }
} 