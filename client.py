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
    result = await poll_for_events()
    return result


async def poll_for_events():
    sockets = await poller.poll()
    return sockets


def is_input_tab(input):
    tab = "\t"

    has_letters = any(char.isalpha() for char in input)
    has_numbers = any(char.isdigit() for char in input)

    if tab in input and not (has_letters or has_numbers):
        return True
    else:
        return False


def read_input():
    input = sys.stdin.readline()
    if is_input_tab(input):
        return "\t"
    else:
        return input


def send_msg(msg):
    dealer.send(msg.encode())


async def response():
    msg = await dealer.recv()
    print(msg)
    msg = msg.decode()
    print(type(msg))
    print(msg)
    return msg


async def main():
    USERNAME = input("What's your username? ").title()
    # send_msg(f"UserName: {client_name}")

    while True:
        sockets = dict(await supervisor())
        # sockets = asyncio.create_task(poll_for_events())
        # sockets = await sockets
        # sockets = dict(sockets)

        for socket_or_fd, events in sockets.items():
            if socket_or_fd == 0:  # if we have an input from stdin
                message = read_input()  # use readline to capture that input/msg
                if message == "\t":
                    send_msg("\t")
                else:
                    send_msg(f"From {USERNAME}: {message}")  # send msg to server
            elif socket_or_fd == subscriber:
                message = await subscriber.recv()
                message = message.decode()
                print(f"{message}")
            elif socket_or_fd == dealer:
                print(f"\n{socket_or_fd}")
                res = response()
                print(res)


asyncio.run(main())
