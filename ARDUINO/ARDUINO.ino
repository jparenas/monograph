#include <Wire.h>
#include <Adafruit_MCP4725.h>

#define REPETITIONS 3

Adafruit_MCP4725 dac;

int voltage;
long timePerSample;

void setup() {
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);

  pinMode(13, OUTPUT);

  dac.begin(0x60);
  
  Serial.begin(115200);
}

void loop() {
  voltage = 0;
  timePerSample = 0;
  bool check = false;

  while (!check) {
    while (Serial.available() > 0) {
      voltage = Serial.readStringUntil('\n').toInt();
      voltage = constrain(voltage, 0, 4095);
      if(voltage) {
        check = true;
      }
    }
  }

  check = false;
  while (!check) {
    while (Serial.available() > 0) {
      timePerSample = Serial.readStringUntil('\n').toInt();
      timePerSample = constrain(timePerSample, 0, 100000);
      if(timePerSample) {
        check = true;
      }
    }
  }

  dac.setVoltage(voltage, false);

  delay(5);

  long startTime = millis();

  Serial.println("START");

  digitalWrite(13, HIGH);

  while(millis() - startTime <= timePerSample) {
    for(int i = 0; i < REPETITIONS; i++) {
      analogRead(A0);
    }
    int firstSample = analogRead(A0);
    for(int i = 0; i < REPETITIONS; i++) {
      analogRead(A1);
    }
    int secondSample = analogRead(A1);
  
    Serial.println(secondSample - firstSample);
  }

  Serial.println("END");

  digitalWrite(13, LOW);
}
