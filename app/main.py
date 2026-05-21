from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.gold_price_service import get_live_gold_price
from app.services.account_service import initialize_system_accounts
from app.routers import payment

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await initialize_system_accounts()

@app.get("/")
async def root():
    return {"message": "SwarnaSetu API Running Successfully"}

app.include_router(payment.router)

@app.get("/gold-price")
def gold_price():

    price = get_live_gold_price()

    return {
        "price_per_gram": price
    }