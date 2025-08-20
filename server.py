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
                print(f'\nClient wants to terminate.\nConnection closed!')
                connections.remove(client_conn)
                print('Removed client from list.')
                break
            else:
                print(f'\nMessage from client says: {message}')

            server_msg_to_client = msgpack.packb(input('\nSend message to Client: '))
            client_conn.sendall(server_msg_to_client)
    except KeyboardInterrupt:
        server_msg_to_client = msgpack.packb('quit')
        client_conn.sendall(server_msg_to_client)
        client_conn.close()
        connections.remove(client_conn)
        print('\nClient connection removed.')
        print(len(connections))

    finally:
        if len(connections) == 0:
            return 0
        return 1

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('127.0.0.1', 8000)
    server_socket.bind(server_address)
    server_socket.listen(5)
    _, PORT = server_address
    print(f"Server running on port: {PORT}")
    threads = []

    try:
        while True:
            client_conn, client_addr = server_socket.accept()
            print(f'\nI got a connection from{client_addr}')
            print(f'Client Socket: {client_conn}')
            connections.append(client_conn)

            client_thread = threading.Thread(target=handle_clients, args=(client_conn,))
            threads.append(client_thread)
            client_thread.start()
            print(threading.active_count())

            # for connection in connections:
            #     response = handle_clients(connection)
            #     if response == 0:
            #         print('All clients shutdown.')
    finally:
        server_socket.close()
        print('Server shutdown.')

start_tcp_server()
