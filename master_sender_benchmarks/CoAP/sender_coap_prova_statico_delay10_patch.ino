#include <WiFi.h>
#include <WiFiUdp.h>
#include <coap-simple.h>

#define SIGNAL_PIN 4
#define LED_PIN 2
const int high_duration_ms = 200;

//SENDER

// WiFi credentials
const char* ssid = "my_SSID";
const char* password = "my_password";

// Receiver IP address
IPAddress receiver_ip(192, 168, 1, 201);

// UDP and CoAP class
WiFiUDP udp;
Coap coap(udp, 512);

//-------
//6 mins 360 sec
// 3mins 180
unsigned long max_execution_time_seconds_per_run=360*1000;
int max_runs = 5;

bool done = false;

//unsigned long packetCount = 0;

void setup_leds_and_gpio()
{
    pinMode(SIGNAL_PIN, OUTPUT);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(SIGNAL_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
}
//-------

// CoAP client response callback
void callback_response(CoapPacket &packet, IPAddress ip, int port) 
{
  Serial.println("[CoAP Response received]");
  Serial.print("From: ");
  Serial.println(ip);
  
  char p[packet.payloadlen + 1];
  memcpy(p, packet.payload, packet.payloadlen);
  p[packet.payloadlen] = '\0';
  
  Serial.print("Response: ");
  Serial.println(p);
  Serial.println("---");
}

void setup() 
{
  setup_leds_and_gpio();
  Serial.begin(19200);
  Serial.println("Starting CoAP Sender...");

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

  // Test basic connectivity to receiver
  Serial.print("Testing ping to receiver at ");
  Serial.println(receiver_ip);
  
  // Client response callback
  Serial.println("Setup Response Callback");
  coap.response(callback_response);

  // Start CoAP client
  coap.start();
  
  Serial.println("CoAP Sender ready");
  Serial.print("Will send JSON to: ");
  Serial.print(receiver_ip);
  Serial.println(":5683/json");
  Serial.println("JSON payload:");
  //Serial.println(json_data);
  Serial.println("========================");
  
  // Wait a bit before starting to send
  //delay(2000);
}


//---------------------------------------

void delay_and_poll_in_the_meanwhile(float delay_time_provided, float max_runtime=0, float run_starttime=0)
{
  unsigned long start_time_while_delay_loop = millis();
  while(millis()-start_time_while_delay_loop <= delay_time_provided)
  {
    if (max_runtime>0 && millis()-run_starttime > max_runtime)
      {
        break;
      }
    if ((delay_time_provided - (millis() - start_time_while_delay_loop))>10)
      {
        delay(10);
      }
      
    coap.loop();
  }
}

float get_frequency_seconds(uint8_t type) 
{
  //for type1 will be 300
  //for type2 will be 3
  //for type3 will be 0.033
  if (type == 1)
    return 300.0; //TODO put it back at 300.0
  else if (type == 2)
    return 3.0; //TODO put it back at 3.0
  else if (type == 3)
    return 0.035; //TODO put it back at 0.033
  else
    return -1.0;   // default case
}

//uint8_t to save a bit of memory instead of int
String generatePayload(uint8_t type) 
{
  String output;

  if (type == 1) {
    // --- TYPE 1: 21 bytes fixed ---
    // Format example: {"t":01234,"h":5678}
    // Always 21 chars
    char buf[22]; // +1 for null terminator
    snprintf(buf, sizeof(buf), "{\"t\":%05lu,\"h\":%04lu}",
             millis() % 100000, millis() % 10000);
    output = buf;
  }
  else if (type == 2) {
    // --- TYPE 2: 160 bytes fixed ---
    // We'll pad with spaces so it’s always 160
    char buf[200]; // temp buffer
    snprintf(buf, sizeof(buf),
      "{\"id\":%05lu,\"ts\":\"%010lu\",\"lat\":%011lu,"
      "\"lon\":%011lu,\"alt\":%05lu,\"spd\":%04lu,"
      "\"bat\":%02lu,\"sat\":%02lu}",
      millis() % 100000, millis(),
      millis() % 100000000000UL, millis() % 100000000000UL,
      millis() % 100000, millis() % 10000,
      millis() % 100, millis() % 100
    );

    output = buf;

    // Pad with spaces until length is 160
    while (output.length() < 160) {
      output += ' ';
    }
  }
  else if (type == 3) {
    // --- TYPE 3: 58 KB fixed ---
    const size_t CAPACITY = 58 * 1024; // 59392 bytes
    output.reserve(CAPACITY);

    // Small JSON-like header with fixed width
    char head[32];
    snprintf(head, sizeof(head), "{\"millis\":%010lu}", millis());
    output = head;

    // Fill the rest with a varying character
    char filler = 'A' + (millis() % 26);
    while (output.length() < CAPACITY) {
      output += filler;
    }

    // Ensure exact size
    output.remove(CAPACITY);
  }

  return output;
}


void finished_with_all_benchmarks()
{
  //Serial.print("Total packets: ");
  //Serial.println(packetCount);
  
  while (true) 
  {
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(SIGNAL_PIN, HIGH);
      delay(180000);
  }
}


void run_or_benchmark_change(float extra_cooldown_time_between_runs)
{
    // HIGH signal
    digitalWrite(SIGNAL_PIN, HIGH);
    digitalWrite(LED_PIN, HIGH);

    //delay to have teh HIGH gpio recognized
    //TODO would this be unfair advantage? since the polling here would not be counted
    //but when re starting connection is already good
    delay_and_poll_in_the_meanwhile(high_duration_ms);

    //if we want extra delay to cooldown 
    delay_and_poll_in_the_meanwhile(extra_cooldown_time_between_runs);

    // LOW signal
    digitalWrite(SIGNAL_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
}


void main_task(int current_bench)
{
  //packetCount++;

  String message = generatePayload(current_bench);

  Serial.println("Sending PUT request with JSON payload...");

  int json_msgid = coap.put(receiver_ip, 5683, "json", message.c_str());

  Serial.print("JSON PUT Message ID: ");
  Serial.println(json_msgid);
  Serial.print("payload: "+message);

  coap.loop();

  Serial.println("Message type "+ String(current_bench) +" sended ");

}



void handling_bitrate(int current_bench)
{

  //start al tempo della run
  unsigned long track_this_run_time_start = millis();

  //loop if max time still valid
  while(millis()-track_this_run_time_start <= max_execution_time_seconds_per_run)
  {
    //invia
    main_task(current_bench);
    
    //we need the delay to respect bitrate
    delay_and_poll_in_the_meanwhile(get_frequency_seconds(current_bench)*1000, max_execution_time_seconds_per_run, track_this_run_time_start);

  }

}

void loop() 
{

  if(!done)
  {
    //loop for benchmark types
    // put limit at 2 instead of 3 cause didnt manage to execute bench3
    for (int count_bench_level = 1; count_bench_level <= 2; count_bench_level++) 
      {
        for (int current_run = 0; current_run < max_runs; current_run++) 
        {  
          run_or_benchmark_change(60000);
          handling_bitrate(count_bench_level);

        }
      }
    
    done=true;
  }

  finished_with_all_benchmarks();
  //just to avoid super fast looping once finished
  delay(3000);

}
