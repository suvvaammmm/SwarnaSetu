import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise Exception("MONGO_URL not found in .env file")

print("MONGO URL Loaded:", MONGO_URL)

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URL)

# Database
db = client["roundpay"]

# Collections
accounts_collection = db["accounts"]
payments_collection = db["payments"]
ledger_collection = db["ledger_entries"]
transactions_collection = db["transactions"]
user_settings_collection = db["user_settings"]
pending_investments_collection = db["pending_investments"]
user_investments_collection = db["user_investments"]