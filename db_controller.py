from db_connect import cnx as db_cnx

cursor = db_cnx.cursor()


def db_does_client_exist(name):
    select = "SELECT Client "
    table = "FROM message_history "
    where = f"WHERE Client='{name}'"
    query = select + table + where
    cursor.execute(query)
    user_data = cursor.fetchall()
    if user_data:
        return True
    return False


def db_store_client_data(client_data):
    name, id, team, squad = client_data
    columns = "INSERT INTO message_history (Client, ClientID)"
    data = f" VALUES ('{name}', '{id}')"
    query = columns + data
    cursor.execute(query)
    db_cnx.commit()


def db_insert_data(name, message, channel):
    insert_columns = "INSERT INTO message_history (Client, Client_history, Channels)"
    data = f" VALUES ('{name}', '{message}', '{channel}');"
    query = insert_columns + data
    cursor.execute(query)
    db_cnx.commit()
