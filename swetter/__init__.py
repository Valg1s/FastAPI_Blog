import os

from dotenv import load_dotenv, find_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv(find_dotenv())

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

scheduler = BackgroundScheduler()
