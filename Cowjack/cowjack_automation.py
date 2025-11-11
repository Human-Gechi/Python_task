import requests
from jira import JIRA
import supabase
import os
from dotenv import load_dotenv
from logs import logger
load_dotenv()
#Making a connection to my Jira workspace
jira_connection = JIRA(
                    server=os.getenv("JIRA_SERVER"),
                    basic_auth=(os.getenv("SENDER_EMAIL"), os.getenv("JIRA_API_KEY"))
                        )
try:
    #Successful connection
    user = jira_connection.current_user()
    logger.info(f"Connection successful! Logged in as: {user}")
except Exception as e:
    logger.info("Connection failed:", e)

def supabase_conn():
    pass
