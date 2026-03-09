from protocol import EEPROMProgrammer
from io import BufferedReader, BufferedWriter


def dump_eeprom(programmer: EEPROMProgrammer, start_address: int, size: int):
  end_address = min(start_address + size, 2048)
  end_base = min((end_address >> 4) + 1, 2048 >> 4)

  for base_address in range(start_address >> 4, end_base):
    address = max(base_address << 4, start_address)
    length = min((base_address + 1) << 4, end_address) - address

    if length == 0:
      continue

    data = list(programmer.read(address, length))
    if length < 16:
      left_padding = max(start_address - (base_address << 4), 0)
      right_padding = max(16 - length - left_padding, 0)
      data = [None] * left_padding + data + [None] * right_padding

    data = [f"{x:02x}" if x is not None else "··" for x in data]
    print(f"{base_address:03x}: {' '.join(data[:8])}  {' '.join(data[8:])}")


def read_eeprom(
  programmer: EEPROMProgrammer,
  file: BufferedWriter,
  start_address: int,
  size: int,
  block_size: int,
):
  print(
    f"Reading {size} bytes from 0x{start_address:03x} to 0x{start_address + size - 1:03x}",
    end="",
    flush=True,
  )

  left = size % block_size
  for address in range(start_address, (start_address + size) - left, block_size):
    file.write(programmer.read(address, block_size))
    print(".", end="", flush=True)

  if left > 0:
    file.write(programmer.read((start_address + size) - left, left))

  print(" done")


from io import BufferedReader
import time
from protocol import EEPROMProgrammer


def write_eeprom(
  programmer: EEPROMProgrammer,
  file: BufferedReader,
  start_address: int,
  block_size: int,
  no_verify: bool,
):
  address = start_address
  while True:
    chunk = file.read(block_size)
    if not chunk:
      break
    programmer.write(address, chunk)

    if not no_verify:
      time.sleep(0.1)

      written = programmer.read(address, len(chunk))
      time.sleep(0.1)
      for i in range(len(chunk)):
        if written[i] != chunk[i]:
          print(f"Correcting write error at {address + i}")
          programmer.write(address + i, chunk[i].to_bytes(1, "big"))

    address += len(chunk)
