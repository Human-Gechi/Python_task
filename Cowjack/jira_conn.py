import os
import psycopg2
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import logging
import time
from logs import logger
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()  # Load environment variables

class PhoneRequestHandler:
    def __init__(self, db_conn, jira_server, jira_email, jira_api_token, serviceDeskId, requestTypeId):
        self.conn = db_conn
        self.jira_server = jira_server
        self.jira_email = jira_email
        self.jira_api_token = jira_api_token
        self.serviceDeskId = serviceDeskId
        self.requestTypeId = requestTypeId
    def fetch_new_requests(self):
        """Funtion to fetch unprocessed phone requests from database"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_schema, table_name 
                    FROM information_schema.tables 
                    WHERE table_name ILIKE 'phonerequest'
                """)
                tables = cursor.fetchall()
                logger.info(f"Found tables: {tables}")

                query = """
                    SELECT
                        newusername,
                        samplename,
                        phonenumber,
                        departmentname,
                        job,
                        emailaddress,
                        costcenter,
                        telephonelinesandinstallations,
                        handsetsandheadsets,
                        timeframe,
                        dateneededby,
                        createdat
                    FROM public.phonerequest;
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.error(f" Error fetching requests: {e}")
            return []

class JiraAutomation:
    def __init__(self):
        """Initializing database and Jira connections"""
        # PostgreSQL Configuration
        self.db_config = {
            'host': os.getenv('HOST'),
            'port': os.getenv('PORT', '6543'),
            'database': os.getenv('DBNAME'),
            'user': os.getenv('USERNAME'),
            'password': os.getenv('DBPASSWORD')
        }

        # Jira SETUP
        self.jira_server = os.getenv('JIRA_SERVER')
        self.jira_email = os.getenv('JIRA_EMAIL')
        self.jira_api_token = os.getenv('JIRA_API_KEY')

        self.serviceDeskId = os.getenv('SERVICE_DESK_ID', '1')
        self.requestTypeId = os.getenv('REQUEST_TYPE_ID', '1')

        self.db_conn = None
        self.connect_db()

        self.handler = PhoneRequestHandler(
            self.db_conn,
            self.jira_server,
            self.jira_email,
            self.jira_api_token,
            self.serviceDeskId,
            self.requestTypeId
        )

    def connect_db(self):
        """Funtion to make a connection to PostgreSQL"""
        try:
            self.db_conn = psycopg2.connect(**self.db_config)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
