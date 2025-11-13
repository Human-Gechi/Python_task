import os
import logging

#Parent directoy path location
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#Joining parent directory to log file
log_file_path = os.path.join(parent_dir, 'email_logs.log')

#Log file configuration
logging.basicConfig(
    filename=log_file_path,
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
#Assign variable logger to the log file
logger = logging.getLogger(__name__)
