package com.vibrenthealth.apiclient.examples;

import com.vibrenthealth.apiclient.core.ConfigManager;
import com.vibrenthealth.apiclient.core.SurveyDataExporter;
import com.vibrenthealth.apiclient.utils.Helpers;
import io.github.cdimascio.dotenv.Dotenv;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Example showing how to use the Vibrent Health API Client programmatically
 */
public class ConfiguredExport {
    private static final Logger logger = LoggerFactory.getLogger(ConfiguredExport.class);

    public static void main(String[] args) {
        // Load environment variables
        Dotenv dotenv = Dotenv.load();
        dotenv.entries().forEach(entry -> 
            System.setProperty(entry.getKey(), entry.getValue())
        );

        try {
            // Setup logging
            Helpers.setupLogging();
            logger.info("Starting configured export example");

            // Load configuration from a specific file
            String configFile = "shared/config/vibrent_config.yaml";
            ConfigManager configManager = new ConfigManager(configFile);

            // Create exporter with specific environment
            String environment = "staging"; // or "production"
            SurveyDataExporter exporter = new SurveyDataExporter(configManager, environment, null);

            // Run the export
            exporter.runExport();

            logger.info("Configured export completed successfully");

        } catch (Exception e) {
            logger.error("Configured export failed: {}", e.getMessage());
            System.exit(1);
        }
    }
} 