#include "eeprom.h"
#include "protocol.h"

uint8_t cmd[PACKET_MAX_LENGTH];

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  initEEPROM();

  Serial.begin(115200);
}

void sendPacket(uint8_t command, uint8_t *payload, uint8_t payloadLength) {
  uint8_t i = 0, checksum = 0;

  cmd[i++] = PACKET_HEADER_MSB;
  cmd[i++] = PACKET_HEADER_LSB;
  cmd[i++] = command;
  cmd[i++] = payloadLength;
  for (int j = 0; j < payloadLength; j++) {
    cmd[i++] = payload[j];
    checksum += payload[j];
  }
  cmd[i++] = ~checksum + 1;
  cmd[i++] = PACKET_FOOTER;

  for (int j = 0; j < i; j++) {
    Serial.write(cmd[j]);
  }
}

void sendError(uint8_t errorCode, uint8_t *data, uint8_t dataLength) {
  uint8_t payload[dataLength + 2];
  payload[0] = errorCode;
  payload[1] = dataLength;
  memcpy(&payload[2], data, dataLength);

  sendPacket(PACKET_COMMAND_ERROR, payload, sizeof(payload));
}

void sendAck(uint8_t command, uint8_t payloadLength, uint8_t checksum) {
  uint8_t payload[3] = { command, payloadLength, checksum };
  sendPacket(PACKET_COMMAND_ACK, payload, 3);
}

void loop() {
  digitalWrite(LED_BUILTIN, LOW);
  if (Serial.available() < 6) return;

  // 1. Check packet header (0x00 and 0xFF in sequence)
  if (Serial.read() != PACKET_HEADER_MSB || Serial.peek() != PACKET_HEADER_LSB) return;
  Serial.read();  // Consume the remaining 0xFF

  digitalWrite(LED_BUILTIN, HIGH);

  // 2. Read the command byte
  uint8_t command = Serial.read();

  // 3. Read the payload length
  uint8_t payloadLength = Serial.read();
  if (payloadLength > PACKET_MAX_PAYLOAD_LENGTH) {
    sendError(PACKET_ERROR_INVALID_LENGTH, NULL, 0);
    return;
  }

  // 4. Read the payload and calculate the checksum locally
  uint8_t payload[payloadLength];
  uint8_t localChecksum = 0;
  uint32_t startTime = millis();

  for (int i = 0; i < payloadLength; i++) {
    while (!Serial.available()) {
      if (millis() - startTime > 100) return;
    }
    payload[i] = Serial.read();
    localChecksum += payload[i];
  }
  localChecksum = ~localChecksum + 1;

  // 5. Read the checksum and verify it
  while (!Serial.available()) {
    if (millis() - startTime > 100) return;
  }
  uint8_t checksum = Serial.read();
  if (checksum != localChecksum) {
    sendError(PACKET_ERROR_CHECKSUM_MISMATCH, NULL, 0);
    return;
  }

  // 6. Check packet footer (0xFF)
  while (!Serial.available()) {
    if (millis() - startTime > 100) return;
  }
  if (Serial.read() != PACKET_FOOTER) return;

  // Process the command
  if (command == PACKET_COMMAND_READ) {
    if (payloadLength != 3) {
      sendError(PACKET_ERROR_INVALID_LENGTH, NULL, 0);
      return;
    }

    uint16_t address = payload[0] << 8 | payload[1];
    uint8_t readLength = payload[2];
    if (readLength > PACKET_MAX_PAYLOAD_LENGTH) {
      sendError(PACKET_ERROR_INVALID_LENGTH, NULL, 0);
      return;
    }
    sendAck(command, payloadLength, checksum);

    uint8_t data[readLength];
    readChunkEEPROM(address, data, readLength);
    sendPacket(PACKET_COMMAND_READ, data, readLength);
  } else if (command == PACKET_COMMAND_WRITE) {
    uint16_t address = payload[0] << 8 | payload[1];
    sendAck(command, payloadLength, checksum);

    writeChunkEEPROM(address, &payload[2], payloadLength - 2);
    sendPacket(PACKET_COMMAND_WRITE, NULL, 0);
  } else {
    sendError(PACKET_ERROR_UNKNOWN_COMMAND, &command, 1);
  }
}
