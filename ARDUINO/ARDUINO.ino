// This sketch monitors the analog pin over a short period of time determined by serial input, 
// transmitting the data over Serial in order to plot it in a computer using the complementary Python script.

int voltage;
int repetitions;

void setup() {
  Serial.begin(115200);

  pinMode(13, OUTPUT);
}

void loop() {
  bool check = false;
  
  // Waits for the start command, followed by the properties.
  while (!check) {
    while (Serial.available() > 0) {
      String string = Serial.readStringUntil('\n');
      if (string == "START") {
        Serial.println("READY");
        check = true;
        break;
      }
    }
  }
  check = false;

  while (!check) {
    while (Serial.available() > 0) {
      String string = Serial.readStringUntil('\n');
      if (string == "MEASURE") {
        check = true;
        break;
      } else {
        int index = string.indexOf("V:");
        if (index != -1) {
          voltage = constrain(string.substring(index+2).toInt(), 0, (2 << 11 - 1));
        }
        index = string.indexOf("R:");
        if (index != -1) {
          repetitions = string.substring(index+2).toInt();
        }
      }
    }
  }

  digitalWrite(13, HIGH);
  long timeStarted = millis();
  for (int i = 0; i < repetitions; i++) {
    Serial.print(analogRead(A0));
    Serial.print(" ");
    Serial.print(analogRead(A0));
    Serial.print(" ");
    Serial.println(millis() - timeStarted);
  }
  digitalWrite(13, LOW);
}
