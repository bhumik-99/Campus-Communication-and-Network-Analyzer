import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("127.0.0.1", 5001))
server.listen(1)

print("Server Started...")

while True:

    client_socket, client_address = server.accept()

    print("\nClient connected:", client_address)

    message = client_socket.recv(1024).decode()

    print("Received:", message)

    parts = message.split("|")

    if parts[0] == "LOGIN":

        username = parts[1]
        password = parts[2]

        print("Username:", username)
        print("Password:", password)

        client_socket.send("LOGIN_SUCCESS".encode())

    elif parts[0] == "SEND_MESSAGE":

        session_id = parts[1]
        user_message = parts[2]

        print("Session ID:", session_id)
        print("Message:", user_message)

        client_socket.send("MESSAGE_RECEIVED".encode())

    elif parts[0] == "LOGOUT":

        session_id = parts[1]

        print("Session ID:", session_id)
        print("User Logged Out")

        client_socket.send("LOGOUT_SUCCESS".encode())

    else:

        client_socket.send("INVALID_REQUEST".encode())

    client_socket.close()