import asyncio
import itertools
import sys
from asyncio.exceptions import CancelledError
from random import randint

import msgpack
import rich
import zmq
import zmq.asyncio
from rich.console import Console

from db_controller import (
    db_does_client_exist,
    db_get_client_data,
    db_store_client_chat_history,
    db_store_client_data,
    db_update_online_status,
)

context = zmq.asyncio.Context()
console = Console()


port = "5556"
port1 = "5557"
print(sys.argv)
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

publisher = context.socket(zmq.PUB)
reply = context.socket(zmq.REP)
publisher.bind(f"tcp://localhost:{port1}")
reply.bind(f"tcp://localhost:{port}")

channel_data = {
    "All": [],
    "Team1": [],
    "Team2": [],
    "total_connected": 0,
}

unique_ids = set()


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
    reply.send(msgpack.packb(data))


def route_clients_to_squads(client_data, team):
    id = len(team)

    if len(team) == 0:
        team.append({f"Squad{id}": []})
    if id > 0:
        if len(team[id - 1][f"Squad{id - 1}"]) < 2:
            id -= 1
            team[id][f"Squad{id}"].append(client_data)
            return f"Squad{id}"
        else:
            team.append({f"Squad{id}": []})
            team[id][f"Squad{id}"].append(client_data)
    else:
        team[id][f"Squad{id}"].append(client_data)

    return f"Squad{id}"


def generate_unique_random_number(unique_ids):
    unique_id = randint(0, 100)
    if unique_id in unique_ids:
        return generate_unique_random_number(unique_ids)
    else:
        unique_ids.add(unique_id)
        return unique_id


def route_clients_to_teams(client):
    total_clients = channel_data["total_connected"]
    unique_id = generate_unique_random_number(unique_ids)
    client_data = {client: str(unique_id)}
    print("how many times going into all")
    channel_data["All"].append(client_data)

    if total_clients % 2 == 0:
        squad_ch = route_clients_to_squads(client_data, channel_data["Team1"])
        channels = f"Team1:Team1{squad_ch}"

    else:
        squad_ch = route_clients_to_squads(client_data, channel_data["Team2"])
        channels = f"Team2:Team2{squad_ch}"

    channel_data["total_connected"] += 1
    send_channel_subscriptions(channels)
    topics_and_id = f"{unique_id}:{channels}"
    team_ch = channels.split(":")[0]
    return [client, unique_id, team_ch, squad_ch, topics_and_id]


def parse(message):
    data = message.split(":")
    return data


async def supervisor():
    spinner = asyncio.create_task(spin("waiting for incoming messages"))
    result = await receive()
    spinner.cancel()
    return result


async def receive():
    msg = await reply.recv()
    msg = msgpack.unpackb(msg)
    return parse(msg)


def client_joined_chat(msg_data):
    channel, _, name = msg_data
    found = db_does_client_exist(name)

    if not found:
        data = route_clients_to_teams_and_create_channels(name)
        topics_and_id = data.pop()
        db_store_client_data(data)
        send_channel_subscriptions(topics_and_id)
        # send_channel_subscriptions()
    # else:
    rich.print(channel_data, "do we reach this?")
    payload = f"{channel}:{name} has joined."
    publish_message(payload)
    # id = data.split(":")[0]
    # print(id)
    # if not online:
    #     db_insert_client(name, id)


def make_private_channel_for_clients(client_data):
    ids = list(client_data.values())
    return "pm".join(ids)


def prepare_to_make_topic_subscription(msg_data):
    _, _, requesting_client, requested_id = msg_data
    requested_client = None
    client_data = {}

    for data in channel_data["All"]:
        if requesting_client in data:
            if data[requesting_client] not in client_data:
                requester_client_id = data[requesting_client]
                client_data[requesting_client] = requester_client_id
        else:
            if requested_id in data.values():
                requested_client = list(data.keys())[0]
                client_data[requested_client] = requested_id

    topic_sub = make_private_channel_for_clients(client_data)
    rich.print(channel_data)
    payload = f"All:{topic_sub}:{requesting_client}:{requested_client}"
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
            if isinstance(obj, dict):
                for _, value in obj.items():
                    if isinstance(value, list):
                        remove_client_from_list(value, name)

    empty_team_list(lst)


def find_lists(name):
    data = channel_data
    for key, value in data.items():
        if isinstance(value, list):
            # if isinstance(value, list) and key != "Private_channels":
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
            _, name, _ = msg_data
            remove_client_from_all_lists(name)
            payload = f"All:{name} left the chat."
            publish_message(payload)
            reply.send(msgpack.packb(""))
        elif "username" in msg_data:
            client_joined_chat(msg_data)
            reply.send(msgpack.packb(""))

        elif "True" in msg_data[0]:
            if len(msg_data) == 4:
                console.print(
                    "\n[bold purple]Picked client to private message.\n"
                    "Sending back pm channel to clients"
                )
                # bool_str, channel, requesting_client, id = msg_data
                payload = prepare_to_make_topic_subscription(msg_data)
                publish_message(payload)
                reply.send(msgpack.packb(""))
            else:
                console.print(
                    "\n[bold purple]Private message requested.\nSending back list"
                )
                # length of msg_data 2 at this point
                # send requesting client list of avaialable clients to DM
                private_message_list = msgpack.packb(channel_data["All"])
                reply.send(private_message_list)
        else:
            channel, client, message = msg_data
            db_insert_data(client, message, channel)
            payload = f"{channel}:{client}:{message}"

            publish_message(payload)
            reply.send(msgpack.packb(""))


asyncio.run(start_tcp_server())
