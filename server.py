import socket
import msgpack
import threading
from _thread import start_new_thread

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

def start_tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server running on port: {PORT}")

    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        while True:

            data_from_client = conn.recv(1024)

            print(f'Unpack message from client. \nMessage says: {msgpack.unpackb(data_from_client)}')

            server_msg_to_client = msgpack.packb(input('\nSend message to Client: '))
            conn.sendall(server_msg_to_client)

start_tcp_server()


