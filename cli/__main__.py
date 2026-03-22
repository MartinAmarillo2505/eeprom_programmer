import argparse
import sys
import time
from serial import Serial
import serial.tools.list_ports

from commands import dump_eeprom, read_eeprom, write_eeprom, verify_eeprom
from protocol import EEPROMProgrammer

BAUDRATE = 115200


def auto_int(x: str) -> int:
  return int(x, 0)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()

  parser.add_argument("-port", type=str, help=f"set serial port (default: auto)")
  parser.add_argument(
    "-speed", type=int, default=BAUDRATE, help=f"set serial speed (default: {BAUDRATE})"
  )

  subparsers = parser.add_subparsers(dest="command", required=True)

  dump = subparsers.add_parser("dump", help="show EEPROM data")
  dump.add_argument(
    "address",
    type=auto_int,
    nargs="?",
    default=0,
    help="start address (default: 0x000)",
  )
  dump.add_argument(
    "size", type=auto_int, nargs="?", default=2048, help="size (default: 2048)"
  )

  read = subparsers.add_parser("read", help="copy EEPROM to file")
  read.add_argument(
    "-block-size", type=auto_int, default=64, help="block size (default: 64)"
  )
  read.add_argument("file", type=argparse.FileType("wb"), help="file to write to")
  read.add_argument(
    "address",
    type=auto_int,
    nargs="?",
    default=0,
    help="start address (default: 0x000)",
  )
  read.add_argument(
    "size", type=auto_int, nargs="?", default=2048, help="size (default: 2048)"
  )

  write = subparsers.add_parser("write", help="copy file to EEPROM")
  write.add_argument(
    "-no-verify",
    nargs="?",
    default=False,
    const=True,
    help="do not verify written data (default: False)",
  )
  write.add_argument(
    "-block-size", type=auto_int, default=64, help="block size (default: 64)"
  )
  write.add_argument("file", type=argparse.FileType("rb"), help="file to read from")
  write.add_argument(
    "address",
    type=auto_int,
    nargs="?",
    default=0,
    help="start address (default: 0x000)",
  )

  verify = subparsers.add_parser("verify", help="verify EEPROM data")
  verify.add_argument(
    "-block-size", type=auto_int, default=64, help="block size (default: 64)"
  )
  verify.add_argument("file", type=argparse.FileType("rb"), help="file to read from")
  verify.add_argument(
    "address",
    type=auto_int,
    nargs="?",
    default=0,
    help="start address (default: 0x000)",
  )
  verify.add_argument(
    "fix", nargs="?", default=False, const=True, help="fix errors (default: False)"
  )

  args = parser.parse_args()

  if "block_size" in args:
    if args.block_size > 0 and (args.block_size & args.block_size - 1) != 0:
      raise Exception("Block size must be a power of 2")

  if args.port is None:
    port_names = [port.device for port in serial.tools.list_ports.comports()]
    print(f"Found {len(port_names)} serial ports...")
    if len(port_names) == 0:
      sys.exit(1)
    args.port = port_names[0]

  with Serial(port=args.port, baudrate=args.speed, timeout=5) as ser:
    programmer = EEPROMProgrammer(ser)

    print(f"Connected to {ser.port} at {ser.baudrate}")
    time.sleep(1)

    if args.command == "dump":
      dump_eeprom(programmer, start_address=args.address, size=args.size)
    elif args.command == "read":
      read_eeprom(
        programmer,
        file=args.file,
        start_address=args.address,
        size=args.size,
        block_size=args.block_size,
      )
    elif args.command == "write":
      write_eeprom(
        programmer,
        file=args.file,
        start_address=args.address,
        block_size=args.block_size,
        no_verify=args.no_verify,
      )
    elif args.command == "verify":
      verify_eeprom(
        programmer,
        file=args.file,
        start_address=args.address,
        block_size=args.block_size,
        fix=args.fix,
      )
    else:
      raise Exception("Unknown command. Try --help for a list of commands.")
