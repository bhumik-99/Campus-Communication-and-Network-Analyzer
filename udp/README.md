# UDP Reliability Module

This module sends real UDP datagrams and implements:

- Sequence numbers.
- Cumulative acknowledgments.
- Timeout and retransmission.
- Stop-and-Wait ARQ.
- Go-Back-N sliding-window ARQ.
- Duplicate and out-of-order packet handling.
- Bounded receiver state and retry behavior.

Stop-and-Wait uses a window size of 1. Go-Back-N uses the shared default window size of 4.

Only Python 3.9+ and the standard library are required. No third-party packages are needed.

## Setup

Run all commands from the repository root:

```text
Campus-Communication-and-Network-Analyzer/
```

On Windows, use `py` instead of `python` if Python was installed through the Python launcher.

The `-m` option is recommended because it preserves the repository package imports.

## Demo 1: Stop-and-Wait

Open one terminal and start the receiver:

```powershell
python -m udp.udp_server
```

Open a second terminal and send two messages:

```powershell
python -m udp.udp_client --mode stop-and-wait --message "Hello campus" --message "Second message"
```

The sender sends packet 0, waits for ACK 0, and then sends packet 1. The receiver prints each accepted payload. The client prints success only after all acknowledgments are received.

Running the client without `--message` asks for one message interactively:

```powershell
python -m udp.udp_client --mode stop-and-wait
```

## Demo 2: Stop-and-Wait ACK Loss

Stop the previous server with `Ctrl+C`.

Start a server that drops ACK 0 once:

```powershell
python -m udp.udp_server --drop-ack-once 0
```

In the second terminal, run:

```powershell
python -m udp.udp_client --mode stop-and-wait --message "Hello campus"
```

Expected behavior:

1. The receiver accepts packet 0.
2. The receiver deliberately skips the first ACK.
3. The sender waits for the timeout.
4. The sender retransmits packet 0.
5. The receiver identifies the duplicate.
6. The receiver sends ACK 0 again.
7. The payload is delivered only once.

## Demo 3: Go-Back-N Without Loss

Restart the server without loss simulation:

```powershell
python -m udp.udp_server
```

Run the client in Go-Back-N demo mode:

```powershell
python -m udp.udp_client --mode gbn --demo
```

Eight telemetry strings are sent using a sliding window. Up to four packets can remain unacknowledged at the same time.

An ACK for packet 2 is cumulative. It confirms that packets 0, 1, and 2 have been accepted in order.

## Demo 4: Go-Back-N Packet Loss

Stop the server and restart it with packet 2 dropped once:

```powershell
python -m udp.udp_server --drop-once 2
```

In the second terminal, run:

```powershell
python -m udp.udp_client --mode gbn --demo
```

Expected observations:

1. The server prints `SIMULATED DATA LOSS packet=2`.
2. Later packets are discarded while the receiver is waiting for packet 2.
3. The client reports a timeout.
4. The client retransmits all outstanding packets, not only packet 2.
5. The receiver accepts the retransmitted packets in order.
6. The client reports successful completion.

This deliberately drops a datagram inside the application after it reaches the socket. It demonstrates ARQ recovery; it is not a measurement of physical network packet loss.

The exact order of terminal log messages can vary because of operating-system scheduling. The configured packet is dropped only once per transfer.

## Command-Line Options

### UDP server

```powershell
python -m udp.udp_server --help
```

Important options include:

```text
--host
--port
--drop-once
--drop-ack-once
```

Example:

```powershell
python -m udp.udp_server --host 127.0.0.1 --port 5001
```

### UDP client

```powershell
python -m udp.udp_client --help
