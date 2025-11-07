from db_connect import cnx as db_cnx

cursor = db_cnx.cursor()


def db_insert_client(client, id):
    if db is not None:
        cursor = db.cursor()
        columns = "INSERT INTO message_history (client, clientID)"
        data = f" VALUES ('{client}', '{id}')"
        query = columns + data
        cursor.execute(query)
        db.commit()


def db_insert_data(client, message, channel):
    if db is not None:
        cursor = db.cursor()
        insert_columns = "INSERT INTO message_history (client, message, Channel)"
        data = f" VALUES ('{client}', '{message}', '{channel}');"
        query = insert_columns + data
        cursor.execute(query)
        db.commit()
