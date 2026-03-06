#include "eeprom.h"

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  initEEPROM();

  Serial.begin(115200);
  while (!Serial) {}  // wait for serial port to open

  Serial.print(F("Erasing EEPROM"));
  for (int address = 0; address < 2048; address++) {
    digitalWrite(LED_BUILTIN, HIGH);
    writeEEPROM(address, 0xFF);
    digitalWrite(LED_BUILTIN, LOW);

    if (address % 64 == 0) {
      Serial.print(F("."));
    }
  }
  Serial.println(F(" OK"));

  delay(1000);

  Serial.println(F("Reading EEPROM contents"));
  for (int base = 0; base < 128; base++) {
    uint8_t data[16];
    readChunkEEPROM(base, data, sizeof(data));

    char msg[60];
    sprintf_P(msg, PSTR("%03x: %02x %02x %02x %02x %02x %02x %02x %02x  %02x %02x %02x %02x %02x %02x %02x %02x"),
              base, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
              data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15]);

    Serial.println(msg);
  }
}

void loop() {
  // Put your main code here, to run repeatedly:
}
