# app/routers/payment.py

from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.database import payments_collection, db, user_settings_collection
from app.services.suggestion_engine import calculate_rounding
from app.services.ledger_service import post_transaction
from app.services.investment_service import create_pending_investment
from app.services.investment_service import update_user_investment
from app.database import user_investments_collection
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()

accounts_collection = db["accounts"]
users_collection = db["users"]


# ------------------------------------------------
# WALLET TOP-UP
# ------------------------------------------------

@router.post("/topup")
async def wallet_topup(user_id: str, amount: float):

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    # Find user
    user_account = await accounts_collection.find_one({"_id": user_id})

    if not user_account:
        raise HTTPException(status_code=404, detail="User wallet not found")

    # Current balance
    current_balance = float(user_account.get("balance", 0))

    # New balance
    new_balance = current_balance + amount

    # Update MongoDB
    await accounts_collection.update_one(
        {"_id": user_id},
        {
            "$set": {
                "balance": new_balance
            }
        }
    )

    return {
        "message": "Wallet topped up successfully",
        "user_id": user_id,
        "old_balance": current_balance,
        "new_balance": new_balance
    }


# ------------------------------------------------
# PAYMENT + SPARE CHANGE INVESTMENT
# ------------------------------------------------

@router.post("/pay")
async def make_payment(user_id: str, merchant_upi: str, amount: float):

    rounding_data = calculate_rounding(amount)
    spare_change = rounding_data["spare"]

    # Correct user account ID
    user_account_id = user_id

    # Find user wallet
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
        await update_user_investment(
    user_id,
    spare_change
)

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
        "message": "Payment processed successfully",
        "payment_id": str(result.inserted_id),
        "investment_mode": investment_mode,
        "rounding": rounding_data
    }
@router.get("/balance/{user_id}")
async def get_balance(user_id: str):

    user = await accounts_collection.find_one({"_id": user_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user_id,
        "balance": user["balance"],
        "currency": user["currency"]
    }
@router.get("/transactions/{user_id}")
async def get_transactions(user_id: str):

    payments = await payments_collection.find(
        {"user_id": user_id}
    ).to_list(length=100)

    for payment in payments:
        payment["_id"] = str(payment["_id"])

    return payments

@router.post("/create-user")
async def create_user(user_id: str):

    existing = await accounts_collection.find_one({"_id": user_id})

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = {
        "_id": user_id,
        "type": "user",
        "balance": 0,
        "currency": "INR"
    }

    await accounts_collection.insert_one(user)

    return {
        "message": "User created successfully"
    }
    
@router.post("/signup")
async def signup(
    username: str,
    password: str
):

    existing_user = await users_collection.find_one({
        "_id": username
    })

    existing_wallet = await accounts_collection.find_one({
        "_id":username
    })
    
    if existing_user or existing_wallet:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    hashed_password = hash_password(password)

    user_doc = {
        "_id": username,
        "password": hashed_password
    }

    await users_collection.insert_one(user_doc)

    wallet_doc = {
        "_id": username,
        "type": "user",
        "balance": 0,
        "currency": "INR"
    }

    await accounts_collection.insert_one(wallet_doc)

    return {
        "message": "Signup successful"
    }
    
@router.post("/login")
async def login(
    username: str,
    password: str
):

    user = await users_collection.find_one({
        "_id": username
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    valid_password = verify_password(
        password,
        user["password"]
    )

    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = create_access_token({
        "sub": username
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str):

    investment = await user_investments_collection.find_one({
        "_id": user_id
    })

    if not investment:

        return {
            "user_id": user_id,
            "total_invested": 0,
            "gold_grams": 0,
            "portfolio_value": 0,
            "profit_loss": 0
        }

    from app.services.gold_price_service import (
        get_live_gold_price
    )

    current_gold_price = get_live_gold_price()

    gold_grams = investment.get(
        "gold_grams",
        0
    )

    portfolio_value = (
        gold_grams * current_gold_price
    )

    total_invested = investment.get(
        "total_invested",
        0
    )

    profit_loss = (
        portfolio_value - total_invested
    )

    return {
        "user_id": user_id,
        "total_invested": total_invested,
        "gold_grams": gold_grams,
        "current_gold_price": current_gold_price,
        "portfolio_value": portfolio_value,
        "profit_loss": profit_loss
    }