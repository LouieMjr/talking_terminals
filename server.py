import asyncio
import itertools
import sys
from asyncio.exceptions import CancelledError

import rich
import zmq
import zmq.asyncio

context = zmq.asyncio.Context()

port = "5556"
port1 = "5557"
print(sys.argv)
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

publisher = context.socket(zmq.PUB)
route = context.socket(zmq.PULL)
publisher.bind(f"tcp://localhost:{port1}")
route.bind(f"tcp://localhost:{port}")


async def spin(msg):
    for char in itertools.cycle(r"\|/-"):
        status = f"\r{char} {msg} {char}"
        print(status, flush=True, end="")
        try:
            await asyncio.sleep(0.1)
        except CancelledError:
            break

    # move up 4 lines, clear entire line, move down 3 lines
    # print("\033[4A\033[2K\033[3B")
    # use for loop here to find correct line to erase

    blanks = " " * len(status)
    print(f"\r{blanks}\r", end="")


def parse(message):
    data = message.split(":")
    print(data)
    return data


async def supervisor():
    spinner = asyncio.create_task(spin("waiting for incoming messages"))
    result = await receive()
    spinner.cancel()
    return result


async def receive():
    msg = await route.recv()
    msg = msg.decode()
    # msg = check_for_client_name(msg)
    return msg


# def check_for_client_name(message):
#     msg = message.split(":")
#     msg[0] = msg[0].lower()
#     if "username" in msg:
#         clients_connected = clients["data"]
#         name = msg[1].title().strip()
#         clients["data"].append({"username": name, "id": len(clients_connected) + 1})
#         print(clients)
#         global NAME
#         NAME = name
#         return name
#     else:
#         return message


def check_for_channel_change_signal(signal):
    print("printing signal", signal)
    if signal == "\t":
        global channel
        if channel == channels[0]:
            channel = channels[1]
        else:
            channel = channels[0]

        return f"{channel} channel activated.".encode()
    return False


async def start_tcp_server():
    rich.print(f"Server running on port: {port}")

    while True:
        broadcast = await supervisor()
        channel_switch = check_for_channel_change_signal(broadcast)
        if channel_switch:
            publisher.send(channel_switch)
        else:
            rich.print(f"Clients message:\n{broadcast}")
            publisher.send(f"{channel} ch - {broadcast}".encode())


asyncio.run(start_tcp_server())
