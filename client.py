import zmq, zmq.asyncio, sys

context = zmq.Context()



#  Socket to talk to server
print("Connecting to server...")
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5556")
print(sys.argv[1])
print(sys.argv[1].encode('utf-8'))

socket.subscribe(sys.argv[1].encode('utf-8'))
# socket.subscribe(b'10002')

while True:
    #  Get the reply.
    message = socket.recv_string()
    print(f"Received reply [ {message} ]")


# import socket
# import zmq, zmq.asyncio
# import msgpack
# import selectors
# import sys
# import io
#
# HOST = "127.0.0.1"
# PORT = 8000
# ctx = zmq.asyncio.Context()
# running = True
# selector = selectors.DefaultSelector()
#
# def write(client):
#     msg_to_clients = input('')
#     client.sendall(msgpack.packb(msg_to_clients))
#
# def read(client):
#     data = client.recv(1024)
#     if not data:
#         print(f'Data {data}. Server closed the connection.\nShutting Down!')
#         return False
#     else:
#         response = msgpack.unpackb(data)
#         print(f'From Chat: {response}')
#         return True
#
# def disconnect(client):
#     client.close()
#     print('Client side connection Closed!')
#
# def run_client():
#     global running
#     # client = ctx.socket(zmq.SUB)
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client.connect((HOST, PORT))
#     selector.register(client, selectors.EVENT_READ)
#     selector.register(sys.stdin, selectors.EVENT_READ)
#     try:
#         while running:
#
#             events = selector.select()
#
#             for event, _ in events:
#
#                 print(f'event: {event}')
#                 if isinstance(event.fileobj, io.TextIOWrapper):
#
#                     print(f'event: {event}\nFileObject: {event.fileobj}')
#                     write(client)
#                 else:
#                     if not read(client):
#                         running = False
#                         break
#                     else:
#                         read(client)
#
#     except KeyboardInterrupt:
#         client.sendall(msgpack.packb('quit'))
#         print('sent quit to server')
#     finally:
#         disconnect(client)
#
# run_client()
