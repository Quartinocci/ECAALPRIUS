
#include <WiFi.h>
#include <WiFiUdp.h>
#include <coap-simple.h>

//RECEIVER

// WiFi credentials
const char* ssid = "my_SSID";
const char* password = "my_password";

// UDP and CoAP class
WiFiUDP udp;
Coap coap(udp, 512);

unsigned long packetCount = 0;

// CoAP server endpoint URL for receiving JSON
void callback_json(CoapPacket &packet, IPAddress ip, int port) 
{
  Serial.println("=== CoAP Request Received ===");
  Serial.print("From IP: ");
  Serial.println(ip);
  Serial.print("Port: ");
  Serial.println(port);
  Serial.print("Message ID: ");
  Serial.println(packet.messageid);
  Serial.print("Type: ");
  Serial.println(packet.type);
  Serial.print("Code: ");
  Serial.println(packet.code);
  Serial.print("Payload length: ");
  Serial.println(packet.payloadlen);

  packetCount++;
  Serial.print("Total packets: ");
  Serial.println(packetCount);
  
  /*
  // Extract and print payload
  if (packet.payloadlen > 0) 
  {
    char p[packet.payloadlen + 1];
    memcpy(p, packet.payload, packet.payloadlen);
    p[packet.payloadlen] = '\0';
    
    Serial.println("Received JSON:");
    Serial.println(p);
  } else 
  {
    Serial.println("No payload (GET request)");
  }
  */
  
  Serial.println("========================");
  
  // Send appropriate response based on request type
  if (packet.code == COAP_GET) 
  {
    // Respond to GET with current status
    coap.sendResponse(ip, port, packet.messageid, "GET received - JSON endpoint active");
  } else if (packet.code == COAP_PUT || packet.code == COAP_POST) 
  {
    // Respond to PUT/POST with acknowledgment
    coap.sendResponse(ip, port, packet.messageid, "JSON data received and processed");
  } else 
  {
    // Generic response
    coap.sendResponse(ip, port, packet.messageid, "Request received");
  }
}

// CoAP client response callback
//This function gets automatically called whenever a CoAP response arrives.
//basically When someone replies to my message, automatically print what they said to the serial monitor.
void callback_response(CoapPacket &packet, IPAddress ip, int port) 
{
  Serial.println("[CoAP Response received]");
  
  char p[packet.payloadlen + 1];
  memcpy(p, packet.payload, packet.payloadlen);
  p[packet.payloadlen] = '\0';
  
  Serial.println(p);
}

void setup() 
{
  Serial.begin(19200);
  Serial.println("Starting CoAP Receiver...");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) 
  {
      delay(500);
      Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Setup CoAP server endpoint for receiving JSON
  Serial.println("Setup JSON Callback");
  coap.server(callback_json, "json");

  // Client response callback
  Serial.println("Setup Response Callback");
  coap.response(callback_response);

  // Start CoAP server/client
  coap.start();
  Serial.println("CoAP Receiver ready on port 5683");
  Serial.println("Waiting for JSON data on endpoint: /json");
}

void loop() 
{
  static unsigned long lastHeartbeat = 0;
  unsigned long currentTime = millis();
  
  // Print heartbeat every 10 seconds to show the receiver is running
  if (currentTime - lastHeartbeat >= 10000) 
  {
    Serial.println("CoAP Receiver is running... Listening on port 5683");
    Serial.print("My IP: ");
    Serial.println(WiFi.localIP());
    lastHeartbeat = currentTime;
  }
  //When a message arrives, it triggers the appropriate callback functions
  //Listens for new CoAP requests and responses arriving over the network
  //and more but basically Check for Incoming Messages, Process Network Buffers, Handle Timeouts and Retransmissions and Send Queued Messages
  coap.loop();
  
  delay(10);
}

