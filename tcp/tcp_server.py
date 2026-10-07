import socket

HOST = "127.0.0.1"
PORT = 5001

USERS = {
    "vinayak": "1234",
    "admin": "admin",
    "apoorv": "1234"
}

sessions = {}

def process_request(message):
    parts = message.split("|", 2)

    if not parts:
        return "ERROR|Empty request"

    command = parts[0]

    if command == "LOGIN":
        if len(parts) != 3:
            return "ERROR|Invalid LOGIN format"

        username = parts[1]
        password = parts[2]

        if USERS.get(username) != password:
            return "LOGIN_FAILED"

        session_id = "1001"
        sessions[session_id] = username

        return f"LOGIN_SUCCESS|{session_id}"

    elif command == "SEND_MESSAGE":
        if len(parts) != 3:
            return "ERROR|Invalid SEND_MESSAGE format"

        session_id = parts[1]
        user_message = parts[2]

        if session_id not in sessions:
            return "ERROR|Invalid session"

        print(f"{sessions[session_id]} sent: {user_message}")

        return "MESSAGE_RECEIVED"

    elif command == "LOGOUT":
        if len(parts) != 2:
            return "ERROR|Invalid LOGOUT format"

        session_id = parts[1]

        if session_id not in sessions:
            return "ERROR|Invalid session"

        del sessions[session_id]

        return "LOGOUT_SUCCESS"

    return "ERROR|Unknown command"


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((HOST, PORT))
        server.listen(5)

        print(f"TCP server started on {HOST}:{PORT}")

        while True:
            client_socket, client_address = server.accept()

            with client_socket:
                print("Client connected:", client_address)

                try:
                    message = client_socket.recv(1024).decode("utf-8")

                    if not message:
                        continue

                    print("Received:", message)

                    response = process_request(message)

                    client_socket.sendall(response.encode("utf-8"))

                except Exception as error:
                    print("Client error:", error)


if __name__ == "__main__":
    main()