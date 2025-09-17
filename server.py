import sys

import zmq
import zmq.asyncio
import zmq.utils.monitor
from rich import print

context = zmq.Context()

port = "5556"
port1 = "5557"
print(sys.argv)
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)


channels = ["All", "Team1", "Team2", "Squad"]
channel = channels[0]


def start_tcp_server():
    publisher = context.socket(zmq.PUB)
    route = context.socket(zmq.PULL)
    publisher.bind(f"tcp://localhost:{port1}")
    route.bind(f"tcp://localhost:{port}")
    print(f"Server running on port: {port}")

    while True:
        broadcast = route.recv().decode()
        print(f"type: {type(broadcast)}")
        # print(f"what is broadcast: {broadcast not in ['', ' ']}")
        # if broadcast not in [" ", ""]:  # this isnt working. Look into it
        #     route.send_string("Message received by server!")
        # else:
        #     print(f"what is broadcast: {broadcast}")
        print(f"message from client: {broadcast}")
        publisher.send(f"{channel}, {broadcast}".encode())


start_tcp_server()

# connections = {
#     "All": [],
#     "Team_even": {
#         "All": [],
#         "Squads": {
#             "squad_1": [],
#         },
#     },
#     "Team_odd": {
#         "All": [],
#         "Squads": {"squad_1": []},
#     },
# }

# all_clients = connections['All']
# team_even = connections['Team_even']
# team_odd = connections['Team_odd']
#
# def group_all_clients(client):
#     all_clients.append(client)
#     add_client_to_team(all_clients, client)
#
# def add_client_to_team(all_clients, client):
#     if len(all_clients) % 2 == 0:
#         team_even['All'].append(client)
#         # add_client_to_squad(team_even, client)
#     else:
#         team_odd['All'].append(client)
#         # add_client_to_squad(team_odd, client)
#
# def create_squad_on_current_team(team, id):
#     team['Squads'][f'squad_{id+1}'] = []
#
# A squad is a group of no more than 2 connections
# def add_client_to_squad(team, client):
#     all_squads = team['Squads']

#     current_squad = all_squads[f'squad_{id}']
#
#     if len(current_squad) < 2:
#         current_squad.append(client)
#     else:
#         create_squad_on_current_team(team, id)
#         add_client_to_squad(team, client)

# print(f'How many squads in current team {len(all_squads)}\n')
# print(f'Team Even total: {len(team_even['Team'])}')
# print(f'Team Odd total: {len(team_odd['Team'])}\n')
# print(f'All Clients total: {len(connections['All'])} : '
#         f'{len(connections['All']) == len(team_even['Team']) +
#         len(team_odd['Team'])}')

# tasks = []

# async def echo(connection: socket.socket,  loop: AbstractEventLoop) -> None:
#     try:
#         while data := await loop.sock_recv(connection, 1024):
#             print(f'Data coming in: {data}')
#             message = msgpack.unpackb(data)
#             if message == 'boom':
#                 raise Exception('Unexpected Network Error')
#             disconnected = await handle_client_disconnects(connection, message)
#             if disconnected:
#                 break
# clients = route_message_to_correct_clients
# print(f'clients {clients}')


# clients = [client for client_obj in all_clients
#                     for client in list(client_obj.keys())
#                         if not client == connection]


# for client in clients:
#     print(f'WHO IS SENDING: {connection}')
#     await loop.sock_sendall(client, data)
#     print(f'WHO JUST RECEIVED: {client}')

# for client_obj in all_clients:
#     print(client_obj)
#     for client in list(client_obj.keys()):
#         if not client == connection:
#             print(f'WHO IS SENDING: {connection}')
#             await loop.sock_sendall(client, data)
#             print(f'WHO JUST RECEIVED: {client}')


# for client in all_clients:
#     if not client == connection:
#         print(f'WHO IS SENDING: {connection}')
#         await loop.sock_sendall(client, data)
#         print(f'WHO JUST RECEIVED: {client}')

# except Exception as ex:
#     logging.exception(ex)
# finally:
#     connection.close()
#     if connection in connections:
#         connections['All'].remove(connection)

# async def accept_connections(server_socket, loop: AbstractEventLoop):
#     while True:
#         print('before await')
#         connection = server_socket.poll()
#         print('after await')
#         print(connection)
# c_conn, c_address = await loop.sock_accept(server_socket)
# c_conn.setblocking(False)
# print(f'\nConnection accepted:\n{c_conn} from {c_address}\n')
# group_all_clients({c_conn: {'channel': 'all'}})
#
# task = create_task(echo(c_conn, loop))
# tasks.append(task)

# async def handle_client_disconnects(client, message):
#     if message == 'q' or message == 'quit':
#         print('\nClient wants to disconnect.')
#         print('About to close client connection.')
#         client.close()
#         if client in connections:
#             connections['All'].remove(client)
#         print('\nClient Disconnected')
#         print(f'You are connected to {len(connections["All"])} client(s)')
#         return True
#     return False

# class GracefulExit(SystemExit):
#     pass
#
# def shutdown():
#     raise GracefulExit()

# async def close_tasks(tasks: list[asyncio.Task]):
#     waiters = [wait_for(task, 2) for task in tasks]
#     for task in waiters:
#         try:
#             await task
#         except asyncio.exceptions.TimeoutError:
#             # Expect a timeout error here
#             ('Did I hit the Timeout Error--!')
#             pass

# asyncio.run(start_tcp_server(), debug=True)

# topic = random.choice(channels)
# print(topic)
# received_msg = route.recv()
# socket.send(f'{topic}, {received_msg}')
# topic = random.randrange(9999,10005)
# messagedata = random.randrange(1,215) - 80
# print ("%d %d" % (topic, messagedata))
# print(f'{topic} {messagedata}')
# socket.send_string(f'{topic}, {messagedata}')
# socket.send_string("%d %d" % (topic, messagedata))

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server_socket.setblocking(False)

# server_address = ('127.0.0.1', 8000)
# server_socket.bind(server_address)
# server_socket.listen(5)
# _, PORT = server_address
# print(f"Server running on port: {PORT}")

# for signame in {'SIGINT', 'SIGTERM'}:
#     loop.add_signal_handler(getattr(signal, signame), shutdown)
# await accept_connections(server_socket, asyncio.get_event_loop())

# loop = asyncio.new_event_loop()

# asyncio.run(start_tcp_server(), debug=True)
# try:
#     loop.run_until_complete(main())
# except GracefulExit:
#     loop.run_until_complete(close_tasks(tasks))
# finally:
#     loop.close()
