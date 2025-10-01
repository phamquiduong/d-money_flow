import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Root path
BASE_DIR = Path(__file__).resolve().parent.parent


# Load env file
env_file = BASE_DIR / 'configs/.env'
if not load_dotenv(env_file):
    raise FileNotFoundError(f'.env file does not exist: {env_file}')


# MongoDB Connection
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']


# JWT config
SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

ACCESS_EXPIRED = timedelta(minutes=5)
REFRESH_EXPIRED = timedelta(days=1)


# Location
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh')
