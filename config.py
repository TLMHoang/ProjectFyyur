import os

from dotenv import load_dotenv

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_SERVICE_NAME = os.getenv('DB_SERVICE_NAME')
# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_SERVICE_NAME, DB_NAME)
