import asyncio, socket, msgpack, logging, signal
from asyncio import AbstractEventLoop, create_task, wait_for

connections = []

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
        create_task(echo(c_conn, loop))

async def handle_client_disconnects(client, message):
    if message == 'q' or message == 'quit':
        client.close()
        connections.remove(client)
        print('\nClient Disconnected')
        print(f'You are connected to {len(connections)} client(s)')
        return True
    return False



async def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(False)
    server_address = ('127.0.0.1', 8000)
    server_socket.bind(server_address)
    server_socket.listen(5)
    _, PORT = server_address
    print(f"Server running on port: {PORT}")

    await accept_connections(server_socket, asyncio.get_event_loop())

async def main():
   await start_tcp_server()

asyncio.run(main(), debug=True)
