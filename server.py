import socket
from sys import exception
import msgpack
import threading

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

def handle_clients(client_conn, addr):
    try:
        data = client_conn.recv(1024)
        message = msgpack.unpackb(data)

        if message.lower() in ('q', 'quit'):
            return

        print(f'\nMessage from client says: {message}')

        server_msg_to_client = msgpack.packb(input('\nSend message to Client: '))
        client_conn.sendall(server_msg_to_client)

    except Exception as e:
        print(f'Error while handling client: {e}')
    finally:
        return 'close'

def start_tcp_server():

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((HOST, PORT))
            server.listen(5)
            print(f"Server running on port: {PORT}")

            client_conn, addr = server.accept()
            with client_conn as client:

                while True:
                    print(f"Connected by {addr[0]}:{addr[1]}")
                    print(f'client: {client}')
                    response = handle_clients(client, addr)
                    if response == 'close':
                        print(f"Connection to client ({addr[0]}:{addr[1]}) closed")
                        print('client shutdown')
                        break

            print('server shutdown')

start_tcp_server()
