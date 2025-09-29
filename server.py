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
route = context.socket(zmq.REP)
publisher.bind(f"tcp://localhost:{port1}")
route.bind(f"tcp://localhost:{port}")

channel_data = {"All": [], "Team1": [], "Team2": [], "total_connected": 0}


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


def send_team_status(data):
    route.send(data.encode())


def route_clients_to_teams(client):
    channel_data["All"].append(client)
    if channel_data["total_connected"] % 2 == 0:
        channel_data["Team1"].append(client)
        send_team_status("Team1")

    else:
        channel_data["Team2"].append(client)
        send_team_status("Team2")
    channel_data["total_connected"] += 1


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
    return parse(msg)


async def start_tcp_server():
    rich.print(f"Server running on port: {port}")

    while True:
        msg_data = await supervisor()
        # print(f"any zero in here: {msg_data}")
        if "0" in msg_data:
            print("printing 0")
        elif "username" in msg_data:
            channel, _, name = msg_data
            route_clients_to_teams(name)
            rich.print(channel_data)
            publisher.send(f"{channel}:{name} has joined.".encode())

        else:
            channel, client, message = msg_data
            route.send(b"")
            # print(f"Before publisher sends back\nWhat channel: {channel}")
            publisher.send(f"{channel}:{client}:{message}".encode())


asyncio.run(start_tcp_server())
