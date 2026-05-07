from app.database import accounts_collection
from datetime import datetime

async def create_system_account(account_id: str):
    existing = await accounts_collection.find_one({"_id": account_id})
    if not existing:
        await accounts_collection.insert_one({
            "_id": account_id,
            "type": "system",
            "balance": 0,
            "currency": "INR",
            "created_at": datetime.utcnow()
        })

async def initialize_system_accounts():
    await create_system_account("acc_platform_escrow")
    await create_system_account("acc_gold_pool")