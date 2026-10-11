import socket
HOST = "127.0.0.1"
PORT = 5001
TIMEOUT = 5
def send_request(message):
    """Send one request and return the server response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(TIMEOUT)
            client.connect((HOST, PORT))
            client.sendall(message.encode("utf-8"))
            response = client.recv(4096).decode("utf-8").strip()
            if not response:
                print("The server closed the connection without a response.")
                return None
            print("Server Response:", response)
            return response
    except ConnectionRefusedError:
        print("Connection refused. Is the TCP server running?")
    except socket.timeout:
        print(f"Connection timed out after {TIMEOUT} seconds.")
    except OSError as error:
        print("Socket error:", error)
    except UnicodeDecodeError:
        print("The server response was not valid UTF-8.")
    return None
def main():
    session_id = None
    logged_in = False
    while True:
        print("\n--- Campus Communication Client ---")
        print("1. LOGIN")
        print("2. SEND_MESSAGE")
        print("3. LOGOUT")
        print("4. EXIT")
        try:
            choice = input("Enter choice: ").strip()
        except EOFError:
            print("No interactive input available. Exiting client.")
            break
        if choice == "1":
            if logged_in:
                print("You are already logged in.")
                continue
            try:
                username = input("Enter username: ").strip()
                password = input("Enter password: ")
            except EOFError:
                print("No interactive input available. Exiting client.")
                break
            if not username or not password:
                print("Username and password cannot be empty.")
                continue
            response = send_request(f"LOGIN|{username}|{password}")
            if response == "LOGIN_SUCCESS":
                logged_in = True
                session_id = None
                print("Login successful.")
            elif response and response.startswith("LOGIN_SUCCESS|"):
                session_id = response.split("|", 1)[1]
                logged_in = bool(session_id)
                if logged_in:
                    print("Login successful. Session ID saved.")
            elif response == "LOGIN_FAILED":
                print("Login failed. Check your username and password.")
        elif choice == "2":
            if not logged_in:
                print("Please log in first.")
                continue
            try:
                message = input("Enter message: ").strip()
            except EOFError:
                print("No interactive input available. Exiting client.")
                break
            if not message:
                print("Message cannot be empty.")
                continue
            if session_id:
                request = f"SEND_MESSAGE|{session_id}|{message}"
            else:
                request = f"SEND_MESSAGE|local-session|{message}"
            response = send_request(request)
            if response and response.startswith("ERROR|Invalid session"):
                logged_in = False
                session_id = None
                print("Your session is invalid. Please log in again.")
        elif choice == "3":
            if not logged_in:
                print("You are not logged in.")
                continue
            if session_id:
                response = send_request(f"LOGOUT|{session_id}")
            else:
                response = send_request("LOGOUT|local-session")
            if response == "LOGOUT_SUCCESS":
                logged_in = False
                session_id = None
                print("Logged out successfully.")
        elif choice == "4":
            if logged_in:
                print("Please log out before exiting.")
                continue
            print("Exiting client.")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")
if __name__ == "__main__":
    main()
