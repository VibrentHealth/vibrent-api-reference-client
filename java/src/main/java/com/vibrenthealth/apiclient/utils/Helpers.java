package com.vibrenthealth.apiclient.utils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.logging.LogManager;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

/**
 * Utility helper functions for Vibrent Health API Client
 */
public class Helpers {
    private static final Logger logger = LoggerFactory.getLogger(Helpers.class);

    /**
     * Setup logging configuration
     */
    public static void setupLogging() {
        // Create logs directory if it doesn't exist
        try {
            String logsDir = getLogsDirectory();
            Files.createDirectories(Paths.get(logsDir));
            logger.info("Logs directory: {}", logsDir);
        } catch (IOException e) {
            logger.warn("Failed to create logs directory: {}", e.getMessage());
        }
    }

    /**
     * Get the logs directory path
     */
    public static String getLogsDirectory() {
        // Get the repo root by finding the directory that contains both 'java' and 'shared' folders
        String currentDir = System.getProperty("user.dir");
        String repoRoot = findRepoRoot(currentDir);
        
        // Always use the repo root as the base, then add java/output/logs
        return Paths.get(repoRoot, "java", "output", "logs").toString();
    }

    /**
     * Find the repo root by looking for directories containing both 'java' and 'shared' folders
     */
    private static String findRepoRoot(String currentDir) {
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
     * Safely create an object from a map with error handling
     */
    public static <T> T safeFromMap(Class<T> clazz, Map<String, Object> data, Logger logger) {
        try {
            if (clazz == com.vibrenthealth.apiclient.models.Survey.class) {
                @SuppressWarnings("unchecked")
                T result = (T) com.vibrenthealth.apiclient.models.Survey.fromMap(data);
                return result;
            } else if (clazz == com.vibrenthealth.apiclient.models.ExportRequest.class) {
                @SuppressWarnings("unchecked")
                T result = (T) com.vibrenthealth.apiclient.models.ExportRequest.fromMap(data);
                return result;
            } else if (clazz == com.vibrenthealth.apiclient.models.ExportStatus.class) {
                @SuppressWarnings("unchecked")
                T result = (T) com.vibrenthealth.apiclient.models.ExportStatus.fromMap(data);
                return result;
            } else if (clazz == com.vibrenthealth.apiclient.models.ExportMetadata.class) {
                @SuppressWarnings("unchecked")
                T result = (T) com.vibrenthealth.apiclient.models.ExportMetadata.fromMap(data);
                return result;
            } else {
                throw new IllegalArgumentException("Unsupported class: " + clazz.getName());
            }
        } catch (Exception e) {
            logger.error("Failed to create {} from map: {}", clazz.getSimpleName(), e.getMessage());
            throw e;
        }
    }

    /**
     * Get current timestamp in ISO format
     */
    public static String getCurrentTimestamp() {
        return LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
    }

    /**
     * Format duration in seconds to a human-readable string
     */
    public static String formatDuration(double seconds) {
        if (seconds < 60) {
            return String.format("%.2f seconds", seconds);
        } else if (seconds < 3600) {
            return String.format("%.2f minutes", seconds / 60);
        } else {
            return String.format("%.2f hours", seconds / 3600);
        }
    }
} 