#Importing necessary libraties
from dotenv import load_dotenv
import os
import psycopg2
from google.oauth2.service_account import Credentials
import gspread
from logs import logger
from pyhunter import PyHunter


load_dotenv()
#Funtion to make a postgres connection
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
    """
    Funtion to create table users in the postgres db hosted in aiven
    Parameters :
        None
    """
    conn = None
    cursor = None
    try:#Making a connection to the db by calling the get_connection function
        conn = get_connection()
        cursor = conn.cursor()
        logger.info("Database connection is successful") #Log meaasage

        #Dynamic sql for table creation
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
        #executing query
        cursor.execute(create_table_query)
        conn.commit()
        logger.info("Table 'users' has been created successfully") #Log meassgae
    except Exception as e: #Catching exception if any
        logger.exception(f"Error creating table: {e}")

    finally: #final blck of exception
        if cursor:
            cursor.close() #closing cursor
        if conn:
            conn.close() #closing connection to the db
        logger.info("Database connection closed after table creation")
def insert_data(): #Inserting data into the database
    conn = None
    cursor = None
    try: #Getting postgres connection
        conn = get_connection()
        cursor = conn.cursor()
        logger.info("Database connection is successful")
        #Connection to google sheets having user info
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        json_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "Zenquotes/crested-pursuit-457714-c8-f5a68d29f980.json") #service_Account credentials
        creds = Credentials.from_service_account_file(json_path, scopes=scopes)

        authorization = gspread.authorize(creds)

        sheet = authorization.open_by_url(os.getenv("URL"))#opening the url of the form
        worksheet = sheet.sheet1 #Accessing sheet on of the form
        data = worksheet.get_all_values() #Getting all rows from the sheet
        logger.info("Connection to Google Sheets was successful") #log message for successful sheets connection

        rows = data[1:] #Accessing data from the furst row

        for row in rows: #looping through each row
            if len(row) < 5: #column number check
                logger.warning(f"Skipping malformed row (expected 5 columns): {row}") #Log message
                continue
            created_at, first_name, last_name, email_address, emailfrequency = row[:5]
            cursor.execute("SELECT 1 FROM users WHERE email_address = %s;", (email_address,)) #Checking if some email_addresses exist
            exists = cursor.fetchone()

            if not exists:#if they don;t exist in db :insert data
                cursor.execute("""
                    INSERT INTO users (created_at, first_name, last_name, email_address, email_frequency)
                    VALUES (%s, %s, %s, %s, %s)
                """, (created_at, first_name, last_name, email_address, emailfrequency))
                #Message notification if new users were added

                if "@" in email_address:
                    name, domain = email_address.split("@", 1)
                    masked = f"{name[:5]}***@{domain}"
                    logger.info(f"New user added: {masked}")
            else:
                #Log info if the emails addresses are already existing
                if "@" in email_address:
                    name, domain = email_address.split("@", 1)
                    masked = f"{name[:5]}***@{domain}"
                    logger.info(f"User already exists: {masked}")
                else: #elif it has not @symbol but the record was filed with something indicate
                    logger.info(f"User already exists: {email_address}")

        conn.commit() #commiting tranasactions
        logger.info("Data insertion completed successfully.") #logger message

    except Exception as e:
        logger.exception("Error inserting data:") #Error exceptions
    finally:
        if cursor:
            cursor.close() #close the cursor
        if conn:
            conn.close() #close the connection
        logger.info("Database connection was closed after data insertion")

def select_users(): #Select users
    all_users = [] #List to hold all users
    conn = None
    cursor = None
    try: #Making a connection to Postgres db
        conn = get_connection()
        cursor = conn.cursor()
        #Log message for successful database connection
        logger.info("Database connection for selecting users is successful")

        #Selecting first_name of users
        cursor.execute("SELECT first_name FROM users;")
        users = cursor.fetchall() #Fetching all selected names
        for user in users: #looping throught the tuple of users
            if user[0]: #f a user is located
                all_users.append(user[0].strip())#append to the list of all users stripping any backspaces
        return all_users #retrun the list of users

    except Exception as e: #Error messgae if there be an errors
        logger.error(f"An error occurred when selecting users from the database: {e}")
    finally:
        if cursor:
            cursor.close() #close cursor
        if conn:
            conn.close() #close connection
        logger.info("Database connection closed after selecting users") #Log message for successful db closure

def select_user_emails():#Select users
    all_emails = [] #List to hold all email addresses
    conn = None
    cursor = None
    try: #make a connection to the db
        conn = get_connection() #get a connection
        cursor = conn.cursor()
        logger.info("Database connection for selecting email addresses of users is successful") #Log message for successful db connection

        cursor.execute("SELECT email_address FROM users;") #Selecting email_addresses from the table
        emails = cursor.fetchall() #fetching all selected users
        for email_tuple in emails: #looping through the tuple of emails
            if email_tuple[0]:
                all_emails.append(email_tuple[0].strip()) #Appending to the list of emails and stripping for backspaces
    except Exception as e:
        logger.error(f"Error selecting user emails: {e}") #Error message if email selection was unsuccessful
    finally:
        if cursor:
            cursor.close()#Closing the cursor
        if conn:
            conn.close() #closing the connection
        logger.info("Database connection closed after selecting user emails") #db connection closure
    return all_emails

def select_unverified_emails():#selecting unverified emails
    unverified_emails = []
    conn = None
    cursor = None
    try:#Making a conneciton to the db
        conn = get_connection()
        cursor = conn.cursor()
        logger.info("Selecting unverified emails") #Log message indicating the start of selecting unverified emails
        cursor.execute("SELECT email_address FROM users WHERE COALESCE(is_verified, FALSE) = FALSE;") #Slecting emails where is_verified is false
        rows = cursor.fetchall() #Fetching all emails in that category
        for r in rows: #looping through the rows of unverified emails
            if r and r[0]:
                unverified_emails.append(r[0]) #Appending to the list of emails
    except Exception as e:
        logger.exception("Error selecting unverified emails: %s", e) #Error message when selecting a particular email
    finally:
        if cursor:
            cursor.close() #close cursor
        if conn:
            conn.close() #close connection
    return unverified_emails #Retrun the list of unverified emails

def update_user_active_status(email, verification_status):

    accepted_good_status = ('valid') #Email validity status for the Pyhunter email verifier
    is_good = verification_status in accepted_good_status #Check for verification status

    conn = None
    cursor = None
    try:
        conn = get_connection()#get db connection
        cursor = conn.cursor()
        if is_good: #if the email_satus is in is_good which is in accepetd_good_status
            cursor.execute("""
                UPDATE users
                SET
                    is_verified = TRUE,
                    email_verification_date = CURRENT_TIMESTAMP,
                    subscription_status = CASE WHEN subscription_status IS NULL OR subscription_status = 'Inactive' THEN 'Active' ELSE subscription_status END
                WHERE email_address = %s
            """, (email,)) #Verify unverified email_addresses
        else:
            cursor.execute("""
                UPDATE users
                SET
                    is_verified = FALSE
                WHERE email_address = %s
            """, (email,))
        conn.commit()
        logger.info("DB updated for %s -> verified=%s status=%s", email, is_good, verification_status)
    except Exception as e:
        logger.exception("Failed to update verification for %s: %s", email, e)
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def verify_email(api_key):
    hunter = PyHunter(api_key)
    results = []

    emails = select_unverified_emails()
    if not emails:
        logger.info("No unverified emails found to verify")
        return results

    gathered = []
    for email in emails:
        try:
            verification = hunter.email_verifier(email)

            try:
                status = verification.get('status')
            except Exception:
                status = None
            gathered.append((email, status))
        except Exception as e:
            logger.exception("Verification API error for %s: %s", email, e)
            gathered.append((email, None))

    for email, status in gathered:
        try:
            if status is None:
                update_user_active_status(email, 'invalid')
            else:
                update_user_active_status(email, status)
            results.append((email, status))
        except Exception as e:
            logger.exception("Failed to update DB after verification for %s: %s", email, e)
            results.append((email, status))

    return results

if __name__ == "__main__":

    insert_data()
    verify_email(api_key=os.getenv("API_KEY"))
