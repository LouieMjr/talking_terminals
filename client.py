import socket
import msgpack

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    while True:
        client_msg_to_server = input('\nSend message to Server: ')

        client.sendall(msgpack.packb(client_msg_to_server))
        if client_msg_to_server.lower() in ['q', 'quit']:
            break

        response = client.recv(1024)
        if not response or response.lower() in ['q', 'quit']:
            break

        print(f'\nMessage says: {msgpack.unpackb(response)}')

        answer = input('Do you want to close the connection (y/n):')
        if answer.lower() == 'y':
            print('Shutting down connection...')
            break

    client.shutdown(socket.SHUT_RDWR)
    client.close()
    print('Client side connection Closed!')

run_client()
