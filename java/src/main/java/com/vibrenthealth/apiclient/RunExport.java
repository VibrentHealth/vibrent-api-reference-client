package com.vibrenthealth.apiclient;

import com.vibrenthealth.apiclient.core.ConfigManager;
import com.vibrenthealth.apiclient.core.Constants;
import com.vibrenthealth.apiclient.core.SurveyDataExporter;
import com.vibrenthealth.apiclient.utils.Helpers;
import io.github.cdimascio.dotenv.Dotenv;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;

/**
 * Main entry point for Vibrent Health API Client
 */
public class RunExport {
    private static final Logger logger = LoggerFactory.getLogger(RunExport.class);

    public static void main(String[] args) {
        try {
            // Parse command line arguments
            String configFile = null;
            if (args.length > 0) {
                configFile = args[0];
            }

            // Load configuration
            ConfigManager configManager = new ConfigManager(configFile);

            // Setup logging
            Helpers.setupLogging();
            logger.info("Vibrent Health API Client - Java Reference Implementation");

            // Print license information
            printLicenseInfo();

            // Initialize and run exporter
            String environment = System.getProperty("VIBRENT_ENVIRONMENT");
            if (environment == null) {
                environment = (String) configManager.get(Constants.ConfigKeys.ENVIRONMENT + "." + Constants.ConfigKeys.DEFAULT);
            }

            SurveyDataExporter exporter = new SurveyDataExporter(configManager, environment, null);
            exporter.runExport();

        } catch (ConfigManager.ConfigurationError e) {
            System.err.println("Configuration error: " + e.getMessage());
            System.err.println("\nPlease make sure to:");
            System.err.println("1. Replace placeholder URLs in shared/config/vibrent_config.yaml with your actual Vibrent Health API URLs");
            System.err.println("2. Set VIBRENT_CLIENT_ID and VIBRENT_CLIENT_SECRET environment variables");
            System.err.println("3. You can specify a custom config file: java -jar vibrent-api-client.jar <path_to_config>");
            System.exit(1);
        } catch (Exception e) {
            logger.error("Application failed: {}", e.getMessage());
            System.exit(1);
        }
    }

    /**
     * Print license and warning information
     */
    private static void printLicenseInfo() {
        System.out.println("Vibrent Health API Client - Reference Implementation");
        System.out.println("=".repeat(50));
        System.out.println("⚠️  IMPORTANT: This is a reference implementation only");
        System.out.println("   - Not intended for production use without testing");
        System.out.println("   - No active support or updates provided");
        System.out.println("   - No version compatibility guarantees");
        System.out.println("   - Report issues to info@vibrenthealth.com");
        System.out.println("   - Use at your own risk");
        System.out.println("=".repeat(50));
    }
} 