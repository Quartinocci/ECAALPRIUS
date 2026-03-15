/*
 * ESP32 WebSocket Receiver - Simple JSON receiver
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <WebSocketsServer.h>

WiFiMulti WiFiMulti;
WebSocketsServer webSocket = WebSocketsServer(81);

unsigned long packetCount = 0;

// WiFi credentials
const char* ssid = "my_SSID";
const char* password = "my_password";

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[%u] Client disconnected!\n", num);
            break;
            
        case WStype_CONNECTED:
            {
                IPAddress ip = webSocket.remoteIP(num);
                Serial.printf("[%u] Client connected from %s\n", num, ip.toString().c_str());
            }
            break;
            
        case WStype_TEXT:
            //Serial.printf("[%u] Received JSON: %s\n", num, payload);
            // Process your JSON data here
            // You can parse it or just use it as needed
            packetCount++;
            Serial.print("Total packets: ");
            Serial.println(packetCount);
            //Serial.printf("[%u] Received JSON, length: %u\n", num, length);
            break;
            
        case WStype_BIN:
            //Serial.printf("[%u] Received binary data, length: %u\n", num, length);
            packetCount++;
            Serial.print("Total packets: ");
            Serial.println(packetCount);
            break;
            
        case WStype_ERROR:
        case WStype_FRAGMENT_TEXT_START:
        case WStype_FRAGMENT_BIN_START:
        case WStype_FRAGMENT:
        case WStype_FRAGMENT_FIN:
            break;
    }
}

void setup() {
    Serial.begin(19200);
    Serial.println("=== ESP32 WebSocket Receiver ===");
    
    // Connect to WiFi
    WiFiMulti.addAP(ssid, password);
    Serial.println("Connecting to WiFi...");
    
    while(WiFiMulti.run() != WL_CONNECTED) {
        Serial.print(".");
        delay(500);
    }
    
    Serial.println();
    Serial.printf("WiFi connected! IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.println("*** Use this IP in the sender code ***");
    
    // Start WebSocket server
    webSocket.begin();
    webSocket.onEvent(webSocketEvent);
    
    Serial.println("WebSocket server started on port 81");
    Serial.println("Waiting for connections...");
}

void loop() {
    webSocket.loop();
    //delay(10);
}
