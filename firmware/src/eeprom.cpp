#include "eeprom.h"

void initEEPROM() {
  pinMode(SHIFT_DATA, OUTPUT);
  pinMode(SHIFT_CLK, OUTPUT);
  pinMode(SHIFT_LATCH, OUTPUT);

  digitalWrite(EEPROM_OUT_EN, HIGH);
  digitalWrite(EEPROM_WR_EN, HIGH);
  pinMode(EEPROM_OUT_EN, OUTPUT);
  pinMode(EEPROM_WR_EN, OUTPUT);
}

void setAddress(uint16_t address) {
  shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, address >> 8);
  shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, address);

  // Latch shift
  digitalWrite(SHIFT_LATCH, LOW);
  delayMicroseconds(1);
  digitalWrite(SHIFT_LATCH, HIGH);
  delayMicroseconds(1);
  digitalWrite(SHIFT_LATCH, LOW);
}

void setDataPinsMode(uint8_t mode) {
  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin++) {
    pinMode(pin, mode);
  }
}

uint8_t readDataPins() {
  uint8_t data = 0;
  for (int pin = EEPROM_D7; pin >= EEPROM_D0; pin--) {
    data = (data << 1) | digitalRead(pin);
  }
  return data;
}

void readChunkEEPROM(uint16_t start, uint8_t *buf, size_t length) {
  setDataPinsMode(INPUT);
  delayMicroseconds(1);
  digitalWrite(EEPROM_OUT_EN, LOW);

  for (size_t i = 0; i < length; i++) {
    setAddress(start + i);
    delayMicroseconds(1);
    buf[i] = readDataPins();
  }
}

uint8_t readEEPROM(uint16_t address) {
  uint8_t data = 0;
  readChunkEEPROM(address, &data, 1);
  return data;
}

void writeDataPins(uint8_t data) {
  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin++) {
    digitalWrite(pin, data & 1);
    data >>= 1;
  }
}

void writeChunkEEPROM(uint16_t address, uint8_t *buf, size_t length) {
  digitalWrite(EEPROM_OUT_EN, HIGH);
  delayMicroseconds(1);
  setDataPinsMode(OUTPUT);

  for (size_t i = 0; i < length; i++) {
    setAddress(address + i);
    writeDataPins(buf[i]);

    digitalWrite(EEPROM_WR_EN, LOW);
    delayMicroseconds(1);
    digitalWrite(EEPROM_WR_EN, HIGH);

    delay(WRITE_DELAY_MS);
  }
}

void writeEEPROM(uint16_t address, uint8_t data) {
  writeChunkEEPROM(address, &data, 1);
}
