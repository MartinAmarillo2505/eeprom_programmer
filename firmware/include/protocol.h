/*
 * Packet format: 00 FF <command> <payload length> <payload> <checksum> FF
 *  - 00 FF: Packet Header
 *  - <command>: Packet command (1 byte)
 *  - <payload length>: Payload length (1 byte)
 *  - <payload>: Payload (variable length)
 *  - <checksum>: Checksum (1 byte). Calculated as the two's complement of the sum of the payload bytes
 *  - FF: Packet Footer
 * 
 *  - The total length of the packet cannot exceed 255 bytes
 *  - Because of the total packet length, the payload length cannot exceed 249 bytes (6 bytes + payload = 255)
 *  - When the payload length is 0, the checksum is 0xFF (two's complement of 0).
*/

#pragma once

#define PACKET_HEADER_MSB 0x00
#define PACKET_HEADER_LSB 0xFF
#define PACKET_FOOTER 0xFF

#define PACKET_MAX_LENGTH 255
#define PACKET_MAX_PAYLOAD_LENGTH PACKET_MAX_LENGTH - 6  // 6 bytes for all the non-payload fields

/* Packet commands */

/*
* Acknowledge the previous packet. Only used as a response.
* If not sent, the previous packet will be resent by the host.
*
* Response payload format: <command> <length> <checksum>
*  - <command>: Previous packet command (1 byte)
*  - <length>: Previous packet payload length (1 byte)
*  - <checksum>: Previous packet checksum (1 byte)
*/
#define PACKET_COMMAND_ACK 0x00

/*
 * Read the contents of an address in the EEPROM
 *
 * Request payload format: <address> <length>
 *  - <address>: Memory address (2 bytes big endian)
 *  - <length>: Length of data to read (1 byte). Maximum length is 249 bytes (maximum payload length)
 * 
 * Response payload format: <data>
 *  - <data>: Data read from the address (variable length)
 */
#define PACKET_COMMAND_READ 0x01

/*
 * Write the contents of an address in the EEPROM
 *
 * Request payload format: <address> <data>
 *  - <address>: Memory address (2 bytes big endian)
 *  - <data>: Data to write (variable length)
 * 
 * Response payload format: none (payload length 0)
 */
#define PACKET_COMMAND_WRITE 0x02

/*
 * Error packet. Only used as a response when an error occurs.
 * 
 * Response payload format: <code> <length> <data>
 *  - <error code>: Error code (1 byte)
 *  - <error length>: Error data length (1 byte)
 *  - <error data>: Error data (variable length)
 */
#define PACKET_COMMAND_ERROR 0xFF

/* Packet error codes */

/*
 * Unknown command received from the host
 * 
 * Response data format: <command>
 * - <command>: Previous packet command (1 byte)
 */
#define PACKET_ERROR_UNKNOWN_COMMAND 0x00

/*
 * Invalid length received from the host. This can occur when the host wants to read or write data that will not fit in a packet
 * 
 * Response data format: none (data length 0)
 */
#define PACKET_ERROR_INVALID_LENGTH 0x01

/*
 * Checksum mismatch
 * 
 * Response data format: none (data length 0)
 */
#define PACKET_ERROR_CHECKSUM_MISMATCH 0x02
