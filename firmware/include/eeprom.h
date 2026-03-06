#pragma once

#include <Arduino.h>

#define SHIFT_DATA 2
#define SHIFT_CLK 3
#define SHIFT_LATCH 4

#define EEPROM_D0 5
#define EEPROM_D7 12

#define EEPROM_OUT_EN A1
#define EEPROM_WR_EN A2

#define WRITE_DELAY_MS 10

void initEEPROM();

void setAddress(uint16_t address);

void readChunkEEPROM(uint16_t start, uint8_t *buf, size_t length);

uint8_t readEEPROM(uint16_t address);

void writeChunkEEPROM(uint16_t address, uint8_t *buf, size_t length);

void writeEEPROM(uint16_t address, uint8_t data);
