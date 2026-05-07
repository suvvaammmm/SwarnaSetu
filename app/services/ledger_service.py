from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.database import client, db
from bson import ObjectId

accounts_collection = db["accounts"]
transactions_collection = db["transactions"]
ledger_collection = db["ledger_entries"]

async def post_transaction(entries: list, txn_type: str, description: str):
    """
    entries = [
        {"account_id": "acc_user_1", "type": "debit", "amount": 10},
        {"account_id": "acc_gold_pool", "type": "credit", "amount": 10}
    ]
    """

    total_debit = sum(e["amount"] for e in entries if e["type"] == "debit")
    total_credit = sum(e["amount"] for e in entries if e["type"] == "credit")

    if total_debit != total_credit:
        raise Exception("Transaction not balanced!")

    session = await client.start_session()

    async with session.start_transaction():
        txn = {
            "type": txn_type,
            "description": description,
            "created_at": datetime.utcnow()
        }

        txn_result = await transactions_collection.insert_one(txn, session=session)
        txn_id = txn_result.inserted_id

        for entry in entries:
            ledger_entry = {
                "transaction_id": txn_id,
                "account_id": entry["account_id"],
                "entry_type": entry["type"],
                "amount": entry["amount"],
                "created_at": datetime.utcnow()
            }

            await ledger_collection.insert_one(ledger_entry, session=session)

            # Update balance
            if entry["type"] == "debit":
                await accounts_collection.update_one(
                    {"_id": entry["account_id"]},
                    {"$inc": {"balance": -entry["amount"]}},
                    session=session
                )
            else:
                await accounts_collection.update_one(
                    {"_id": entry["account_id"]},
                    {"$inc": {"balance": entry["amount"]}},
                    session=session
                )

    await session.end_session()

    return str(txn_id)
