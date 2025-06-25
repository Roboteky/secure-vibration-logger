const int vibrationPin = 2;

void setup() {
  pinMode(vibrationPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  int state = digitalRead(vibrationPin);
  if (state == HIGH) {
    Serial.println("Vibration detected");
    delay(1000);  // Debounce
  }
}
