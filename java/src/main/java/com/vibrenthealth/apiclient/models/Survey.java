package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Map;
import java.util.Objects;

/**
 * Represents a survey object from the API
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Survey {
    private int id;
    private String name;
    
    @JsonProperty("displayName")
    private String displayName;
    
    @JsonProperty("platformFormId")
    private int platformFormId;
    
    @JsonProperty("export_details")
    private Map<String, Object> exportDetails;

    public static Survey fromMap(Map<String, Object> data) {
        Survey survey = new Survey();
        survey.setId((Integer) data.getOrDefault("id", 0));
        survey.setName((String) data.getOrDefault("name", "Unknown Survey"));
        survey.setDisplayName((String) data.getOrDefault("displayName", "Unknown Survey"));
        survey.setPlatformFormId((Integer) data.getOrDefault("platformFormId", 0));
        survey.setExportDetails((Map<String, Object>) data.get("export_details"));
        return survey;
    }
} 