import os

from dotenv import load_dotenv

if not load_dotenv():
    raise FileNotFoundError('.env file is not exist')


MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']
