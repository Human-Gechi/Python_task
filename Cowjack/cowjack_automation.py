import requests
from jira import JIRA
import supabase
import os
from dotenv import load_dotenv

load_dotenv()
#Making a connection to my Jira workspace
jira_connection = JIRA(
                    server=os.getenv("JIRA_SERVER"),
                    basic_auth=(os.getenv("SENDER_EMAIL"), os.getenv("JIRA_API_KEY"))
                        )
try:
    #Successful connection
    user = jira_connection.current_user()
    print(f"Connection successful! Logged in as: {user}")
except Exception as e:
    print("Connection failed:", e)
