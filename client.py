import asyncio
import itertools
import sys
from asyncio.exceptions import CancelledError

import zmq
import zmq.asyncio

context = zmq.asyncio.Context()
channels = ["All", "Team"]

print("Connecting to server...")
dealer = context.socket(zmq.PUSH)
dealer.connect("tcp://localhost:5556")

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5557")
subscriber.subscribe(channels[0].encode())
subscriber.subscribe(channels[1].encode())
print(subscriber, "what is this?\n")

poller = zmq.asyncio.Poller()
poller.register(subscriber, zmq.POLLIN)
poller.register(dealer, zmq.POLLIN)
poller.register(0, zmq.POLLIN)  # registering stdin
# print(type(sys.stdin))
# print(sys.stdin)


async def spin(msg):
    for idx, char in enumerate(itertools.cycle(r"\|/-")):
        status = f"\r{char} {msg} {char}"
        print(status, flush=True, end="")
        try:
            await asyncio.sleep(0.1)
        except CancelledError:
            break

    blanks = " " * len(status)
    print(f"\r{blanks}\r", end="")


async def supervisor():
    # spinner = asyncio.create_task(spin("waiting for poller"))
    result = await poll_for_events()
    # spinner.cancel()
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
