package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

/**
 * Represents an EHR export request (single or multi-participant)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class EHRExportRequest {

    @JsonProperty("dateFrom")
    private Long dateFrom;

    @JsonProperty("dateTo")
    private Long dateTo;

    @JsonProperty("participantIds")
    private List<Long> participantIds;

    @JsonProperty("manifestOnly")
    private boolean manifestOnly = false;

    @SuppressWarnings("unchecked")
    public static EHRExportRequest fromMap(Map<String, Object> data) {
        EHRExportRequest request = new EHRExportRequest();
        request.setDateFrom(data.get("dateFrom") != null ? ((Number) data.get("dateFrom")).longValue() : null);
        request.setDateTo(data.get("dateTo") != null ? ((Number) data.get("dateTo")).longValue() : null);
        request.setParticipantIds((List<Long>) data.get("participantIds"));
        request.setManifestOnly((Boolean) data.getOrDefault("manifestOnly", false));
        return request;
    }
}
