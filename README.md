# EEPROM Programmer

A **cross-platform EEPROM programmer** inspired by the design from Ben Eater’s SAP-1 computer project.

This project reimplements the EEPROM programmer from
[https://github.com/beneater/eeprom-programmer](https://github.com/beneater/eeprom-programmer) with a **custom communication protocol** and a **command-line interface**.

## Background

This project was initially inspired by
[https://github.com/moefh/eeprom_writer](https://github.com/moefh/eeprom_writer).

While that implementation introduced useful wiring changes and a working firmware, it was **Unix-only** and didn’t work in my environment. I decided to build a **fully cross-platform implementation from scratch**.

## Project Structure

The project is split into two main components:

### CLI

A **cross-platform command-line interface** used to interact with the programmer from the host computer.

Responsibilities include:

- Sending read/write commands
- Transferring EEPROM data
- Handling communication with the device

### Firmware

The firmware runs directly on the **EEPROM programmer hardware** and is responsible for:

- Executing commands received from the host
- Reading and writing EEPROM memory
- Managing hardware interactions

## Communication Protocol

The host-to-device communication protocol was designed and built from the ground up.

It provides:

- Structured command handling
- Error detection
- Reliable data transfer between the CLI and the programmer

## Contributing

Contributions are welcome.

Please follow the **Conventional Commits specification**:
[https://www.conventionalcommits.org/](https://www.conventionalcommits.org/)

## License

This project is licensed under the **MIT License**.
