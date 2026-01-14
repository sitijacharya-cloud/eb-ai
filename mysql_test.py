import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nepal@2001",
        database="vector_db"
    )

    if conn.is_connected():
        print("Connected to MySQL database")

        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        print(cursor.fetchall())  # should show [('documents',)]

except Error as e:
    print("Error while connecting:", e)

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("MySQL connection closed")
