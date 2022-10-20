#include "Adafruit_VL53L0X.h"
#include "config.h"

typedef enum {
    SHT_LOX_SENSOR1_0_DEG = 28,
    SHT_LOX_SENSOR2_15_DEG = 30,
    SHT_LOX_SENSOR3_30_DEG = 32,
    SHT_LOX_SENSOR4_45_DEG = 34,
    SHT_LOX_SENSOR5_60_DEG = 36,
    SHT_LOX_SENSOR6_75_DEG = 38,
    SHT_LOX_SENSOR7_90_DEG = 40,
    SHT_LOX_SENSOR8_105_DEG = 42,
    SHT_LOX_SENSOR9_120_DEG = 44,
    SHT_LOX_SENSOR10_135_DEG = 46,
    SHT_LOX_SENSOR11_150_DEG = 48,
    SHT_LOX_SENSOR12_165_DEG = 47,
    SHT_LOX_SENSOR13_180_DEG = 33,
    SHT_LOX_SENSOR14_195_DEG = 31,
    SHT_LOX_SENSOR15_210_DEG = 29,
    SHT_LOX_SENSOR16_225_DEG = 39,
    SHT_LOX_SENSOR17_240_DEG = 37,
    SHT_LOX_SENSOR18_255_DEG = 35,
    SHT_LOX_SENSOR19_270_DEG = 45,
    SHT_LOX_SENSOR20_285_DEG = 43,
    SHT_LOX_SENSOR21_300_DEG = 41,
    SHT_LOX_SENSOR22_315_DEG = 51,
    SHT_LOX_SENSOR23_330_DEG = 49,
    SHT_LOX_SENSOR24_345_DEG = 50
} sht_lox_pins_e;

#define foreach(SENSORS_NUM, iter) for(uint8_t iter = 0; iter < SENSORS_NUM; iter++)

sht_lox_pins_e shut_pins[SENSORS_NUM] = {
  [0] = SHT_LOX_SENSOR24_345_DEG,
  [1] = SHT_LOX_SENSOR1_0_DEG,
  [2] = SHT_LOX_SENSOR2_15_DEG,
  [3] = SHT_LOX_SENSOR3_30_DEG,
  [4] = SHT_LOX_SENSOR4_45_DEG,
  [5] = SHT_LOX_SENSOR5_60_DEG,
  [6] = SHT_LOX_SENSOR6_75_DEG,
  [7] = SHT_LOX_SENSOR7_90_DEG,
  [8] = SHT_LOX_SENSOR8_105_DEG,
  [9] = SHT_LOX_SENSOR9_120_DEG,
  [10] = SHT_LOX_SENSOR10_135_DEG,
  [11] = SHT_LOX_SENSOR11_150_DEG,
  [12] = SHT_LOX_SENSOR12_165_DEG,
  [13] = SHT_LOX_SENSOR13_180_DEG,
  [14] = SHT_LOX_SENSOR14_195_DEG,
  [15] = SHT_LOX_SENSOR15_210_DEG,
  [16] = SHT_LOX_SENSOR16_225_DEG,
  [17] = SHT_LOX_SENSOR17_240_DEG,
  [18] = SHT_LOX_SENSOR18_255_DEG,
  [19] = SHT_LOX_SENSOR19_270_DEG,
  [20] = SHT_LOX_SENSOR20_285_DEG,
  [21] = SHT_LOX_SENSOR21_300_DEG,
  [22] = SHT_LOX_SENSOR22_315_DEG,
  [23] = SHT_LOX_SENSOR23_330_DEG
};

struct sensors {
  Adafruit_VL53L0X sensors[SENSORS_NUM];
  uint32_t magic_number;
} __attribute__((packed)) sensors_s;

// Accounting
double volume = 0.0f;
float prev_scans[SENSORS_NUM];
float new_scans[SENSORS_NUM];
const uint32_t magic_number = 0x9F8A32F1;

void initSensors()
{
  foreach(SENSORS_NUM, iter) {
    sensors_s.sensors[iter] = Adafruit_VL53L0X();
  }
}

void setID() {
  // reset
  foreach(SENSORS_NUM, iter) {
    digitalWrite(shut_pins[iter], LOW);  
  }
  delay(10);
  foreach(SENSORS_NUM, iter) {
    digitalWrite(shut_pins[iter], HIGH);  
  }
  delay(10);
  foreach(SENSORS_NUM, iter) {
    digitalWrite(shut_pins[iter], LOW);  
  }
  // set ID
  Serial.println("Boot");
  foreach(SENSORS_NUM, iter) {
    digitalWrite(shut_pins[iter], HIGH);
    delay(100);
    if (sensors_s.magic_number != magic_number) {
      Serial.println("Memory overwrite");
      while(1);
    }

    if(!sensors_s.sensors[iter].begin(LOX_START_ADDRESS + iter)) {
      Serial.print("Failed to boot VL53L0X #");
      Serial.println(iter);
      delay(100);
      digitalWrite(shut_pins[iter], LOW);  
    }
    delay(100);
  } 
}

void setupSensors() {
  foreach(SENSORS_NUM, iter) {
    sensors_s.sensors[iter].setMeasurementTimingBudgetMicroSeconds(1);
    sensors_s.sensors[iter].startRangeContinuous(1);
    delay(100);
  }
}

void accumulate_volume(float* prev_scans, float* new_scans) {

  for (int i = 0; i < SENSORS_NUM - 1; i++) {
    float r1_o = prev_scans[i];
    float r1_d = new_scans[i];
    float r2_o = prev_scans[i + 1];
    float r2_d = new_scans[i + 1];

    volume += (
        2 * r1_o * r1_o +
        2 * r1_d * r1_d +
        2 * r2_o * r2_o +
        2 * r2_d * r2_d +
        2 * r1_o * r2_o +
        2 * r1_o * r1_d +
        2 * r1_d * r2_d +
        2 * r2_o * r2_d +
        r1_o * r2_d +
        r1_d * r2_o
      );
  }
  float r1_o = prev_scans[SENSORS_NUM - 1];
  float r1_d = new_scans[SENSORS_NUM - 1];
  float r2_o = prev_scans[0];
  float r2_d = new_scans[0];

  volume += (
    2 * r1_o * r1_o +
    2 * r1_d * r1_d +
    2 * r2_o * r2_o +
    2 * r2_d * r2_d +
    2 * r1_o * r2_o +
    2 * r1_o * r1_d +
    2 * r1_d * r2_d +
    2 * r2_o * r2_d +
    r1_o * r2_d +
    r1_d * r2_o
  );

}

void setup() {

  sensors_s.magic_number = magic_number;

  Serial.begin(115200);

  // wait until serial port opens for native USB devices
  while (! Serial) {
     delay(1); 
  }

  digitalWrite(SDA, 1);
  digitalWrite(SCL, 1);

  foreach(SENSORS_NUM, iter) {
    pinMode(shut_pins[iter], OUTPUT);
  }

  Serial.println("Shutdown pins inited...");
  Serial.println("Starting...");

  setID();
  setupSensors();

  memset(&prev_scans[0], 0, SENSORS_NUM);
  memset(&new_scans[0], 0, SENSORS_NUM);
}

void loop() {
   volume = 0.0f;

   for (int i = 0; i < 2; i++) {

    memcpy(&prev_scans[0], &new_scans[0], SENSORS_NUM); // prev = new

    foreach(SENSORS_NUM, iter) {
      new_scans[iter] = RING_RADIUS - ((float)sensors_s.sensors[iter].readRangeResult())/1000;
    }
    accumulate_volume(&prev_scans[0], &new_scans[0]);
  }
  
  foreach(SENSORS_NUM, iter) {
    Serial.print("#");
    Serial.print(iter);
    Serial.print(" ");
    Serial.print(new_scans[iter]);
    Serial.print(" |  ");
  }
  Serial.println("");

}
