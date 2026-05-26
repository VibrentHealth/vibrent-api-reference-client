package com.vibrenthealth.apiclient.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

/**
 * Represents a device data export request (single or multi-participant)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class DeviceDataExportRequest {

    @JsonProperty("dateFrom")
    private Long dateFrom;

    @JsonProperty("dateTo")
    private Long dateTo;

    @JsonProperty("participantIds")
    private List<Long> participantIds;

    @JsonProperty("deviceTypes")
    private List<String> deviceTypes;

    @JsonProperty("dataTypes")
    private List<String> dataTypes;

    @JsonProperty("manifestOnly")
    private boolean manifestOnly = false;

    @SuppressWarnings("unchecked")
    public static DeviceDataExportRequest fromMap(Map<String, Object> data) {
        DeviceDataExportRequest request = new DeviceDataExportRequest();
        request.setDateFrom(data.get("dateFrom") != null ? ((Number) data.get("dateFrom")).longValue() : null);
        request.setDateTo(data.get("dateTo") != null ? ((Number) data.get("dateTo")).longValue() : null);
        request.setParticipantIds((List<Long>) data.get("participantIds"));
        request.setDeviceTypes((List<String>) data.get("deviceTypes"));
        request.setDataTypes((List<String>) data.get("dataTypes"));
        request.setManifestOnly((Boolean) data.getOrDefault("manifestOnly", false));
        return request;
    }
}
