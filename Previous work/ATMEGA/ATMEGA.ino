// Date and time functions using a DS3231 RTC connected via I2C and Wire lib
#include <Wire.h>
#include "RTClib.h"
#include <SPI.h>
#include "SdFat.h"
#include "LowPower.h"

//#define DEBUG

const byte timeDelay = 2;

#ifdef DEBUG
  const byte firstItirerations = 0;
  const byte secondItirerations = 0;
  const byte thirdItirerations = 1;
#else
  const byte firstItirerations = 1;
  const byte secondItirerations = 1;
  const byte thirdItirerations = 3;
#endif

const byte timePin = 9;
const byte ledPin = 2;

const byte initTime = 160;
const byte standByTime = 100;

unsigned long lastFileSize = 0;

RTC_DS3231 rtc;

SdFat SD;
File logFile;

void setup () {
  #ifdef DEBUG
    Serial.begin(115200);
  #endif

  #ifdef DEBUG
    Serial.println("Let's begin!");
  #endif

  pinMode(timePin, OUTPUT);
  pinMode(A0, INPUT);

  //Sets the reference voltage to the 1.1V internal one, and reads a few results
  //in order to calibrate it
  analogReference(INTERNAL);
  for (int i = 0; i < 6; i++) {analogRead(A0);};

  digitalWrite(timePin, LOW);
  delay(timeDelay);
  
  if (!rtc.begin()) {
    #ifdef DEBUG
      Serial.println("Couldn't find RTC");
    #endif
    digitalWrite(timePin, HIGH);
    
    while(true) {
      debugLed(2, initTime);
      delay(1000);
    };
  }

  #ifdef DEBUG
    Serial.println("RTC Found!");
  #endif

  if (rtc.lostPower()) {
    #ifdef DEBUG
      Serial.println("RTC lost power, lets set the time!");
    #endif
    //rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    
    while(true) {
      debugLed(4, initTime);
      delay(1000);  
    };
  }

  digitalWrite(timePin, HIGH);
  digitalWrite(SDA, LOW);
  digitalWrite(SCL, LOW);

  #ifdef DEBUG
    Serial.println("Finding SD Card!");
  #endif

  if (!SD.begin(10)) {
    #ifdef DEBUG
      Serial.println("initialization failed!");
    #endif
    while(true) {
      debugLed(3, initTime);
      delay(1000);  
    };
  }

  #ifdef DEBUG
    Serial.println("SD Card Found!");
  #endif

  logFile = SD.open("samples.txt", FILE_WRITE);

  logFile.seek(logFile.size());

  debugLed(1, initTime);
}

void loop () {
  //First, this gets the time and formats it
  digitalWrite(timePin, LOW);
  digitalWrite(SDA, HIGH);
  digitalWrite(SCL, HIGH);
  delay(timeDelay);
  
  DateTime now = rtc.now();

  String currentSample;

  digitalWrite(timePin, HIGH);
  digitalWrite(SDA, LOW);
  digitalWrite(SCL, LOW);
  
  currentSample = now.month();
  currentSample += '/';
  currentSample += now.day();
  currentSample += '-';
  currentSample += now.hour();
  currentSample += ":";
  currentSample += now.minute();
  currentSample += "#";
  currentSample += now.second();
  currentSample += "&";

  currentSample += analogRead(A0);

  currentSample += ";";

  #ifdef DEBUG
    Serial.print(currentSample);
    Serial.print(" File size so far:");
    Serial.println(logFile.size());
  #endif

  logFile.print(currentSample);

  logFile.flush();

  if (logFile.size() == lastFileSize) {
    logFile.close();
    logFile = SD.open("samples.txt", FILE_WRITE);
  }
  else {
    lastFileSize = logFile.size();
  }

  for(byte x = 0; x < firstItirerations;x++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF); 
    debugLed(1, standByTime);
  }
  for(byte x = 0; x < secondItirerations;x++) {
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF); 
    debugLed(1, standByTime);
  }
  for(byte x = 0; x < thirdItirerations;x++) {
    LowPower.powerDown(SLEEP_1S, ADC_OFF, BOD_OFF); 
    debugLed(1, standByTime);
  }
}

void debugLed(byte pulses, byte period) {
  pinMode(ledPin, OUTPUT);
  for (byte i = 0; i < pulses; i++) {
    digitalWrite(ledPin, HIGH);
    delay(period);
    digitalWrite(ledPin, LOW);
    delay(period);
  }
  pinMode(ledPin, INPUT);
}

