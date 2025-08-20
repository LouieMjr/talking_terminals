import socket
import msgpack
import threading

connections = []

def handle_clients(client_conn):
    try:
        while True:
            data = client_conn.recv(1024)
            message = msgpack.unpackb(data)

            if message.lower() in ('q', 'quit'):
                client_conn.close()
                print(f'\nClient wants to {message}.\nConnection closed!')
                connections.remove(client_conn)
                print('Removed client from list.')
                break
            else:
                print(f'\nMessage from client says: {message}')

            server_msg_to_client = msgpack.packb(input('\nSend message to Client: '))
            client_conn.sendall(server_msg_to_client)
    finally:
        return

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 8000)
    server_socket.bind(server_address)
    server_socket.listen(5)
    _, PORT = server_address
    print(f"Server running on port: {PORT}")

    try:
        while True:
            client_conn, client_addr = server_socket.accept()
            print(f'I got a connection from{client_addr}')
            print(f'client: {client_conn}')
            connections.append(client_conn)

            for connection in connections:
                response = handle_clients(connection)
                if response == 'close':
                    print('client shutdown')
                    break
    finally:
        server_socket.close()


start_tcp_server()
