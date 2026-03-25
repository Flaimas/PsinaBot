import json
import logging
import traceback

from fastapi import FastAPI, Request, HTTPException

from database.database import succeeded_transaction
from services.payment import successful_payment
from yookassa.domain.notification import WebhookNotification
from bot_instance import bot

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    try:
        notification = WebhookNotification(json.loads(body))
    except Exception as e:
        logging.error(f"Webhook error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400)
    try:
        payment_id = notification.object.id
        if notification.event == 'payment.succeeded':
            success = await succeeded_transaction(payment_id)
            if success:
                user_id, tariff, day = success
                await successful_payment(bot, user_id, tariff, day, payment_id)
            else:
                logging.error(f'Ошибка! Success == None!')

    except Exception as e:
        logging.error(f"Payment processing error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500)

    return {"status": "ok"}