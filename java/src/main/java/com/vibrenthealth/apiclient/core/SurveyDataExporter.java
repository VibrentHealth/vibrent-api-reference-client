package com.vibrenthealth.apiclient.core;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vibrenthealth.apiclient.models.ExportMetadata;
import com.vibrenthealth.apiclient.models.ExportRequest;
import com.vibrenthealth.apiclient.models.ExportStatus;
import com.vibrenthealth.apiclient.models.Survey;
import org.apache.commons.compress.archivers.zip.ZipArchiveEntry;
import org.apache.commons.compress.archivers.zip.ZipFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Main class for orchestrating the survey data export process
 */
public class SurveyDataExporter {
    private static final Logger logger = LoggerFactory.getLogger(SurveyDataExporter.class);

    private final ConfigManager configManager;
    private final String environment;
    private final VibrentHealthAPIClient client;
    private final String exportFormat;
    private final boolean extractFiles;
    private final boolean removeZipAfterExtract;
    private final int pollingInterval;
    private final Integer maxWaitTime;
    private final boolean continueOnFailure;
    private final Path outputDir;
    private final String exportSessionId;
    private final LocalDateTime startTime;
    private final ExportMetadata exportMetadata;
    private final Map<Integer, Map<String, Object>> exportDetailsBySurvey;
    private final ObjectMapper objectMapper;

    public SurveyDataExporter(ConfigManager configManager, String environment, String outputBaseDir) {
        this.configManager = configManager;
        this.environment = environment != null ? environment :
                (String) configManager.get(Constants.ConfigKeys.ENVIRONMENT + "." + Constants.ConfigKeys.DEFAULT);
        this.client = new VibrentHealthAPIClient(configManager, this.environment);

        // Get output configuration
        Map<String, Object> outputConfig = configManager.getOutputConfig();

        // Get export configuration
        Map<String, Object> exportConfig = (Map<String, Object>) configManager.get(Constants.ConfigKeys.EXPORT);
        this.exportFormat = (String) exportConfig.getOrDefault(Constants.ConfigKeys.FORMAT, Constants.ExportFormat.JSON);
        this.extractFiles = (Boolean) outputConfig.getOrDefault(Constants.ConfigKeys.EXTRACT_FILES, true);
        this.removeZipAfterExtract = (Boolean) outputConfig.getOrDefault(Constants.ConfigKeys.REMOVE_ZIP_AFTER_EXTRACT, true);

        // Get monitoring configuration
        Map<String, Object> monitoringConfig = (Map<String, Object>) exportConfig.get(Constants.ConfigKeys.MONITORING);
        this.pollingInterval = (Integer) monitoringConfig.getOrDefault(Constants.ConfigKeys.POLLING_INTERVAL,
                Constants.TimeConstants.DEFAULT_POLLING_INTERVAL);
        Object maxWaitTimeObj = monitoringConfig.get(Constants.ConfigKeys.MAX_WAIT_TIME);
        this.maxWaitTime = maxWaitTimeObj != null ? (Integer) maxWaitTimeObj : null;
        this.continueOnFailure = (Boolean) monitoringConfig.getOrDefault(Constants.ConfigKeys.CONTINUE_ON_FAILURE, true);

        // Create output directory with timestamp
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd_MM_yyyy_HHmmss"));

        // Get the survey output directory
        String surveyOutputDir = configManager.getSurveyOutputDirectory();
        this.outputDir = Paths.get(surveyOutputDir, "survey_data_" + timestamp);
        try {
            Files.createDirectories(this.outputDir);
        } catch (IOException e) {
            throw new RuntimeException("Failed to create output directory: " + e.getMessage());
        }

        this.exportSessionId = "export_" + timestamp;
        this.startTime = LocalDateTime.now();
        this.exportDetailsBySurvey = new HashMap<>();
        this.objectMapper = new ObjectMapper();

        this.exportMetadata = new ExportMetadata();
        this.exportMetadata.setExportSessionId(this.exportSessionId);
        this.exportMetadata.setStartTimestamp(this.startTime.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        this.exportMetadata.setTotalSurveys(0);
        this.exportMetadata.setSuccessfulExports(0);
        this.exportMetadata.setFailedExports(0);
        this.exportMetadata.setOutputDirectory(this.outputDir.toString());
    }

    /**
     * Create export request based on configuration
     */
    public ExportRequest createExportRequest() {
        Map<String, Long> dateRange = configManager.getDateRange();

        return new ExportRequest(
                dateRange.get("start_time"),
                dateRange.get("end_time"),
                exportFormat
        );
    }

    /**
     * Wait for all exports to complete and return completed and failed exports
     */
    public Map<String, ExportStatus> waitForExportsCompletion(Map<Integer, String> exportMapping) {
        Map<String, ExportStatus> completedExports = new HashMap<>();
        List<String> failedExports = new ArrayList<>();
        Set<String> pendingExports = new HashSet<>(exportMapping.values());
        long startWaitTime = System.currentTimeMillis();

        // Initialize cumulative status counts
        Map<String, Integer> cumulativeStatusCounts = new HashMap<>();
        cumulativeStatusCounts.put(Constants.ExportStatus.COMPLETED, 0);
        cumulativeStatusCounts.put(Constants.ExportStatus.FAILED, 0);
        cumulativeStatusCounts.put(Constants.ExportStatus.IN_PROGRESS, pendingExports.size());

        logger.info("Checking Export Status: Waiting for {} exports to complete", pendingExports.size());

        while (!pendingExports.isEmpty()) {
            // Check if we've exceeded max wait time
            if (maxWaitTime != null && (System.currentTimeMillis() - startWaitTime) > maxWaitTime * 1000L) {
                logger.warn("Maximum wait time ({}s) exceeded. {} exports still pending.", maxWaitTime, pendingExports.size());
                break;
            }

            try {
                Thread.sleep(pollingInterval * 1000L);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }

            // Reset current iteration status counts
            Map<String, Integer> currentStatusCounts = new HashMap<>();
            currentStatusCounts.put(Constants.ExportStatus.COMPLETED, 0);
            currentStatusCounts.put(Constants.ExportStatus.FAILED, 0);
            currentStatusCounts.put(Constants.ExportStatus.IN_PROGRESS, 0);

            for (String exportId : new ArrayList<>(pendingExports)) {
                try {
                    ExportStatus status = client.getExportStatus(exportId);

                    if (Constants.ExportStatus.COMPLETED.equals(status.getStatus())) {
                        currentStatusCounts.put(Constants.ExportStatus.COMPLETED,
                                currentStatusCounts.get(Constants.ExportStatus.COMPLETED) + 1);
                        completedExports.put(exportId, status);
                        pendingExports.remove(exportId);

                    } else if (Constants.ExportStatus.FAILED.equals(status.getStatus())) {
                        currentStatusCounts.put(Constants.ExportStatus.FAILED,
                                currentStatusCounts.get(Constants.ExportStatus.FAILED) + 1);
                        failedExports.add(exportId);
                        pendingExports.remove(exportId);

                        // Add to failures metadata
                        Map<String, Object> failure = new HashMap<>();
                        failure.put("exportId", exportId);
                        failure.put("failureReason", status.getFailureReason());
                        failure.put("status", status);
                        exportMetadata.getFailures().add(failure);

                    } else if (Constants.ExportStatus.SUBMITTED.equals(status.getStatus()) ||
                            Constants.ExportStatus.IN_PROGRESS.equals(status.getStatus())) {
                        currentStatusCounts.put(Constants.ExportStatus.IN_PROGRESS,
                                currentStatusCounts.get(Constants.ExportStatus.IN_PROGRESS) + 1);
                    }

                } catch (Exception e) {
                    logger.error("Error checking status for {}: {}", exportId, e.getMessage());
                    if (!continueOnFailure) {
                        throw new RuntimeException(e);
                    }
                    currentStatusCounts.put(Constants.ExportStatus.FAILED,
                            currentStatusCounts.get(Constants.ExportStatus.FAILED) + 1);
                    failedExports.add(exportId);
                    pendingExports.remove(exportId);
                }
            }

            // Update cumulative status counts
            cumulativeStatusCounts.put(Constants.ExportStatus.COMPLETED,
                    cumulativeStatusCounts.get(Constants.ExportStatus.COMPLETED) + currentStatusCounts.get(Constants.ExportStatus.COMPLETED));
            cumulativeStatusCounts.put(Constants.ExportStatus.FAILED,
                    cumulativeStatusCounts.get(Constants.ExportStatus.FAILED) + currentStatusCounts.get(Constants.ExportStatus.FAILED));
            cumulativeStatusCounts.put(Constants.ExportStatus.IN_PROGRESS, pendingExports.size());

            logger.info("Status after this check: TOTAL: {}, COMPLETED: {}, FAILED: {}, IN_PROGRESS: {}",
                    exportMapping.size(),
                    cumulativeStatusCounts.get(Constants.ExportStatus.COMPLETED),
                    cumulativeStatusCounts.get(Constants.ExportStatus.FAILED),
                    cumulativeStatusCounts.get(Constants.ExportStatus.IN_PROGRESS));
        }

        return completedExports;
    }

    /**
     * Extract export files (JSON or CSV) from zip archives based on configured format
     */
    public void extractExportFiles(List<Path> zipFiles) {
        if (zipFiles == null) {
            logger.error("List of zip files is null");
            return;
        }

        if (!extractFiles) {
            logger.info("File extraction disabled in configuration");
            return;
        }

        logger.info("Extracting {} files from zip archives", exportFormat);

        for (Path zipFile : zipFiles) {
            boolean extractionSuccessful = true;
            try (ZipFile zip = new ZipFile(zipFile.toFile())) {
                Enumeration<ZipArchiveEntry> entries = zip.getEntries();
                while (entries.hasMoreElements()) {
                    ZipArchiveEntry entry = entries.nextElement();
                    Path extractedPath = outputDir.resolve(entry.getName());
                    Files.createDirectories(extractedPath.getParent());

                    try (InputStream inputStream = zip.getInputStream(entry);
                         FileOutputStream outputStream = new FileOutputStream(extractedPath.toFile())) {
                        byte[] buffer = new byte[8192];
                        int bytesRead;
                        while ((bytesRead = inputStream.read(buffer)) != -1) {
                            outputStream.write(buffer, 0, bytesRead);
                        }
                    }

                    Path relativePath = Paths.get("").toAbsolutePath().relativize(extractedPath);
                    logger.info("Extracted: {}", relativePath);
                }
            } catch (IOException e) {
                logger.error("Error extracting {}: {}", zipFile, e.getMessage());
                extractionSuccessful = false;
            }

            if (extractionSuccessful && removeZipAfterExtract) {
                try {
                    Files.delete(zipFile);
                    logger.debug("Removed zip file: {}", zipFile);
                } catch (IOException e) {
                    logger.error("Error deleting zip file {}: {}", zipFile, e.getMessage());
                }
            }
        }
    }

    /**
     * Save export metadata to JSON file
     */
    public void saveExportMetadata() {
        Map<String, Object> metadataConfig = configManager.getMetadataConfig();

        if (!(Boolean) metadataConfig.getOrDefault(Constants.ConfigKeys.SAVE_METADATA, true)) {
            logger.info("Metadata saving disabled in configuration");
            return;
        }

        String metadataFilename = (String) metadataConfig.getOrDefault(Constants.ConfigKeys.FILENAME,
                Constants.FileConstants.DEFAULT_METADATA_FILENAME);
        Path metadataFile = outputDir.resolve(metadataFilename);

        try {
            objectMapper.writerWithDefaultPrettyPrinter().writeValue(metadataFile.toFile(), exportMetadata);
            Path relativePath = Paths.get("").toAbsolutePath().relativize(metadataFile);
            logger.info(String.format(Constants.SuccessMessages.METADATA_SAVED, relativePath));
        } catch (IOException e) {
            logger.error("Failed to save metadata: {}", e.getMessage());
        }
    }
    
    /**
     * Run the complete export process
     */
    public void runExport() {
        try {
            logger.info("Starting survey data export (Session: {})", exportSessionId);

            List<Survey> surveys = getSurveys();
            List<Survey> filteredSurveys = filterSurveys(surveys);

            if (filteredSurveys.isEmpty()) {
                logger.warn("No surveys match the filter criteria");
                return;
            }
            logger.info("Total surveys data to be exported: {} surveys", filteredSurveys.size());

            Map<Integer, String> exportMapping = requestExports(filteredSurveys);

            if (exportMapping.isEmpty()) {
                logger.error("No exports were successfully requested");
                return;
            }

            Map<String, ExportStatus> completedExports = waitForExportsCompletion(exportMapping);
            List<Path> downloadedFiles = downloadCompletedExports(completedExports, exportMapping);

            if (!downloadedFiles.isEmpty()) {
                extractExportFiles(downloadedFiles);
            }

            updateMetadata(completedExports);
            createSurveyMetadata(filteredSurveys);
            finalizeExport();

        } catch (Exception e) {
            logger.error("Export process failed: {}", e.getMessage());
            throw new RuntimeException(e);
        }
    }

    private List<Survey> getSurveys() {
        List<Survey> surveys = client.getSurveys();
        exportMetadata.setTotalSurveys(surveys.size());

        if (surveys.isEmpty()) {
            logger.warn(Constants.ErrorMessages.NO_SURVEYS_FOUND);
        }
        return surveys;
    }

    private List<Survey> filterSurveys(List<Survey> surveys) {
        Map<String, Object> surveyFilter = configManager.getSurveyFilter();
        Integer maxSurveys = (Integer) surveyFilter.get(Constants.ConfigKeys.MAX_SURVEYS);

        List<Survey> filteredSurveys = new ArrayList<>();
        for (Survey survey : surveys) {
            if (configManager.shouldIncludeSurvey(survey.getPlatformFormId(), survey.getName())) {
                filteredSurveys.add(survey);
                if (maxSurveys != null && filteredSurveys.size() >= maxSurveys) {
                    break;
                }
            }
        }
        return filteredSurveys;
    }

    private Map<Integer, String> requestExports(List<Survey> filteredSurveys) {
        ExportRequest exportRequest = createExportRequest();
        Map<Integer, String> exportMapping = new HashMap<>();

        for (int i = 0; i < filteredSurveys.size(); i++) {
            Survey survey = filteredSurveys.get(i);
            try {
                logger.info("[{}/{}] Requesting export for survey id: {} (Name: '{}')",
                        i + 1, filteredSurveys.size(), survey.getPlatformFormId(), survey.getName());
                String exportId = client.requestSurveyExport(survey.getPlatformFormId(), exportRequest);
                logger.info("[{}/{}] Requested export for survey id: {}, export id: {}",
                        i + 1, filteredSurveys.size(), survey.getPlatformFormId(), exportId);
                exportMapping.put(survey.getPlatformFormId(), exportId);
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            } catch (Exception e) {
                logger.error(String.format(Constants.ErrorMessages.EXPORT_REQUEST_FAILED,
                        survey.getPlatformFormId(), e.getMessage()));

                Map<String, Object> failure = new HashMap<>();
                failure.put("surveyId", survey.getPlatformFormId());
                failure.put("error", e.getMessage());
                failure.put("stage", "export_request");
                exportMetadata.getFailures().add(failure);
            }
        }
        return exportMapping;
    }

    private List<Path> downloadCompletedExports(Map<String, ExportStatus> completedExports, Map<Integer, String> exportMapping) {
        List<Path> downloadedFiles = new ArrayList<>();
        int completedCount = 0;
        for (Map.Entry<String, ExportStatus> entry : completedExports.entrySet()) {
            String exportId = entry.getKey();
            ExportStatus status = entry.getValue();
            completedCount++;

            try {
                logger.info("[{}/{}] Downloading export: {}", completedCount, completedExports.size(), exportId);
                Path filePath = client.downloadExport(exportId, outputDir);
                Path relativePath = Paths.get("").toAbsolutePath().relativize(filePath);
                logger.info("[{}/{}] Downloaded: {}", completedCount, completedExports.size(), relativePath);
                downloadedFiles.add(filePath);

                Map<String, Object> exportDetail = new HashMap<>();
                exportDetail.put("exportId", exportId);
                exportDetail.put("status", status);

                for (Map.Entry<Integer, String> mapping : exportMapping.entrySet()) {
                    if (mapping.getValue().equals(exportId)) {
                        exportDetailsBySurvey.put(mapping.getKey(), exportDetail);
                        break;
                    }
                }

            } catch (Exception e) {
                logger.error(String.format(Constants.ErrorMessages.EXPORT_DOWNLOAD_FAILED, exportId, e.getMessage()));

                Map<String, Object> failure = new HashMap<>();
                failure.put("exportId", exportId);
                failure.put("error", e.getMessage());
                failure.put("stage", "download");
                exportMetadata.getFailures().add(failure);
            }
        }
        return downloadedFiles;
    }

    private void updateMetadata(Map<String, ExportStatus> completedExports) {
        exportMetadata.setSuccessfulExports(completedExports.size());
        exportMetadata.setFailedExports(exportMetadata.getFailures().size());
    }

    private void createSurveyMetadata(List<Survey> filteredSurveys) {
        Map<String, Object> metadataConfig = configManager.getMetadataConfig();
        boolean includeSurveyDetails = (Boolean) metadataConfig.getOrDefault(Constants.ConfigKeys.INCLUDE_SURVEY_DETAILS, true);
        boolean includeExportStatus = (Boolean) metadataConfig.getOrDefault(Constants.ConfigKeys.INCLUDE_EXPORT_STATUS, true);

        if (includeSurveyDetails) {
            List<Map<String, Object>> surveyDicts = new ArrayList<>();
            for (Survey survey : filteredSurveys) {
                Map<String, Object> surveyDict = new HashMap<>();
                surveyDict.put("id", survey.getId());
                surveyDict.put("name", survey.getName());
                surveyDict.put("displayName", survey.getDisplayName());
                surveyDict.put("platformFormId", survey.getPlatformFormId());

                if (includeExportStatus && exportDetailsBySurvey.containsKey(survey.getPlatformFormId())) {
                    surveyDict.put("export_details", exportDetailsBySurvey.get(survey.getPlatformFormId()));
                }
                surveyDicts.add(surveyDict);
            }

            exportMetadata.setSurveys(surveyDicts);
        }
    }

    private void finalizeExport() {
        LocalDateTime endTime = LocalDateTime.now();
        exportMetadata.setEndTimestamp(endTime.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        double durationSeconds = java.time.Duration.between(startTime, endTime).toMillis() / 1000.0;
        exportMetadata.setDurationSeconds(durationSeconds);

        saveExportMetadata();

        logger.info(Constants.SuccessMessages.EXPORT_COMPLETED);
        logger.info("Total surveys: {}", exportMetadata.getTotalSurveys());
        logger.info("Successful exports: {}", exportMetadata.getSuccessfulExports());
        logger.info("Failed exports: {}", exportMetadata.getFailedExports());
        logger.info(String.format("Duration: %.2f seconds", exportMetadata.getDurationSeconds()));
        logger.info("Output directory: {}", outputDir);
    }
} 