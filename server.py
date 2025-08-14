import socket
import threading
import msgpack

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

print(threading.active_count())
print(threading.current_thread())
storeData = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
conn, addr = s.accept()
with conn:
    print(f"Connected by {addr}")
    while True:
        data_from_client = conn.recv(1024)
        print(f'Unpack message from client. \nMessage says: {msgpack.unpackb(data_from_client)}')

        # if not data:
        #     break
        server_msg_to_client = msgpack.packb(input('\nSend message to Client: '))
        conn.sendall(server_msg_to_client)


