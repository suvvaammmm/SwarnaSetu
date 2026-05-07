from datetime import datetime
from app.database import pending_investments_collection

async def create_pending_investment(user_id, amount):

    investment_doc = {
        "user_id": user_id,
        "amount": amount,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = await pending_investments_collection.insert_one(investment_doc)

    return str(result.inserted_id)