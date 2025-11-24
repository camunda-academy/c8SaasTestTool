package com.camunda.academy;

import io.camunda.client.CamundaClient;
import io.camunda.client.api.response.Topology;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletionException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Camunda 8 SaaS Connection Test Tool - Java Version
 * 
 * This tool tests connectivity to Camunda 8 SaaS by:
 * 1. Checking Java version (must be 17+)
 * 2. Loading environment variables from envVarsExtended.txt
 * 3. Creating Camunda cloud client
 * 4. Testing connection via topology request
 * 
 * Exit codes:
 * 0 = Success
 * 1 = SSL Error
 * 2 = Connection Error
 * 3 = Authentication Error
 * 4 = Other/Unexpected Error
 * 
 * Author: Camunda Academy
 */
public class TestConnection {

    private static final int EXIT_SUCCESS = 0;
    private static final int EXIT_SSL_ERROR = 1;
    private static final int EXIT_CONNECTION_ERROR = 2;
    private static final int EXIT_AUTH_ERROR = 3;
    private static final int EXIT_OTHER_ERROR = 4;

    private static final String ENV_FILE = "envVarsExtended.txt";

    public static void main(String[] args) {
        try {
            checkJavaVersion();

            System.out.println("Loading environment variables...");
            Map<String, String> envVars = loadEnvVars();

            System.out.println("Connecting to Camunda 8 SaaS...");
            testConnection(envVars);

            printSuccess();
            System.exit(EXIT_SUCCESS);

        } catch (Exception e) {
            handleException(e);
        }
    }

    private static void checkJavaVersion() {
        String javaVersion = System.getProperty("java.version");
        String[] versionParts = javaVersion.split("\\.");
        int majorVersion;

        try {
            if (versionParts[0].equals("1")) {
                majorVersion = Integer.parseInt(versionParts[1]);
            } else {
                majorVersion = Integer.parseInt(versionParts[0]);
            }

            if (majorVersion < 17) {
                printError("Java 17 or higher is required. Current version: " + javaVersion +
                        "\nPlease upgrade Java or contact your training manager." +
                        "\nDownload Java from: https://adoptium.net/");
                System.exit(EXIT_OTHER_ERROR);
            }

            System.out.println("Java version check passed: " + javaVersion);

        } catch (NumberFormatException e) {
            System.out.println("Warning: Could not parse Java version, continuing anyway...");
        }
    }

    private static Map<String, String> loadEnvVars() throws IOException {
        Path envPath = Paths.get(ENV_FILE);

        if (!Files.exists(envPath)) {
            Path parentPath = Paths.get("..", ENV_FILE);
            if (Files.exists(parentPath)) {
                envPath = parentPath;
            } else {
                throw new IOException(ENV_FILE
                        + " file not found. Double check that this file is available in this directory or parent directory");
            }
        }

        Map<String, String> envVars = new HashMap<>();
        Pattern pattern = Pattern.compile("export\\s+(\\w+)='(.+)'");

        try (BufferedReader reader = new BufferedReader(new FileReader(envPath.toFile()))) {
            String line;
            int lineNum = 0;

            while ((line = reader.readLine()) != null) {
                lineNum++;
                line = line.trim();

                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }

                Matcher matcher = pattern.matcher(line);
                if (matcher.matches()) {
                    String varName = matcher.group(1);
                    String varValue = matcher.group(2);
                    envVars.put(varName, varValue);
                } else {
                    throw new IOException("Invalid format in " + ENV_FILE + " at line " + lineNum + ": " + line);
                }
            }
        }

        String[] requiredVars = {
                "CAMUNDA_CLUSTER_ID",
                "CAMUNDA_CLIENT_ID",
                "CAMUNDA_CLIENT_SECRET",
                "CAMUNDA_CLUSTER_REGION"
        };

        for (String var : requiredVars) {
            if (!envVars.containsKey(var)) {
                throw new IOException("Missing required environment variable: " + var);
            }
        }

        return envVars;
    }

    private static void testConnection(Map<String, String> envVars) throws Exception {
        String clusterId = envVars.get("CAMUNDA_CLUSTER_ID");
        String clientId = envVars.get("CAMUNDA_CLIENT_ID");
        String clientSecret = envVars.get("CAMUNDA_CLIENT_SECRET");
        String region = envVars.get("CAMUNDA_CLUSTER_REGION");

        System.out.println("Using client ID: " + maskCredential(clientId));

        try (CamundaClient client = CamundaClient.newCloudClientBuilder()
                .withClusterId(clusterId)
                .withClientId(clientId)
                .withClientSecret(clientSecret)
                .withRegion(region)
                .build()) {

            System.out.println("Testing connection...");
            Topology topology = client.newTopologyRequest().send().join();

            if (topology.getBrokers().isEmpty()) {
                throw new Exception("Connected but no brokers found in topology");
            }

        } catch (CompletionException e) {
            throw (Exception) e.getCause();
        }
    }

    private static String maskCredential(String credential) {
        if (credential == null || credential.length() < 8) {
            return "***";
        }
        return credential.substring(0, 4) + "****" + credential.substring(credential.length() - 4);
    }

    private static void handleException(Exception e) {
        String errorMsg = e.getMessage() != null ? e.getMessage().toLowerCase() : "";
        String className = e.getClass().getName().toLowerCase();

        if (errorMsg.contains("ssl") || errorMsg.contains("certificate") || className.contains("ssl")) {
            printError("SSL error: " + e.getMessage());
            System.exit(EXIT_SSL_ERROR);
        } else if (errorMsg.contains("connection") || errorMsg.contains("connect") ||
                errorMsg.contains("network") || errorMsg.contains("timeout") ||
                errorMsg.contains("timed out") || className.contains("connection") ||
                className.contains("timeout")) {
            printError("Connection error: " + e.getMessage());
            System.exit(EXIT_CONNECTION_ERROR);
        } else if (errorMsg.contains("401") || errorMsg.contains("403") ||
                errorMsg.contains("unauthorized") || errorMsg.contains("forbidden") ||
                errorMsg.contains("authentication") || errorMsg.contains("token") ||
                errorMsg.contains("credential")) {
            printError("Authentication error: " + e.getMessage());
            System.exit(EXIT_AUTH_ERROR);
        } else {
            printError("Unexpected error: " + e.getMessage());
            if (e.getCause() != null) {
                System.err.println("Caused by: " + e.getCause().getMessage());
            }
            System.exit(EXIT_OTHER_ERROR);
        }
    }

    private static void printError(String message) {
        System.out.println("***** CONNECTION FAILED: " + message + " *****");
    }

    private static void printSuccess() {
        System.out.println("***** CONNECTION SUCCESSFUL *****");
    }
}
