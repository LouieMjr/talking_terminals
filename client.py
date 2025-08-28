import socket
import msgpack
import selectors
import sys
import io

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8000  # The port used by the server
selector = selectors.DefaultSelector()

def write(client):
    msg_to_clients = input('')
    client.sendall(msgpack.packb(msg_to_clients))

def read(client):
    data = client.recv(1024)
    if not data:
        print(f'Data {data}. Server closed the connection.\nShutting Down!')
    else:
        response = msgpack.unpackb(data)
        print(f'From Chat: {response}')

def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    selector.register(client, selectors.EVENT_READ)
    selector.register(sys.stdin, selectors.EVENT_READ)
    try:
        while True:
            events = selector.select()
            for event, _ in events:
                if isinstance(event.fileobj, io.TextIOWrapper):
                    write(client)
                else:
                    read(client)
    except KeyboardInterrupt:
        client.shutdown(socket.SHUT_RDWR)
        client.close()
    finally:
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        print('Client side connection Closed!')

run_client()
