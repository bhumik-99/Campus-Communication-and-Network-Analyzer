# Campus Communication and Network Analyzer

A Computer Networks project that combines **campus network design**, **TCP client-server communication**, **UDP reliability mechanisms**, **session management**, **data processing**, and **automated testing** in one integrated repository.

## Project Overview

This project models a campus communication environment using two main layers:

- A simulated campus network designed using Cisco Packet Tracer.
- Python-based communication modules using TCP and UDP socket programming.

The project demonstrates important Computer Networks concepts such as:

- Network topology.
- IP addressing.
- VLANs.
- Routing.
- DNS.
- TCP socket programming.
- UDP socket programming.
- Flow control and retransmission.
- Session management.
- Encryption and data integrity.
- Automated testing.

## Problem Statement

In a campus environment, multiple users, departments, laboratories, and servers need to communicate efficiently and securely.

The purpose of this project is to design and demonstrate a campus communication system that can:

- Represent a campus network.
- Separate different departments logically.
- Support reliable client-server communication.
- Demonstrate UDP reliability mechanisms.
- Manage authenticated user sessions.
- Protect and verify transferred data.
- Validate the complete system through automated testing.

## Objectives

The main objectives of this project are:

1. To design a campus network topology using Cisco Packet Tracer.
2. To configure IP addressing, VLANs, routing, and DNS-related components.
3. To implement TCP client-server communication using Python sockets.
4. To implement UDP communication with acknowledgements and retransmission.
5. To manage user sessions with login, validation, timeout, and logout.
6. To process data using serialization, compression, encryption, and integrity checking.
7. To test the complete project using automated unit and integration tests.

## Input and Output

### Input

The project accepts the following types of input:

#### Network Design Input

- Network topology.
- VLAN configuration.
- IP addresses.
- Subnet masks.
- Default gateways.
- Router and switch connections.
- DNS server details.
- Hostname records.

#### Communication Input

Example TCP requests:

```text
LOGIN|username|password
SEND_MESSAGE|session_id|Hello campus
LOGOUT|session_id
```

UDP input includes:

- Message data.
- Packet sequence number.
- Transfer identifier.
- Packet size.
- Timeout value.
- Acknowledgement information.

Session-management input includes:

- Username.
- Password.
- Session ID.
- User activity.
- Logout request.

Data-processing input includes:

- Messages.
- JSON objects.
- Unicode text.
- File content.

### Output

The project produces the following outputs:

- A simulated campus network topology.
- Configured VLAN and IP addressing information.
- Routing and DNS verification results.
- TCP responses such as:

```text
LOGIN_SUCCESS
MESSAGE_RECEIVED
LOGOUT_SUCCESS
```

- UDP outputs such as:

```text
ACK_RECEIVED
TIMEOUT_OCCURRED
PACKET_RETRANSMITTED
TRANSFER_COMPLETED
```

- Session outputs such as:

```text
SESSION_CREATED
SESSION_VALID
SESSION_EXPIRED
LOGOUT_SUCCESS
INVALID_SESSION
```

- Data-processing outputs such as:

```text
SERIALIZATION_SUCCESS
COMPRESSION_SUCCESS
ENCRYPTION_SUCCESS
INTEGRITY_VERIFIED
TAMPERING_DETECTED
```

- Automated test results confirming whether the modules work correctly.

## System Architecture

```text
                 +----------------------+
                 |   Campus Network     |
                 |  Cisco Packet Tracer |
                 +----------+-----------+
                            |
                     Network Devices
                            |
          +-----------------+-----------------+
          |                                   |
   TCP Communication                    UDP Communication
          |                                   |
   TCP Client <----> TCP Server        UDP Client <----> UDP Server
          |                                   |
          +-----------------+-----------------+
                            |
                  Session Management
                            |
                  Data Processing Layer
                            |
       JSON -> Compression -> Encryption -> SHA-256
                            |
                    Automated Testing
```

## Project Modules

### 1. Network Design Module

The `network_design/` folder contains the Cisco Packet Tracer files and documentation related to the campus network.

This module covers:

- Network topology.
- Routers and switches.
- End devices and servers.
- IP addressing.
- VLAN planning.
- Routing configuration.
- DNS planning.
- Connectivity verification.

Expected outputs include:

- Packet Tracer topology.
- IP addressing table.
- VLAN configuration.
- Routing information.
- DNS configuration.
- Successful ping and hostname-resolution tests.

### 2. TCP Communication Module

The `tcp/` folder contains the TCP client-server implementation.

TCP is used for reliable, connection-oriented communication.

Supported operations include:

- Login.
- Sending a message.
- Logout.
- Invalid-request handling.
- Session validation.

Typical request formats:

```text
LOGIN|username|password
SEND_MESSAGE|session_id|message
LOGOUT|session_id
```

Typical responses:

```text
LOGIN_SUCCESS
MESSAGE_RECEIVED
LOGOUT_SUCCESS
INVALID_REQUEST
INVALID_SESSION
```

### 3. UDP Reliability Module

The `udp/` folder contains the UDP communication and reliability implementation.

UDP is connectionless and does not automatically guarantee delivery, ordering, or duplicate prevention. Therefore, reliability is implemented at the application level.

This module demonstrates:

- Stop-and-Wait communication.
- Go-Back-N communication.
- Acknowledgements.
- Sequence numbers.
- Timeout handling.
- Packet retransmission.
- Packet-loss simulation.
- Malformed-datagram handling.

Example output:

```text
Packet 1 sent
ACK 1 received
Packet 2 sent
ACK 2 lost
Timeout occurred
Packet 2 retransmitted
Transfer completed
```

### 4. Session Management Module

The `integration/session_manager.py` file manages user sessions.

The session workflow is:

```text
Login
  |
Create session
  |
Validate session
  |
Send messages
  |
Refresh activity time
  |
Logout or session expiry
```

The session manager supports:

- Session creation.
- Session validation.
- Activity refresh.
- Idle timeout.
- Session cleanup.
- Logout invalidation.
- Invalid-session detection.

### 5. Data Processing Module

The `integration/data_processing.py` file provides data-processing functions.

The processing pipeline is:

```text
Original Data
     |
JSON Serialization
     |
Compression
     |
Encryption
     |
SHA-256 Integrity Hash
     |
Processed Data
```

The reverse process is:

```text
Processed Data
     |
Integrity Verification
     |
Decryption
     |
Decompression
     |
JSON Deserialization
     |
Original Data
```

This module demonstrates:

- JSON serialization.
- JSON deserialization.
- Compression.
- Decompression.
- Encryption.
- Decryption.
- SHA-256 hashing.
- Tamper detection.
- Unicode data handling.

Encryption protects the content from unauthorized reading, while SHA-256 helps detect whether the content was modified.

## Repository Structure

```text
Campus-Communication-and-Network-Analyzer/
|
├── .github/
│   └── workflows/
│       └── python-tests.yml
|
├── docs/
│   └── member4_session_data_processing.md
|
├── integration/
│   ├── __init__.py
│   ├── config.py
│   ├── data_processing.py
│   └── session_manager.py
|
├── network_design/
│   ├── README.md
│   ├── config/
│   │   ├── dns_plan.md
│   │   └── routing_config.txt
│   ├── documentation/
│   │   ├── ip_addressing_plan.md
│   │   └── network_topology.md
│   └── packet_tracer/
│       ├── campus_network_devices_placed.pkt
│       ├── campus_network_devices_placed_backup.pkt
│       └── campus_network_vlan_dns_configured_v1.pkt
|
├── results/
│   ├── member3_udp_demo.log
│   ├── member3_udp_test_results.md
│   └── member5_tcp_test_results.md
|
├── tcp/
│   ├── README.md
│   ├── tcp_client.py
│   └── tcp_server.py
|
├── tests/
│   ├── test_member4_data_processing.py
│   ├── test_member4_session_manager.py
│   ├── test_tcp_integration.py
│   ├── test_tcp_session.py
│   └── test_udp.py
|
├── udp/
│   ├── README.md
│   ├── __init__.py
│   ├── go_back_n.py
│   ├── udp_client.py
│   └── udp_server.py
|
├── member4_demo.py
├── requirements-member4.txt
└── README.md
```

## Team Contribution

| Member | Responsibility |
|---|---|
| Member 1 | Campus network topology, Packet Tracer, IP addressing, VLANs, routing, and DNS planning |
| Member 2 | TCP client-server communication |
| Member 3 | UDP communication and reliability mechanisms |
| Member 4 | Session management, compression, encryption, and integrity checking |
| Member 5 | Integration, automated testing, documentation, and presentation |

## Technologies Used

| Component | Technology |
|---|---|
| Network simulation | Cisco Packet Tracer |
| Programming language | Python 3 |
| TCP/UDP communication | Python `socket` module |
| Testing | Python `unittest` |
| Encryption | Python `cryptography` library |
| Integrity checking | SHA-256 |
| Version control | Git and GitHub |
| Continuous integration | GitHub Actions |

## Installation

### 1. Clone the Repository

```bash
git clone [https://github.com/bhumik-99/Campus-Communication-and-Network-Analyzer.git](https://github.com/bhumik-99/Campus-Communication-and-Network-Analyzer.git)
cd Campus-Communication-and-Network-Analyzer
```

### 2. Check Python Installation

```bash
python --version
```

Python 3 or later is recommended.

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements-member4.txt
```

## How to Run

### Run the TCP Server

Open the first terminal:

```bash
python tcp/tcp_server.py
```

### Run the TCP Client

Open a second terminal:

```bash
python tcp/tcp_client.py
```

The TCP client can demonstrate:

- Login.
- Sending a message.
- Receiving a response.
- Logout.

### Run the Session and Data-Processing Demo

```bash
python member4_demo.py
```

### Open the Network Design

Open the following file using Cisco Packet Tracer:

```text
network_design/packet_tracer/campus_network_vlan_dns_configured_v1.pkt
```

Backup files are available in the same folder.

## Run All Tests

From the repository root, run:

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

This command discovers and runs all test files inside the `tests/` directory.

Expected final output:

```text
Ran 51 tests in X.XXXs

OK
```

## Test Categories

The test suite covers the following areas:

### Data Processing Tests

- JSON round-trip.
- Unicode data.
- Compression round-trip.
- Encryption round-trip.
- Encryption tampering detection.
- SHA-256 file integrity.
- Combined processing pipeline.

### Session Tests

- Session creation.
- Session validation.
- Empty username rejection.
- Activity refresh.
- Session expiration.
- Logout invalidation.
- Unknown-session handling.

### TCP Tests

- Valid login.
- Invalid login.
- Sending messages.
- Invalid sessions.
- Logout.
- Invalid request formats.
- Connection refusal.
- Socket timeout.
- Response framing.
- Actual TCP client behavior.

### UDP Tests

- Stop-and-Wait transmission.
- Go-Back-N transmission.
- ACK loss.
- First-packet loss.
- Middle-packet loss.
- Retransmission.
- Silent receiver.
- Malformed datagrams.
- Unicode and pipe characters.
- Transfer state validation.

## Suggested Project Demonstration

The project can be demonstrated in the following sequence:

1. Open the GitHub repository.
2. Explain the project title and objective.
3. Show the repository folder structure.
4. Open the Packet Tracer campus topology.
5. Explain IP addressing, VLANs, routing, and DNS.
6. Start the TCP server.
7. Start the TCP client.
8. Demonstrate login.
9. Demonstrate message transfer.
10. Demonstrate logout.
11. Explain UDP acknowledgements and retransmission.
12. Run `member4_demo.py`.
13. Demonstrate session validation and data processing.
14. Run the complete test suite.
15. Show the final result:

```text
Ran 51 tests
OK
```

## Final Output Summary

The final output of the project includes:

- A working campus network topology.
- Network addressing and configuration documentation.
- TCP client-server communication.
- UDP reliability and retransmission.
- User session management.
- Data serialization and compression.
- Encryption and decryption.
- SHA-256 integrity checking.
- Tamper detection.
- Automated test validation.

## Academic Relevance

This project is related to the following Computer Networks topics:

- Network topologies.
- OSI and TCP/IP concepts.
- IP addressing.
- Subnetting.
- VLANs.
- Routing.
- DNS.
- TCP.
- UDP.
- Flow control.
- Error control.
- Socket programming.
- Network security.
- Performance and reliability analysis.

## Limitations

The current project is an academic demonstration and has the following limitations:

- The TCP server is intended for controlled demonstration.
- The Packet Tracer network is simulated rather than deployed physically.
- The project does not provide a complete production-grade authentication database.
- Performance benchmarking is limited.
- The project does not yet provide a web-based monitoring dashboard.
- Application-level encryption is demonstrated, but full TLS deployment is outside the current scope.

## Future Enhancements

Possible future improvements include:

- Adding a web-based dashboard.
- Adding database-backed user authentication.
- Supporting multiple concurrent TCP clients.
- Adding real-time network monitoring.
- Adding packet capture and visualization.
- Measuring latency and throughput.
- Adding role-based access control.
- Deploying the system across multiple machines.
- Adding stronger protocol framing.
- Adding more detailed performance reports.

## Conclusion

The Campus Communication and Network Analyzer demonstrates a complete educational communication system by combining network simulation, TCP and UDP socket programming, reliability mechanisms, session management, secure data processing, and automated testing.

The project shows the complete flow:

```text
Network Configuration
        |
User or Application Input
        |
Communication and Data Processing
        |
Validation and Reliability
        |
Final Network and Test Output
```

The final integrated repository provides a practical demonstration of Computer Networks concepts and their implementation using Cisco Packet Tracer, Python, Git, GitHub, and automated testing.
