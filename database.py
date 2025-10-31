import mysql.connector

cnx = None
cursor = None

try:
    cnx = mysql.connector.connect(
        user="root", password="", host="127.0.0.1", database="menagerie"
    )
    if cnx.is_connected():
        print("connnected to mysql database")

    cursor = cnx.cursor()
    query = "SELECT * from pet"
    cursor.execute(query)
    row = cursor.fetchone()

    while row is not None:
        print(row)
        row = cursor.fetchone()

except mysql.connector.Error as e:
    print(e)

finally:
    if cursor:
        cursor.close()
        print("cursor closed")
    if cnx:
        cnx.close()
        print("database connection closed")
