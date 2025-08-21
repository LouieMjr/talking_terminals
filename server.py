import socket
import msgpack
import threading
from queue import Queue



connections = []
threads = []
running = True

def handle_clients(client_conn):
    try:
        while True:
            data = client_conn.recv(1024)
            if not data:
                break

            message = msgpack.unpackb(data)

            if message.lower() in ('q', 'quit'):
                client_conn.close()
                print(f'\nClient wants to terminate.\nConnection closed!')
                print(f'How many clients connected: {len(connections)}')
                connections.remove(client_conn)
                print('Removed client from list.')
                print(f'How many clients connected: {len(connections)}')
                break
            else:
                print(f'\nMessage from client says: {message}')

            server_msg = input('\nSend message to Client: ')
            if server_msg.lower() in ('q', 'quit'):
                client_conn.close()
                global running
                running = False

                temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = ('127.0.0.1', 8000)
                temp_socket.connect(server_address)
                temp_socket.close()

                break

            client_conn.sendall(msgpack.packb(server_msg))

    finally:
        print('Client thread finished')

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('127.0.0.1', 8000)
    server_socket.bind(server_address)
    server_socket.listen(5)
    _, PORT = server_address
    print(f"Server running on port: {PORT}")

    try:
        while running:
            client_conn, client_addr = server_socket.accept()
            connections.append(client_conn)
            print(f'\nI got a connection from{client_addr}')
            print(f'Client Socket: {client_conn}')
            print(f'You are connected to: {len(connections)} client(s)')

            client_thread = threading.Thread(target=handle_clients,
                                             args=(client_conn,))
            threads.append(client_thread)
            client_thread.start()

    except OSError:
            pass

    finally:
        for connection in connections:
            connection.close()
        connections[:] = []

        for t in threads:
            t.join()

        print('\nShutting Down server.')
        print(f'Connections remaining: {len(connections)}')
        server_socket.close()
        print('Server Shutdown!')

start_tcp_server()
