import os
import logging


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

log_file_path = os.path.join(parent_dir, 'email_logs.log')

logging.basicConfig(
    filename=log_file_path,
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
