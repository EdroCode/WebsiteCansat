#include <SPI.h>
#include <RadioLib.h>
#include <FastCRC.h>
#include <Arduino.h>

#define SEND_TIME 15000 // 15 seconds
#define PCSerial Serial
#define DEBUG
#define DEBUG_WAIT_FOR_USB

// Radio config
#define radio_ss 10
#define radio_dio0 3
#define radio_rst 4
#define MOSI_PIN 11
#define MISO_PIN 12
#define SCK_PIN 13

#define STATUS_GREEN_LED 10 
#define STATUS_RED_LED 11 
#define RADIO_GREEN_LED 12 
#define RADIO_RED_LED 13 

struct __attribute__((packed)) FULLDATA {
  uint8_t gps_crc;              
  uint16_t number;              

  int16_t inside_temp;          
  int16_t inside_hum;           
  int16_t external_temp;        
  int16_t external_hum;         

  float accel_x; // 4                
  float accel_y; // 4                
  float accel_z; // 4                

  float gyro_x; // 4                
  float gyro_y; // 4                
  float gyro_z; // 4                

  int16_t pi_temp;              

  int32_t lat;                  
  int32_t lon;                  
  uint16_t alt;                 

  uint16_t pressure;            
  int16_t temp_bmp;             
  uint16_t alt_bmp;             

  uint8_t uv;                   
  uint8_t ambient_light;        
  uint8_t uvi;                  
  uint8_t lux;                  

  uint8_t cpl;                  
};

FULLDATA data_struct;

const int dataSize = sizeof(FULLDATA);
byte data_bytes[dataSize];

FastCRC8 CRC8;
unsigned long last_sent_radio = 0;

struct TLoRaSettings {
  float Frequency = 439.666;
  float Bandwidth = 31.25;
  uint8_t SpreadFactor = 12;
  uint8_t CodeRate = 7;
  uint8_t SyncWord = 0x12;
  uint8_t Power = 17;
  uint8_t CurrentLimit = 100;
  uint16_t PreambleLength = 8;
  uint8_t Gain = 0;
} LoRaSettings;

uint16_t RadioCounter = 0;
SX1278 radio = new Module(radio_ss, radio_dio0, radio_rst, -1);
int transmissionState = RADIOLIB_ERR_NONE;
volatile bool transmittedFlag = false;
volatile bool enableRadioInterrupt = false;
bool radio_connected = false;
long radio_connected_time = 0;
bool has_dio0_action = false;

void setup() {
#if defined DEBUG
  #if defined DEBUG_WAIT_FOR_USB
    while (!PCSerial) delay(10);
  #endif
  PCSerial.begin(9600);
  PCSerial.println("Start");
#endif

  pinMode(radio_ss, OUTPUT);
  digitalWrite(radio_ss, HIGH);

  ConnectRadio();
  last_sent_radio = millis();
}

void ConnectRadio() {
  digitalWrite(RADIO_GREEN_LED, LOW);
  digitalWrite(RADIO_RED_LED, LOW);

  digitalWrite(radio_ss, LOW);
  radio_connected_time = millis();

#if defined DEBUG
  PCSerial.print(F("[SX1278] Initializing ... "));
#endif
  int state = radio.begin(
    LoRaSettings.Frequency,
    LoRaSettings.Bandwidth,
    LoRaSettings.SpreadFactor,
    LoRaSettings.CodeRate,
    LoRaSettings.SyncWord,
    LoRaSettings.Power,
    LoRaSettings.PreambleLength,
    LoRaSettings.Gain
  );

  if (state == RADIOLIB_ERR_NONE) {
#if defined DEBUG
    PCSerial.println(F("[SX1278] Connection success!"));
#endif
    radio_connected = true;
    if (!has_dio0_action) {
      radio.setDio0Action(radioTransmitted);
      has_dio0_action = true;
    }
    digitalWrite(STATUS_GREEN_LED, HIGH);
    digitalWrite(STATUS_RED_LED, LOW);
  } else {
#if defined DEBUG
    PCSerial.print(F("[SX1278] Connection failed, code "));
    PCSerial.println(state);
#endif
    digitalWrite(STATUS_GREEN_LED, LOW);
    digitalWrite(STATUS_RED_LED, HIGH);
    radio_connected = false;
  }
  digitalWrite(radio_ss, HIGH);
}

#if defined(ESP8266) || defined(ESP32)
  ICACHE_RAM_ATTR
#endif
void radioTransmitted(void) {
  transmittedFlag = true;
}

void loop() {
  unsigned long start_time_loop = millis();

  if (!radio_connected || radio.getChipVersion() != 18) {
    radio_connected = false;
    ConnectRadio();
  }

  data_struct.number = RadioCounter;


  if (PCSerial.available()) {
    String csv = PCSerial.readStringUntil('\n');
    csv.trim();

    float vals[22];
    int idx = 0;
    char *token = strtok((char*)csv.c_str(), ",");

    while (token && idx < 22) {
      vals[idx++] = atof(token);
      token = strtok(NULL, ",");
    }

    if (idx == 22) {
      data_struct.inside_temp     = vals[0];
      data_struct.inside_hum      = vals[1];
      data_struct.external_temp   = vals[2];
      data_struct.external_hum    = vals[3];

      data_struct.accel_x         = vals[4];
      data_struct.accel_y         = vals[5];
      data_struct.accel_z         = vals[6];

      data_struct.gyro_x          = vals[7];
      data_struct.gyro_y          = vals[8];
      data_struct.gyro_z          = vals[9];

      data_struct.pi_temp         = vals[10];

      data_struct.lat             = vals[11];
      data_struct.lon             = vals[12];
      data_struct.alt             = vals[13];

      data_struct.pressure        = vals[14];
      data_struct.temp_bmp        = vals[15];
      data_struct.alt_bmp         = vals[16];

      data_struct.uv              = vals[17];
      data_struct.ambient_light   = vals[18];
      data_struct.uvi             = vals[19];
      data_struct.lux             = vals[20];

      data_struct.cpl             = vals[21];

      memcpy(data_bytes + 1, ((uint8_t*)&data_struct) + 1, dataSize - 1);
      data_struct.gps_crc = CRC8.smbus(data_bytes + 1, dataSize - 1);
      data_bytes[0] = data_struct.gps_crc;

#if defined DEBUG
      PCSerial.println(F("[SX1278] Transmitting packet ... "));
      for (int k = 0; k < dataSize; k++) {
        printHex(data_bytes[k]);
      }
#endif

      if (radio_connected) {
        transmittedFlag = false;
        enableRadioInterrupt = true;
        digitalWrite(radio_ss, LOW);
        transmissionState = radio.startTransmit(data_bytes, dataSize);

        while (!transmittedFlag) {
          if (millis() - start_time_loop > SEND_TIME) {
            transmittedFlag = true;
            transmissionState = RADIOLIB_ERR_TX_TIMEOUT;
          }
        }

        enableRadioInterrupt = false;

        if (transmissionState == RADIOLIB_ERR_NONE) {
#if defined DEBUG
          PCSerial.println(F("[SX1278] Success!"));
          PCSerial.print(F("[SX1278] Datarate:\t"));
          PCSerial.print(radio.getDataRate());
          PCSerial.println(F(" bps"));
#endif
        } else {
#if defined DEBUG
          PCSerial.print(F("[SX1278] Failed code: "));
          PCSerial.println(transmissionState);
#endif
        }
        digitalWrite(radio_ss, HIGH);
      }
      RadioCounter++;
    }
  }

  unsigned long delta_time_loop = millis() - start_time_loop;
  if (delta_time_loop < SEND_TIME) {
    delay(SEND_TIME - delta_time_loop);
  }
}

char hexCar[] = {'0','0'};
void printHex(byte num) {
  sprintf(hexCar, "%02X ", num);
#if defined DEBUG
  PCSerial.print(hexCar);
#endif
}
