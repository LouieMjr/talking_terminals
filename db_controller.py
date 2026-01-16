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


# rename to get client data
def db_get_client_data(name):
    select = "SELECT Client, ClientID "
    table = "FROM message_history "
    where = f"WHERE Client='{name}'"
    query = select + table + where
    cursor.execute(query)
    user_data_list = cursor.fetchall()
    user_data = user_data_list[0]
    client_name_and_id = {user_data[0]: str(user_data[1])}
    return client_name_and_id


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


def db_store_client_chat_history(name, message):
    table = "UPDATE message_history "
    update = f"SET Client_history = CONCAT_WS(':', Client_history, '{message}') "
    where = f"WHERE Client='{name}'"
    query = table + update + where
    cursor.execute(query)
    db_cnx.commit()


def db_update_online_status(name):
    select = "SELECT Online "
    table = "FROM message_history "
    where = f"WHERE Client='{name}'"
    select_query = select + table + where
    cursor.execute(select_query)
    data = cursor.fetchall()

    online_status = data[0][0]
    new_status = "T" if online_status == "F" else "F"
    table = "UPDATE message_history "
    update = f"SET Online = '{new_status}' "
    update_query = table + update + where
    cursor.execute(update_query)
    db_cnx.commit()
