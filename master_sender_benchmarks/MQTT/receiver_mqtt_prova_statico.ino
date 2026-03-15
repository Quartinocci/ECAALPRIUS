/*
  ESP32 MQTT JSON Receiver with QoS Support
  
  This example connects to a MQTT broker and subscribes to JSON messages
  with different QoS levels. It prints the raw JSON received.
  
  Based on ArduinoMqttClient library examples.
*/

#include <ArduinoMqttClient.h>
#include <WiFi.h>

// WiFi credentials
const char* ssid = "my_SSID";
const char* password = "my_password";

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = "192.168.1.205";  // Change to your Mosquitto broker IP
int        port     = 1883;
const char topic[]  = "esp32/json";

unsigned long packetCount = 0;

void setup() {
  Serial.begin(19200);
 
  Serial.println("ESP32 MQTT JSON Receiver Starting...");
  
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }

  Serial.println();
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  // Set client ID to make it unique
  String clientId = "ESP32Receiver-" + String(random(0xffff), HEX);
  mqttClient.setId(clientId.c_str());

  Serial.print("Attempting to connect to MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    while (1);
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();

  // Subscribe to topic with QoS 2 (highest level)
  Serial.print("Subscribing to topic: ");
  Serial.println(topic);
  Serial.println();

  mqttClient.subscribe(topic, 2);  // Subscribe with QoS 2

  Serial.println("Waiting for JSON messages...");
  Serial.println("Commands:");
  Serial.println("  Type 'r' to reconnect to broker");
  Serial.println("  Type 'i' to show connection info");
  Serial.println();
}

void loop() 
{
  // Keep MQTT connection alive and check for messages
  mqttClient.poll();

  // Check for serial commands
  if (Serial.available()) 
  {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toLowerCase();
    
    if (command == "r") 
    {
      reconnectToBroker();
    } 
    else if (command == "i") 
    {
      showConnectionInfo();
    }
  }

  // Check for incoming messages
  int messageSize = mqttClient.parseMessage();
  if (messageSize) {
    packetCount++;
    
    Serial.println("========================================");
    Serial.print("Message #");
    Serial.print(packetCount);
    Serial.print(" received from topic: ");
    Serial.println(mqttClient.messageTopic());
    Serial.print("Message length: ");
    Serial.print(messageSize);
    Serial.println(" bytes");
    Serial.print("QoS Level: ");
    Serial.println(mqttClient.messageQoS());
    Serial.print("Retained: ");
    Serial.println(mqttClient.messageRetain() ? "Yes" : "No");
    Serial.print("Duplicate: ");
    Serial.println(mqttClient.messageDup() ? "Yes" : "No");
    Serial.println();
    Serial.println("Raw JSON content:");
    Serial.println("----------------------------------------");

    // Print the raw JSON message
    String receivedJson = "";
    while (mqttClient.available()) {
      char c = mqttClient.read();
      Serial.print(c);
      receivedJson += c;
    }
    
    Serial.println();
    Serial.println("----------------------------------------");
    Serial.print("Timestamp: ");
    Serial.println(millis());
    Serial.println("========================================");
    Serial.println();
  }
}

void reconnectToBroker() {
  Serial.println("Attempting to reconnect to MQTT broker...");
  
  if (mqttClient.connected()) {
    mqttClient.stop();
  }
  
  if (mqttClient.connect(broker, port)) {
    Serial.println("Reconnected successfully!");
    mqttClient.subscribe(topic, 2);
    Serial.println("Resubscribed to topic with QoS 2");
  } else {
    Serial.print("Reconnection failed! Error code = ");
    Serial.println(mqttClient.connectError());
  }
  Serial.println();
}

void showConnectionInfo() {
  Serial.println("========================================");
  Serial.println("Connection Information:");
  Serial.print("WiFi Status: ");
  Serial.println(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("MQTT Connected: ");
  Serial.println(mqttClient.connected() ? "Yes" : "No");
  Serial.print("Broker: ");
  Serial.println(broker);
  Serial.print("Port: ");
  Serial.println(port);
  Serial.print("Subscribed Topic: ");
  Serial.println(topic);
  Serial.print("Messages Received: ");
  Serial.println(packetCount);
  Serial.println("========================================");
  Serial.println();
}
