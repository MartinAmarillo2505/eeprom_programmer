COMMON_CATHODE = True

DIGITS = b"\x7e\x30\x6d\x79\x33\x5b\x5f\x70\x7f\x7b\x77\x1f\x4e\x3d\x4f\x47"
SIGN = 0x01
BLANK = 0x00


def get_digit(address: int) -> int:
  twos_complement = (address >> 10) & 0x01 != 0
  display_idx = (address >> 8) & 0x03
  number = address & 0xFF

  is_negative = twos_complement and (number >> 7) & 1 != 0
  absolute = (~number + 1) & 0xFF if is_negative else number

  if display_idx == 3:  # sign display
    return SIGN if is_negative else BLANK

  digit_idx = (absolute // 10**display_idx) % 10
  return DIGITS[digit_idx]


rom = bytearray(get_digit(addr) for addr in range(2048))

if not COMMON_CATHODE:
  rom = bytearray(~x & 0xFF for x in rom)

for address in range(0, 2048, 16):
  data = rom[address : address + 16]
  print(f'{address:03x}: {data[:8].hex(" ")}  {data[8:].hex(" ")}')

with open("output-display.bin", "wb") as f:
  f.write(rom)
