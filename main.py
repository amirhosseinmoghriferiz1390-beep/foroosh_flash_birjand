import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
title="Flash Birjand Orders",
version="1.0.0"
)

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=False,
allow_methods=["*"],
allow_headers=["*"],
)

RUBIKA_TOKEN = os.getenv("RUBIKA_TOKEN", "")
RUBIKA_CHAT_ID = os.getenv("RUBIKA_CHAT_ID", "")

RUBIKA_API = "https://botapi.rubika.ir/v3"

class Order(BaseModel):
name: str = Field(..., min_length=2, max_length=100)
phone: str = Field(..., min_length=5, max_length=30)
product: str = Field(..., min_length=1, max_length=200)
quantity: int = Field(..., ge=1, le=100)
description: str = Field(default="", max_length=1000)

@app.get("/")
async def home():
return {
"service": "Flash Birjand Orders",
"status": "online"
}

@app.get("/health")
async def health():
return {
"status": "ok",
"rubika_configured": bool(RUBIKA_TOKEN and RUBIKA_CHAT_ID)
}

async def send_to_rubika(message: str):

```
if not RUBIKA_TOKEN:
    raise HTTPException(
        status_code=500,
        detail="RUBIKA_TOKEN تنظیم نشده است."
    )

if not RUBIKA_CHAT_ID:
    raise HTTPException(
        status_code=500,
        detail="RUBIKA_CHAT_ID تنظیم نشده است."
    )

url = f"{RUBIKA_API}/{RUBIKA_TOKEN}/sendMessage"

payload = {
    "chat_id": RUBIKA_CHAT_ID,
    "text": message
}

try:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            url,
            json=payload
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail="ارسال پیام به روبیکا ناموفق بود."
        )

    return response.json()

except httpx.RequestError:
    raise HTTPException(
        status_code=502,
        detail="ارتباط با سرور روبیکا برقرار نشد."
    )
```

@app.post("/orders")
async def create_order(order: Order):

```
message = (
    "🛍️ سفارش جدید — فلش بیرجند\n\n"
    f"👤 نام مشتری:\n{order.name}\n\n"
    f"📞 شماره تماس:\n{order.phone}\n\n"
    f"💾 محصول:\n{order.product}\n\n"
    f"🔢 تعداد:\n{order.quantity}\n\n"
    f"📝 توضیحات:\n"
    f"{order.description or 'بدون توضیحات'}\n\n"
    "━━━━━━━━━━━━━━\n"
    "🌐 ثبت شده از سایت فلش بیرجند"
)

await send_to_rubika(message)

return {
    "success": True,
    "message": "سفارش با موفقیت ثبت شد."
}
```
