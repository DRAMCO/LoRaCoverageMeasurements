/*  ____  ____      _    __  __  ____ ___
   |  _ \|  _ \    / \  |  \/  |/ ___/ _ \
   | | | | |_) |  / _ \ | |\/| | |  | | | |
   | |_| |  _ <  / ___ \| |  | | |__| |_| |
   |____/|_| \_\/_/   \_\_|  |_|\____\___/
                             research group
                               dramco.be/

    KU Leuven - Technology Campus Gent,
    Gebroeders De Smetstraat 1,
    B-9000 Gent, Belgium

           File: transmitter.ino
        Created: 2018-10-26
         Author: Chesney Buylle and Gilles Callebaut
        Version: 1.0
    Description:
              LoRa Transmitter for P2P communication

              Receive LoRa packets

              Each packet contains 2 bytes
              of data, in the form of:
                - transmit power
                - spreading factor

                LoRa Receiver for P2P communication
                This example listens for LoRa transmissions and tries to
                receive them. To successfully receive data, the following
                settings have to be the same on both transmitter
                and receiver:
                 - carrier frequency
                 - bandwidth
                 - spreading factor
                 - coding rate
                 - sync word
                 - preamble length
*/


#include <LoRaLibMod.h>
#include <TinyGPS++.h> //https://github.com/mikalhart/TinyGPSPlus
#include <SoftwareSerial.h>
#include <SPI.h>
#include <SD.h>

#define POWER_ENABLE_PIN          8
#define GPS_WRITE_UPDATE_INTERVAL 1000
#define SETTING_CHANGE_INTERVAL   20000
#define MAX_TRANSMISSIONCASE      3
#define DELIMETER                 ','
#define GPS_RX_PIN                7
#define GPS_TX_PIN                10
#define GPS_BAUD                  9600
#define CAN_WE_WRITE_PIN          A1
#define MAX_SETTINGS              3

float FREQ = 869.525;

//#define DEBUG
#define DEBUG_ERR

// be sure that DEBUG ERR is defined if DEBUG is on
#ifdef DEBUG
#define DEBUG_ERR
#endif


// create instance of LoRa class using SX1278 module
// NSS/CS pin:        6
// DIO0/INT0 pin:     2
// DIO1/INT1 pin:     3
SX1278 lora = new Module(6, 2, 3);

File myFile;


const uint8_t SPREADING_FACTORS[] = {7, 9, 12};
uint8_t current_spreading_factor_id = 0;

// The TinyGPS++ object
TinyGPSPlus gps;
// The serial connection to the GPS device
SoftwareSerial ss(GPS_RX_PIN, GPS_TX_PIN);

TinyGPSCustom pdop(gps, "GPGSA", 15); // $GPGSA sentence, 15th element
TinyGPSCustom hdop(gps, "GPGSA", 16); // $GPGSA sentence, 16th element
TinyGPSCustom vdop(gps, "GPGSA", 17); // $GPGSA sentence, 17th element

float latitude;
float longitude;
boolean locationValid = false;
unsigned long satVal;
boolean satValid = false;
float hdopVal;
float vdopVal;
float pdopVal;
boolean hdopValid = false;
unsigned long ageVal;
boolean ageValid = false;
TinyGPSDate dateVal;
TinyGPSTime timeVal;
float altitudeVal;
boolean altitudeValid = false;
float courseVal;
boolean courseValid = false;
float speedVal;
boolean speedValid;
uint8_t spreadingFactor = 0;

boolean packetReceived = false;

uint32_t lastGPSupdate;
uint32_t lastSettingsChanged;

volatile bool receivedFlag = false;



void blink() {
  if (myFile) {
    myFile.close();
  }
  while (1) {
    digitalWrite(A0, HIGH);
    delay(500);
    digitalWrite(A0, LOW);
    delay(500);
  }
}



void setup() {
  pinMode(A0, OUTPUT);
  digitalWrite(A0, LOW);

  pinMode(CAN_WE_WRITE_PIN, INPUT);
  checkCanWrite();
  Serial.begin(9600);

  // Begin serial connection to the GPS device
  ss.begin(GPS_BAUD);

  //Enable Pin 3V3 LDO
  pinMode(POWER_ENABLE_PIN, OUTPUT);
  digitalWrite(POWER_ENABLE_PIN, HIGH);

  initLoRa();

  //debug(F("Initializing SD card..."));
  if (!SD.begin(10)) {
   //debug(F("initialization SD failed!"));
    blink();
  } else {
    myFile = SD.open("PACKETS.txt", FILE_WRITE);
  }
  //debug(F("initialization SD done."));

  lastGPSupdate = millis();
  lastSettingsChanged = millis();
}

String getDateTimeString(TinyGPSDate &d, TinyGPSTime &t)
{
  char sz[32];
  sprintf(sz, "%02d/%02d/%02d ", d.month(), d.day(), d.year());

  String s = sz;


  sprintf(sz, "%02d:%02d:%02d ", t.hour(), t.minute(), t.second());
  s.concat(sz);
  debug(s);
  return s;

  smartDelay(0);
}
void writeToSD(bool packet) {
  checkCanWrite();

  if (myFile) {
    myFile.print(getDateTimeString(gps.date, gps.time));
    myFile.print(DELIMETER);
    myFile.print(satVal, 5);
    myFile.print(DELIMETER);
    myFile.print(satValid);
    myFile.print(DELIMETER);
    myFile.print(hdopVal, 5);
    myFile.print(DELIMETER);
    myFile.print(hdopValid);
    myFile.print(DELIMETER);
    myFile.print(vdopVal, 5);
    myFile.print(DELIMETER);
    myFile.print(pdopVal, 5);
    myFile.print(DELIMETER);
    myFile.print(latitude, 6);
    myFile.print(DELIMETER);
    myFile.print(longitude, 6);
    myFile.print(DELIMETER);
    myFile.print(locationValid);
    myFile.print(DELIMETER);
    myFile.print(ageVal, 5);
    myFile.print(DELIMETER);
    myFile.print(ageValid);
    myFile.print(DELIMETER);
    myFile.print(altitudeVal, 6);
    myFile.print(DELIMETER);
    myFile.print(altitudeValid);
    myFile.print(DELIMETER);
    myFile.print(courseVal, 2);
    myFile.print(DELIMETER);
    myFile.print(courseValid);
    myFile.print(DELIMETER);
    myFile.print(speedVal, 2);
    myFile.print(DELIMETER);
    myFile.print(speedValid);
    myFile.print(DELIMETER);
    myFile.print(lora.lastPacketRSSI);
    myFile.print(DELIMETER);
    myFile.print(lora.lastPacketSNR);
    myFile.print(DELIMETER);
    myFile.print(lora.getFrequencyError());
    myFile.print(DELIMETER);

    myFile.print(spreadingFactor);

    myFile.print(DELIMETER);
    myFile.println(packet);

    //debug(F("DONE."));
  }
}

void loop() {
  checkRx();

  uint32_t currentTime = millis();

  if (analogRead(CAN_WE_WRITE_PIN) > 25) {
    blink();
  }

  if (currentTime - lastGPSupdate > GPS_WRITE_UPDATE_INTERVAL) {
    writeToSD(false);
    lastGPSupdate = millis();
  }

  checkRx();

  if (currentTime - lastSettingsChanged > SETTING_CHANGE_INTERVAL) {
    hopToDifferentSF();
    lastSettingsChanged = millis();
  }

  checkRx();

  receiveGPS();

  checkRx();


}

void checkRx() {
  if (receivedFlag) {
    digitalWrite(A0, HIGH);
    receivePacket();
    receivedFlag = false;
    digitalWrite(A0, LOW);

  }
}

void hopToDifferentSF() {
  current_spreading_factor_id = (current_spreading_factor_id + 1) % MAX_SETTINGS;
  loraSetSF(SPREADING_FACTORS[current_spreading_factor_id]);
  loraListen();
}


bool receivePacket() {
  byte arr[1];

  int state = lora.readData(arr, 1);
  if (state == ERR_NONE) {
    //debug(F("PACKET RECEIVED"));
    spreadingFactor = arr[0];
    debug(String(spreadingFactor));
  } else {
    //error(F("packet rx?"), state);
  }

  writeToSD(true);

}

// This custom version of delay() ensures that the gps object
// is being "fed".
static void smartDelay(unsigned long ms)
{
  unsigned long start = millis();
  do
  {
    while (ss.available())
      gps.encode(ss.read());
  } while (millis() - start < ms && !receivedFlag);
}




void receiveGPS() {
  smartDelay(1000);

  latitude = gps.location.lat();
  longitude = gps.location.lng();
  locationValid = gps.location.isValid();
  satVal = gps.satellites.value();
  satValid = gps.satellites.isValid();
  hdopVal = gps.hdop.hdop();
  hdopValid = gps.hdop.isValid();
  ageVal = gps.location.age();
  ageValid = gps.location.isValid();
  dateVal = gps.date;
  timeVal = gps.time;
  altitudeVal = gps.altitude.meters();
  altitudeValid = gps.altitude.isValid();
  courseVal = gps.course.deg();
  courseValid = gps.course.isValid();
  speedVal = gps.speed.kmph();
  speedValid = gps.speed.isValid();
  pdopVal = String(pdop.value()).toFloat(); 
  vdopVal = String(vdop.value()).toFloat();

}




void checkCanWrite() {
  if (analogRead(CAN_WE_WRITE_PIN) > 25) {
    blink();
  }
}

void setMsgRx() {
  receivedFlag = true;
}

void initLoRa() {
  debug(F("Initializing ... "));
  loraBegin();
  lora.setDio0Action(setMsgRx);
  loraSetSF(SPREADING_FACTORS[current_spreading_factor_id]);
  loraSetFreq();
  loraListen();
}

/* LORA specific methods */
void loraBegin() {
  int16_t state = lora.begin();
  if (state == ERR_NONE) {
    success(F("Initialization successful"));
  } else {
    error("Initialization failed", state);
  }
}

void loraListen() {
  debug(F("Starting to listen ... "));
  int16_t state = lora.startReceive();
  if (state == ERR_NONE) {
    success(F("success!"));
  } else {
    error(F("failed, code "), state);
  }
}


void loraSetSF(uint8_t sf) {
  // ------------------- SPREADING FACTOR -------------------
  //debug(F("Setting Spreading Factor"));
  int state = lora.setSpreadingFactor(sf);
  if (state != ERR_NONE) {
    error(state);
  }
  else {
    //success(String(sf));
  }
}


void loraSetFreq() {
  // ------------------- CARRIER FREQ -------------------
  //debug(F("Setting Frequency"));
  int16_t state = lora.setFrequency(FREQ);
  if (state != ERR_NONE) {
    error(state);
  }
  else {
    //String s = "FREQ set ";
    //s.concat(FREQ);
    //success(s);
  }
}


/* SERIAL output information */
void debug(String s) {
#ifdef DEBUG
  Serial.println(s);
#endif
}

void error(String s) {
#ifdef DEBUG_ERR
  Serial.println(s);
#endif
  blink();
}

void error(String s, uint16_t state) {
#ifdef DEBUG_ERR
  Serial.println(s);
  Serial.println(state);
#endif
  blink();
}

void error(uint16_t state) {
#ifdef DEBUG_ERR
  Serial.println(state);
#endif
  blink();
}

void success(String s) {
#ifdef DEBUG
  Serial.println(s);
#endif
}
