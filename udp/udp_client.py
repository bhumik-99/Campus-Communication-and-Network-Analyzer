"""Command-line client for Stop-and-Wait and Go-Back-N."""

import argparse

from integration.config import SERVER_HOST, UDP_PORT, UDP_TIMEOUT, WINDOW_SIZE
from udp.go_back_n import send_packets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=SERVER_HOST)
    parser.add_argument("--port", type=int, default=UDP_PORT)
    parser.add_argument("--mode", choices=["stop-and-wait", "gbn"], default="stop-and-wait")
    parser.add_argument("--window", type=int, default=WINDOW_SIZE)
    parser.add_argument("--timeout", type=float, default=UDP_TIMEOUT)
    parser.add_argument("--message", action="append", help="Repeat for multiple packets")
    parser.add_argument("--demo", action="store_true", help="Send eight numbered telemetry packets")
    args = parser.parse_args()
    if args.demo and args.message is not None:
        parser.error("Use either --demo or --message")
    payloads = ([f"Telemetry reading {i}" for i in range(8)] if args.demo
                else args.message if args.message is not None
                else [input("Enter message: ")])
    try:
        send_packets(payloads, host=args.host, port=args.port,
                     window_size=1 if args.mode == "stop-and-wait" else args.window,
                     timeout=args.timeout)
    except (OSError, ValueError, TimeoutError) as exc:
        parser.exit(1, f"Transfer failed: {exc}\n")


if __name__ == "__main__":
    main()
