# Reliable File Transfer System with Error Simulation

A Python-based client-server application implementing a reliable file transfer protocol with error detection, retransmission mechanism, and configurable error simulation. This system demonstrates fundamental networking concepts including error detection, packet fragmentation, and reliability protocols.

## Features

### Core Functionality
- **Client-Server Architecture**: TCP-based communication system
- **File Fragmentation**: Splits files into manageable segments for transmission
- **Checksum Verification**: 16-bit Internet checksum algorithm for error detection
- **Automatic Retransmission**: Implements retry mechanism for corrupted or lost packets
- **Multi-threading**: Supports multiple concurrent client connections
- **File Reassembly**: Automatic reconstruction of received file fragments

### Error Simulation
- **Configurable Error Rate**: Adjustable error probability (0.0 to 0.8)
- **Bit-level Error Injection**: Random bit flipping to simulate transmission errors
- **Error Statistics**: Comprehensive tracking of transmission errors and retransmissions

### Performance Monitoring
- **Transfer Statistics**:
  - Total fragments transmitted
  - Number of corrupted fragments
  - Retransmission count
  - Error rate calculation
  - Transfer duration
- **Real-time Progress Updates**: Console-based progress tracking
- **Detailed Logging**: Server and client-side operation logging

## Requirements

- Python 3.6 or higher
- Standard Python libraries:
  - socket
  - struct
  - os
  - threading
  - random
  - time

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/reliable-file-transfer.git
cd reliable-file-transfer
```

2. No additional dependencies needed - uses standard Python libraries only.

## Usage

1. Start the server:
```bash
python server.py
```

2. Start the client in a separate terminal:
```bash
python client.py
```

3. Follow the client prompts to transfer files:
   - Enter the filename when prompted
   - Monitor transfer progress and statistics
   - Type 'exit' to quit

### Configuring Error Simulation

In `server.py`, modify the ERROR_PROBABILITY constant:
```python
ERROR_PROBABILITY = 0.3  # Set between 0.0 and 0.8
```
- 0.0: No artificial errors
- 0.3: 30% error probability
- 0.5: 50% error probability
- 0.8: 80% error probability

## Protocol Description

### Packet Structure
- Header (4 bytes):
  - Sequence Number (2 bytes)
  - Checksum (2 bytes)
- Payload: File fragment data

### Transfer Process
1. Client requests file from server
2. Server validates file existence and size
3. Server splits file into fragments
4. For each fragment:
   - Server calculates checksum
   - Server sends fragment with header
   - Client verifies checksum
   - Client sends ACK/NACK
   - Server retransmits if needed
5. Client reassembles file upon successful reception

### Error Handling
- Checksum verification for each fragment
- Maximum retry limit for failed transmissions
- Graceful handling of file not found errors
- Connection error recovery
- Incomplete transfer detection

## Technical Details

### Checksum Algorithm
Implements the 16-bit Internet checksum:
- Processes data in 16-bit words
- Handles odd-length data with zero padding
- Returns 16-bit verification value
- Compatible with standard networking protocols

### Error Simulation
- Random bit flipping in transmitted data
- Configurable probability settings
- Affects only data segments, not control messages
- Helps test system reliability

### Performance Considerations
- Buffer size: 1024 bytes
- Default fragment count: 4
- Maximum retry attempts: 5
- Minimum file size enforcement

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Acknowledgments

- Based on standard networking protocols and best practices
- Implements reliable data transfer concepts
- Inspired by real-world networking challenges

## Notes

- For testing purposes, ensure files are in the same directory as the server
- Larger files will be automatically split into fragments
- Error simulation can be disabled by setting ERROR_PROBABILITY to 0
- System provides detailed logs for debugging
