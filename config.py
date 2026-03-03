import os
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "pyuser"),
        password=os.getenv("DB_PASSWORD", "py123"),
        database=os.getenv("DB_NAME", "pypro")
    )
