import socket

print("1. LOGIN")
print("2. SEND_MESSAGE")
print("3. LOGOUT")

choice = input("Enter Choice: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5001))

if choice == "1":

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    message = f"LOGIN|{username}|{password}"

elif choice == "2":

    session_id = input("Enter Session ID: ")
    msg = input("Enter Message: ")

    message = f"SEND_MESSAGE|{session_id}|{msg}"

elif choice == "3":

    session_id = input("Enter Session ID: ")

    message = f"LOGOUT|{session_id}"

else:

    print("Invalid Choice")
    client.close()
    exit()

client.send(message.encode())

response = client.recv(1024).decode()

print("Server Response:", response)

client.close()