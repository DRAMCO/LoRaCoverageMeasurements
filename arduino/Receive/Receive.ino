/*
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

// Include libraries
#include <LoRaLib.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include <SPI.h>
#include <SD.h>

#define POWER_ENABLE_PIN 8

// create instance of LoRa class using SX1278 module
// NSS/CS pin:        6
// DIO0/INT0 pin:     2
// DIO1/INT1 pin:     3
SX1278 lora = new Module(6, 2, 3);

File myFile;

// Variable declarations
int transmissioncase = 1;

#define MAX_TRANSMISSIONCASE  3

#define DELIMETER ','

// Reception time interval in ms
#define RECEPTION_INTERVAL  20000
//const int GPS_WAIT_INTERVAL_MS = 3500;
#define GPS_UPDATE_INTERVAL  1000
#define SETTING_CHANGE_INTERVAL  20000

//pin 7 en pin 10 gebruiken
static const int RXPin = 7, TXPin = 10;
static const uint32_t GPSBaud = 9600;

// The TinyGPS++ object
TinyGPSPlus gps;

// The serial connection to the GPS device
SoftwareSerial ss(RXPin, TXPin);

int spreadingFactor = 7;
String receivedTransmissioncase;

float latitude;
float longitude;
boolean locationValid = false;
unsigned long satVal;
boolean satValid = false;
float hdopVal;
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

boolean packetReceived = false;

uint32_t lastGPSupdate;
uint32_t lastSettingsChanged;

volatile bool receivedFlag = false;

int CAN_WE_WRITE_PIN = A1;

void blink(){
  if(myFile){
    myFile.close();
  }
  while (1){
      digitalWrite(A0, HIGH);
      delay(500);
      digitalWrite(A0, LOW);
      delay(500);
    }
}

void checkCanWrite(){
  if(analogRead(CAN_WE_WRITE_PIN) > 25){blink();}
}

void setMsgRx(){
  receivedFlag = true;
}

void initLoRa(){
  
  // Initialize SX1278 with default settings
  Serial.print(F("Initializing ... "));
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

  lora.setDio0Action(setMsgRx);

  
  

  state = lora.setSpreadingFactor(7);
  if(state != ERR_NONE) {
    Serial.println(F("SF error"));
  }
  else Serial.println(F("SF set to 7"));

  // configure publicly accessible settings
  state = lora.setFrequency(869.525);
  if(state != ERR_NONE) {
    Serial.println(F("Frequency ERROR"));
  }
  else Serial.println(F("Frequency SET"));


  Serial.print(F("Starting to listen ... "));
  state = lora.startReceive();
  if (state == ERR_NONE) {
    Serial.println(F("success!"));
  } else {
    Serial.print(F("failed, code "));
    Serial.println(state);
    while (true);
  }
}

void setup() {
  pinMode(A0, OUTPUT);
  digitalWrite(A0, LOW);

  pinMode(CAN_WE_WRITE_PIN, INPUT);
  checkCanWrite();
  Serial.begin(9600);

  // Begin serial connection to the GPS device
  ss.begin(GPSBaud);

  //Enable Pin 3V3 LDO
  pinMode(POWER_ENABLE_PIN, OUTPUT);
  digitalWrite(POWER_ENABLE_PIN, HIGH);


  initLoRa();
  

  
  Serial.println(F("Initializing SD card..."));
  if (!SD.begin(10)) {
    Serial.println(F("initialization SD failed!"));
    blink();
  }else{
     myFile = SD.open("PACKETS.txt", FILE_WRITE);
  }
  Serial.println(F("initialization SD done."));

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
     Serial.println(s);
     return s;

  smartDelay(0);
}
void writeToSD(bool packet){
  checkCanWrite();
  
  digitalWrite(A0, HIGH);

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
    
    myFile.print(receivedTransmissioncase);
    myFile.print(DELIMETER);
    myFile.print(spreadingFactor);
    
    myFile.print(DELIMETER);
    myFile.println(packet);
    
    Serial.println(F("DONE."));
    digitalWrite(A0, LOW);
  }
}

void loop() {
  uint32_t currentTime = millis();

  while(analogRead(CAN_WE_WRITE_PIN) > 25){blink();}
  
  if (currentTime - lastGPSupdate > GPS_UPDATE_INTERVAL){
    writeToSD(false);
    lastGPSupdate = millis();
  }

  if(receivedFlag) {
    Serial.println("RX flag");
    receivePacket();
    receivedFlag = false;
    writeToSD(true);
  }

  if (currentTime - lastSettingsChanged > SETTING_CHANGE_INTERVAL){
    updateTransmissioncase();
    setLoRaSettings();
    lastSettingsChanged = millis();
  }

  if(receivedFlag) {
    Serial.println("RX flag");
    receivePacket();
    receivedFlag = false;
    writeToSD(true);
  }
  
  receiveGPS();
  
  if(receivedFlag) {
    Serial.println("RX flag");
    receivePacket();
    receivedFlag = false;
    writeToSD(true);
  }

  
}

void changeLoRaSettings(uint8_t sf){
  int16_t state;
  
  state = lora.setSpreadingFactor(sf);
  if(state != ERR_NONE) {
    Serial.println("Failed to set SF");
  }
  else{
    Serial.print("Spreading Factor set to ");
    Serial.println(sf);
    spreadingFactor = sf;
  }
  lora.startReceive();
}

void setLoRaSettings(){
  if (transmissioncase == 1){
    changeLoRaSettings(7);
  }
  if (transmissioncase == 2){
    changeLoRaSettings(7);
  }  
  if (transmissioncase == 3){
    changeLoRaSettings(7);
  }
}

void updateTransmissioncase(){
  if (transmissioncase == MAX_TRANSMISSIONCASE){
    transmissioncase = 1;
  }
  else transmissioncase++;
}


bool receivePacket(){
  String str;
  int state;
  
  state = lora.readData(str);
  if (state == ERR_NONE){
    Serial.print("PACKET RECEIVED");
    receivedTransmissioncase = str.substring(0,1);
    Serial.print("RECEIVED TRANSMISSION CASE: ");
    Serial.println(receivedTransmissioncase);    
  }
  
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

static void printFloat(float val, bool valid, int len, int prec){
  if (!valid)
  {
    while (len-- > 1)
      Serial.print('*');
    Serial.print(' ');
  }
  else
  {
    Serial.print(val, prec);
    int vi = abs((int)val);
    int flen = prec + (val < 0.0 ? 2 : 1); // . and -
    flen += vi >= 1000 ? 4 : vi >= 100 ? 3 : vi >= 10 ? 2 : 1;
    for (int i=flen; i<len; ++i)
      Serial.print(' ');
  }
  smartDelay(0);
}

static void printInt(unsigned long val, bool valid, int len)
{
  char sz[32] = "*****************";
  if (valid)
    sprintf(sz, "%ld", val);
  sz[len] = 0;
  for (int i=strlen(sz); i<len; ++i)
    sz[i] = ' ';
  if (len > 0) 
    sz[len-1] = ' ';
  Serial.print(sz);
  smartDelay(0);
}

void receiveGPS(){
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
}
