import os
import requests
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db_conn import get_connection
from datetime import datetime
from dotenv import load_dotenv
from logs import logger
load_dotenv()

url = "https://zenquotes.io/api/random"
recent_quotes = set()
max_quotes = 50
max_retries = 3

def make_request():
    global recent_quotes

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            quote = f"{data[0]['q']} - {data[0]['a']}"

            if quote in recent_quotes and attempt < max_retries - 1:
                time.sleep(1)
                continue
            recent_quotes.add(quote)

            if len(recent_quotes) > max_quotes:
                recent_quotes = set(list(recent_quotes)[-max_quotes:])

            return quote

        except requests.exceptions.RequestException as err:
            logger.info(f"Attempt {attempt + 1} failed: {err}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

def daily_send_email(server, port, sender_email, sender_password):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT first_name, email_address 
            FROM users 
            WHERE subscription_status = 'Active'
            AND email_frequency = 'Daily'
        """)
        subscribers = cursor.fetchall()

        if not subscribers:
            logger.info("No active subscribers found for daily emails")
            return


        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)

            for first_name, recipient_email in subscribers:

                quote = make_request()

                msg = MIMEMultipart("alternative")
                msg["From"] = sender_email
                msg["To"] = recipient_email
                msg["Subject"] = "Your Personal Daily Quote from ThriveWell"

                email_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2>✨ Hello <span style="color:#008080;">{first_name} 😊</span>!</h2>
                    <p>Here's your inspirational quote of the day:</p>
                    <blockquote style="border-left: 4px solid #0078D7; padding-left: 10px;">
                        {quote}
                    </blockquote>
                    <p>Stay Cheered Up 🐥!<br>— ThriveWell Team ;)</p>
                </body>
                </html>
                """

                msg.attach(MIMEText(email_content, "html"))

                try:
                    time.sleep(5)
                    smtp.sendmail(sender_email, recipient_email, msg.as_string())
                    print(f"Email successfully sent to {recipient_email}")
                except Exception as e:
                    print(f"Failed to send to {recipient_email}: {e}")
    except Exception as e:
        logger.info(f"Error during email sending process: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def weekly_send_email(server, port, sender_email, sender_password):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT first_name, email_address 
            FROM users 
            WHERE subscription_status = 'Active'
            AND email_frequency = 'Weekly'
        """)
        subscribers = cursor.fetchall()

        if not subscribers:
            logger.info("No active subscribers found for daily emails")
            return


        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)

            for first_name, recipient_email in subscribers:
                quote = make_request()

                msg = MIMEMultipart("alternative")
                msg["From"] = sender_email
                msg["To"] = recipient_email
                msg["Subject"] = "Your Personal Daily Quote from ThriveWell"

                email_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2>✨ Hello <span style="color:#008080;">{first_name} 😊</span>!</h2>
                    <p>Here's your inspirational quote of the day:</p>
                    <blockquote style="border-left: 4px solid #0078D7; padding-left: 10px;">
                        {quote}
                    </blockquote>
                    <p>Stay Cheered Up 🐥!<br>— ThriveWell Team ;)</p>
                </body>
                </html>
                """

                msg.attach(MIMEText(email_content, "html"))

                try:
                    time.sleep(5)
                    smtp.sendmail(sender_email, recipient_email, msg.as_string())
                    print(f"Email successfully sent to {recipient_email}")
                except Exception as e:
                    print(f"Failed to send to {recipient_email}: {e}")
    except Exception as e:
        logger.info(f"Error during email sending process: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():

    today = datetime.today()
    weekday = today.weekday()

    daily_send_email("smtp.gmail.com", 587, os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))

    if weekday == 0:
        weekly_send_email("smtp.gmail.com", 587, os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))
main()