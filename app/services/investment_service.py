from datetime import datetime

from app.database import (
    pending_investments_collection,
    user_investments_collection
)

from app.services.gold_price_service import (
    get_live_gold_price
)


# ------------------------------------------------
# CREATE PENDING INVESTMENT
# ------------------------------------------------

async def create_pending_investment(
    user_id,
    amount
):

    investment_doc = {
        "user_id": user_id,
        "amount": amount,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = await pending_investments_collection.insert_one(
        investment_doc
    )

    return str(result.inserted_id)


# ------------------------------------------------
# UPDATE USER INVESTMENT
# ------------------------------------------------

async def update_user_investment(
    user_id: str,
    amount: float
):

    # FETCH LIVE GOLD PRICE
    gold_price = get_live_gold_price()

    # CALCULATE GOLD GRAMS
    gold_grams = amount / gold_price

    existing = await user_investments_collection.find_one({
        "_id": user_id
    })

    # ------------------------------------------------
    # UPDATE EXISTING USER
    # ------------------------------------------------

    if existing:

        await user_investments_collection.update_one(
            {"_id": user_id},
            {
                "$inc": {
                    "total_invested": amount,
                    "gold_grams": gold_grams
                }
            }
        )

    # ------------------------------------------------
    # CREATE NEW USER PORTFOLIO
    # ------------------------------------------------

    else:

        doc = {
            "_id": user_id,
            "total_invested": amount,
            "gold_grams": gold_grams,
            "created_at": datetime.utcnow()
        }

        await user_investments_collection.insert_one(doc)