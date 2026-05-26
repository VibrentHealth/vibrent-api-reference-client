package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

/**
 * Represents a communication events batch export request
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class CommunicationEventsExportRequest {

    @JsonProperty("dateFrom")
    private Long dateFrom;

    @JsonProperty("dateTo")
    private Long dateTo;

    @JsonProperty("participantIds")
    private List<String> participantIds;

    @JsonProperty("manifestOnly")
    private Boolean manifestOnly;

    @JsonProperty("eventSources")
    private List<String> eventSources;

    @JsonProperty("eventTypes")
    private List<String> eventTypes;

    @SuppressWarnings("unchecked")
    public static CommunicationEventsExportRequest fromMap(Map<String, Object> data) {
        CommunicationEventsExportRequest request = new CommunicationEventsExportRequest();
        request.setDateFrom(data.get("dateFrom") != null ? ((Number) data.get("dateFrom")).longValue() : null);
        request.setDateTo(data.get("dateTo") != null ? ((Number) data.get("dateTo")).longValue() : null);
        request.setParticipantIds((List<String>) data.get("participantIds"));
        request.setManifestOnly((Boolean) data.get("manifestOnly"));
        request.setEventSources((List<String>) data.get("eventSources"));
        request.setEventTypes((List<String>) data.get("eventTypes"));
        return request;
    }
}
