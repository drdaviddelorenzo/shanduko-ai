from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
import asyncio

from config import VERIFY_TOKEN
from database import init_db, save_message, get_history
from ai_engine import get_ai_response
from whatsapp import send_message

app = FastAPI(title="Shanduko AI", description="SRH WhatsApp Chatbot for Zimbabwean Youth")


@app.on_event("startup")
def startup():
    init_db()


# Webhook verification (Meta calls this when you register the webhook)
@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


# Incoming messages handler
@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()

    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # Ignore status updates (delivered, read receipts)
        if "statuses" in value:
            return {"status": "ok"}

        messages = value.get("messages", [])
        if not messages:
            return {"status": "ok"}

        message = messages[0]
        phone_number = message["from"]
        msg_type = message.get("type")

        if msg_type != "text":
            await send_message(
                phone_number,
                "Hi! I can only read text messages right now. Please type your question and I'll help you."
            )
            return {"status": "ok"}

        user_text = message["text"]["body"].strip()

        # Allow user to reset conversation
        if user_text.lower() in ["reset", "start over", "new chat"]:
            from database import clear_history
            clear_history(phone_number)
            await send_message(phone_number, "Chat cleared! Hi, I'm Shanduko AI. How can I help you today?")
            return {"status": "ok"}

        # Save user message
        save_message(phone_number, "user", user_text)

        # Get conversation history
        history = get_history(phone_number, limit=10)

        # Get AI response
        ai_reply = get_ai_response(phone_number, user_text, history[:-1])

        # Save AI response
        save_message(phone_number, "assistant", ai_reply)

        # Send reply via WhatsApp
        await send_message(phone_number, ai_reply)

    except (KeyError, IndexError):
        pass

    return {"status": "ok"}


@app.get("/")
def health_check():
    return {"status": "Shanduko AI is running", "version": "1.0.0"}
