package com.vibrenthealth.apiclient.core;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.type.MapType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.yaml.snakeyaml.Yaml;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Configuration manager for Vibrent Health API Client
 */
public class ConfigManager {
    private static final Logger logger = LoggerFactory.getLogger(ConfigManager.class);
    private final String configFile;
    private Map<String, Object> config;
    private final ObjectMapper objectMapper;
    private final Yaml yaml;

    public ConfigManager() {
        this(null);
    }

    public ConfigManager(String configFile) {
        this.configFile = configFile != null ? configFile : findConfigFile();
        this.objectMapper = new ObjectMapper();
        this.yaml = new Yaml();
        loadConfig();
    }

    /**
     * Find the configuration file in common locations
     */
    private String findConfigFile() {
        // Get the repo root by finding the directory that contains both 'java' and 'shared' folders
        String currentDir = System.getProperty("user.dir");
        String repoRoot = findRepoRoot(currentDir);
        
        List<String> possiblePaths = Arrays.asList(
            Paths.get(repoRoot, "shared", "config", "vibrent_config.yaml").toString(),
            Paths.get(repoRoot, "java", "shared", "config", "vibrent_config.yaml").toString(),
            "shared/config/vibrent_config.yaml",
            "config/vibrent_config.yaml",
            "vibrent_config.yaml",
            "config.yaml",
            "config.yml"
        );

        for (String path : possiblePaths) {
            if (Files.exists(Paths.get(path))) {
                logger.info("Found config file: {}", path);
                return path;
            }
        }

        // If no config file found, create a default one in shared directory
        String defaultConfigPath = Paths.get(repoRoot, "shared", "config", "vibrent_config.yaml").toString();
        logger.info("Creating default config at: {}", defaultConfigPath);
        createDefaultConfig(defaultConfigPath);
        return defaultConfigPath;
    }

    /**
     * Find the repo root by looking for directories containing both 'java' and 'shared' folders
     */
    private String findRepoRoot(String currentDir) {
        Path currentPath = Paths.get(currentDir);
        
        while (currentPath != null && currentPath.getParent() != null) {
            Path javaDir = currentPath.resolve("java");
            Path sharedDir = currentPath.resolve("shared");
            
            if (Files.exists(javaDir) && Files.exists(sharedDir)) {
                return currentPath.toString();
            }
            
            currentPath = currentPath.getParent();
        }
        
        // Fallback to current directory if repo root not found
        return System.getProperty("user.dir");
    }

    /**
     * Create a default configuration file
     */
    private void createDefaultConfig(String configPath) {
        try {
            Path path = Paths.get(configPath);
            Files.createDirectories(path.getParent());
            
            Map<String, Object> defaultConfig = createDefaultConfigMap();
            
            try (FileWriter writer = new FileWriter(configPath)) {
                yaml.dump(defaultConfig, writer);
            }
            
            logger.info("Created default configuration file: {}", configPath);
        } catch (IOException e) {
            throw new ConfigurationError("Failed to create default configuration file: " + e.getMessage());
        }
    }

    /**
     * Create the default configuration map
     */
    private Map<String, Object> createDefaultConfigMap() {
        Map<String, Object> config = new LinkedHashMap<>();
        
        // Environment configuration
        Map<String, Object> environment = new LinkedHashMap<>();
        environment.put(Constants.ConfigKeys.DEFAULT, Constants.Environment.STAGING);
        
        Map<String, Object> environments = new LinkedHashMap<>();
        
        Map<String, Object> staging = new LinkedHashMap<>();
        staging.put(Constants.ConfigKeys.BASE_URL, "YOUR_STAGING_BASE_URL_HERE");
        staging.put(Constants.ConfigKeys.TOKEN_URL, "YOUR_STAGING_TOKEN_URL_HERE");
        environments.put(Constants.Environment.STAGING, staging);
        
        Map<String, Object> production = new LinkedHashMap<>();
        production.put(Constants.ConfigKeys.BASE_URL, "YOUR_PRODUCTION_BASE_URL_HERE");
        production.put(Constants.ConfigKeys.TOKEN_URL, "YOUR_PRODUCTION_TOKEN_URL_HERE");
        environments.put(Constants.Environment.PRODUCTION, production);
        
        environment.put(Constants.ConfigKeys.ENVIRONMENTS, environments);
        config.put(Constants.ConfigKeys.ENVIRONMENT, environment);
        
        // Auth configuration
        Map<String, Object> auth = new LinkedHashMap<>();
        auth.put(Constants.ConfigKeys.TIMEOUT, Constants.TimeConstants.DEFAULT_TIMEOUT);
        auth.put(Constants.ConfigKeys.REFRESH_BUFFER, Constants.TimeConstants.TOKEN_REFRESH_BUFFER);
        config.put(Constants.ConfigKeys.AUTH, auth);
        
        // API configuration
        Map<String, Object> api = new LinkedHashMap<>();
        api.put(Constants.ConfigKeys.TIMEOUT, Constants.TimeConstants.DEFAULT_TIMEOUT);
        config.put(Constants.ConfigKeys.API, api);
        
        // Export configuration
        Map<String, Object> export = new LinkedHashMap<>();
        
        Map<String, Object> dateRange = new LinkedHashMap<>();
        dateRange.put(Constants.ConfigKeys.DEFAULT_DAYS_BACK, 30);
        dateRange.put(Constants.ConfigKeys.ABSOLUTE_START_DATE, null);
        dateRange.put(Constants.ConfigKeys.ABSOLUTE_END_DATE, null);
        export.put(Constants.ConfigKeys.DATE_RANGE, dateRange);
        
        export.put(Constants.ConfigKeys.FORMAT, Constants.ExportFormat.JSON);
        
        Map<String, Object> request = new LinkedHashMap<>();
        request.put(Constants.ConfigKeys.MAX_SURVEYS, null);
        request.put(Constants.ConfigKeys.SURVEY_IDS, null);
        request.put(Constants.ConfigKeys.EXCLUDE_SURVEY_IDS, null);
        export.put(Constants.ConfigKeys.REQUEST, request);
        
        Map<String, Object> monitoring = new LinkedHashMap<>();
        monitoring.put(Constants.ConfigKeys.POLLING_INTERVAL, Constants.TimeConstants.DEFAULT_POLLING_INTERVAL);
        monitoring.put(Constants.ConfigKeys.MAX_WAIT_TIME, null);
        monitoring.put(Constants.ConfigKeys.CONTINUE_ON_FAILURE, true);
        export.put(Constants.ConfigKeys.MONITORING, monitoring);
        
        config.put(Constants.ConfigKeys.EXPORT, export);
        
        // Output configuration
        Map<String, Object> output = new LinkedHashMap<>();
        output.put(Constants.ConfigKeys.BASE_DIRECTORY, Constants.FileConstants.OUTPUT_BASE_DIR);
        output.put(Constants.ConfigKeys.SURVEY_EXPORTS_DIR, Constants.FileConstants.SURVEY_EXPORTS_DIR);
        output.put(Constants.ConfigKeys.EXTRACT_JSON, true);
        output.put(Constants.ConfigKeys.REMOVE_ZIP_AFTER_EXTRACT, true);
        config.put(Constants.ConfigKeys.OUTPUT, output);
        
        // Metadata configuration
        Map<String, Object> metadata = new LinkedHashMap<>();
        metadata.put(Constants.ConfigKeys.SAVE_METADATA, true);
        metadata.put(Constants.ConfigKeys.FILENAME, Constants.FileConstants.DEFAULT_METADATA_FILENAME);
        metadata.put(Constants.ConfigKeys.INCLUDE_SURVEY_DETAILS, true);
        metadata.put(Constants.ConfigKeys.INCLUDE_EXPORT_STATUS, true);
        config.put(Constants.ConfigKeys.METADATA, metadata);
        
        return config;
    }

    /**
     * Load configuration from YAML file
     */
    private void loadConfig() {
        try (FileInputStream input = new FileInputStream(configFile)) {
            config = yaml.load(input);
            
            if (config == null) {
                throw new ConfigurationError("Configuration file is empty");
            }
            
            logger.info("Loaded configuration from: {}", configFile);
            validateConfig();
        } catch (IOException e) {
            throw new ConfigurationError(String.format(Constants.ErrorMessages.CONFIG_FILE_NOT_FOUND, configFile));
        }
    }

    /**
     * Validate the loaded configuration
     */
    private void validateConfig() {
        List<String> requiredSections = Arrays.asList(
            Constants.ConfigKeys.ENVIRONMENT,
            Constants.ConfigKeys.AUTH,
            Constants.ConfigKeys.API,
            Constants.ConfigKeys.EXPORT,
            Constants.ConfigKeys.OUTPUT
        );

        for (String section : requiredSections) {
            if (!config.containsKey(section)) {
                throw new ConfigurationError("Missing required configuration section: " + section);
            }
        }

        // Validate environment configuration
        @SuppressWarnings("unchecked")
        Map<String, Object> envConfig = (Map<String, Object>) config.get(Constants.ConfigKeys.ENVIRONMENT);
        
        if (!envConfig.containsKey(Constants.ConfigKeys.DEFAULT)) {
            throw new ConfigurationError("Missing default environment configuration");
        }

        String defaultEnv = (String) envConfig.get(Constants.ConfigKeys.DEFAULT);
        if (!Arrays.asList(Constants.Environment.STAGING, Constants.Environment.PRODUCTION).contains(defaultEnv)) {
            throw new ConfigurationError(String.format(Constants.ErrorMessages.INVALID_ENVIRONMENT, defaultEnv));
        }

        if (!envConfig.containsKey(Constants.ConfigKeys.ENVIRONMENTS)) {
            throw new ConfigurationError("Missing environment-specific configurations");
        }

        @SuppressWarnings("unchecked")
        Map<String, Object> environments = (Map<String, Object>) envConfig.get(Constants.ConfigKeys.ENVIRONMENTS);
        
        for (Map.Entry<String, Object> entry : environments.entrySet()) {
            @SuppressWarnings("unchecked")
            Map<String, Object> envSettings = (Map<String, Object>) entry.getValue();
            
            if (!envSettings.containsKey(Constants.ConfigKeys.BASE_URL)) {
                throw new ConfigurationError("Missing base_url for environment: " + entry.getKey());
            }
            if (!envSettings.containsKey(Constants.ConfigKeys.TOKEN_URL)) {
                throw new ConfigurationError("Missing token_url for environment: " + entry.getKey());
            }
        }
    }

    /**
     * Get a configuration value using dot notation
     */
    public Object get(String keyPath) {
        return get(keyPath, null);
    }

    /**
     * Get a configuration value using dot notation with default
     */
    public Object get(String keyPath, Object defaultValue) {
        String[] keys = keyPath.split("\\.");
        Object value = config;

        try {
            for (String key : keys) {
                @SuppressWarnings("unchecked")
                Map<String, Object> map = (Map<String, Object>) value;
                value = map.get(key);
                if (value == null) {
                    return defaultValue;
                }
            }
            return value;
        } catch (ClassCastException | NullPointerException e) {
            return defaultValue;
        }
    }

    /**
     * Get configuration for a specific environment
     */
    public Map<String, String> getEnvironmentConfig(String environment) {
        if (environment == null) {
            environment = (String) get(Constants.ConfigKeys.ENVIRONMENT + "." + Constants.ConfigKeys.DEFAULT);
        }

        @SuppressWarnings("unchecked")
        Map<String, Object> envConfig = (Map<String, Object>) get(
            Constants.ConfigKeys.ENVIRONMENT + "." + Constants.ConfigKeys.ENVIRONMENTS + "." + environment
        );
        
        if (envConfig == null) {
            throw new ConfigurationError("Environment configuration not found: " + environment);
        }

        Map<String, String> result = new HashMap<>();
        for (Map.Entry<String, Object> entry : envConfig.entrySet()) {
            result.put(entry.getKey(), String.valueOf(entry.getValue()));
        }
        
        return result;
    }

    /**
     * Get the configured date range for exports
     */
    public Map<String, Long> getDateRange() {
        @SuppressWarnings("unchecked")
        Map<String, Object> dateConfig = (Map<String, Object>) get(Constants.ConfigKeys.EXPORT + "." + Constants.ConfigKeys.DATE_RANGE);

        // Check for absolute dates first
        String absoluteStart = (String) dateConfig.get(Constants.ConfigKeys.ABSOLUTE_START_DATE);
        String absoluteEnd = (String) dateConfig.get(Constants.ConfigKeys.ABSOLUTE_END_DATE);

        if (absoluteStart != null && absoluteEnd != null) {
            // Convert ISO date strings to timestamps
            LocalDateTime startDt = LocalDateTime.parse(absoluteStart);
            LocalDateTime endDt = LocalDateTime.parse(absoluteEnd);
            
            long startTime = startDt.toEpochSecond(java.time.ZoneOffset.UTC) * 1000;
            long endTime = endDt.toEpochSecond(java.time.ZoneOffset.UTC) * 1000;
            
            Map<String, Long> result = new HashMap<>();
            result.put("start_time", startTime);
            result.put("end_time", endTime);
            return result;
        } else {
            // Use relative date range
            Integer daysBack = (Integer) dateConfig.getOrDefault(Constants.ConfigKeys.DEFAULT_DAYS_BACK, 30);
            long endTime = System.currentTimeMillis();
            long startTime = endTime - (daysBack * Constants.TimeConstants.MS_PER_DAY);
            
            Map<String, Long> result = new HashMap<>();
            result.put("start_time", startTime);
            result.put("end_time", endTime);
            return result;
        }
    }

    /**
     * Get survey filtering configuration
     */
    public Map<String, Object> getSurveyFilter() {
        @SuppressWarnings("unchecked")
        Map<String, Object> requestConfig = (Map<String, Object>) get(Constants.ConfigKeys.EXPORT + "." + Constants.ConfigKeys.REQUEST);

        Map<String, Object> result = new HashMap<>();
        result.put("max_surveys", requestConfig.get(Constants.ConfigKeys.MAX_SURVEYS));
        result.put("survey_ids", requestConfig.get(Constants.ConfigKeys.SURVEY_IDS));
        result.put("exclude_survey_ids", requestConfig.get(Constants.ConfigKeys.EXCLUDE_SURVEY_IDS));
        
        return result;
    }

    /**
     * Check if a survey should be included based on configuration
     */
    public boolean shouldIncludeSurvey(int surveyId, String surveyName) {
        Map<String, Object> filterConfig = getSurveyFilter();
        
        @SuppressWarnings("unchecked")
        List<Integer> surveyIds = (List<Integer>) filterConfig.get("survey_ids");
        @SuppressWarnings("unchecked")
        List<Integer> excludeSurveyIds = (List<Integer>) filterConfig.get("exclude_survey_ids");

        // Precedence 1: survey_ids (inclusion) takes highest priority
        if (surveyIds != null) {
            if (surveyIds.contains(surveyId)) {
                logger.debug("Including survey {} ({}) - in survey_ids list", surveyId, surveyName);
                return true;
            } else {
                logger.debug("Skipping survey {} ({}) - not in survey_ids list", surveyId, surveyName);
                return false;
            }
        }

        // Precedence 2: exclude_survey_ids (exclusion)
        if (excludeSurveyIds != null) {
            if (excludeSurveyIds.contains(surveyId)) {
                logger.debug("Skipping survey {} ({}) - in exclude_survey_ids list", surveyId, surveyName);
                return false;
            }
        }

        // If no inclusion/exclusion rules, include the survey
        logger.debug("Including survey {} ({}) - no filtering rules apply", surveyId, surveyName);
        return true;
    }

    /**
     * Get output configuration
     */
    public Map<String, Object> getOutputConfig() {
        @SuppressWarnings("unchecked")
        Map<String, Object> outputConfig = (Map<String, Object>) get(Constants.ConfigKeys.OUTPUT);
        return outputConfig != null ? outputConfig : new HashMap<>();
    }

    /**
     * Get the survey output directory path
     */
    public String getSurveyOutputDirectory() {
        Map<String, Object> outputConfig = getOutputConfig();
        String baseDir = (String) outputConfig.getOrDefault(Constants.ConfigKeys.BASE_DIRECTORY, Constants.FileConstants.OUTPUT_BASE_DIR);
        String surveyDir = (String) outputConfig.getOrDefault(Constants.ConfigKeys.SURVEY_EXPORTS_DIR, Constants.FileConstants.SURVEY_EXPORTS_DIR);

        // Get the repo root (same logic as findConfigFile)
        String currentDir = System.getProperty("user.dir");
        String repoRoot = findRepoRoot(currentDir);
        
        // Always use the repo root as the base, then add java/output
        String fullBaseDir = Paths.get(repoRoot, "java", baseDir).toString();
        
        return Paths.get(fullBaseDir, surveyDir).toString();
    }

    /**
     * Get metadata configuration
     */
    public Map<String, Object> getMetadataConfig() {
        @SuppressWarnings("unchecked")
        Map<String, Object> metadataConfig = (Map<String, Object>) get(Constants.ConfigKeys.METADATA);
        return metadataConfig != null ? metadataConfig : new HashMap<>();
    }

    /**
     * Reload configuration from file
     */
    public void reload() {
        loadConfig();
        logger.info("Configuration reloaded successfully");
    }

    /**
     * Custom exception for configuration errors
     */
    public static class ConfigurationError extends RuntimeException {
        public ConfigurationError(String message) {
            super(message);
        }
    }
} 