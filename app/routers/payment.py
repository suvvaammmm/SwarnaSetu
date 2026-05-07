# app/routers/payment.py

from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.database import payments_collection, db, user_settings_collection
from app.services.suggestion_engine import calculate_rounding
from app.services.ledger_service import post_transaction
from app.services.investment_service import create_pending_investment

router = APIRouter()

accounts_collection = db["accounts"]


# ------------------------------------------------
# WALLET TOP-UP
# ------------------------------------------------

@router.post("/topup")
async def wallet_topup(user_id: str, amount: float):

    user_account_id = f"acc_user_{user_id}"

    user_account = await accounts_collection.find_one({"_id": user_account_id})

    if not user_account:
        raise HTTPException(status_code=404, detail="User wallet not found")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    # Escrow → Wallet
    txn_id = await post_transaction(
        entries=[
            {"account_id": "acc_platform_escrow", "type": "debit", "amount": amount},
            {"account_id": user_account_id, "type": "credit", "amount": amount}
        ],
        txn_type="topup",
        description="Wallet top-up"
    )

    return {
        "message": "Wallet topped up successfully",
        "transaction_id": txn_id,
        "amount": amount
    }


# ------------------------------------------------
# PAYMENT + SPARE CHANGE INVESTMENT
# ------------------------------------------------

@router.post("/pay")
async def make_payment(user_id: str, merchant_upi: str, amount: float):

    rounding_data = calculate_rounding(amount)
    spare_change = rounding_data["spare"]

    user_account_id = f"acc_user_{user_id}"

    user_account = await accounts_collection.find_one({"_id": user_account_id})

    if not user_account:
        raise HTTPException(status_code=404, detail="User wallet not found")

    # ------------------------------------------------
    # CHECK USER SETTINGS
    # ------------------------------------------------

    settings = await user_settings_collection.find_one({"_id": f"user_{user_id}"})

    investment_mode = "auto"

    if settings:
        investment_mode = settings.get("investment_mode", "auto")

    # ------------------------------------------------
    # AUTO INVESTMENT MODE
    # ------------------------------------------------

    if investment_mode == "auto":

        if user_account["balance"] < spare_change:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")

        txn_id = await post_transaction(
            entries=[
                {"account_id": user_account_id, "type": "debit", "amount": spare_change},
                {"account_id": "acc_gold_pool", "type": "credit", "amount": spare_change}
            ],
            txn_type="investment",
            description="Spare change investment"
        )

        ledger_txn = txn_id
        pending_id = None

    # ------------------------------------------------
    # MANUAL INVESTMENT MODE
    # ------------------------------------------------

    else:

        pending_id = await create_pending_investment(user_id, spare_change)

        ledger_txn = None

    # ------------------------------------------------
    # STORE PAYMENT RECORD
    # ------------------------------------------------

    payment_doc = {
        "user_id": user_id,
        "merchant_upi": merchant_upi,
        "original_amount": rounding_data["original"],
        "rounded_amount": rounding_data["rounded"],
        "spare_change": spare_change,
        "investment_mode": investment_mode,
        "ledger_transaction_id": ledger_txn,
        "pending_investment_id": pending_id,
        "status": "success",
        "created_at": datetime.utcnow()
    }

    result = await payments_collection.insert_one(payment_doc)

    return {
        "message": "Payment processed",
        "payment_id": str(result.inserted_id),
        "investment_mode": investment_mode,
        "rounding": rounding_data
    }