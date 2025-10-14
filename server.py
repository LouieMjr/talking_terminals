import asyncio
import itertools
import sys
from asyncio.exceptions import CancelledError

import msgpack
import rich
import zmq
import zmq.asyncio
from rich.console import Console

context = zmq.asyncio.Context()
console = Console()


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
    "uid": 0,
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


def route_clients_to_squads(client_data, team):
    number = channel_data["total_connected"]
    id = len(team)

    if number % 4 == 0:  # start a new squad of 2 for each team
        team.append({f"Squad{id}": []})
        channel_data["Team2"].append({f"Squad{id}": []})
    else:
        if len(team) != 0:
            id -= 1

    team[id][f"Squad{id}"].append(client_data)
    return f"Squad{id}"


def route_clients_to_teams(client):
    total_clients = channel_data["total_connected"]
    unique_id = channel_data["uid"]
    client_data = {client: str(unique_id)}
    channel_data["All"].append(client_data)

    if total_clients % 2 == 0:
        squad_ch = route_clients_to_squads(client_data, channel_data["Team1"])
        channels = f"Team1 Team1{squad_ch}"

    else:
        squad_ch = route_clients_to_squads(client_data, channel_data["Team2"])
        channels = f"Team2 Team2{squad_ch}"

    channel_data["total_connected"] += 1
    channel_data["uid"] += 1
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
    payload = f"{channel}:{name} has joined."
    publish_message(payload)


def make_private_channel_for_clients(client_data):
    ids = list(client_data.values())
    return "pm".join(ids)


def prepare_to_make_topic_subscription(msg_data):
    _, _, name, requested_id = msg_data
    client_data = {}

    for data in channel_data["All"]:
        if name in data:
            print(f"{data[name]} not in {client_data}: {data[name] not in client_data}")
            if data[name] not in client_data:
                requester_client_id = data[name]
                client_data[name] = requester_client_id
        else:
            if requested_id in data.values():
                requested_client = list(data.keys())[0]
                client_data[requested_client] = requested_id

    topic_sub = make_private_channel_for_clients(client_data)

    if topic_sub not in channel_data["Private_channels"]:
        channel_data["Private_channels"].append(topic_sub)
    rich.print(channel_data)

    client1, client2 = list(client_data.keys())

    payload = f"All:{topic_sub}:{client1}:{client2}"
    return payload


def empty_team_list(lst):
    for obj in lst:
        for key, array in obj.items():
            if "Squad" in key:
                if len(array) == 0:
                    lst.remove(obj)


def remove_client_from_list(lst, name):
    for obj in lst:
        if name in obj:
            lst.remove(obj)
            break
        else:
            for _, value in obj.items():
                if isinstance(value, list):
                    remove_client_from_list(value, name)

    empty_team_list(lst)


def find_lists(name):
    data = channel_data
    for _, value in data.items():
        if isinstance(value, list):
            remove_client_from_list(value, name)


def remove_client_from_all_lists(name):
    find_lists(name)
    update_total_connected()


def update_total_connected():
    if len(channel_data["All"]) != channel_data["total_connected"]:
        channel_data["total_connected"] = len(channel_data["All"])


def publish_message(payload):
    publisher.send(payload.encode())


async def start_tcp_server():
    rich.print(f"Server running on port: {port}")

    while True:
        msg_data = await supervisor()
        if "quit" == msg_data[-1]:
            channel, name, message = msg_data
            remove_client_from_all_lists(name)
            route.send(msgpack.packb("quit"))
        elif "username" in msg_data:
            client_joined_chat(msg_data)
            route.send(msgpack.packb(""))

        elif "True" in msg_data[0]:
            if len(msg_data) == 4:
                console.print(
                    "\n[bold purple]Picked client to private message.\nSending back pm channel to clients"
                )
                bool_str, channel, name, id = msg_data
                payload = prepare_to_make_topic_subscription(msg_data)
                publish_message(payload)
                route.send(msgpack.packb(""))
            else:
                console.print(
                    "\n[bold purple]Private message requested.\nSending back list"
                )
                # length of msg_data 2 at this point
                # send requesting client list of avaialable clients to DM
                private_message_list = msgpack.packb(channel_data["All"])
                route.send(private_message_list)
        else:
            channel, client, message = msg_data
            payload = f"{channel}:{client}:{message}"
            publish_message(payload)
            route.send(msgpack.packb(""))


asyncio.run(start_tcp_server())
