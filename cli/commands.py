import time
from protocol import EEPROMProgrammer
from io import BufferedReader, BufferedWriter


def dump_eeprom(programmer: EEPROMProgrammer, start_address: int, size: int):
  end_address = start_address + size
  end_base = (end_address >> 4) + 1

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
    print(f"{base_address << 4:03x}: {' '.join(data[:8])}  {' '.join(data[8:])}")


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


def write_eeprom(
  programmer: EEPROMProgrammer,
  file: BufferedReader,
  start_address: int,
  block_size: int,
  no_verify: bool,
):
  address = start_address

  print(f"Writing {file.name} to 0x{address:03x}", end="", flush=True)
  while True:
    chunk = file.read(block_size)
    if not chunk:
      break
    programmer.write(address, chunk)
    print(".", end="", flush=True)

    address += len(chunk)

  if no_verify:
    return

  file.seek(0)
  print()
  print("Verifying", end="", flush=True)
  while True:
    chunk = file.read(block_size)
    if not chunk:
      break
    written = programmer.read(address, len(chunk))
    if written != chunk:
      raise Exception(f"Verification error at 0x{address:03x}")
    print(".", end="", flush=True)
    address += len(chunk)

  print(" done")
