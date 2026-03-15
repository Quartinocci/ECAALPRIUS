
#include <ArduinoMqttClient.h>
#include <WiFi.h>

const char* ssid = "my_SSID";
const char* password = "my_password";

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = "192.168.1.205"; 
int        port     = 1883;
const char topic[]  = "esp32/json";

int currentQoS = 1;  //QoS level (0, 1, or 2)

#define SIGNAL_PIN 4
#define LED_PIN 2
const int high_duration_ms = 200;

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

void setup() 
{
  setup_leds_and_gpio();
  Serial.begin(19200);

  WiFi.begin(ssid, pass);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");

  Serial.println();
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  // Set client ID to make it unique
  String clientId = "ESP32Sender-" + String(random(0xffff), HEX);
  mqttClient.setId(clientId.c_str());

  Serial.print("Attempting to connect to MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) 
  {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    while (1);
  }

  Serial.println("You're connected to the MQTT broker!");

}

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
    mqttClient.poll();
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

  // Send message with specified QoS
  mqttClient.beginMessage(topic, false, currentQoS);  // topic, retain, qos
  mqttClient.print(message);
  mqttClient.endMessage();

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
