import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="flaskuser",
        password="password123",
        database="incident_db"
    )

