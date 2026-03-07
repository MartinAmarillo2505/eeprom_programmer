from time import sleep
from enum import Enum
from serial import Serial

PACKET_HEADER = b"\x00\xff"
PACKET_FOOTER = b"\xff"

PACKET_MAX_LENGTH = 255
PACKET_MAX_PAYLOAD_LENGTH = PACKET_MAX_LENGTH - 6


# Packet commands
class CommandCode(Enum):
  ACKNOWLEDGE = 0x00
  READ = 0x01
  WRITE = 0x02
  ERROR = 0xFF

  def parse_payload(self, payload: bytes):
    if self == CommandCode.READ:
      return payload
    if self == CommandCode.ERROR:
      code = ErrorCode(payload[0])
      length = payload[1]
      data = payload[2:] if length > 0 else b""
      return code, data


# Packet error codes
class ErrorCode(Enum):
  UNKNOWN_COMMAND = 0x00
  INVALID_LENGTH = 0x01
  CHECKSUM_MISMATCH = 0x02


class EEPROMProgrammer:
  def __init__(self, ser: Serial):
    self._ser = ser

  def _send_packet(self, command: CommandCode, payload=b"", attempts=5):
    if attempts <= 0:
      raise Exception("Failed to send packet")

    if len(payload) > PACKET_MAX_PAYLOAD_LENGTH:
      raise Exception("Payload too long")

    cmd = (
      PACKET_HEADER
      + command.value.to_bytes(1, "big")
      + len(payload).to_bytes(1, "big")
      + payload
      + compute_checksum(payload).to_bytes(1, "big")
      + PACKET_FOOTER
    )

    self._ser.write(cmd)

    # Wait for ACK or ERROR packet
    try:
      acknowledge = self._wait_for_packet()
      if acknowledge is None or acknowledge[0] is CommandCode.ERROR:
        sleep(0.1)
        return self._send_packet(command, payload, attempts - 1)
      elif acknowledge[0] is not CommandCode.ACKNOWLEDGE:
        raise Exception(
          f"Unexpected response: {acknowledge[0].value:x} {acknowledge[1].hex(' ')}"
        )
    except Exception as e:
      sleep(0.1)
      return self._send_packet(command, payload, attempts - 1)

    # Wait for response
    response = self._wait_for_packet()
    if response is None:
      sleep(0.1)
      return self._send_packet(command, payload, attempts - 1)

    if response[0] is not command:
      raise Exception(
        f"Unexpected response: {response[0].value:x} {response[1].hex(' ')}"
      )

    return response[1]

  def _wait_for_packet(self) -> tuple[CommandCode, bytes] | None:
    """
    Receives a packet from the serial port

    Returns:
      The command and the payload or None if no packet was received in time

    Raises:
      Exception: If the packet is invalid or the checksum is incorrect
    """
    if not self._ser.read_until(PACKET_HEADER).endswith(PACKET_HEADER):
      return None

    command = CommandCode(self._ser.read()[0])
    payloadLength = self._ser.read()[0]

    if payloadLength > PACKET_MAX_PAYLOAD_LENGTH:
      raise Exception("Payload too long")

    payload = self._ser.read(payloadLength)
    checksum = self._ser.read()[0]

    if self._ser.read() != PACKET_FOOTER:
      raise Exception("Invalid packet")

    if checksum != compute_checksum(payload):
      raise Exception("Checksum mismatch")

    return command, payload

  def read(self, address: int, length: int):
    return self._send_packet(
      CommandCode.READ, address.to_bytes(2, "big") + length.to_bytes(1, "big")
    )

  def write(self, address: int, data: bytes):
    self._send_packet(CommandCode.WRITE, address.to_bytes(2, "big") + data)


def compute_checksum(payload: bytes):
  checksum = 0
  for byte in payload:
    checksum = (checksum + byte) & 0xFF
  return (~checksum + 1) & 0xFF
