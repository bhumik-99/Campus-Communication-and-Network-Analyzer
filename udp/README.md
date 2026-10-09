# Member 3 - UDP and Reliability

This module sends real UDP datagrams and implements sequence numbers,
cumulative acknowledgments, timeout, retransmission and a sliding window.
Stop-and-Wait uses a window of 1. Go-Back-N uses the shared default window of 4.
Only Python 3.9+ and its standard library are required. No pip install is needed.

## Get the code in VS Code

### If you received the downloadable ZIP

The GitHub app could read the repository but returned HTTP 403 when creating
the branch, so this package has not been pushed. Add it from your own GitHub
account as follows:

1. Clone the repository using the command below and open it in VS Code.
2. Run `git switch -c udp-member` from the repository root. If that branch
   already exists, use `git switch udp-member` instead.
3. Extract this ZIP to a temporary folder. Copy its `udp`, `integration`, `tests`
   and `results` folders plus `.gitignore` into the repository root. The paths
   should be `Campus-Communication-and-Network-Analyzer/udp/udp_client.py`, etc.
   If your teammates have added files with the same names since this package
   was prepared, compare/merge them rather than overwriting their work.
4. Run the test command below, then run the two-terminal demo.
5. Publish the files:

```bash
git add .gitignore udp integration/config.py integration/__init__.py tests/test_udp.py results/member3_udp_demo.log results/member3_udp_test_results.md
git commit -m "Add Member 3 UDP Stop-and-Wait and Go-Back-N module"
git push -u origin udp-member
```

6. Open the repository on GitHub, click **Compare & pull request**, choose
   `main` as the base and `udp-member` as the compare branch, then create the
   pull request. Ask the integration member to review it before merging.
   If push returns permission denied, confirm that your teammate added your
   GitHub account as a collaborator and that you accepted the invitation.

### After the branch has been published

After this branch is pushed, open a terminal and run:

```bash
git clone https://github.com/bhumik-99/Campus-Communication-and-Network-Analyzer.git
cd Campus-Communication-and-Network-Analyzer
git switch udp-member
code .
```

If you already cloned it, open that folder in VS Code and run:

```bash
git status
git fetch origin
git switch udp-member
git pull --ff-only
```

Commit or stash your own unfinished edits before switching branches. On Windows,
use `py` instead of `python` if Python is installed through the Python launcher.
Every command below runs from the repository root, not from inside `udp/`.
The `-m` option loads the module with its shared configuration imports working.

## Demo 1: Stop-and-Wait

Open Terminal > New Terminal. Start the receiver:

```bash
python -m udp.udp_server
```

Open a second terminal (keep the first running):

```bash
python -m udp.udp_client --mode stop-and-wait --message "Hello campus" --message "Second message"
```

The sender sends packet 0, waits for ACK 0, then sends packet 1. The receiver
prints each accepted payload. The client prints SUCCESS only after all ACKs.
Running the client without `--message` asks you to type one message.

## Demo 2: Stop-and-Wait timeout

Stop the old server with Ctrl+C, then start:

```bash
python -m udp.udp_server --drop-ack-once 0
```

In terminal 2:

```bash
python -m udp.udp_client --mode stop-and-wait --message "Hello campus"
```

The receiver accepts packet 0 but deliberately skips its first ACK. After one
second the sender retransmits packet 0. The receiver discards the duplicate,
sends ACK 0 again, and delivers the payload only once.

## Demo 3: Go-Back-N without loss

Restart the server without loss switches:

```bash
python -m udp.udp_server
```

In terminal 2:

```bash
python -m udp.udp_client --mode gbn --demo
```

Eight telemetry strings are sent in a sliding window. Up to four packets can be
unacknowledged at once. ACK 2 means packets 0, 1 and 2 have all been accepted.

## Demo 4: Go-Back-N with packet loss (T6)

Stop the server and start it again with:

```bash
python -m udp.udp_server --drop-once 2
```

In terminal 2:

```bash
python -m udp.udp_client --mode gbn --demo
```

Expected observations:

1. The server prints `SIMULATED DATA LOSS packet=2`.
2. Later packets are discarded while the receiver is expecting packet 2.
3. The client prints `TIMEOUT: retransmit packets 2..5` for this eight-packet demo.
4. The client retransmits **all outstanding packets**, not only packet 2.
5. The server accepts the retransmitted packets in order; the client prints SUCCESS.

This deliberately drops a datagram inside the application after it reaches the
socket. It demonstrates ARQ recovery; it is not a measured physical-network loss.
Exact log interleaving can vary with OS scheduling. Loss happens once per transfer.

## Tests and evidence

```bash
python -m unittest discover -s tests -p "test_udp.py" -v
```

The tests use actual localhost sockets on OS-selected ports. They cover T4 and T6,
Stop-and-Wait, no-loss Go-Back-N, first-packet loss, ACK loss, duplicate suppression,
independent transfers, malformed packets, invalid ACKs, input limits, receiver
capacity/expiry and a silent receiver. Checked-in evidence is in
`results/member3_udp_test_results.md` and `results/member3_udp_demo.log`.
Take your own screenshots of both terminals during Demo 4 for the faculty report.

## Wire format

```text
DATA|sequence_number|transfer_id|total_packets|payload
ACK|sequence_number|transfer_id
```

Sequences start at 0. ACKs are cumulative; ACK -1 means nothing has been accepted
yet. The receiver only accepts the next expected sequence and discards duplicates
and later sequences. A timeout retransmits the entire unacknowledged window.
The sender uses one monotonic timer for the oldest unacknowledged packet and
allows at most 10 timeout retransmissions without ACK progress before failing.

The PDF's suggested DATA/ACK format is extended with a fresh 32-character transfer
ID and total count. The ID keeps delayed ACKs and separate transfers isolated;
the count lets the receiver identify completion. Payloads may contain `|` and
Unicode because the receiver splits only the four header delimiters. Tell the
integration lead to use this documented format, not the earlier three-field demo.

Datagrams are limited to 1200 encoded bytes including headers to reduce IP
fragmentation on typical networks; paths with smaller MTUs may still fragment.
Each transfer has at most 1000 packets. The receiver retains at most 128 transfer
states, expiring them after 300 seconds of inactivity. Completed transfers retain
their sequence state to re-ACK duplicates but release their payload storage.
Receiver restart or state expiry loses duplicate history. This is a teaching
transport with bounded retries, not durable storage or guaranteed delivery under
unlimited loss. UDP ACKs are not cryptographic authentication.

## Hand-off to Member 5

All ports/host/window settings are defined in `integration/config.py`. Localhost
is the independent-development default. TCP port 5000 is reserved for Member 2.
The existing network plan names `campus-app.local`; use it only when the real
machine's resolver is configured. The Python programs do not run inside Packet
Tracer's simulated PCs, and a Packet Tracer DNS record does not configure Windows
DNS automatically.

Start the UDP server in a background thread alongside the TCP server:

```python
import threading
from udp.udp_server import UDPServer

def receive_telemetry(payloads, address, transfer_id):
    print("Completed UDP transfer:", transfer_id, payloads)

udp_server = UDPServer(on_complete=receive_telemetry)
stop = threading.Event()
thread = threading.Thread(target=udp_server.serve, args=(stop,))
thread.start()
# On application shutdown:
stop.set()
thread.join()
udp_server.close()
```

To send from the integrated client's menu:

```python
from udp.go_back_n import send_packets, send_stop_and_wait

send_stop_and_wait(["Hello campus"])
metrics = send_packets(["Reading 0", "Reading 1", "Reading 2", "Reading 3"])
print(metrics)
```

`on_complete` receives the ordered strings once per retained transfer. It should
return quickly. ACK confirms transport acceptance; downstream callback success
is not separately acknowledged. Member 4 must supply session validation and
formatting separately; these packets do not authenticate users or encrypt data.
No main server/client entry points are added yet because those belong to Member 5.

For two real laptops on the same reachable network, bind the server with
`--host 0.0.0.0` and give the client `--host <server-laptop-IP>`. Allow UDP 5001 in
the server firewall for the lab network. Campus Wi-Fi client isolation can block
peer traffic. Start with localhost first.

For Wireshark, capture on the loopback interface for localhost (Windows normally
needs Npcap loopback support) or the active network interface for two laptops.
Use display filter `udp.port == 5001`. The intentional loss packet can still appear
in the capture, since the application discards it after reception. Use terminal
logs together with repeated sequence numbers in packets to explain recovery.
`elapsed_seconds` is total transfer duration including retries, not per-packet
latency. `payload_bytes / elapsed_seconds` is application payload goodput, not
link throughput; retransmissions include DATA resends but not ACK traffic.

## Your next changes on GitHub

Make changes on `udp-member`, then:

```bash
python -m unittest discover -s tests -p "test_udp.py" -v
git add udp tests/test_udp.py integration/config.py
git commit -m "Improve UDP reliability demonstration"
git push origin udp-member
```

Ask the integration member to review the pull request and merge it after testing.
If you use VS Code's Source Control panel, stage these files, enter a meaningful
commit message, click Commit, then Push. Do not commit generated `__pycache__` files.

## Faculty explanation

"UDP does not guarantee delivery or ordering. I added sequence numbers and
cumulative ACKs. Stop-and-Wait sends one packet at a time. Go-Back-N sends up to
four packets before waiting, discards out-of-order packets at the receiver, and
retransmits all outstanding packets when the oldest packet's timer expires.
I deliberately drop packet 2 to show timeout and recovery."
