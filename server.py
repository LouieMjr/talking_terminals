import asyncio
import itertools
import sys
from asyncio.exceptions import CancelledError

import msgpack
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

channel_data = {
    "All": [],
    "Team1": [],
    "Team2": [],
    "Private_channels": [],
    "total_connected": 0,
}


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
    # eventually use for loop here to find correct line to clear

    blanks = " " * len(status)
    print(f"\r{blanks}\r", end="")


def send_channel_subscriptions(data):
    route.send(msgpack.packb(data))


def route_clients_to_squads(client, team):
    number = channel_data["total_connected"]
    id = len(team)

    if number % 4 == 0:  # start a new squad of 2 for each team
        team.append({f"Squad{id}": []})
        channel_data["Team2"].append({f"Squad{id}": []})
    else:
        if len(team) != 0:
            id -= 1

    team[id][f"Squad{id}"].append(client)
    return f"Squad{id}"


def route_clients_to_teams(client):
    total_clients = channel_data["total_connected"]
    channel_data["All"].append({client: str(total_clients)})

    if total_clients % 2 == 0:
        squad_ch = route_clients_to_squads(client, channel_data["Team1"])
        channels = f"Team1 Team1{squad_ch}"

    else:
        squad_ch = route_clients_to_squads(client, channel_data["Team2"])
        channels = f"Team2 Team2{squad_ch}"

    channel_data["total_connected"] += 1
    send_channel_subscriptions(channels)


def parse(message):
    data = message.split(":")
    return data


async def supervisor():
    spinner = asyncio.create_task(spin("waiting for incoming messages"))
    result = await receive()
    spinner.cancel()
    return result


async def receive():
    msg = await route.recv()
    msg = msgpack.unpackb(msg)
    return parse(msg)


def client_joined_chat(msg_data):
    channel, _, name = msg_data
    route_clients_to_teams(name)
    rich.print(channel_data)
    publisher.send(f"{channel}:{name} has joined.".encode())


def make_subscription_out_of_even_elements(lst):
    data = []

    for idx in range(len(lst)):
        if idx % 2 == 0:
            if lst[idx] == "True":
                data.append("pm")
            else:
                data.append(lst[idx])

    subscription = ""
    data.sort()

    for part in data:
        subscription += part
        if part in lst:
            lst.remove(part)
    lst.remove("True")
    return subscription


def create_subscription_between_two_clients(msg_data):
    bool_str, channel, name, id = msg_data
    clients = []
    clients.append(bool_str)
    clients.append(channel)
    for client_data in channel_data["All"]:
        if name in client_data:
            if client_data[name] not in clients:
                clients.append(client_data[name])
                clients.append(name)
        else:
            if id in client_data.values():
                clients.append(id)
                clients += list(client_data.keys())

    topic_sub = make_subscription_out_of_even_elements(clients)

    if topic_sub not in channel_data["Private_channels"]:
        channel_data["Private_channels"].append(topic_sub)
    rich.print(channel_data)

    print(f"what is clients: {clients}\nand its length: {len(clients)}")
    channel, client1, client2 = clients
    return f"All:{topic_sub}:{client1}:{client2}".encode()


async def start_tcp_server():
    rich.print(f"Server running on port: {port}")

    while True:
        msg_data = await supervisor()
        if "quit" in msg_data:
            _, name = msg_data
            if name in channel_data["All"]:
                channel_data["All"].remove(name)
                print(channel_data)
            route.send(msgpack.packb(""))
        elif "username" in msg_data:
            client_joined_chat(msg_data)
            route.send(msgpack.packb(""))

        elif "True" in msg_data[0]:
            if len(msg_data) == 4:
                bool_str, channel, name, id = msg_data
                """
                Below works if requesting client made a selection to DM
                another client, while in either of these channels
                """
                if channel == "All" or "Team" in channel or "Squad" in channel:
                    message = create_subscription_between_two_clients(msg_data)
                    publisher.send(message)

                else:
                    # otherwise this is where actual private messages are being
                    # sent on those private channels
                    message = f"{channel}:{name}:{id}".encode()
                    publisher.send(message)
                route.send(msgpack.packb(""))
            else:
                # length of msg_data 2 at this point
                # send requesting client list of avaialable clients to DM
                private_message_list = msgpack.packb(channel_data["All"])
                route.send(private_message_list)
        else:
            channel, client, message = msg_data
            message = f"{channel}:{client}:{message}".encode()
            publisher.send(message)
            route.send(msgpack.packb(""))


asyncio.run(start_tcp_server())
