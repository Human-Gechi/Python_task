from dotenv import load_dotenv
from logs import logger
import psycopg2

load_dotenv()

def db_connection():
    try:
        conn = psycopg2.connect(
            host=("aws-1-eu-west-2.pooler.supabase.com"),
            port=6543,
            database=("postgres"),
            user=("postgres.tykuknkebjhzenngzujf"),
            password=("cowjacketdec")
        )
        logger.info("Connection to the database successfully!")
        return conn
    except Exception as e:
        logger.info(f"Failed to connect to the database: {e}")
        print("Failed to connect to the database")
        return None

def select_users():
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM phonerequest")
    users = [row[0] for row in cursor.fetchall()]

    conn.close()
    logger.info(f"{len(users)} users were retrieved")
    return users
if __name__ == "__main__":
    select_users()
