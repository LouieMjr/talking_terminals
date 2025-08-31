import asyncio, socket, msgpack, logging, signal
from asyncio import AbstractEventLoop, create_task, wait_for

connections = {
    'All': [],
    'Team_even': {
        'Team': [],
        'Squads': {
            'squad_1': [],

        },
    },
    'Team_odd': {
        'Team': [],
        'Squads': {
            'squad_1': []

        },
    },
}

team_even = connections['Team_even']
team_odd = connections['Team_odd']

def group_all_clients(connections, connection):
    connections.append(connection)
    separate_clients_into_teams(connections, connection)

def separate_clients_into_teams(all_clients, client):
    if len(all_clients) % 2 == 0:
        team_even['Team'].append(client)
        group_clients_into_squads_of_two(team_even, client)
    else:
        team_odd['Team'].append(client)
        group_clients_into_squads_of_two(team_odd, client)

    print(f'Team Even total: {len(team_even['Team'])}')
    print(f'Team Odd total: {len(team_odd['Team'])}')
    print(f'All Clients total: {len(all_clients)} : '
            f'{len(all_clients) == len(team_even['Team']) +
            len(team_odd['Team'])}')


def create_squad(team, id):
    team['Squads'][f'squad_{id}'] = []
    # squad = team['Squads'][f'squad_{id}']
    # return squad

def group_clients_into_squads_of_two(team, client):
    all_squads = team['Squads']
    id = len(all_squads)
    print('len of all squads', id)

    # for squad in all_squads.values():
    #     if len(squad) < 2:
    #         squad.append(client)
    #         print('is this hitting', squad)
    #     else:
    #         create_squad(team, id)

tasks = []

async def echo(connection: socket.socket, loop: AbstractEventLoop) -> None:
    try:
        while data := await loop.sock_recv(connection, 1024):
            print(f'Data coming in: {data}')
            message = msgpack.unpackb(data)
            if message == 'boom':
                raise Exception('Unexpected Network Error')
            disconnected = await handle_client_disconnects(connection, message)
            if disconnected:
                break
            for client in connections['All']:
                if not client == connection:
                    await loop.sock_sendall(client, data)
    except Exception as ex:
        logging.exception(ex)
    finally:
        connection.close()
        if connection in connections:
            connections['All'].remove(connection)

async def accept_connections(server_socket: socket.socket, loop: AbstractEventLoop):
    while True:
        c_conn, c_address = await loop.sock_accept(server_socket)
        c_conn.setblocking(False)
        print(f'\nConnection accepted {c_conn} from {c_address}\n')
        group_all_clients(connections['All'], c_conn)
        print(f'Connected to {len(connections["All"])} client(s)')
        task = create_task(echo(c_conn, loop))
        tasks.append(task)

async def handle_client_disconnects(client, message):
    if message == 'q' or message == 'quit':
        print('\nClient wants to disconnect.')
        print('About to close client connection.')
        client.close()
        if client in connections:
            connections['All'].remove(client)
        print('\nClient Disconnected')
        print(f'You are connected to {len(connections["All"])} client(s)')
        return True
    return False

class GracefulExit(SystemExit):
    pass

def shutdown():
    raise GracefulExit()

async def close_tasks(tasks: list[asyncio.Task]):
    waiters = [wait_for(task, 2) for task in tasks]
    for task in waiters:
        try:
            await task
        except asyncio.exceptions.TimeoutError:
            # Expect a timeout error here
            print('Did I hit the Timeout Error--!')
            pass

async def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(False)

    server_address = ('127.0.0.1', 8000)
    server_socket.bind(server_address)
    server_socket.listen(5)
    _, PORT = server_address
    print(f"Server running on port: {PORT}")

    for signame in {'SIGINT', 'SIGTERM'}:
        loop.add_signal_handler(getattr(signal, signame), shutdown)
    await accept_connections(server_socket, asyncio.get_event_loop())

loop = asyncio.new_event_loop()

async def main():
   await start_tcp_server()

try:
    loop.run_until_complete(main())
except GracefulExit:
    loop.run_until_complete(close_tasks(tasks))
finally:
    loop.close()

# asyncio.run(main(), debug=True)
