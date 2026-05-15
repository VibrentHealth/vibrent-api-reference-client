package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

/**
 * Represents a participant profiles batch export request
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ParticipantProfilesExportRequest {

    @JsonProperty("dateFrom")
    private Long dateFrom;

    @JsonProperty("dateTo")
    private Long dateTo;

    @JsonProperty("participantIds")
    private List<String> participantIds;

    @SuppressWarnings("unchecked")
    public static ParticipantProfilesExportRequest fromMap(Map<String, Object> data) {
        ParticipantProfilesExportRequest request = new ParticipantProfilesExportRequest();
        request.setDateFrom(data.get("dateFrom") != null ? ((Number) data.get("dateFrom")).longValue() : null);
        request.setDateTo(data.get("dateTo") != null ? ((Number) data.get("dateTo")).longValue() : null);
        request.setParticipantIds((List<String>) data.get("participantIds"));
        return request;
    }
}
