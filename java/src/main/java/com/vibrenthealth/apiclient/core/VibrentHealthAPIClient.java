package com.vibrenthealth.apiclient.core;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vibrenthealth.apiclient.models.ExportRequest;
import com.vibrenthealth.apiclient.models.ExportStatus;
import com.vibrenthealth.apiclient.models.Survey;
import okhttp3.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Main client for interacting with Vibrent Health APIs
 */
public class VibrentHealthAPIClient {
    private static final Logger logger = LoggerFactory.getLogger(VibrentHealthAPIClient.class);

    private final ConfigManager configManager;
    private final String environment;
    private final AuthenticationManager authManager;
    private final String baseUrl;
    private final int timeout;
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper;

    public VibrentHealthAPIClient(ConfigManager configManager, String environment) {
        this.configManager = configManager;
        this.environment = environment != null ? environment :
                (String) configManager.get(Constants.ConfigKeys.ENVIRONMENT + "." + Constants.ConfigKeys.DEFAULT);
        this.authManager = new AuthenticationManager(configManager, this.environment);

        // Get environment configuration
        Map<String, String> envConfig = configManager.getEnvironmentConfig(this.environment);
        this.baseUrl = envConfig.get(Constants.ConfigKeys.BASE_URL);

        if (this.baseUrl == null) {
            throw new AuthenticationManager.VibrentHealthAPIError(
                    String.format(Constants.ErrorMessages.INVALID_ENVIRONMENT, this.environment)
            );
        }

        // Get API configuration
        Map<String, Object> apiConfig = (Map<String, Object>) configManager.get(Constants.ConfigKeys.API);
        this.timeout = (Integer) apiConfig.getOrDefault(Constants.ConfigKeys.TIMEOUT, Constants.TimeConstants.DEFAULT_TIMEOUT);

        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(timeout, TimeUnit.SECONDS)
                .readTimeout(timeout, TimeUnit.SECONDS)
                .writeTimeout(timeout, TimeUnit.SECONDS)
                .build();

        this.objectMapper = new ObjectMapper();
    }

    /**
     * Make an authenticated request to the API
     */
    private Response makeRequest(String method, String endpoint, RequestBody body) throws IOException {
        String token = authManager.getValidToken();
        String url = baseUrl + endpoint;

        Request.Builder requestBuilder = new Request.Builder()
                .url(url)
                .addHeader(Constants.Headers.AUTHORIZATION, "Bearer " + token);

        if (body != null) {
            requestBuilder.method(method, body);
        } else {
            requestBuilder.method(method, null);
        }

        Request request = requestBuilder.build();
        Response response = httpClient.newCall(request).execute();

        if (!response.isSuccessful()) {
            String errorBody = response.body() != null ? response.body().string() : "No response body";
            throw new AuthenticationManager.VibrentHealthAPIError(
                    String.format(Constants.ErrorMessages.API_REQUEST_FAILED,
                            "HTTP " + response.code() + ": " + errorBody)
            );
        }

        return response;
    }

    /**
     * Get list of available surveys
     */
    public List<Survey> getSurveys() {
        logger.info("Fetching surveys");

        try {
            Response response = makeRequest("GET", Constants.APIEndpoints.SURVEYS, null);

            if (response.body() != null) {
                String responseBody = response.body().string();
                List<Map<String, Object>> surveysData = objectMapper.readValue(responseBody, new TypeReference<List<Map<String, Object>>>() {
                });

                List<Survey> surveys = new ArrayList<>();
                for (int i = 0; i < surveysData.size(); i++) {
                    try {
                        Map<String, Object> surveyData = surveysData.get(i);
                        Survey survey = Survey.fromMap(surveyData);
                        surveys.add(survey);
                    } catch (Exception e) {
                        logger.warn("Failed to create Survey object from data at index {}: {}", i, e.getMessage());
                        logger.debug("Survey data: {}", surveysData.get(i));
                    }
                }

                logger.info("Total surveys associated with this study: {}", surveys.size());
                return surveys;
            } else {
                throw new AuthenticationManager.VibrentHealthAPIError("Empty response body");
            }
        } catch (IOException e) {
            throw new AuthenticationManager.VibrentHealthAPIError(
                    String.format(Constants.ErrorMessages.API_REQUEST_FAILED, e.getMessage())
            );
        }
    }

    /**
     * Request export for a specific survey
     */
    public String requestSurveyExport(int surveyId, ExportRequest exportRequest) {
        try {
            String endpoint = Constants.APIEndpoints.EXPORT_REQUEST.replace("{survey_id}", String.valueOf(surveyId));
            String jsonBody = objectMapper.writeValueAsString(exportRequest);

            RequestBody body = RequestBody.create(jsonBody, MediaType.get("application/json"));
            Response response = makeRequest("POST", endpoint, body);

            if (response.body() != null) {
                String responseBody = response.body().string();
                JsonNode exportData = objectMapper.readTree(responseBody);
                return exportData.get("exportId").asText();
            } else {
                throw new AuthenticationManager.VibrentHealthAPIError("Empty response body");
            }
        } catch (IOException e) {
            throw new AuthenticationManager.VibrentHealthAPIError(
                    String.format(Constants.ErrorMessages.EXPORT_REQUEST_FAILED, surveyId, e.getMessage())
            );
        }
    }

    /**
     * Get status of an export request
     */
    public ExportStatus getExportStatus(String exportId) {
        try {
            String endpoint = Constants.APIEndpoints.EXPORT_STATUS.replace("{export_id}", exportId);
            Response response = makeRequest("GET", endpoint, null);

            if (response.body() != null) {
                String responseBody = response.body().string();
                Map<String, Object> statusData = objectMapper.readValue(responseBody, new TypeReference<Map<String, Object>>() {
                });
                return ExportStatus.fromMap(statusData);
            } else {
                throw new AuthenticationManager.VibrentHealthAPIError("Empty response body");
            }
        } catch (IOException e) {
            throw new AuthenticationManager.VibrentHealthAPIError(
                    String.format(Constants.ErrorMessages.API_REQUEST_FAILED, e.getMessage())
            );
        }
    }

    /**
     * Download an export file
     */
    public Path downloadExport(String exportId, Path outputPath) {
        try {
            String endpoint = Constants.APIEndpoints.EXPORT_DOWNLOAD.replace("{export_id}", exportId);
            Response response = makeRequest("GET", endpoint, null);

            // Determine filename
            String filename = "export_" + exportId + ".zip";
            String contentDisposition = response.header("Content-Disposition");
            if (contentDisposition != null && contentDisposition.contains("filename=")) {
                filename = exportId + "_" + contentDisposition.split("filename=")[1].replace("\"", "");
            }

            Path filePath = outputPath.resolve(filename);

            // Ensure output directory exists
            Files.createDirectories(outputPath);

            // Write file
            if (response.body() != null) {
                try (InputStream inputStream = response.body().byteStream();
                     FileOutputStream outputStream = new FileOutputStream(filePath.toFile())) {

                    byte[] buffer = new byte[8192];
                    int bytesRead;
                    while ((bytesRead = inputStream.read(buffer)) != -1) {
                        outputStream.write(buffer, 0, bytesRead);
                    }
                }
            }

            return filePath;
        } catch (IOException e) {
            throw new AuthenticationManager.VibrentHealthAPIError(
                    String.format(Constants.ErrorMessages.EXPORT_DOWNLOAD_FAILED, exportId, e.getMessage())
            );
        }
    }
} 