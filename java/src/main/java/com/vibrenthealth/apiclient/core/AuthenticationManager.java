package com.vibrenthealth.apiclient.core;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.concurrent.TimeUnit;
import java.util.Map;

/**
 * Handles OAuth2 authentication for Vibrent Health APIs
 */
public class AuthenticationManager {
    private static final Logger logger = LoggerFactory.getLogger(AuthenticationManager.class);
    
    private final ConfigManager configManager;
    private final String environment;
    private final String clientId;
    private final String clientSecret;
    private final String tokenUrl;
    private final int timeout;
    private final int refreshBuffer;
    
    private String accessToken;
    private Long tokenExpiresAt;
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper;

    public AuthenticationManager(ConfigManager configManager, String environment) {
        this.configManager = configManager;
        this.environment = environment != null ? environment : 
            (String) configManager.get(Constants.ConfigKeys.ENVIRONMENT + "." + Constants.ConfigKeys.DEFAULT);
        
        this.clientId = System.getenv("VIBRENT_CLIENT_ID");
        this.clientSecret = System.getenv("VIBRENT_CLIENT_SECRET");
        
        if (this.clientId == null || this.clientSecret == null) {
            throw new VibrentHealthAPIError(Constants.ErrorMessages.MISSING_CREDENTIALS);
        }

        // Get environment configuration
        Map<String, String> envConfig = configManager.getEnvironmentConfig(this.environment);
        this.tokenUrl = envConfig.get(Constants.ConfigKeys.TOKEN_URL);
        
        if (this.tokenUrl == null) {
            throw new VibrentHealthAPIError(
                String.format(Constants.ErrorMessages.INVALID_ENVIRONMENT, this.environment)
            );
        }

        // Get auth configuration
        Map<String, Object> authConfig = (Map<String, Object>) configManager.get(Constants.ConfigKeys.AUTH);
        this.timeout = (Integer) authConfig.getOrDefault(Constants.ConfigKeys.TIMEOUT, Constants.TimeConstants.DEFAULT_TIMEOUT);
        this.refreshBuffer = (Integer) authConfig.getOrDefault(Constants.ConfigKeys.REFRESH_BUFFER, Constants.TimeConstants.TOKEN_REFRESH_BUFFER);

        this.httpClient = new OkHttpClient.Builder()
            .connectTimeout(timeout, TimeUnit.SECONDS)
            .readTimeout(timeout, TimeUnit.SECONDS)
            .writeTimeout(timeout, TimeUnit.SECONDS)
            .build();
            
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Authenticate and get access token
     */
    public String authenticate() {
        logger.info("Authenticating with {} environment", environment);
        logger.info("Token URL: {}", tokenUrl);

        String credentials = okhttp3.Credentials.basic(clientId, clientSecret);
        
        RequestBody formBody = new FormBody.Builder()
            .add("grant_type", "client_credentials")
            .build();

        Request request = new Request.Builder()
            .url(tokenUrl)
            .addHeader(Constants.Headers.AUTHORIZATION, credentials)
            .addHeader(Constants.Headers.CONTENT_TYPE, Constants.Headers.APPLICATION_X_WWW_FORM_URLENCODED)
            .post(formBody)
            .build();

        logger.info("Client ID: {}", clientId);
        logger.info("Client Secret: {}...", clientSecret.substring(0, Math.min(8, clientSecret.length())));

        try (Response response = httpClient.newCall(request).execute()) {
            logger.info("Response status: {}", response.code());

            if (response.isSuccessful() && response.body() != null) {
                String responseBody = response.body().string();
                JsonNode tokenData = objectMapper.readTree(responseBody);
                
                this.accessToken = tokenData.get("access_token").asText();
                int expiresIn = tokenData.has("expires_in") ? tokenData.get("expires_in").asInt() : 3600;
                this.tokenExpiresAt = System.currentTimeMillis() / 1000 + expiresIn;

                logger.info("Authentication successful");
                return this.accessToken;
            } else {
                // Log error response for debugging
                String errorBody = response.body() != null ? response.body().string() : "No response body";
                logger.error("Authentication failed: {}", errorBody);
                
                throw new VibrentHealthAPIError(
                    String.format(Constants.ErrorMessages.AUTHENTICATION_FAILED, 
                        "HTTP " + response.code() + ": " + errorBody)
                );
            }
        } catch (IOException e) {
            throw new VibrentHealthAPIError(
                String.format(Constants.ErrorMessages.AUTHENTICATION_FAILED, e.getMessage())
            );
        }
    }

    /**
     * Get a valid access token, refreshing if necessary
     */
    public String getValidToken() {
        if (accessToken == null || 
            (tokenExpiresAt != null && System.currentTimeMillis() / 1000 >= tokenExpiresAt - refreshBuffer)) {
            authenticate();
        }
        return accessToken;
    }

    /**
     * Custom exception for Vibrent Health API errors
     */
    public static class VibrentHealthAPIError extends RuntimeException {
        public VibrentHealthAPIError(String message) {
            super(message);
        }
    }
} 