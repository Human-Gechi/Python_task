#importing necessary libraries
import os
import requests
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db_conn import get_connection #importing the get_connection functionn from the db_conn.py file
from datetime import datetime
from dotenv import load_dotenv
from logs import logger #importing the logger variable for logs
load_dotenv()

#url for meking requests
url = "https://zenquotes.io/api/random"

#Maximium number of quotes
maximium_quotes = 100 #Max quotes to be fetched
max_retries = 3 # Number of trials before sending previous quotes

recent_quotes = set() #set object for holding unique quotes

def make_request():
    """
    Makes requests to the zenquotes random quotes endpoint

    Parameters:
        None
    
    Returns:
        Str: Quotes - Author
    
    Raises:
        Request errors - If max attempts have been reached 
        KeyErrors - If Number of Unique quotes is greater than the number.
    """
    #For loop for handling quotes retrieval
    for attempt in range(max_retries):
        try:

            response = requests.get(url, timeout=10) #Making a request to the url and setting a timeout to 10 in cases of internet connectivity issues
            response.raise_for_status() # Raising Http codes, 200 : if OK etc
            data = response.json() #Parsing response to a json object
            quote = f"{data[0]['q']} - {data[0]['a']}" #Quote/Response -> Quote -

            #if statement for handling repetition of quotes
            if quote in recent_quotes: #If statement for checking recent quotes
                logger.debug(f"Duplicate quote fetched; attempt {attempt + 1}") #Duplictaes quoted fetched message and increment for the number of attempts
                if attempt < max_retries - 1: #subtracting the number of entries
                    time.sleep(10) #Time.sleep(10) for timing delays
                    continue

            #Adding the fetched quoted to the set of quotes
            recent_quotes.add(quote)
            if len(recent_quotes) > maximium_quotes: #if the total number of quotes fetched is greater then the max quotes
                try: #try except block
                    recent_quotes.pop() #deleted the most recent quote
                except KeyError:
                    pass #do nothing

            time.sleep(30) #Timing delay before another quote is fetched
            return quote #Return the fetched quote

        except requests.exceptions.RequestException as err:
            logger.info(f"Attempt {attempt + 1} failed: {err}") #Message after the max entries have been reached
            if attempt < max_retries - 1: #Subtracting the trial from the most recent attempt made.
                time.sleep(10)
                continue
     #If statement after all the trials have been exhausted to fetch recent_quotes in the set
    if recent_quotes:
        cached = next(iter(recent_quotes)) #Iterating through the set() of quotes
        logger.info("Using old quotes") #Log message for recent_quotes
        return cached #return cahced quotes
    logger.info("No quotes available from API; Sorry🥺")


def daily_send_email(server, port, sender_email, sender_password):
    """
    Function to send emails to users daily
    
    Parameters:
        server: Google Smtp server
        port: port service
        sender_email : Email of the sender
        sender_password : App password provided by Google
    Returns:
        Sent emails to susbscribed users
    """
    #Calling the function for maving a connection to Aiven DB
    conn = get_connection()
    cursor = None #Setting cursor to None
    try:

        cursor = conn.cursor()
        #execute sql query to select user first_name,email_adresss of active and daily users
        cursor.execute("""
            SELECT first_name, email_address
            FROM users
            WHERE subscription_status = 'Active'
            AND email_frequency = 'Daily'

        """)
        subscribers = cursor.fetchall() #Fecthing all users using .fetchall() metthod

        if not subscribers: #If there are no suscribers in the db:
            logger.info("No active subscribers found for daily emails") #Logger info
            return None #retun None if there are no users/susbsribers

        #Making a connection to the SMTP server
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)

            #looping through the tuple of users in subscribers
            for first_name, recipient_email in subscribers:

                quote = make_request() #Calling the make_request() function to fetch a quote

                msg = MIMEMultipart("alternative")
                msg["From"] = sender_email #Sender
                msg["To"] = recipient_email #Recipient
                msg["Subject"] = "Your Personal Daily Quote from MindFuel"

                email_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color:333333;">
                    <h2>✨ Hello <span style="color:#1A3E5D;">{first_name} 😊</span>!</h2>
                    <p>Here's your inspirational quote of the day:</p>
                    <blockquote style="border-left: 4px solid #919191; padding-left: 10px;">
                        {quote}
                    </blockquote>
                    <p>Stay Cheesed Up 🐥!<br> — Mindfuel Team ^_^ </p>
                </body>
                </html>
                """
                #Email method for sending emails that are not plain text
                msg.attach(MIMEText(email_content, "html"))
                #Try except block
                try:
                    time.sleep(5) #Timing delay before sending an email
                    smtp.sendmail(sender_email, recipient_email, msg.as_string()) #Sending email to receipient
                    print(f"Email successfully sent=======") #Output message for successfully sent emails
                except Exception as e: #Except any errors
                    print(f"Failed to send email=====") #Output message for failures
    except Exception as e:
        logger.info(f"Error during email sending process: {e}")
    finally: #Final block close the connection to db
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def weekly_send_email(server, port, sender_email, sender_password):
    """
    Function to send emails to users Weekly
    
    Parameters:
        server: Google Smtp server
        port: port service
        sender_email : Email of the sender
        sender_password : App password provided by Google

    Returns:
        Sent emails to susbscribed users
    """

    #Calling the function for maving a connection to Aiven DB
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        #execute sql query to select user first_name,email_adresss of active and weekly users
        cursor.execute("""
            SELECT first_name, email_address
            FROM users
            WHERE subscription_status = 'Active'
            AND email_frequency = 'Weekly'
        """)
        subscribers = cursor.fetchall() #Fecthing all users using .fetchall() metthod

        if not subscribers:#If there are no suscribers in the db:
            logger.info("No active subscribers found for weekly emails")#Logger info
            return  #retun None if there are no users/susbsribers

        #Making a connection to the SMTP server
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)

            #looping through the tuple of users in subscribers
            for first_name, recipient_email in subscribers:
                quote = make_request()#Calling the make_request() function to fetch a quote

                msg = MIMEMultipart("alternative")
                msg["From"] = sender_email #sender
                msg["To"] = recipient_email #receiver
                msg["Subject"] = "Your Personal Weekly Quote from Mindfuel" #Email subject

                email_content = f"""
                   <html>
                    <body style="font-family: Arial, sans-serif; color:#333333;">
                        <h2>✨ Hello <span style="color:#1A3E5D;">{first_name} 😊</span>!</h2>
                        <p>Here's your inspirational quote of the week:</p>
                        <blockquote style="border-left: 4px solid #919191; padding-left: 10px;">
                            {quote}
                        </blockquote>
                        <p>Stay Cheesed Up 🐥!<br> — Mindfuel Team ^_^ </p>
                    </body>
                    </html>
                """
                #Email method for sending emails that are not plain text
                msg.attach(MIMEText(email_content, "html"))

                #Try except block
                try:
                    time.sleep(5) #Timing delay before sending an email
                    smtp.sendmail(sender_email, recipient_email, msg.as_string())  #Sending email to receipient
                    print(f"Email successfully sent========") #Output message for successfully quotes sent to the users
                except Exception as e:
                    print(f"Failed to send email: {e}")
    except Exception as e:
        logger.info(f"Error during email sending process: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
#Main funtion or running the functions
def main():

    today = datetime.today() #Fetching today's date
    weekday = today.weekday() #Fetching weekdays

    daily_send_email("smtp.gmail.com", 587, os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD")) #send emails daily

    if weekday == 0: #if weekday() is Monday; Send mails to weekly users
         weekly_send_email("smtp.gmail.com", 587, os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))
main()