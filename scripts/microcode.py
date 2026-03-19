# --- Control signals
# Left ROM
HLT = 0b10000000_00000000_00000000  # Halt clock
MI = 0b01000000_00000000_00000000  # Memory address register in
RI = 0b00100000_00000000_00000000  # RAM data in
II = 0b00010000_00000000_00000000  # Instruction register in
AI = 0b00001000_00000000_00000000  # A register in

RO = 0b00000001_00000000_00000000  # RAM data out
IO = 0b00000010_00000000_00000000  # Instruction register out # TODO: useless after memory upgrade. Replace with SR?
AO = 0b00000011_00000000_00000000  # A register out
EO = 0b00000100_00000000_00000000  # ALU out
BO = 0b00000101_00000000_00000000  # B register out
CO = 0b00000110_00000000_00000000  # Program counter out
SR = 0b00000111_00000000_00000000  # Step counter reset

# Middle ROM
SUB = 0b00000000_10000000_00000000  # ALU subtract
BI = 0b00000000_01000000_00000000  # B register in
OI = 0b00000000_00100000_00000000  # Output register in
CE = 0b00000000_00010000_00000000  # Program counter enable
JMP = 0b00000000_00001000_00000000  # Jump (program counter in)
FI = 0b00000000_00000100_00000000  # Flag register in

# Right ROM

UCODE_TEMPLATE = (
  (CO | MI, RO | II | CE, SR),  # 0000 - NOP
  (CO | MI, RO | II | CE, IO | MI, RO | AI, SR),  # 0001 - LDA
  (CO | MI, RO | II | CE, IO | MI, RO | BI, EO | AI | FI, SR),  # 0010 - ADD
  (CO | MI, RO | II | CE, IO | MI, RO | BI, EO | AI | SUB | FI, SR),  # 0011 - SUB
  (CO | MI, RO | II | CE, IO | MI, AO | RI, SR),  # 0100 - STA
  (CO | MI, RO | II | CE, IO | AI, SR),  # 0101 - LDI
  (CO | MI, RO | II | CE, IO | JMP, SR),  # 0110 - JMP
  (CO | MI, RO | II | CE, SR),  # 0111
  (CO | MI, RO | II | CE, SR),  # 1000
  (CO | MI, RO | II | CE, SR),  # 1001
  (CO | MI, RO | II | CE, SR),  # 1010
  (CO | MI, RO | II | CE, SR),  # 1011
  (CO | MI, RO | II | CE, SR),  # 1100
  (CO | MI, RO | II | CE, SR),  # 1101
  (CO | MI, RO | II | CE, AO | OI, SR),  # 1110 - OUT
  (CO | MI, RO | II | CE, HLT | SR),  # 1111 - HLT
)


def get_microstep(address: int):
  step = address & 0x07
  opcode = (address >> 7) & 0x0F  # TODO: use all 8 bits after memory upgrade
  carry_flag = (address >> 11) & 0x01
  zero_flag = (address >> 12) & 0x01

  microsteps = UCODE_TEMPLATE[opcode]
  try:
    return microsteps[step]
  except IndexError:
    return 0


left_rom = bytearray(2**15)
middle_rom = bytearray(2**15)
right_rom = bytearray(2**15)

for address in range(2**15):
  microstep = get_microstep(address)
  left_rom[address] = (microstep >> 16) & 0xFF
  middle_rom[address] = (microstep >> 8) & 0xFF
  right_rom[address] = microstep & 0xFF

with open("microcode-left.bin", "wb") as f:
  f.write(left_rom)

with open("microcode-middle.bin", "wb") as f:
  f.write(middle_rom)

with open("microcode-right.bin", "wb") as f:
  f.write(right_rom)
