from db_connect import cnx as db_cnx

cursor = db_cnx.cursor()


def db_find_client(name):
    select = "SELECT Client, ClientID, Team, Squad "
    table = "FROM message_history "
    where = f"WHERE Client='{name}'"
    query = select + table + where
    cursor.execute(query)
    user_data = cursor.fetchall()
    print(user_data)
    print(type(user_data))
    if user_data:
        for data in user_data:
            topics_and_id = []
            for part in data:
                if data[0] != part:
                    topics_and_id.append(part)
            return topics_and_id
        # return user_data
    return False


def db_store_client_data(client_data):
    print(client_data)
    name, id, team, squad = client_data
    columns = "INSERT INTO message_history (Client, ClientID, Team, Squad)"
    data = f" VALUES ('{name}', '{id}', '{team}', '{squad}')"
    query = columns + data
    cursor.execute(query)
    db_cnx.commit()


def db_insert_data(name, message, channel):
    insert_columns = "INSERT INTO message_history (Client, Client_history, Channel)"
    data = f" VALUES ('{name}', '{message}', '{channel}');"
    query = insert_columns + data
    cursor.execute(query)
    db_cnx.commit()
