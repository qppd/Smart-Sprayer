#ifndef FIREBASE_CONFIG_H
#define FIREBASE_CONFIG_H

#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "FIREBASE_CREDENTIALS.h"
#include "NTP_CONFIG.h"

#define MAX_TOKENS 10  // Maximum number of device tokens to store

// Forward declaration for communication interface
class ESPCommunication;

class FirebaseManager {
public:
    FirebaseManager() {
        tokenCount = 0;
        tokenParentPath = "smart-sprayer";
        controlParentPath = "smart-sprayer/devices";
        deviceId = "SmartSprayer_ESP32_001"; // Default device ID
        espComm = nullptr;
        lastTokenCheck = 0;
        controlStreamActive = false;
        lastMode = "";
        lastFanSpeed = -1;
        globalFirebaseManager = this;
    }

    void begin() {
        // Connect to Wi-Fi
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        Serial.print("Connecting to Wi-Fi");
        while (WiFi.status() != WL_CONNECTED) {
            Serial.print(".");
            delay(300);
        }

        Serial.println();
        Serial.print("Connected with IP: ");
        Serial.println(WiFi.localIP());
        Serial.println();

        // Print network diagnostics for debugging
        printNetworkDiagnostics();

        // Since NTP is already initialized in WiFiManager, just get current time
        Serial.println("Using NTP time configured during WiFi setup...");
        getNTPDate();

        Serial.printf("Firebase Client v%s\n\n", FIREBASE_CLIENT_VERSION);

        // Assign Firebase credentials
        config.api_key = API_KEY;
        config.database_url = DATABASE_URL;

        config.service_account.data.client_email = FIREBASE_CLIENT_EMAIL;
        config.service_account.data.project_id = FIREBASE_PROJECT_ID;
        config.service_account.data.private_key = PRIVATE_KEY;

        // Optional: Token status callback (using library's default)
        // config.token_status_callback = tokenStatusCallback;

        // Set network reconnection
        Firebase.reconnectNetwork(true);

        // Configure buffer sizes - Reduced for ESP32 memory constraints
        fbdo.setBSSLBufferSize(1024, 512);  // Reduced from 4096, 1024
        fbdo.setResponseSize(1024);         // Reduced from 4096

        // Set timeouts to handle slow connections
        config.timeout.serverResponse = 10 * 1000; // 10 seconds
        config.timeout.socketConnection = 10 * 1000; // 10 seconds
        config.timeout.sslHandshake = 30 * 1000; // 30 seconds
        config.timeout.rtdbKeepAlive = 45 * 1000; // 45 seconds
        config.timeout.rtdbStreamReconnect = 1 * 1000; // 1 second
        config.timeout.rtdbStreamError = 3 * 1000; // 3 seconds

        // Begin Firebase with retry logic
        Serial.println("Initializing Firebase...");

        int retryCount = 0;
        const int maxRetries = 5;
        const int baseDelay = 2000; // 2 seconds

        while (retryCount < maxRetries) {
            Firebase.begin(&config, &auth);

            // Wait for Firebase to initialize with timeout
            int initWait = 0;
            const int maxInitWait = 30; // 30 seconds max wait

            while (!Firebase.ready() && initWait < maxInitWait) {
                delay(1000);
                initWait++;
                Serial.print(".");
            }

            if (Firebase.ready()) {
                Serial.println("\nFirebase initialized successfully!");
                break;
            } else {
                retryCount++;
                Serial.printf("\nFirebase initialization failed (attempt %d/%d)\n", retryCount, maxRetries);

                if (retryCount < maxRetries) {
                    int delayTime = baseDelay * (1 << (retryCount - 1)); // Exponential backoff
                    Serial.printf("Retrying in %d seconds...\n", delayTime / 1000);
                    delay(delayTime);

                    // Get current time before retry
                    getNTPDate();
                }
            }
        }

        if (!Firebase.ready()) {
            Serial.println("Failed to initialize Firebase after all retries!");
            return;
        }

        // Initialize streams for real-time monitoring
        initializeStreams();
    }

    void setESPCommunication(ESPCommunication* comm) {
        espComm = comm;
    }

    void initializeStreams() {
        Serial.println("Initializing Firebase streams...");

        // Initialize control stream for real-time manual/auto and fan speed monitoring
        initializeControlStream();

        // Load tokens once at startup (non-streaming)
        loadTokensFromDatabase();

        Serial.println("Firebase streams initialization completed!");
    }

    void initializeControlStream() {
        String controlPath = controlParentPath + "/" + deviceId + "/control";
        Serial.println("Starting control stream for path: " + controlPath);

        if (!Firebase.RTDB.beginMultiPathStream(&controlStream, controlPath)) {
            Serial.printf("Control stream initialization failed: %s\n", controlStream.errorReason().c_str());
            controlStreamActive = false;
        } else {
            Firebase.RTDB.setMultiPathStreamCallback(&controlStream, controlStreamCallback, controlStreamTimeoutCallback);
            controlStreamActive = true;
            Serial.println("Firebase control stream initialized successfully!");
        }
    }

    void handleStreams() {
        // Handle control stream for real-time updates
        if (controlStreamActive && !Firebase.RTDB.readStream(&controlStream)) {
            Serial.printf("Control stream error: %s\n", controlStream.errorReason().c_str());

            // Attempt to reinitialize if stream fails
            if (controlStream.httpCode() != FIREBASE_ERROR_HTTP_CODE_OK) {
                Serial.println("Attempting to reinitialize control stream...");
                initializeControlStream();
            }
        }

        // Check tokens periodically (non-realtime)
        checkTokensUpdate();
    }

    void checkTokensUpdate() {
        if (millis() - lastTokenCheck >= TOKEN_CHECK_INTERVAL) {
            Serial.println("Performing periodic token check...");
            loadTokensFromDatabase();
            lastTokenCheck = millis();
        }
    }

    void loadTokensFromDatabase() {
        String tokenPath = tokenParentPath + "/tokens";

        if (Firebase.RTDB.getJSON(&fbdo, tokenPath)) {
            Serial.println("Loading tokens from database...");

            FirebaseJson json;
            FirebaseJsonData result;
            json.setJsonData(fbdo.jsonString());

            // Clear current tokens
            tokenCount = 0;

            // Begin iterating through all children under /tokens
            size_t count = json.iteratorBegin();

            for (size_t i = 0; i < count; i++) {
                FirebaseJson::IteratorValue value = json.valueAt(i);
                String pushID = value.key;

                // Skip any key that doesn't contain a nested object
                if (!value.value.startsWith("{")) {
                    continue;
                }

                String fullPath = pushID + "/device_token";

                if (json.get(result, fullPath)) {
                    String deviceToken = result.stringValue;
                    Serial.println("✅ Loaded device_token from " + pushID + ": " + deviceToken);

                    // Add to array if not full
                    if (tokenCount < MAX_TOKENS) {
                        deviceTokens[tokenCount] = deviceToken;
                        tokenCount++;
                    }
                }
            }

            json.iteratorEnd();
            Serial.println("Token loading completed. Total tokens: " + String(tokenCount));

        } else {
            Serial.printf("Failed to load tokens: %s\n", fbdo.errorReason().c_str());
        }
    }

    void sendMessageToAll(String title, String body) {
        // TEMPORARILY DISABLED FOR MEMORY OPTIMIZATION
        Serial.println("📲 FCM disabled - would send: " + title + " - " + body);
        /*
        for (int i = 0; i < tokenCount; i++) {
            Serial.println("📲 Sending to: " + deviceTokens[i]);

            FCM_HTTPv1_JSON_Message msg;
            msg.token = deviceTokens[i];
            msg.notification.title = title;
            msg.notification.body = body;

            FirebaseJson payload;
            payload.add("status", "1");
            payload.add("device", "smartfan");
            msg.data = payload.raw();

            if (Firebase.FCM.send(&fbdo, &msg)) {
                Serial.println("Notification sent successfully!");
            } else {
                Serial.println("Error sending notification: " + fbdo.errorReason());
            }
        }
        */
    }

    void sendMessage(String title, String body) {
        // TEMPORARILY DISABLED FOR MEMORY OPTIMIZATION
        Serial.println("📲 FCM disabled - would send: " + title + " - " + body);
        /*
        Serial.print("Send Firebase Cloud Messaging... ");

        FCM_HTTPv1_JSON_Message msg;
        msg.token = DEVICE_REGISTRATION_ID_TOKEN;

        msg.notification.title = title;
        msg.notification.body = body;

        FirebaseJson payload;
        payload.add("status", "1");
        payload.add("device", "smartfan");

        msg.data = payload.raw();

        if (Firebase.FCM.send(&fbdo, &msg)) {
            Serial.printf("FCM sent successfully!\n%s\n\n", Firebase.FCM.payload(&fbdo).c_str());
        } else {
            Serial.println("FCM Error: " + fbdo.errorReason());
        }
        */
    }

    void updateDeviceCurrent(const String& deviceId, float temperature, int fanSpeed, const String& mode, unsigned long lastUpdate, float voltage, float current, float watt, float kwh) {
        // Use static String to avoid frequent allocations
        static String path;
        path = "/smart-sprayer/devices/" + deviceId + "/current";

        FirebaseJson json;
        json.set("temperature", temperature);
        json.set("fanSpeed", fanSpeed);
        json.set("mode", mode);
        json.set("lastUpdate", (int64_t)lastUpdate);
        json.set("voltage", voltage);
        json.set("current", current);
        json.set("watt", watt);
        json.set("kwh", kwh);

        // Update local mode tracking to prevent unnecessary commands
        lastMode = mode;
        lastFanSpeed = fanSpeed;

        if (Firebase.RTDB.setJSON(&fbdo, path, &json)) {
            Serial.println("Device current state updated in Firebase.");
        } else {
            Serial.print("Failed to update device current: ");
            Serial.println(fbdo.errorReason());
        }
    }

    void logDeviceData(const String& deviceId, unsigned long timestamp, float temperature, int fanSpeed, float voltage, float current, float watt, float kwh) {
        // Use static Strings to avoid frequent allocations
        static String logId;
        static String path;

        logId = String(timestamp);
        path = "/smart-sprayer/devices/" + deviceId + "/logs/" + logId;

        FirebaseJson json;
        json.set("timestamp", (int64_t)timestamp);
        json.set("datetime", getFormattedDateTimeWithFallback()); // Add human-readable datetime
        json.set("temperature", temperature);
        json.set("fanSpeed", fanSpeed);
        json.set("voltage", voltage);
        json.set("current", current);
        json.set("watt", watt);
        json.set("kwh", kwh);

        if (Firebase.RTDB.setJSON(&fbdo, path, &json)) {
            Serial.println(getCurrentLogPrefix() + "Device log entry added in Firebase.");
        } else {
            Serial.print(getCurrentLogPrefix() + "Failed to add device log: ");
            Serial.println(fbdo.errorReason());
        }
    }

    void sendSmartSprayerData(float distance, int relay1, int relay2, float voltage, float current, float watt, float kwh) {
        // Create JSON object for Smart Sprayer data
        FirebaseJson json;
        json.set("distance", distance);
        json.set("relay1", relay1);
        json.set("relay2", relay2);
        json.set("voltage", voltage);
        json.set("current", current);
        json.set("watt", watt);
        json.set("kwh", kwh);
        json.set("device_type", "smart_sprayer");
        json.set("timestamp", (int64_t)getNTPTimestampWithFallback()); // Use NTP timestamp with fallback
        json.set("datetime", getFormattedDateTimeWithFallback()); // Add human-readable datetime

        Serial.println(getCurrentLogPrefix() + "Sending Smart Sprayer data as JSON...");

        // Send to Firebase under smart-sprayer path
        if (Firebase.RTDB.setJSON(&fbdo, "/smart-sprayer/data", &json)) {
            Serial.println(getCurrentLogPrefix() + "Smart Sprayer data sent successfully!");
        } else {
            Serial.print(getCurrentLogPrefix() + "Error sending Smart Sprayer data: ");
            Serial.println(fbdo.errorReason());
        }
    }

    void resetWiFiSettings() {
        WiFi.disconnect(true);
        ESP.restart();
    }

    bool isReady() {
        return WiFi.status() == WL_CONNECTED && Firebase.ready();
    }

    // Public Firebase objects for callbacks
    FirebaseData fbdo;
    FirebaseData controlStream;  // For manual/auto and fan speed

private:
    FirebaseAuth auth;
    FirebaseConfig config;
    ESPCommunication* espComm;  // Reference to ESP communication

    // Device token management
    String deviceTokens[MAX_TOKENS];
    int tokenCount;
    unsigned long lastTokenCheck;
    const unsigned long TOKEN_CHECK_INTERVAL = 300000; // Check tokens every 5 minutes

    // Stream configuration
    String tokenParentPath;
    String controlParentPath;
    String deviceId;

    // Stream state tracking
    bool controlStreamActive;
    String lastMode;
    int lastFanSpeed;

    // Internal methods
    void printNetworkDiagnostics() {
        Serial.println("\n=== Network Diagnostics ===");

        // WiFi Status
        Serial.printf("WiFi Status: %s\n",
                      WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
        Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("Gateway: %s\n", WiFi.gatewayIP().toString().c_str());
        Serial.printf("DNS Server: %s\n", WiFi.dnsIP().toString().c_str());
        Serial.printf("Signal Strength (RSSI): %d dBm\n", WiFi.RSSI());

        // DNS Resolution Test
        Serial.println("\nTesting DNS resolution...");
        IPAddress ip;
        if (WiFi.hostByName("pool.ntp.org", ip)) {
            Serial.printf("DNS Test: SUCCESS - pool.ntp.org resolved to %s\n", ip.toString().c_str());
        } else {
            Serial.println("DNS Test: FAILED - Could not resolve pool.ntp.org");
        }

        // NTP Time Check
        time_t now = time(nullptr);
        if (now > 1000000000) { // Valid timestamp (after year 2001)
            Serial.printf("NTP Time: SUCCESS - %s", ctime(&now));
        } else {
            Serial.println("NTP Time: FAILED - Time not synchronized");
        }

        // Memory Status
        Serial.printf("Free Heap: %d bytes\n", ESP.getFreeHeap());
        Serial.printf("Heap Fragmentation: %d%%\n", ESP.getHeapFragmentation());

        Serial.println("=== End Diagnostics ===\n");
    }

    // Callback functions
    static void controlStreamCallback(MultiPathStream stream) {
        if (globalFirebaseManager == nullptr || globalFirebaseManager->espComm == nullptr) return;

        Serial.println("🔥 Control Stream Update Received!");
        Serial.println("Path: " + stream.dataPath);
        Serial.println("Value: " + stream.value);

        // Handle mode changes (manual/auto)
        if (stream.get("/mode")) {
            String newMode = stream.value;
            newMode.replace("\"", ""); // Remove quotes from JSON string

            if (newMode != globalFirebaseManager->lastMode) {
                Serial.println("🔄 Mode changed from '" + globalFirebaseManager->lastMode + "' to '" + newMode + "'");
                globalFirebaseManager->lastMode = newMode;

                // Send mode change to ESP32 immediately
                if (globalFirebaseManager->espComm) {
                    globalFirebaseManager->espComm->setMode(newMode);
                    Serial.println("📡 Sent mode change to ESP32: " + newMode);
                }
            }
        }

        // Handle fan speed changes
        if (stream.get("/fanSpeed")) {
            int newFanSpeed = stream.value.toInt();

            if (newFanSpeed != globalFirebaseManager->lastFanSpeed) {
                Serial.println("🌀 Fan speed changed from " + String(globalFirebaseManager->lastFanSpeed) + " to " + String(newFanSpeed));
                globalFirebaseManager->lastFanSpeed = newFanSpeed;

                // Send fan speed change to ESP32 immediately
                if (globalFirebaseManager->espComm) {
                    globalFirebaseManager->espComm->setFanSpeed(newFanSpeed);
                    Serial.println("📡 Sent fan speed change to ESP32: " + String(newFanSpeed));
                }
            }
        }

        // Handle target temperature changes
        if (stream.get("/targetTemperature")) {
            float targetTemp = stream.value.toFloat();
            Serial.println("🌡️ Target temperature changed to: " + String(targetTemp, 1) + "°C");

            // Send target temperature to ESP32 immediately
            if (globalFirebaseManager->espComm) {
                globalFirebaseManager->espComm->setTargetTemperature(targetTemp);
                Serial.println("📡 Sent target temperature to ESP32: " + String(targetTemp, 1) + "°C");
            }
        }

        // Handle manual control enable/disable
        if (stream.get("/manualControl")) {
            bool manualControl = (stream.value == "true");
            String mode = manualControl ? "manual" : "auto";
            Serial.println("🎛️ Manual control " + String(manualControl ? "enabled" : "disabled"));

            // Send manual control state to ESP32
            if (globalFirebaseManager->espComm) {
                globalFirebaseManager->espComm->setMode(mode);
                Serial.println("📡 Sent manual control state to ESP32: " + mode);
            }
        }
    }

    static void controlStreamTimeoutCallback(bool timeout) {
        if (timeout) {
            Serial.println("⏰ Control stream timed out, attempting to resume...");
        }
        if (globalFirebaseManager && !globalFirebaseManager->controlStream.httpConnected()) {
            Serial.printf("❌ Control Stream Error code: %d, reason: %s\n",
                          globalFirebaseManager->controlStream.httpCode(),
                          globalFirebaseManager->controlStream.errorReason().c_str());

            // Mark stream as inactive so it can be reinitialized
            globalFirebaseManager->controlStreamActive = false;
        }
    }
};

// Global instance for callback access
extern FirebaseManager* globalFirebaseManager;

// Implementation of initFIREBASE
void initFIREBASE() {
    static FirebaseManager firebaseManager;
    globalFirebaseManager = &firebaseManager;
    firebaseManager.begin();
}

#endif // FIREBASE_CONFIG_H