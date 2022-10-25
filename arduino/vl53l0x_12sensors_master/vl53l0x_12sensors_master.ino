#include "Adafruit_VL53L0X.h"

#define RING_RADIUS 0.243f // [m]
#define SENSORS_NUM 12u
#define LOX_START_ADDRESS 0x29
#define SCAN_LENGTH 0.01f
#define ALPHA (TWO_PI / SENSORS_NUM)

#define foreach(SENSORS_NUM, iter) for(uint8_t iter = 0; iter < SENSORS_NUM; iter++)

typedef enum {
    SHT_LOX_SENSOR1_0_DEG = 26,
    SHT_LOX_SENSOR2_15_DEG = 24,
    SHT_LOX_SENSOR3_30_DEG = 22,
    SHT_LOX_SENSOR4_45_DEG = 32,
    SHT_LOX_SENSOR5_60_DEG = 30,
    SHT_LOX_SENSOR6_75_DEG = 28,
    SHT_LOX_SENSOR7_90_DEG = 38,
    SHT_LOX_SENSOR8_105_DEG = 36,
    SHT_LOX_SENSOR9_120_DEG = 34,
    SHT_LOX_SENSOR10_135_DEG = 44,
    SHT_LOX_SENSOR11_150_DEG = 42,
    SHT_LOX_SENSOR12_165_DEG,
    SHT_LOX_SENSOR13_180_DEG,
    SHT_LOX_SENSOR14_195_DEG,
    SHT_LOX_SENSOR15_210_DEG,
    SHT_LOX_SENSOR16_225_DEG,
    SHT_LOX_SENSOR17_240_DEG,
    SHT_LOX_SENSOR18_255_DEG,
    SHT_LOX_SENSOR19_270_DEG,
    SHT_LOX_SENSOR20_285_DEG,
    SHT_LOX_SENSOR21_300_DEG,
    SHT_LOX_SENSOR22_315_DEG,
    SHT_LOX_SENSOR23_330_DEG,
    SHT_LOX_SENSOR24_345_DEG = 40
} sht_lox_pins_e;

typedef enum {
    SYNC_PIN_OUT = 10
} sync_pins_e;

sht_lox_pins_e shut_pins[SENSORS_NUM] = {
   [0] = SHT_LOX_SENSOR1_0_DEG,
   [1] = SHT_LOX_SENSOR2_15_DEG,
   [2] = SHT_LOX_SENSOR3_30_DEG,
   [3] = SHT_LOX_SENSOR4_45_DEG,
   [4] = SHT_LOX_SENSOR5_60_DEG,
   [5] = SHT_LOX_SENSOR6_75_DEG,
   [6] = SHT_LOX_SENSOR7_90_DEG,
   [7] = SHT_LOX_SENSOR8_105_DEG,
   [8] = SHT_LOX_SENSOR9_120_DEG,
   [9] = SHT_LOX_SENSOR10_135_DEG,
   [10] = SHT_LOX_SENSOR11_150_DEG,
   [11] = SHT_LOX_SENSOR24_345_DEG
};


const uint32_t magic_number = 0xFF8A32F1;


struct sensors {
  Adafruit_VL53L0X sensors[SENSORS_NUM];
  uint32_t magic_number;
} sensors_s;

struct scans {
  uint16_t scans[SENSORS_NUM];
  uint32_t starting_time;
} scans_s;

void setID() {
  // reset
  foreach(SENSORS_NUM, iter) {
    digitalWrite(shut_pins[iter], LOW);
    delay(10);
  }
  delay(10); 
  // set ID
  Serial.println("Boot");
  foreach(SENSORS_NUM, iter) {
    digitalWrite(shut_pins[iter], HIGH);
    //pinMode(shut_pins[iter], INPUT);
    delay(10);
    if (sensors_s.magic_number != magic_number) {
      Serial.println("Memory overwrite");
      while(1);
    }
    if(!sensors_s.sensors[iter].begin(LOX_START_ADDRESS + iter)) {
      Serial.print("Failed to boot VL53L0X #");
      digitalWrite(shut_pins[iter], LOW);  
    }
    else {
      Serial.print("Sucessfully boot VLX #");
    }
    Serial.println(iter);
    delay(10);
  } 
}

void setupSensors() {
  foreach(SENSORS_NUM, iter) {
    sensors_s.sensors[iter].setMeasurementTimingBudgetMicroSeconds(1);
    delay(10);
    sensors_s.sensors[iter].startRangeContinuous(1);
    delay(10);
  }
}

void send_data(uint8_t* buf, uint8_t sz) {
  Serial.write(buf, sz);
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
  pinMode(SYNC_PIN_OUT, OUTPUT);
  digitalWrite(SYNC_PIN_OUT, HIGH);

  setID();
  delay(50);
  setupSensors();
  delay(50);
  memset(&scans_s.scans[0], 0, SENSORS_NUM);

  digitalWrite(SYNC_PIN_OUT, LOW);
  scans_s.starting_time = millis();
}

void loop() {

  for(uint8_t iter = 0; iter < SENSORS_NUM; iter++) {
    scans_s.scans[iter] = sensors_s.sensors[iter].readRangeResult();
  }

  const uint8_t data_length = SENSORS_NUM*sizeof(scans_s.scans[0]);
  const uint8_t packet_length = data_length + sizeof(scans_s.starting_time) + 3; // packet_length, sensors_num and CRC
  uint8_t tx[packet_length + 2]; // 11 + 2 = 13
  tx[0] = 0xFF;
  tx[1] = 0xFF;
  tx[2] = packet_length;
  tx[3] = SENSORS_NUM;
  for(uint8_t i = 0; i < SENSORS_NUM; i++) {
    for (size_t s = 0; s < sizeof(scans_s.scans[0]); s++) {
      tx[4+2*i+s] = (scans_s.scans[i] >> s*8) & 0xFF;
    }
  }
  uint32_t delta = millis() - scans_s.starting_time;
  for (size_t s = 0; s < sizeof(scans_s.starting_time); s++) {
    tx[4+data_length+s] = (delta >> s*8) & 0xFF;
  }
  uint16_t check_sum = 0x00;
  for (uint8_t ind = 2; ind < packet_length+1; ++ind) {
    check_sum += tx[ind];
  }
  tx[8+data_length] = (uint8_t)((~check_sum) & 0xff);
  send_data(&tx[0], sizeof(tx));

}