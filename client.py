import socket
import msgpack
import selectors
import sys
import io

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8000  # The port used by the server
running = True
selector = selectors.DefaultSelector()

def write(client):
    msg_to_clients = input('')
    client.sendall(msgpack.packb(msg_to_clients))

def read(client):
    data = client.recv(1024)
    if not data:
        print(f'Data {data}. Server closed the connection.\nShutting Down!')
        return False
    else:
        response = msgpack.unpackb(data)
        print(f'From Chat: {response}')
        return True

def disconnect(client):
    client.close()
    print('Client side connection Closed!')

def run_client():
    global running
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    selector.register(client, selectors.EVENT_READ)
    selector.register(sys.stdin, selectors.EVENT_READ)
    try:
        while running:

            events = selector.select()

            for event, _ in events:

                print(f'event: {event}')
                if isinstance(event.fileobj, io.TextIOWrapper):

                    print(f'event: {event}\nFileObject: {event.fileobj}')
                    write(client)
                else:
                    if not read(client):
                        running = False
                        break
                    else:
                        read(client)

    except KeyboardInterrupt:
        client.sendall(msgpack.packb('quit'))
        print('sent quit to server')
    finally:
        disconnect(client)

run_client()
