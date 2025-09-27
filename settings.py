import os
from datetime import timedelta

from dotenv import load_dotenv

if not load_dotenv():
    raise FileNotFoundError('.env file is not exist')


MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

TIMEZONE = os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh')

ACCESS_EXP = timedelta(minutes=5)
REFRESH_EXP = timedelta(days=1)
