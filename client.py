import asyncio
import sys
from asyncio.exceptions import CancelledError

import msgpack
import rich
import zmq
import zmq.asyncio
from rich.console import Console

context = zmq.asyncio.Context()
console = Console()
channels = ["All"]
channel = channels[0]


print("Connecting to server...")
dealer = context.socket(zmq.REQ)
dealer.connect("tcp://localhost:5556")

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5557")
subscriber.subscribe(channel.encode())

poller = zmq.asyncio.Poller()
poller.register(subscriber, zmq.POLLIN)
poller.register(dealer, zmq.POLLIN)
poller.register(0, zmq.POLLIN)  # registering stdin


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


def change_channels(input):
    private_message_signal = "\t\t\n"
    if input == private_message_signal:
        dealer.send(msgpack.packb("private_message"))
        console.print("[bold purple]Private message mode activated.")
    else:
        global channel
        if channel == channels[0]:
            channel = channels[1]
            console.print(f"[bold blue]{channel} channel active.")
        elif channel == channels[1]:
            channel = channels[2]
            console.print(f"[bold green]{channel[5:len(channel)-1]} channel active.")
        else:
            channel = channels[0]
            console.print(f"[bold yellow]{channel} channel active.")


# def display_all_clients():


def read_input():
    input = sys.stdin.readline()
    if input != "\n":
        erase_input_line()
    if is_input_tab(input):
        change_channels(input)
        # if not change_channels(input):

        return None
    else:
        valid = validate_input(input)
        if not valid:
            return False
        else:
            return input


def send_join_signal(name):
    dealer.send(msgpack.packb(f"{channel}:username:{name}"))


def deliver_msg(msg_data):
    username, message = msg_data
    # print(f"what channel is this on: {channel}")
    dealer.send(msgpack.packb(f"{channel}:{username}:{message}"))


def erase_input_line():
    print("\033[1A\033[2K", end="\r")


def validate_input(input):
    if input == "\n":
        print("\033[1A", end="\r")
        return False
    return True


def add_channel_and_subscribe(new_channels):
    for channel in new_channels:
        channels.append(channel)
        subscriber.subscribe(channel.encode())


async def response():
    response = await dealer.recv()
    response = msgpack.unpackb(response)
    # if isinstance(response, bytes):
    # response = response.decode()
    if response != "":
        new_channels = response.split(" ")
        add_channel_and_subscribe(new_channels)
        # return new_channels


def display_who_joined_chat(msg_data, username):
    _, message = msg_data
    if username in message:
        message = "You joined the chat."

    console.print(f"[bold red]{message}")


def display_client_message(msg_data, username):
    from_channel, user, message = msg_data
    if username in user:
        user = "Me"
    global channel
    if from_channel == "All":
        console.print(f"[yellow][All][{user}]: {message}", end="")
    elif (
        "Team" in from_channel
        and from_channel in channels
        and "Squad" not in from_channel
    ):
        console.print(f"[blue][Team][{user}]: {message}", end="")
    elif "Squad" in from_channel and from_channel in channels:
        console.print(f"[green][Squad][{user}]: {message}", end="")


async def main():
    USERNAME = input("What should people call you? ").title()
    send_join_signal(USERNAME)

    while True:
        try:
            sockets = dict(await supervisor())
        except CancelledError:
            await dealer.send(msgpack.packb(f"quit:{USERNAME}"))
            print("Pressed CTRL C")
            break

        for socket_or_fd, events in sockets.items():
            if socket_or_fd == 0:  # if we have an input from stdin
                message = read_input()  # use readline to capture that input/msg
                if message is not None and message is not False:
                    deliver_msg([USERNAME, message])
            if socket_or_fd == subscriber:
                msg_data = await subscriber.recv()
                msg_data = msg_data.decode().split(":")

                if len(msg_data) <= 2:
                    display_who_joined_chat(msg_data, USERNAME)
                else:
                    display_client_message(msg_data, USERNAME)
            if socket_or_fd == dealer:
                res = await response()
                if res is not None:
                    rich.print(res)


asyncio.run(main())
