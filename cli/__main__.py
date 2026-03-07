import time
from serial import Serial

from protocol import EEPROMProgrammer

SERIAL_PORT = "COM8"
BAUDRATE = 115200

if __name__ == "__main__":
  ser = Serial(baudrate=BAUDRATE, timeout=10)

  try:
    ser.port = SERIAL_PORT
    ser.open()
    print(f"Connected to {SERIAL_PORT} at {BAUDRATE}")

    programmer = EEPROMProgrammer(ser)
    time.sleep(2)

    print("Erasing EEPROM", end="", flush=True)
    for address in range(0, 2048, 64):
      programmer.write(address, b"\xff" * 64)
      print(".", end="", flush=True)
    print(" OK")

    print(f"Reading EEPROM contents")
    for address in range(0, 2048, 16):
      data = programmer.read(address, 16)
      print(f'{address:03x}: {data[:8].hex(" ")}  {data[8:].hex(" ")}')
  finally:
    ser.close()
