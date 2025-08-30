import asyncio, socket, msgpack, logging, signal
from asyncio import AbstractEventLoop, create_task, wait_for

connections = []
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
            for client in connections:
                if not client == connection:
                    await loop.sock_sendall(client, data)
    except Exception as ex:
        logging.exception(ex)
    finally:
        connection.close()
        if connection in connections:
            connections.remove(connection)

async def accept_connections(server_socket: socket.socket, loop: AbstractEventLoop):
    while True:
        c_conn, c_address = await loop.sock_accept(server_socket)
        c_conn.setblocking(False)
        print('\nConnection accepted' , c_conn, 'from', c_address)
        connections.append(c_conn)
        print(f'Connected to {len(connections)} client(s)')
        task = create_task(echo(c_conn, loop))
        tasks.append(task)

async def handle_client_disconnects(client, message):
    if message == 'q' or message == 'quit':
        print('\nClient wants to disconnect.')
        print('About to close client connection.')
        client.close()
        if client in connections:
            connections.remove(client)
        print('\nClient Disconnected')
        print(f'You are connected to {len(connections)} client(s)')
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
