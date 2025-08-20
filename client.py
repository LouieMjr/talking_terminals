import socket
import msgpack

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8000  # The port used by the server


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    try:
        while True:
            client_msg_to_server = input('\nSend message to Server: ')

            client.sendall(msgpack.packb(client_msg_to_server))
            if client_msg_to_server.lower() in ('q', 'quit'):
                break

            response = msgpack.unpackb(client.recv(1024))
            if not response or response.lower() in ('q', 'quit'):
                print('\nClient side shutting down.\nInitiated from Server!')
                break

            else:
                print(f'\nMessage says: {response}')

    except OSError:
        pass

    finally:
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        print('Client side connection Closed!')

run_client()
