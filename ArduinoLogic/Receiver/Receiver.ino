#include <Arduino.h>
#include <SPI.h>
#include <RadioLib.h>

// ============================================================
// LILYGO T3-S3 SX1262 pins
// ============================================================

#define LORA_SCK    5
#define LORA_MISO   3
#define LORA_MOSI   6
#define LORA_CS     7
#define LORA_RST    8
#define LORA_DIO1  33
#define LORA_BUSY  34

// ============================================================
// LoRa settings
// These MUST match the transmitter
// ============================================================

#define LORA_FREQUENCY 868.0

#define LORA_BANDWIDTH 125.0
#define LORA_SPREADING_FACTOR 9
#define LORA_CODING_RATE 7
#define LORA_SYNC_WORD 0x12
#define LORA_POWER 22
#define LORA_PREAMBLE 1.8

// ============================================================
// Radio
// ============================================================

SX1262 radio = new Module(
    LORA_CS,
    LORA_DIO1,
    LORA_RST,
    LORA_BUSY
);

// Packet received flag
volatile bool packetReceived = false;

void setFlag()
{
    packetReceived = true;
}

// ============================================================
// SETUP
// ============================================================

void setup()
{
    Serial.begin(115200);
    delay(1000);

    Serial.println();
    Serial.println("================================");
    Serial.println(" LILYGO T3-S3 LoRa Receiver");
    Serial.println("================================");

    // Start SPI using the T3-S3 SX1262 pins
    SPI.begin(
        LORA_SCK,
        LORA_MISO,
        LORA_MOSI
    );

    Serial.println("Initializing SX1262...");

    // Initialize radio
    int state = radio.begin(
        LORA_FREQUENCY,
        LORA_BANDWIDTH,
        LORA_SPREADING_FACTOR,
        LORA_CODING_RATE,
        LORA_SYNC_WORD,
        LORA_POWER,
        LORA_PREAMBLE
    );

    if (state != RADIOLIB_ERR_NONE)
    {
        Serial.print("LoRa initialization failed, code: ");
        Serial.println(state);

        while (true)
        {
            delay(1000);
        }
    }

    Serial.println("LoRa initialized successfully!");

    // Configure DIO1 interrupt
    radio.setDio1Action(setFlag);

    // Start receiving
    state = radio.startReceive();

    if (state != RADIOLIB_ERR_NONE)
    {
        Serial.print("Failed to start receiver, code: ");
        Serial.println(state);

        while (true)
        {
            delay(1000);
        }
    }

    Serial.println("Listening for LoRa packets...");
    Serial.println();
}

// ============================================================
// LOOP
// ============================================================

void loop()
{
    if (!packetReceived)
    {
        return;
    }

    // Clear flag
    packetReceived = false;

    // Read packet
    String receivedData;

    int state = radio.readData(receivedData);

    if (state == RADIOLIB_ERR_NONE)
    {
        Serial.println("================================");
        Serial.println("PACKET RECEIVED");
        Serial.println("================================");

        Serial.print("Data: ");
        Serial.println(receivedData);

        Serial.print("RSSI: ");
        Serial.print(radio.getRSSI());
        Serial.println(" dBm");

        Serial.print("SNR:  ");
        Serial.print(radio.getSNR());
        Serial.println(" dB");

        Serial.print("Frequency error: ");
        Serial.print(radio.getFrequencyError());
        Serial.println(" Hz");

        Serial.println();
    }
    else
    {
        Serial.print("Error reading packet: ");
        Serial.println(state);
    }

    // Go back to receive mode
    state = radio.startReceive();

    if (state != RADIOLIB_ERR_NONE)
    {
        Serial.print("Failed to restart receiver: ");
        Serial.println(state);
    }
}