import socket
import msgpack

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
while True:
    client_msg_to_server = msgpack.packb(input('\nSend message to Server: '))

    s.sendall(client_msg_to_server)
    data_from_server = s.recv(1024)

    print(f'Unpack message from Server. \nMessage says: {msgpack.unpackb(data_from_server)}')

    # print(f"Bytes from Server: {data_from_server!r}")
    # print(f"Message from Server {msgpack.unpackb(data_from_server)}")
