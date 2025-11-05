import mysql.connector


def db_connection():
    try:
        cnx = mysql.connector.connect(
            user="root", password="", host="127.0.0.1", database="chat_data"
        )
        if cnx.is_connected():
            print("connnected to mysql database")
            return cnx

    except mysql.connector.Error as e:
        print(e)
