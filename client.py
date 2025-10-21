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
USERNAME = ""
private_message_mode = False
private_message_ids = []
incoming_private_message = [False]
client_list = None
running = True

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


def erase_input_line():
    print("\033[1A\033[2K", end="\r")


def validate_input(input):
    global private_message_ids
    if input == "\n":
        print("\033[1A", end="\r")
        return False
    if input == "":
        return False
    if private_message_mode:
        if input not in private_message_ids:
            console.print(
                f"{text_color_based_on_channel(channel, False, True)}Need to enter in a valid id from the list."
            )
            return False
    if incoming_private_message[0]:
        input = input.lower()
        if input != "y":
            return False

    return True


def send_join_signal(name):
    dealer.send(msgpack.packb(f"{channel}:username:{name}"))


def display_joiners_and_leavers(msg_data, username):
    _, message = msg_data
    if username in message:
        message = "You joined the chat."

    console.print(f"[bold red]{message}")


def text_color_based_on_channel(channel, bold, warning=False):
    if warning:
        return "[bold red]"
    if channel not in channels:
        return None
    if channel == "All":
        if bold:
            return "[bold yellow]"
        return "[yellow]"
    elif (
        channel == "Team1"
        and channel in channels
        or channel == "Team2"
        and channel in channels
    ):
        if bold:
            return "[bold blue]"
        return "[blue]"
    elif "Squad" in channel and channel in channels:
        if bold:
            return "[bold green]"
        return "[green]"
    else:
        return "[bold purple]"


# Turn into "Display Channel"
def channel_color(from_ch):
    if from_ch not in channels:
        return None
    if from_ch == "All":
        return "[yellow][All]"
    elif (
        from_ch == "Team1"
        and from_ch in channels
        or from_ch == "Team2"
        and from_ch in channels
    ):
        return "[blue][Team]"
    elif "Squad" in from_ch and from_ch in channels:
        return "[green][Squad]"
    else:
        return "[bold purple][Private]"


def display_client_message(msg_data, username):
    from_channel, user, message = msg_data
    client = None
    if username != user:
        client = user
        incoming_private_message.append(client)
    if username in user:
        user = "Me"

    color_and_channel = channel_color(from_channel)
    if color_and_channel is not None:
        console.print(f"{color_and_channel}[{user}]: {message}")
        if channel != from_channel and "pm" in from_channel:
            incoming_private_message[0] = True
            console.print(f"[bold purple]Would you like message {client}? (y/n).")


def is_input_tab(input):
    tab = "\t"

    has_letters = any(char.isalpha() for char in input)
    has_numbers = any(char.isdigit() for char in input)

    if tab in input and not (has_letters or has_numbers):
        return True
    else:
        return False


def input_is_private_message_request(tab):
    global private_message_mode
    private_message_signal = "\t\t"
    if tab == private_message_signal:
        private_message_mode = True
        console.print("[bold purple]Private message mode activated.")
        return True
    return False


def change_channels():
    global channel

    if channel == channels[0]:
        channel = channels[1]
        console.print(f"[bold blue]{channel} channel active.")
    elif channel == channels[1]:
        channel = channels[2]
        console.print(f"[bold green]{channel[5 : len(channel) - 1]} channel active.")
    else:
        channel = channels[0]
        console.print(f"[bold yellow]{channel} channel active.")


def display_client_options_for_private_messaging(response):
    private_message_list = ""
    for idx in range(len(response)):
        client_data = response[idx]
        # uncomment below to display list of clients in groups of 2
        # if idx % 2 == 0:
        # private_message_list += "\n"
        for name, id in client_data.items():
            if name != USERNAME:
                private_message_ids.append(id)
                private_message_list += f"[{id}: {name}]\n"

    console.print(
        "\n[bold purple]Enter the number of the person you'd like to "
        "speak with below.\nA unique channel "
        "will be created for you and this person to chat on."
    )
    rich.print(private_message_list)


def read_input():
    global private_message_mode, channel
    input = sys.stdin.readline()

    if "\n" in input:
        input = input.replace("\n", "")
    if input != "\n":
        erase_input_line()
    if is_input_tab(input):
        if input_is_private_message_request(input):
            dealer.send(msgpack.packb(f"{private_message_mode}:{USERNAME}:''"))
        else:
            if private_message_mode:
                private_message_mode = False
            change_channels()
        return None
    else:
        valid = validate_input(input)
        if not valid:
            return False
        else:
            if incoming_private_message[0]:
                erase_input_line()
                console.print(
                    f"[bold purple]You are now messaging {incoming_private_message[1]}"
                )
                incoming_private_message[0] = False
                channel = channels[-1]
                return False
            else:
                return input


def send_channel_message(msg_data):
    username, message = msg_data
    if private_message_mode:
        dealer.send(
            msgpack.packb(f"{private_message_mode}:{channel}:{username}:{message}")
        )
    else:
        dealer.send(msgpack.packb(f"{channel}:{username}:{message}"))


def add_channels_and_subscribe(new_channels):
    for channel in new_channels.split(" "):
        if channel not in channels:
            channels.append(channel)
            subscriber.subscribe(channel.encode())


async def response():
    global private_message_mode, client_list

    response = await dealer.recv()
    response = msgpack.unpackb(response)
    if response != "":
        if isinstance(response, str):
            add_channels_and_subscribe(response)
        else:
            if len(response) <= 1:
                private_message_mode = False
                purple_message = "[bold purple]No one available to DM.\n"
                message = f"{text_color_based_on_channel(channel, True)}*{channel} channel is still active*"
                console.print(f"{purple_message}{message}")

            else:
                if isinstance(response[0], dict):
                    #### GET LIST OF AVAILABLE PEOPLE TO DM
                    client_list = response
                    add_channels_and_subscribe(channel)
                    display_client_options_for_private_messaging(client_list)
                else:
                    for client in response[1]:
                        print(client)
                        if USERNAME == client:
                            print(client)


async def main():
    try:
        global USERNAME, running
        USERNAME = input("What should people call you? ").title()
        send_join_signal(USERNAME)
    except KeyboardInterrupt:
        erase_input_line()
        print("Connection closing.")

    while running:
        try:
            sockets = dict(await supervisor())
        except CancelledError:
            await dealer.send(msgpack.packb(f"All:{USERNAME}:quit"))
            break

        for socket_or_fd, events in sockets.items():
            if socket_or_fd == 0:  # if we have an input from stdin
                message = read_input()  # use readline to capture that input/msg
                if message is not None and message is not False:
                    send_channel_message([USERNAME, message])
                    if message == "quit":
                        running = False
            if socket_or_fd == subscriber:
                msg_data = await subscriber.recv()
                msg_data = msg_data.decode().split(":")

                if len(msg_data) <= 2:
                    display_joiners_and_leavers(msg_data, USERNAME)
                elif len(msg_data) == 3:
                    if incoming_private_message[0]:
                        erase_input_line()
                    display_client_message(msg_data, USERNAME)
                else:
                    if USERNAME in msg_data:
                        (
                            all_ch,
                            pm_ch,
                            requesting_client,
                            requested_client,
                        ) = msg_data
                        add_channels_and_subscribe(pm_ch)
                        global channel, private_message_mode
                        private_message_mode = False
                        if requesting_client == USERNAME:
                            channel = pm_ch
                            message = f"You are now messaging {requested_client}"
                            console.print(
                                f"{text_color_based_on_channel(channel, True)}{message}"
                            )
            if socket_or_fd == dealer:
                await response()

    dealer.close()
    subscriber.close()
    context.term()
    print("Connection Closed.")


asyncio.run(main())
