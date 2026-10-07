import socket

HOST = "127.0.0.1"
PORT = 5001
TIMEOUT = 5


def build_message(choice):
    if choice == "1":
        username = input("Enter Username: ").strip()
        password = input("Enter Password: ").strip()

        if not username or not password:
            print("Username and password cannot be empty.")
            return None

        return f"LOGIN|{username}|{password}"

    if choice == "2":
        session_id = input("Enter Session ID: ").strip()
        user_message = input("Enter Message: ").strip()

        if not session_id or not user_message:
            print("Session ID and message cannot be empty.")
            return None

        return f"SEND_MESSAGE|{session_id}|{user_message}"

    if choice == "3":
        session_id = input("Enter Session ID: ").strip()

        if not session_id:
            print("Session ID cannot be empty.")
            return None

        return f"LOGOUT|{session_id}"

    print("Invalid Choice.")
    return None


def main():
    print("1. LOGIN")
    print("2. SEND_MESSAGE")
    print("3. LOGOUT")

    choice = input("Enter Choice: ").strip()
    message = build_message(choice)

    if message is None:
        return

    try:
        with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as client:
            client.sendall(message.encode("utf-8"))
            response = client.recv(1024).decode("utf-8")
            print("Server Response:", response)

    except ConnectionRefusedError:
        print("Error: TCP server is not running.")

    except TimeoutError:
        print("Error: Connection timed out.")

    except OSError as error:
        print(f"Network error: {error}")


if __name__ == "__main__":
    main()