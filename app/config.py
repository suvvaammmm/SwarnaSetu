import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = "roundpay"
print("MONGO URL Loaded: ",MONGO_URL)