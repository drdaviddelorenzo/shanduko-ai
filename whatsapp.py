import httpx
from config import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID

BASE_URL = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"


async def send_message(to: str, text: str):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
