import requests
from jira import JIRA
import os
from dotenv import load_dotenv
from logs import logger
import psycopg2

load_dotenv()

def db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
            database=os.getenv("DBNAME"),
            user=os.getenv("USERNAME"),
            password=os.getenv("DBPASSWORD")
        )
        logger.info("Connection to the database successfully!")
        return conn
    except Exception as e:
        logger.info(f"Failed to connect to the database: {e}")
        print("Failed to connect to the database")
        return None
db_connection()

def select_users():
    conn = db_connection()
    cursor = conn.cursor()
    users_list = []
    cursor.execute("SELECT * FROM phonerequest")
    users = cursor.fetchall()

    for user in users:
        users_list.append(user[0].strip())
    logger.info("Selection of users was successful")

if __name__ == "__main":
    select_users()
