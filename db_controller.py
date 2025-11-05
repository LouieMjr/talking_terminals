from db_connect import db_connection

db = db_connection()


def db_insert_data(client, message, channel):
    if db is not None:
        cursor = db.cursor()
        insert_columns = "INSERT INTO message_history (client, message, Channel)"
        data = f" VALUES ('{client}', '{message}', '{channel}');"
        query = insert_columns + data
        cursor.execute(query)
        db.commit()
