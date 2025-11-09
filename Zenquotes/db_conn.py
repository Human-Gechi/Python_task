from dotenv import load_dotenv
import os
import psycopg2
from google.oauth2.service_account import Credentials
import gspread
from logs import logger
from pyhunter import PyHunter


load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )

def create_users_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        logger.info("Database connection is successful")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP,
            first_name TEXT,
            last_name TEXT,
            email_address TEXT UNIQUE,
            email_frequency TEXT CHECK (email_frequency IN ('Daily', 'Weekly')),
            subscription_status TEXT CHECK (subscription_status IN ('Active', 'Inactive')) DEFAULT 'Active'
        );
        """

        cursor.execute(create_table_query)
        conn.commit()
        logger.info("Table 'users' has been created successfully")
    except Exception as e:
        logger.exception(f"Error creating table: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Database connection closed after table creation")
def insert_data():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        logger.info("Database connection is successful")

        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), scope=scope)


        authorization = gspread.authorize(creds)

        sheet = authorization.open_by_url(os.getenv("URL"))
        worksheet = sheet.sheet1
        data = worksheet.get_all_values()
        logger.info("Connection to Google Sheets was successful")

        rows = data[1:]

        for row in rows:
            created_at, first_name, last_name, email_address, emailfrequency = row
            cursor.execute("SELECT * FROM users WHERE email_address = %s;", (email_address,))
            exists = cursor.fetchall()

            if not exists:
                cursor.execute("""
                    INSERT INTO users (created_at, first_name, last_name, email_address, email_frequency)
                    VALUES (%s, %s, %s, %s, %s)
                """, (created_at, first_name, last_name, email_address, emailfrequency))
                if "@" in email_address:
                    name, domain = email_address.split("@")
                    email_address = f"{name[:5]}***@{domain}"
                    logger.info(f"New user added: {email_address}")
            else:
                if "@" in email_address:
                    name, domain = email_address.split("@")
                    email_address = f"{name[:5]}***@{domain}"
                    logger.info(f"User already exists: {email_address}")
                else:
                    logger.info(f"User already exists: {email_address}")

        conn.commit()
        logger.info("Data insertion completed successfully.")

    except Exception as e:
        logger.exception("Error inserting data:")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Database connection was closed after data insertion")

def select_users():
    all_users = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        logger.info("Database connection for selecting users is successful")

        cursor.execute("SELECT first_name FROM users;")
        users = cursor.fetchall()
        for user in users:
            if user[0]:
                all_users.append(user[0].strip())
        return all_users

    except Exception as e:
        logger.error(f"An error occurred when selecting users from the database: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Database connection closed after selecting users")

def select_user_emails():
    all_emails = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        logger.info("Database connection for selecting email addresses of users is successful")

        cursor.execute("SELECT email_address FROM users;")
        emails = cursor.fetchall()
        for email_tuple in emails:
            if email_tuple[0]:
                all_emails.append(email_tuple[0].strip())
        return all_emails
    except Exception as e:
        logger.error(f"Error selecting user emails: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Database connection closed after selecting user emails")


def verify_email(api_key):
    hunter = PyHunter(api_key)
    results = []
    for email in select_user_emails():
        try:
            email_verify = hunter.email_verifier(email)
            status = email_verify.get('status') if isinstance(email_verify, dict) else None
            results.append((email, status))
        except Exception as e:
            logger.exception(f"Error verifying {email}: {e}")
            results.append((email, None))
            continue
    return results

def update_user_active_status(api_key=None):
    if api_key is None:
        api_key = os.getenv("API_KEY")
    verifications = verify_email(api_key)
    if not verifications:
        logger.info("No emails to verify.")
        return
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for email, status in verifications:
            if status == "invalid" or status is None:
                try:
                    cursor.execute(
                        """
                        UPDATE users
                        SET subscription_status = 'Inactive'
                        WHERE email_address = %s;
                        """,
                        (email,)
                    )
                    conn.commit()
                    logger.info(f"Updated subscription_status to Inactive for {email}")
                except Exception as e:
                    logger.exception(f"Error updating status for {email}: {e}")
    except Exception as e:
        logger.exception(f"Database error while updating stats: {e}")
    finally:
       if cursor:
           cursor.close()
       if conn:
           conn.close()
    logger.info("Database connection closed after updating user suscription_status")


insert_data()
