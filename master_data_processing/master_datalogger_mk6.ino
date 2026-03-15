#include "INA226.h"

INA226 INA(0x40);

#define RECEIVE_PIN 4


bool there_has_been_a_high_before=false;
bool low_has_happened_from_last_count = false;
int current_runs = 0;
int max_runs_per_benchmark = 5;
int current_benchmark = 1;
String current="";
String previous="";


// Energy calculation variables
float previousPower_mW = 0;
unsigned long previoustime = 0;
bool firstReading_of_run = true;


//data colection INA
unsigned long last_ina_data_collection_time = 0;
const long ina_collection_interval = 200;


//to calc energy of each valid low sector
float power_start_of_low_section;
float power_end_of_low_section;
unsigned long start_time_low_section;
unsigned long end_time_low_section;
bool we_are_still_in_same_low = false;

int previous_run = 0;


float run_energy_total=0;


//to start I2c and setup INA settings
void setup_ina()
{
  Wire.begin();
  
  if (!INA.begin())
  {
    Serial.println("could not connect. Fix and Reboot");
  }

  // set calibration for 0.6A peaks and 0.100 ohm shunt
  int err = INA.setMaxCurrentShunt(0.6, 0.100);
  if (err != INA226_ERR_NONE) 
  {
    Serial.print("Calibration error: 0x");
    Serial.println(err, HEX);
    while (1);
  }

  INA.setAverage(INA226_4_SAMPLES);
  
}

void setup()
{
  Serial.begin(115200);

  //to start I2c and setup INA settings
  setup_ina();

  //allow arduino to read GPIO
  pinMode(RECEIVE_PIN, INPUT);
  
  Serial.println("DEBUG: setup OK");
  delay(1500);

}

float calculateEnergy_J_w_rectangular(unsigned long currentTime_ms, unsigned long previousTime_ms, float currentPower_mW) 
{
    // Convert mW to W and ms to s
    float power_W = currentPower_mW / 1000.0;
    float deltaTime_s = (currentTime_ms - previousTime_ms) / 1000.0;
    
    // Energy in Joules: E = P * t
    float energy_J = power_W * deltaTime_s;
    
    return energy_J;
}


void collect_INA_data_and_calc()
{
  if (INA.isConversionReady()) 
  {
      unsigned long current_time = millis();
      float currentPower_mW = INA.getPower_mW();

      if (currentPower_mW == previousPower_mW) 
      {
        Serial.println("DEBUG: Same value as previous one - possible stale read");
      }

      // Calculate energy using rectangular rule (skip first reading)
      if (!firstReading_of_run) 
      {
        //float deltaEnergy_J = calculateEnergy_J_w_rectangular(current_time, previoustime, currentPower_mW)
        //run_energy_total += deltaEnergy_J;


        //runs, benchmark, prev_time, current_time, current_power
        Serial.println("POWER: ," + String(current_runs) + ","+ String(current_benchmark)+ ","+ String(previoustime)+ ","+ String(current_time)+ ","+ String(currentPower_mW));
        //Serial.println("DEBUG: time elapsed from last read of register: " + String(current_time - previoustime));

        previoustime = current_time;
        previousPower_mW = currentPower_mW;
      } 
      else 
      {
        firstReading_of_run = false;

        previoustime = current_time;
        previousPower_mW = currentPower_mW;
      }
  
  } 
  
}

void update_run_bench_counter()
{
  current_runs++;

  if (current_runs > max_runs_per_benchmark)
    {
        current_runs = 1;
        current_benchmark++;
    }
}


void loop()
{
  int pin_state = digitalRead(RECEIVE_PIN);
 
  if(pin_state == HIGH && low_has_happened_from_last_count)
    {
      low_has_happened_from_last_count = false;
      
      there_has_been_a_high_before = true;
      
      //as soon as we end in a high (after a good low) we stop the measurement because run has finished
      if (we_are_still_in_same_low)
        {
            //this is the end of a valid low aka the srtart of a high 
            Serial.println("DEBUG: this is the end of a valid low aka the srtart of a high");

            //update_run_bench_counter();

            we_are_still_in_same_low = false;
            
            //a questo punto loggiamo la energy totale collected durante run
            Serial.println("DEBUG: Run: " + String(current_runs) + " Bench: "+ String(current_benchmark));

        }
    }
  else if (pin_state == LOW)
    {
      low_has_happened_from_last_count=true;
      
      if (there_has_been_a_high_before)
      {
        if(!we_are_still_in_same_low)
        {
            //this is the start of a valid low
            Serial.println("DEBUG: this is the start of a valid low");
            firstReading_of_run = true;
            we_are_still_in_same_low=true;

            update_run_bench_counter();
        }

        unsigned long current_millis = millis();
        
        collect_INA_data_and_calc();

      }
      
    }
  else if (pin_state == HIGH && !low_has_happened_from_last_count)
    {
      //Serial.println("We are still on same high wave, no low have happened from last high");
      ;
    }
  else 
    {
      current="DEBUG: OTHER pinstate: "+String(pin_state)+" low_has_happened_from_last_count: "+String(low_has_happened_from_last_count)+ " current_runs: "+String(current_runs)+ " current_benchmark: "+String(current_benchmark);
      if (current != previous)
        {
          Serial.println(current);
          previous=current;
        }
      
    }
  //delay(10);
}
