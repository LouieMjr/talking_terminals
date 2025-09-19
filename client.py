import asyncio
import itertools
import sys
from asyncio.exceptions import CancelledError

import zmq
import zmq.asyncio

# from rich import print

context = zmq.asyncio.Context()

print("Connecting to server...")
dealer = context.socket(zmq.PUSH)
dealer.connect("tcp://localhost:5556")

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5557")
subscriber.subscribe(b"All")
print(subscriber, "what is this?\n")

poller = zmq.asyncio.Poller()
poller.register(subscriber, zmq.POLLIN)
poller.register(dealer, zmq.POLLIN)
poller.register(0, zmq.POLLIN)
# print(type(sys.stdin))
# print(sys.stdin)


async def spin(msg):
    for idx, char in enumerate(itertools.cycle(r"\|/-")):
        if idx != 0:
            print("\x1b[1A", end="")
        status = f"\r{char} {msg} {char}"
        print(status, flush=True, end="")
        print("\x1b[2B", end="")
        try:
            # time.sleep(0.1)
            await asyncio.sleep(0.1)
        except CancelledError:
            break

    blanks = " " * len(status)
    print(f"\r{blanks}\r", end="")


async def supervisor():
    spinner = asyncio.create_task(spin("waiting for poller"))
    result = await poll_for_events()
    spinner.cancel()
    return result


async def poll_for_events():
    sockets = await poller.poll()
    return sockets


def craft_message():
    msg_to_send = sys.stdin.readline()
    return msg_to_send


def send_msg(msg):
    dealer.send(msg.encode())
    print("message sent!\n")


async def response():
    msg = await dealer.recv()
    print(msg)
    msg = msg.decode()
    print(type(msg))
    print(msg)
    return msg


async def main():
    while True:
        sockets = dict(await supervisor())
        # sockets = asyncio.create_task(poll_for_events())
        # sockets = await sockets
        # sockets = dict(sockets)

        for socket_or_fd, events in sockets.items():
            if socket_or_fd == 0:  # if we have a msg from stdin
                message = craft_message()  # use readline to capture that input/msg
                send_msg(message)  # send msg to server

            elif socket_or_fd == subscriber:
                print(f"\n{socket_or_fd}")
                message = await subscriber.recv()
                print(f"IN SUB. What is message before decode: {message}")
                message = message.decode()
                print(f"\nprint broadcasted msg: {message.split(', ')}")
                for msg in message.split(", "):
                    print(msg)
            elif socket_or_fd == dealer:
                print(f"\n{socket_or_fd}")
                res = response()
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
