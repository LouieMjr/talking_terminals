import asyncio
import threading
import socket
import msgpack

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8000  # The port used by the server
threads = []

def add_threads(thread):
    threads.append(thread)

def start_threads():
    for thread in threads:
        thread.start()

def write(client):
    while True:
        msg_to_clients = input('')
        client.sendall(msgpack.packb(msg_to_clients))

def read(client):
    while True:
        data = client.recv(1024)
        if not data:
            global running
            running = False
            print(f'Data {data}. Server closed the connection.\nShutting Down!')
        else:
            response = msgpack.unpackb(data)
            print(f'\nFrom Chat: {response}')

def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    try:
        write_thread = threading.Thread(target=write, args=(client,))
        read_thread = threading.Thread(target=read, args=(client,))
        threads.append(read_thread)
        threads.append(write_thread)
        start_threads()
    except KeyboardInterrupt:
        for t in threads:
            t.join()

        client.shutdown(socket.SHUT_RDWR)
        client.close()
    finally:

        for t in threads:
            t.join()

        client.shutdown(socket.SHUT_RDWR)
        client.close()
        print('Client side connection Closed!')

run_client()
