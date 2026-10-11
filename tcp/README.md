# TCP Client-Server Communication

## Overview
The TCP client connects to the TCP server, sends requests, receives responses, and supports LOGIN, SEND_MESSAGE, and LOGOUT operations.

## Requirements
- Python 3.x
- No additional packages required

## How to Run

Open two terminals in the project root directory.

**Terminal 1 — Start the server**
```powershell
python .\tcp\tcp_server.py
```

**Terminal 2 — Start the client**
```powershell
python .\tcp\tcp_client.py
```

## Test Credentials
Use the credentials configured in `tcp_server.py`.

## Operations
1. LOGIN — send username and password.
2. SEND_MESSAGE — send a message using a valid session ID.
3. LOGOUT — end the session.
4. EXIT — close the client.

## Error Handling
The client handles connection refusal, connection timeouts, and general socket errors.
