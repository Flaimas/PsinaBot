import json
import logging
import traceback

from fastapi import FastAPI, Request, HTTPException
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
        get_metadata = notification.object.metadata
        user_id = int(get_metadata.get('user_id'))
        tariff = get_metadata.get('tariff')
        day = int(get_metadata.get('day'))

        if notification.event == 'payment.succeeded':
            await successful_payment(bot, user_id, tariff, day)

    except Exception as e:
        logging.error(f"Payment processing error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500)

    return {"status": "ok"}