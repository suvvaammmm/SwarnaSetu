from fastapi import FastAPI
from app.services.account_service import initialize_system_accounts
from app.routers import payment   # 👈 ADD THIS

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await initialize_system_accounts()

# 👇 ADD THIS
app.include_router(payment.router)
