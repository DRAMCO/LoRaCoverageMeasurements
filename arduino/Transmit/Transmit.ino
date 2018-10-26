/*
   LoRa Transmitter for P2P communication

   This example transmits LoRa packets with one second delays
   between them. Each packet contains up to 256 bytes
   of data, in the form of:
    - Arduino String
    - null-terminated char array (C-string)
    - arbitrary binary data (byte array)
*/

// include the library
#include <LoRaLib.h>

#define POWER_ENABLE_PIN  8
#define LED               A0

// create instance of LoRa class using SX1278 module
// NSS/CS pin:        6
// DIO0/INT0 pin:     2
// DIO1/INT1 pin:     3
SX1278 lora = new Module(6, 2, 3);

// Variable declarations
int transmissioncase;

const int MAX_TRANSMISSIONCASE = 3;
const uint8_t spreadingFactor = 7;

// Reception time interval in ms
const int TRANSMISSION_INTERVAL = 5000;

void setup() {
  // Start serial monitor
  Serial.begin(9600);
  
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);

  // Enable Pin 3V3 LDO to wake up LoRa module
  pinMode(POWER_ENABLE_PIN, OUTPUT);
  digitalWrite(POWER_ENABLE_PIN, HIGH);
  
  // Initialize SX1278 with default settings
  Serial.print(F("Initialization SX1278"));
  
  // carrier frequency:           434.0 MHz
  // bandwidth:                   125.0 kHz
  // spreading factor:            9
  // coding rate:                 7
  // sync word:                   0x12
  // output power:                17 dBm
  // current limit:               100 mA
  // preamble length:             8 symbols
  // amplifier gain:              0 (automatic gain control)

  // Start LoRa with the default settings (above)
  int state = lora.begin();
  if (state == ERR_NONE) {
    Serial.println(F("Initialization successful"));
  } else {
    Serial.print(F("Initialization failed, code "));
    Serial.println(state);
    while (true);
  }

  
  state = lora.setSpreadingFactor(spreadingFactor);
  if(state != ERR_NONE) {
    Serial.println("SF error");
  }
  else Serial.println("SF set to 7");

  state : lora.setFrequency(869.525);
  if(state != ERR_NONE){
    Serial.println("FREQ error");
  }
  else Serial.println("FREQ set");
}

void loop() {
  digitalWrite(LED, HIGH);
  sendPacket();
  delay(1000);
  digitalWrite(LED, LOW);
  
  uint32_t startTime = millis();
  while (millis() - startTime < TRANSMISSION_INTERVAL);

  updateTransmissioncase();
  setLoRaSettings();
  
}

void sendPacket(){
  String str;
  
  str.concat(transmissioncase);
  
  Serial.print("Sending packet ... ");
  Serial.print("Spreading factor: ");
  Serial.println(spreadingFactor);

  // you can transmit C-string or Arduino string up to
  // 256 characters long

  int state = lora.transmit(str);

  if (state == ERR_NONE) {
    // the packet was successfully transmitted
    Serial.println(" success!");

    // print measured data rate
    Serial.print("Datarate:\t");
    Serial.print(lora.dataRate);
    Serial.println(" bps");

  } else if (state == ERR_PACKET_TOO_LONG) {
    // the supplied packet was longer than 256 bytes
    Serial.println(" too long!");

  } else if (state == ERR_TX_TIMEOUT) {
    // timeout occurred while transmitting packet
    Serial.println(" timeout!");
  }

  Serial.println();
}

void updateTransmissioncase(){
  if (transmissioncase == MAX_TRANSMISSIONCASE){
    transmissioncase = 1;
  }
  else transmissioncase++;
}

void setLoRaSettings(){
  if (transmissioncase == 1){
    changeLoRaSettings(8);
  }
  if (transmissioncase == 2){
    changeLoRaSettings(10);
  }
  if (transmissioncase == 3){
    changeLoRaSettings(12);
  }  
}

void changeLoRaSettings(int8_t power){
  int16_t state = lora.setOutputPower(power);
  
  if(state != ERR_NONE) {
    Serial.println("Failed to set output power");
  }
  else{
    Serial.print("Output power  to ");
    Serial.println(power);
  }
}
