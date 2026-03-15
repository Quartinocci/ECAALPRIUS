#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "my_SSID";
const char* password = "my_password";

// Create web server on port 80
WebServer server(80);

unsigned long packetCount = 0;

void handleRoot() 
{
  server.send(200, "text/plain", "ESP32 Receiver Ready");
}

void handleData() 
{
  if (server.method() != HTTP_POST) 
  {
    server.send(405, "text/plain", "Method Not Allowed");
    return;
  }

  String body = server.arg("plain");
  Serial.println("Received JSON:");
  //Serial.println(body);

  packetCount++;
  Serial.print("Total packets: ");
  Serial.println(packetCount);

  server.send(200, "application/json", "{\"status\":\"success\"}");
}

void setup() 
{
  Serial.begin(19200);
  delay(1000);

  // Connect to WiFi
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Setup server routes
  server.on("/", handleRoot);
  server.on("/data", handleData);
  
  server.begin();
  Serial.println("HTTP server started");
}

void loop() 
{
  server.handleClient();
}
