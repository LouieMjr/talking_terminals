import asyncio
import sys
from asyncio.exceptions import CancelledError

import zmq
import zmq.asyncio
from rich.console import Console

from client_storage import channels

context = zmq.asyncio.Context()
console = Console()
channel_keys = list(channels)
channel = channel_keys[0]


print("Connecting to server...")
dealer = context.socket(zmq.PUSH)
dealer.connect("tcp://localhost:5556")

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5557")
subscriber.subscribe(channel.encode())
# subscriber.subscribe(channels[1].encode())

poller = zmq.asyncio.Poller()
poller.register(subscriber, zmq.POLLIN)
poller.register(dealer, zmq.POLLIN)
poller.register(0, zmq.POLLIN)  # registering stdin
# print(type(sys.stdin))
# print(sys.stdin)


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


def change_channels():
    global channel
    if channel == channel_keys[0]:
        channel = channel_keys[1]
    else:
        channel = channel_keys[0]


def read_input():
    input = sys.stdin.readline()
    erase_input_line()
    if is_input_tab(input):
        change_channels()
        subscriber.subscribe(channel)
        print(f"{channel} channel activated.")
        return None
    else:
        valid = validate_input(input)
        if not valid:
            return False
        else:
            return input


def send_join_signal(name):
    dealer.send(f"{channel}:username:{name}".encode())


def deliver_msg(msg_data):
    username, message = msg_data
    dealer.send(f"{channel}:{username}:{message}".encode())


def erase_input_line():
    print("\033[1A\033[2K", end="\r")


def validate_input(input):
    if input == "\n":
        print("\033[1A", end="\r")
        return False
    return True


async def response():
    msg = await dealer.recv()
    print(msg)
    msg = msg.decode()
    print(type(msg))
    print(msg)
    return msg


def display_who_joined_chat(msg_data, username):
    _, message = msg_data
    if username in message:
        message = "You joined the chat."

    console.print(f"[bold red]{message}")


def display_client_message(msg_data, username):
    _, user, message = msg_data
    if username in user:
        user = "Me"
    global channel
    if channel == "All":
        console.print(f"[yellow][{user}]: {message}", end="")
    else:
        console.print(f"[blue][{user}]: {message}", end="")
    # rich.print(f"[{user}]: {message}", end="")


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
                if message is not None and message is not False:
                    deliver_msg([USERNAME, message])
            elif socket_or_fd == subscriber:
                msg_data = await subscriber.recv()
                msg_data = msg_data.decode().split(":")

                if len(msg_data) <= 2:
                    display_who_joined_chat(msg_data, USERNAME)
                else:
                    display_client_message(msg_data, USERNAME)
            elif socket_or_fd == dealer:
                print(f"\n{socket_or_fd}")
                res = response()
                print(res)


asyncio.run(main())
