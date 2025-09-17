import asyncio
import sys

import zmq
import zmq.asyncio
from rich import print

context = zmq.Context()

print("Connecting to server...")
dealer = context.socket(zmq.PUSH)
dealer.connect("tcp://localhost:5556")

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5557")
subscriber.subscribe(b"All")
print(subscriber, "what is this?")

poller = zmq.Poller()
poller.register(subscriber, zmq.POLLIN)
poller.register(dealer, zmq.POLLIN)
poller.register(0, zmq.POLLIN)
print(type(sys.stdin))
print(sys.stdin)


def poll_for_events():
    sockets = dict(poller.poll())
    print(f"What does poller have for us:\n{sockets}\n")
    return sockets


def craft_message():
    msg_to_send = sys.stdin.readline()
    return msg_to_send


def send_msg(msg):
    dealer.send(msg.encode())
    print("message sent!\n")


async def response():
    msg = dealer.recv().decode()
    print(type(msg))
    print(msg)
    return msg


async def main():
    while True:
        # sockets = asyncio.create_task(poll_for_events())
        # await sockets
        print("wait for poller")
        sockets = poll_for_events()

        for socket_or_fd, events in sockets.items():
            if socket_or_fd == 0:  # if we have a msg from stdin
                message = craft_message()  # use readline to capture that input/msg
                send_msg(message)  # send msg to server

            elif socket_or_fd == subscriber:
                print(f"\n{socket_or_fd}")
                message = subscriber.recv().decode()
                print(f"\nprint broadcasted msg: {message.split(', ')}")
                for msg in message.split(", "):
                    print(msg)
            elif socket_or_fd == dealer:
                print(f"\n{socket_or_fd}")
                res = await response()
                print(res)


asyncio.run(main())


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
