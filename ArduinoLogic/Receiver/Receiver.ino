#include <RadioLib.h>
#include <FastCRC.h>
#include <SPI.h>

#define RADIO_SS    10  // NSS
#define RADIO_DIO0  2   
#define RADIO_RST   9   

SX1278 radio = new Module(RADIO_SS, RADIO_DIO0, RADIO_RST, -1);
FastCRC8 CRC8;

struct __attribute__((packed)) FULLDATA {
  uint8_t gps_crc;              
  uint16_t number;              

  int16_t inside_temp;          
  int16_t inside_hum;          
  int16_t external_temp;        
  int16_t external_hum;        

  float accel_x;                
  float accel_y;                
  float accel_z;                

  float gyro_x;                
  float gyro_y;                
  float gyro_z;                

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

uint8_t buffer[sizeof(FULLDATA)];  
FULLDATA received;                 

void setup() {
  Serial.begin(9600);
  while (!Serial); 

  Serial.println(F("[SX1278] Initializing ..."));
  int state = radio.begin(439.666, 31.25, 12, 7, 0x12, 17, 8, 0);

  if (state == RADIOLIB_ERR_NONE) {
    Serial.println(F("[SX1278] Radio init successful!"));
  } else {
    Serial.print(F("[SX1278] Failed, code "));
    Serial.println(state);
    while (true); 
  }

  radio.setCRC(false); 
  Serial.println("Receiver ready.");

  radio.startReceive();
}

void loop() {
  if (radio.available()) {
    int len = radio.readData(buffer, sizeof(buffer));
   
    if (len == sizeof(FULLDATA)) {
      memcpy(&received, buffer, sizeof(FULLDATA));

      uint8_t computed_crc = CRC8.smbus(buffer + 1, sizeof(FULLDATA) - 1);
      if (computed_crc != received.gps_crc) {
        Serial.println("CRC MISMATCH! Data corrupted.");
      } else {
        Serial.println(F("\n--- Received Packet ---"));
        Serial.print(F("Packet #: "));            Serial.println(received.number);
       
        Serial.print(F("Inside Temp: "));          Serial.print(received.inside_temp/100.0); Serial.println(F(" °C"));
        Serial.print(F("Inside Humidity: "));      Serial.print(received.inside_hum/100.0); Serial.println(F(" %"));
        Serial.print(F("External Temp: "));        Serial.print(received.external_temp/100.0); Serial.println(F(" °C"));
        Serial.print(F("External Humidity: "));    Serial.print(received.external_hum/100.0); Serial.println(F(" %"));
       
        Serial.print(F("Accel X: "));              Serial.print(received.accel_x); Serial.println(F(" m/s²"));
        Serial.print(F("Accel Y: "));              Serial.print(received.accel_y); Serial.println(F(" m/s²"));
        Serial.print(F("Accel Z: "));              Serial.print(received.accel_z); Serial.println(F(" m/s²"));
       
        Serial.print(F("Gyro X: "));               Serial.print(received.gyro_x); Serial.println(F(" rad/s"));
        Serial.print(F("Gyro Y: "));               Serial.print(received.gyro_y); Serial.println(F(" rad/s"));
        Serial.print(F("Gyro Z: "));               Serial.print(received.gyro_z); Serial.println(F(" rad/s"));
       
        Serial.print(F("Pi Temp: "));              Serial.print(received.pi_temp/10.0); Serial.println(F(" °C"));
       
        Serial.print(F("Latitude: "));             Serial.print(received.lat/1000000.0, 6); Serial.println(F(" °"));
        Serial.print(F("Longitude: "));            Serial.print(received.lon/1000000.0, 6); Serial.println(F(" °"));
        Serial.print(F("Altitude: "));             Serial.print(received.alt/100.0); Serial.println(F(" m"));
       
        Serial.print(F("Pressure: "));             Serial.print(received.pressure/100.0); Serial.println(F(" hPa"));
        Serial.print(F("BMP Temp: "));             Serial.print(received.temp_bmp/100.0); Serial.println(F(" °C"));
        Serial.print(F("BMP Alt: "));              Serial.print(received.alt_bmp/100.0); Serial.println(F(" m"));
       
        Serial.print(F("UV: "));                   Serial.println(received.uv);
        Serial.print(F("Ambient Light: "));        Serial.println(received.ambient_light);
        Serial.print(F("UVI: "));                  Serial.println(received.uvi);
        Serial.print(F("Lux: "));                  Serial.println(received.lux);
        Serial.print(F("CPL: "));                  Serial.println(received.cpl);
       
        Serial.println(F("------------------------"));
      }
    } else {
      Serial.print(F("Received unexpected packet size: "));
      Serial.print(len);
      Serial.print(F(" expected: "));
      Serial.println(sizeof(FULLDATA));
    }

    radio.startReceive(); 
  }
 
  delay(10);
}