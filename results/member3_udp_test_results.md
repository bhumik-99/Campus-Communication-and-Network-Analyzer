# Member 3 UDP test results

Executed on 2026-10-07 UTC using Python in the development workspace. Tests use
real IPv4 localhost UDP sockets with OS-selected ports. These are independent
module results; campus routing, Windows execution, Wireshark captures, authentication
and full five-member integration have not been verified here.

Command:

```bash
python -m unittest discover -s tests -p "test_udp.py" -v
```

| Test | Input / condition | Expected and observed result | Status |
|---|---|---|---|
| T4 / Stop-and-Wait | Two strings, including Unicode and a pipe | Ordered strings delivered, no resends | PASS |
| Go-Back-N | Eight packets, window 4, no loss | Eight accepted, eight DATA sends | PASS |
| T6 / middle packet loss | Drop DATA 2 once | Later packets discarded; timeout and window resend; ordered completion | PASS |
| First packet loss | Drop DATA 0 once | Entire outstanding window retransmitted | PASS |
| Final ACK loss | Drop ACK 2 for three packets | Duplicate DATA re-ACKed, delivery happens once | PASS |
| Stop-and-Wait ACK loss | Drop ACK 0 once | One retransmission, no duplicate delivery | PASS |
| Independent transfers | Two sequential client transfers | Different IDs and independent receiver state | PASS |
| Malformed datagrams | Bad encoding, bad headers and oversized input | Ignored; subsequent valid transfer succeeds | PASS |
| Silent receiver | Bound UDP socket sends no ACK; retry limit 1 | Sender raises TimeoutError within its retry budget | PASS |
| Input validation | Empty transfer, invalid window/timeout/retry, oversized/non-string payload | ValueError before sending | PASS |
| Invalid ACKs | Malformed, wrong transfer ID and ACK for unsent packet | No window advance; valid ACK after retransmission succeeds | PASS |
| Receiver state limits | Capacity 1 and artificially expired state | Excess transfer ignored; expired state reclaimed | PASS |

Summary: **12 tests passed**.

`member3_udp_demo.log` contains a separate actual eight-packet localhost demo
with DATA 2 dropped once. Observed: 12 DATA sends (8 originals + 4 resends),
1 timeout, ordered completion. It uses a shortened 0.1-second timeout for the
recording; CLI default is 1 second. This is simulated application loss, not a
measurement of campus-network packet loss. Capture screenshots and Wireshark
evidence on the team demo machines for the final submission.
