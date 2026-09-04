#include <SoftwareSerial.h>

SoftwareSerial LoRa(2, 3);

void setup() {
  Serial.begin(9600);
  LoRa.begin(9600);
}

void loop() {
  if (LoRa.available()) {
    char c = LoRa.read();
    Serial.write(c);
  }
}